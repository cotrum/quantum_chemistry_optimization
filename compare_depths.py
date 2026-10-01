"""
Depth comparison: constant-depth dynamic circuits vs. CNOT-ladder Pauli exponentials.

    python compare_depths.py                   # all cases, fault-tolerant variant (default)
    python compare_depths.py --variant nisq    # NISQ variant (θ rotation as a single-qubit gate)
    python compare_depths.py --variant nisq_compact   # NISQ-compact variant
    python compare_depths.py --no-draw         # table only
    python compare_depths.py --max-weight 12
    python compare_depths.py --backend <name> --instance <CRN>   # other instance, same saved API key

Variants (separate modules): ft = pauli_exp_dynamic.py (paper Fig. 1, |θ> ancilla, ROT rule),
nisq = pauli_exp_nisq.py (paper Fig. 1 with the θ rotation as a single-qubit gate on q_last),
nisq_compact = pauli_exp_nisq_compact.py (nisq with XX layer 1 as a gate, layers 3+4 as one measurement).
Output folder: depth_comparison_<variant>_<backend>/ (e.g. depth_comparison_nisq_ibm_rensselaer/).

For every case it

1. builds exp(-i θ P) (or a product of terms) two ways:
     * dynamic   : the chosen variant's builder (ft: ROT rule with the |θ> ancilla at the end of
                   each chain; nisq: Rz(±2θ) on the last chain qubit) on the lowest-error patch of the
                   chip, chosen once and frozen in layouts.json (--refresh-layouts to re-choose)
     * CNOT ladder: basis change + CX ladder + Rz(2θ) + un-ladder + basis change
2. computes 2-qubit depth (plus total depth, 2q count, measurement layers, if_else count)
   for the untranspiled and the transpiled (ibm_rensselaer) circuits
     * dynamic   untranspiled: already on physical qubits/couplers (CX basis)
     * ladder    untranspiled: logical, all-to-all
     * dynamic   transpiled  : trivial layout pinned (no routing needed), opt level 3
     * ladder    transpiled  : transpiler picks layout + routing (NOT pinned), opt level 3, best of 5 seeds
3. dumps labelled diagrams into <out>/figures/<case>/
     01_dynamic_circuit.png     dynamic circuit (physical qubits, with layer barriers)
     02_ladder_circuit.png      CNOT-ladder circuit (Qiskit PauliEvolutionGate, CNOT-chain synthesis, logical qubits)
     03_dynamic_layout.png      chip layout + routed chain for every term of the dynamic circuit
     04_ladder_layout.png       chip layout of the transpiled ladder (placement + couplers used)
     04b_dynamic_transpiled_layout.png  same picture for the transpiled dynamic circuit
     05_dynamic_transpiled.png  dynamic circuit transpiled for the backend (ISA: native gates)
     06_ladder_transpiled.png   CNOT ladder transpiled for the backend (ISA: native gates)
   plus <out>/circuits/<case>.qpy = [dynamic, dynamic ISA, ladder, ladder ISA].
   and every diagram again, in order, in <out>/all_diagrams.pdf.

Outputs: <out>/results.csv, results.md and summary plots
    summary_depth.png, summary_2q_depth.png, summary_gate_count.png, summary_2q_count.png
        (vs Pauli weight for exp(-iθ Z⊗w); dynamic/ladder x untranspiled/transpiled)
    summary_all.png        the four above in one 2x2 figure
    summary_all_cases.png  every case (incl. mixed/gapped/product), transpiled, grouped bars
    python compare_depths.py --replot [--variant nisq]   redraws them from results.csv without the backend
Metrics (standard QuantumCircuit methods): 2q depth = qc.depth(lambda instr: len(instr.qubits) == 2),
2q gates = qc.num_nonlocal_gates(), depth = qc.depth(), gate count = count_ops() without
measure/reset/barrier/delay/if_else (gates inside if_else blocks are not included).
"""
from __future__ import annotations

import argparse
import csv
import math
import os
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from qiskit import qpy

from pauli_exp_dynamic import GridDevice, parse_terms
from pauli_bench import (BACKEND_NAME, LAYOUT_FILE, VARIANT_NAMES, add_variant_args, builder, construction_info,
                         add_service_args, check_trivial_layout, draw_dynamic_layout,
                         draw_grid_usage, get_backend, get_layout, ladder_circuit, metrics, terms_label,
                         transpile_dynamic, transpile_ladder)

THETA = 0.4
OUT = "depth_comparison"  # set in main(): depth_comparison_<variant>_<backend>


def cases(max_weight: int):
    """(case_name, list-of-(pauli, theta), num_logical, family)"""
    out = []
    for w in (2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 25):
        if w <= max_weight:
            out.append((f"Z{w}", [("Z" * w, THETA)], w, "Z-string"))
    if max_weight >= 8:
        out.append(("XYZXYZXY", [("XYZXYZXY", THETA)], 8, "mixed"))
        out.append(("ZIIXIYIZ_gapped", [("ZIIXIYIZ", THETA)], 8, "gapped (identity padding)"))
    if max_weight >= 5:
        out.append(("XZZZX+YZZZY", [("XZZZX", THETA), ("YZZZY", THETA)], 5, "2-term product"))
    return out


def gate_summary(qc) -> str:
    """Top-level gate counts, e.g. 'cz:14 rz:20 sx:16 measure:6 if_else:7'."""
    ops = {k: v for k, v in qc.count_ops().items() if k != "barrier"}
    return " ".join(f"{k}:{v}" for k, v in sorted(ops.items(), key=lambda kv: -kv[1]))


def save(fig, path, pdf, dpi=110):
    # fold=-1 gives very wide figures: stay under matplotlib's 65536-pixel limit
    dpi = min(dpi, int(60000 / max(fig.get_size_inches())))
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def draw_circuit(qc, title, path, pdf, fold=-1):
    fig = qc.draw("mpl", idle_wires=False, fold=fold)
    fig.suptitle(title, fontsize=14, x=0.02, ha="left", y=1.0)
    save(fig, path, pdf)


def main():
    global OUT
    ap = argparse.ArgumentParser()
    add_service_args(ap)
    add_variant_args(ap)
    ap.add_argument("--max-weight", type=int, default=25)
    ap.add_argument("--no-draw", action="store_true")
    ap.add_argument("--refresh-layouts", action="store_true",
                    help=f"re-choose the lowest-error patches from today's calibration and overwrite {LAYOUT_FILE}")
    ap.add_argument("--replot", action="store_true",
                    help="only redraw the summary plots from depth_comparison/results.csv")
    args = ap.parse_args()
    OUT = f"depth_comparison_{args.variant}_{args.backend}"
    vname = VARIANT_NAMES[args.variant]
    if args.replot:
        return replot(args.backend, vname)

    os.makedirs(f"{OUT}/figures", exist_ok=True)
    backend = get_backend(args.backend, args.instance)
    device = GridDevice.from_coupling_map(backend.coupling_map)
    build = builder(args.variant)
    print(f"dynamic circuits: {vname}; results in {OUT}/")
    print(f"{backend.name}: {device.rows}x{device.cols} grid, {backend.num_qubits} qubits, "
          f"basis {sorted(backend.target.operation_names)}")
    print("   (all 'transpiled' numbers below are for ISA circuits on this backend's target: "
          "native gates, real coupling map)")

    rows = []
    refreshed = set()
    pdf = None if args.no_draw else PdfPages(f"{OUT}/all_diagrams.pdf")
    for name, spec, n, family in cases(args.max_weight):
        t0 = time.time()
        terms = parse_terms(spec)
        weight = max(len(t) for t, _ in terms)
        label = terms_label(terms)
        layout = get_layout(device, backend, n, refresh=args.refresh_layouts and n not in refreshed)
        refreshed.add(n)
        print(f"{name}: logical->physical {layout.physical_qubits}  (from {LAYOUT_FILE})")

        # --- build -------------------------------------------------------------
        prog_draw = build(spec, layout=layout, barriers=True)
        prog = build(spec, layout=layout, barriers=False)
        dyn = prog.to_qiskit(name=f"dynamic_{name}")
        lad = ladder_circuit(terms, n, name=f"ladder_{name}")

        # --- transpile ---------------------------------------------------------
        dyn_isa = transpile_dynamic(dyn, backend)
        check_trivial_layout(dyn_isa, backend.num_qubits)
        lad_isa = transpile_ladder(lad, backend)  # free layout: transpiler chooses placement + routing

        os.makedirs(f"{OUT}/circuits", exist_ok=True)
        with open(f"{OUT}/circuits/{name}.qpy", "wb") as fq:
            qpy.dump([dyn, dyn_isa, lad, lad_isa], fq)  # untranspiled / ISA, dynamic then ladder

        m = {
            ("dynamic", "untranspiled"): metrics(dyn),
            ("dynamic", "transpiled"): metrics(dyn_isa),
            ("ladder", "untranspiled"): metrics(lad),
            ("ladder", "transpiled"): metrics(lad_isa),
        }
        for (kind, stage), mm in m.items():
            circ = {("dynamic", "untranspiled"): dyn, ("dynamic", "transpiled"): dyn_isa,
                    ("ladder", "untranspiled"): lad, ("ladder", "transpiled"): lad_isa}[kind, stage]
            rows.append(dict(case=name, family=family, paulis=label, num_logical=n, weight=weight,
                             circuit=kind, stage=stage, **mm, gates=gate_summary(circ)))
        print(f"   ISA gates  dynamic: {gate_summary(dyn_isa)}   ladder: {gate_summary(lad_isa)}")
        print(f"{name:18s} w={weight:2d} | 2q depth  dynamic {m['dynamic','untranspiled']['2q_depth']:3d} -> "
              f"{m['dynamic','transpiled']['2q_depth']:3d}   ladder {m['ladder','untranspiled']['2q_depth']:3d} -> "
              f"{m['ladder','transpiled']['2q_depth']:3d}   ({time.time() - t0:.1f}s)")

        # --- diagrams ----------------------------------------------------------
        if pdf is None:
            continue
        d = f"{OUT}/figures/{name}"
        os.makedirs(d, exist_ok=True)
        head = f"exp(-i θ P), θ={THETA}:  P = {label}   ({n} logical qubits)"
        draw_circuit(prog_draw.to_qiskit(name=f"dynamic_{name}"),
                     f"[{name}] DYNAMIC constant-depth circuit, {vname} (untranspiled, physical qubits of {backend.name})\n"
                     f"{head}\n2q depth {m['dynamic','untranspiled']['2q_depth']}, "
                     f"{m['dynamic','untranspiled']['measurements']} mid-circuit measurements, "
                     f"logical→physical {layout.physical_qubits}",
                     f"{d}/01_dynamic_circuit.png", pdf)
        draw_circuit(lad,
                     f"[{name}] CNOT-LADDER circuit (Qiskit PauliEvolutionGate, CNOT-chain synthesis; "
                     f"untranspiled, logical qubits, all-to-all)\n"
                     f"{head}\n2q depth {m['ladder','untranspiled']['2q_depth']}",
                     f"{d}/02_ladder_circuit.png", pdf)

        draw_circuit(dyn_isa,
                     f"[{name}] DYNAMIC circuit, {vname}, TRANSPILED for {backend.name} (ISA: {gate_summary(dyn_isa)})\n"
                     f"{head}\n2q depth {m['dynamic','transpiled']['2q_depth']}, total depth {m['dynamic','transpiled']['depth']}",
                     f"{d}/05_dynamic_transpiled.png", pdf)
        draw_circuit(lad_isa,
                     f"[{name}] CNOT-LADDER circuit TRANSPILED for {backend.name} (ISA: {gate_summary(lad_isa)})\n"
                     f"{head}\n2q depth {m['ladder','transpiled']['2q_depth']}, total depth {m['ladder','transpiled']['depth']}",
                     f"{d}/06_ladder_transpiled.png", pdf)

        # dynamic layout (chip frame, physical numbering): one panel per term
        nt = len(prog.term_info)
        ncol = min(nt, 3)
        nrow = math.ceil(nt / ncol)
        fig, axs = plt.subplots(nrow, ncol, squeeze=False,
                                figsize=(ncol * (device.cols * 0.62 + 1.5), nrow * (device.rows * 0.62 + 1.6)))
        for k, info in enumerate(prog.term_info):
            draw_dynamic_layout(device, layout, info, ax=axs[k // ncol][k % ncol],
                                title=f"term {k}: {terms_label([(info['term'], info['theta'])])}\n"
                                      f"chain length {len(info['chain'])}, {len(info['ancillas'])} ancillas, "
                                      f"{len(info['fillers'])} |0> fillers")
        for k in range(nt, nrow * ncol):
            axs[k // ncol][k % ncol].axis("off")
        fig.suptitle(f"[{name}] DYNAMIC circuit layout, {vname}, on {backend.name} (chip frame; small grey = physical qubit)\n"
                     f"logical→physical {layout.physical_qubits}\n"
                     f"orange = logical qubits (numbered), blue dots = XX/ZZ ancillas, "
                     f"hollow = |0> fillers, " + ("green θ = |θ> ancilla, " if args.variant == "ft" else "")
                     + "blue line = chain", fontsize=10)
        save(fig, f"{d}/03_dynamic_layout.png", pdf)

        fig, ax = plt.subplots(figsize=(device.cols * 0.62 + 1.5, device.rows * 0.62 + 1.8))
        extra = m["ladder", "transpiled"]["2q_count"] - m["ladder", "untranspiled"]["2q_count"]
        draw_grid_usage(device, lad_isa, ax=ax,
                        title=f"[{name}] CNOT-LADDER transpiled for {backend.name}: layout + couplers used\n"
                              f"initial logical→physical {list(lad_isa.layout.initial_index_layout(filter_ancillas=True))} "
                              f"(chosen by the transpiler)\n"
                              f"orange = initial logical placement, dashed = final placement after routing, "
                              f"line width ∝ #2q gates\n2q depth {m['ladder','transpiled']['2q_depth']}, "
                              f"2q gates {m['ladder','transpiled']['2q_count']} "
                              f"({extra:+d} vs. untranspiled from routing)")
        save(fig, f"{d}/04_ladder_layout.png", pdf)

        fig, ax = plt.subplots(figsize=(device.cols * 0.62 + 1.5, device.rows * 0.62 + 1.8))
        draw_grid_usage(device, dyn_isa, ax=ax, placement=layout.physical_qubits,
                        title=f"[{name}] DYNAMIC circuit ({args.variant}) transpiled for {backend.name}: layout + couplers used\n"
                              f"logical→physical {layout.physical_qubits}\n"
                              f"orange = logical qubits (preselected layout, enforced), blue = all other qubits used, "
                              f"line width ∝ #2q gates\n2q depth {m['dynamic','transpiled']['2q_depth']}, "
                              f"2q gates {m['dynamic','transpiled']['2q_count']}")
        save(fig, f"{d}/04b_dynamic_transpiled_layout.png", pdf)

    if pdf is not None:
        pdf.close()

    # --- tables ------------------------------------------------------------------
    keys = list(rows[0])
    with open(f"{OUT}/results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)

    by = {(r["case"], r["circuit"], r["stage"]): r for r in rows}
    names = list(dict.fromkeys(r["case"] for r in rows))
    lines = [
        f"# Dynamic vs CNOT-ladder Pauli exponentials on {backend.name}", "",
        f"Dynamic circuits: {construction_info(variant=args.variant)}", "",
        "2q depth = qc.depth(lambda instr: len(instr.qubits) == 2); 2q gates = qc.num_nonlocal_gates(); "
        "gates = count_ops() without measure/reset/barrier/delay/if_else. "
        "Ladder = Qiskit PauliEvolutionGate with LieTrotter(cx_structure='chain'). Transpiled = ISA circuit for the backend "
        "(dynamic: preselected layout from layouts.json enforced, opt 3; ladder: layout + routing chosen by "
        "the transpiler, opt 3, best of 5 seeds). All diagrams use fold=-1.", "",
        "| case | w | N | 2q depth dyn (untr) | 2q depth dyn (tr) | 2q depth ladder (untr) | 2q depth ladder (tr) "
        "| 2q gates dyn (tr) | 2q gates ladder (tr) | gates dyn (tr) | gates ladder (tr) | depth dyn (tr) | depth ladder (tr) "
        "| mid-circ. meas layers (dyn) "
        "| mid-circ. meas (dyn) | if_else (dyn) | ISA gates dyn | ISA gates ladder |",
        "|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|---|",
    ]
    for c in names:
        du, dt = by[c, "dynamic", "untranspiled"], by[c, "dynamic", "transpiled"]
        lu, lt = by[c, "ladder", "untranspiled"], by[c, "ladder", "transpiled"]
        lines.append(f"| {c} | {du['weight']} | {du['num_logical']} | {du['2q_depth']} | {dt['2q_depth']} | "
                     f"{lu['2q_depth']} | {lt['2q_depth']} | {dt['2q_count']} | {lt['2q_count']} | "
                     f"{dt['gate_count']} | {lt['gate_count']} | "
                     f"{dt['depth']} | {lt['depth']} | {dt['meas_layers']} | {dt['measurements']} | {dt['if_else']} | "
                     f"{dt['gates']} | {lt['gates']} |")
    open(f"{OUT}/results.md", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))

    summary_plots(rows, backend.name, vname)
    print(f"\nwrote {OUT}/results.csv, results.md, summary_*.png"
          + ("" if args.no_draw else ", figures/, all_diagrams.pdf"))


# --- summary plots -------------------------------------------------------------------
METRICS = [("depth", "total depth"), ("2q_depth", "two-qubit depth"),
           ("gate_count", "total gate count"), ("2q_count", "two-qubit gate count")]
STYLE = {  # colour = implementation, line style + marker = stage (identity never colour-only)
    ("dynamic", "untranspiled"): dict(color="#e8743b", ls="--", marker="o", mfc="white"),
    ("dynamic", "transpiled"): dict(color="#e8743b", ls="-", marker="o"),
    ("ladder", "untranspiled"): dict(color="#2f6fb3", ls="--", marker="s", mfc="white"),
    ("ladder", "transpiled"): dict(color="#2f6fb3", ls="-", marker="s"),
}


def _label(kind, stage):
    return f"{'dynamic (constant depth)' if kind == 'dynamic' else 'CNOT ladder'}, {stage}"


def _vs_weight(ax, by, zs, key, ylabel):
    ws = [by[c, "dynamic", "untranspiled"]["weight"] for c in zs]
    for (kind, stage), st in STYLE.items():
        ax.plot(ws, [by[c, kind, stage][key] for c in zs], lw=2, ms=6, label=_label(kind, stage), **st)
    ax.set_xlabel("Pauli weight w   (exp(-iθ Z⊗w))")
    ax.set_ylabel(ylabel)
    ax.set_xticks(ws)
    ax.set_ylim(bottom=0)
    ax.grid(alpha=0.25)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


def summary_plots(rows, backend_name, vname=""):
    """summary_<metric>.png (vs weight, Z strings), summary_all.png (2x2 of those) and
    summary_all_cases.png (every case, transpiled dynamic vs ladder, grouped bars)."""
    by = {(r["case"], r["circuit"], r["stage"]): r for r in rows}
    names = list(dict.fromkeys(r["case"] for r in rows))
    zs = [c for c in names if by[c, "dynamic", "untranspiled"]["family"] == "Z-string"]

    if zs:
        for key, ylabel in METRICS:
            fig, ax = plt.subplots(figsize=(7, 4.5))
            _vs_weight(ax, by, zs, key, ylabel)
            ax.set_title(f"{ylabel[0].upper() + ylabel[1:]} vs Pauli weight — transpiled for {backend_name}\n"
                         f"dynamic: {vname}", fontsize=10)
            ax.legend(frameon=False)
            fig.savefig(f"{OUT}/summary_{key}.png", dpi=150, bbox_inches="tight")
            plt.close(fig)

        fig, axs = plt.subplots(2, 2, figsize=(13, 9))
        for ax, (key, ylabel) in zip(axs.flat, METRICS):
            _vs_weight(ax, by, zs, key, ylabel)
            ax.set_title(ylabel[0].upper() + ylabel[1:])
        h, l = axs[0, 0].get_legend_handles_labels()
        fig.legend(h, l, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.01))
        fig.suptitle(f"Dynamic ({vname}) vs CNOT-ladder exp(-iθ Z⊗w) on {backend_name}", fontsize=13)
        fig.tight_layout(rect=(0, 0.04, 1, 0.97))
        fig.savefig(f"{OUT}/summary_all.png", dpi=150, bbox_inches="tight")
        plt.close(fig)

    # every case (incl. mixed / gapped / product), transpiled only
    fig, axs = plt.subplots(2, 2, figsize=(max(10, 1.0 * len(names) + 4), 9))
    x = list(range(len(names)))
    for ax, (key, ylabel) in zip(axs.flat, METRICS):
        for off, kind in ((-0.2, "dynamic"), (0.2, "ladder")):
            st = STYLE[kind, "transpiled"]
            vals = [by[c, kind, "transpiled"][key] for c in names]
            ax.bar([i + off for i in x], vals, width=0.38, color=st["color"], edgecolor="white", linewidth=1,
                   label=_label(kind, "transpiled"), hatch=None if kind == "dynamic" else "//")
        ax.set_xticks(x, names, rotation=40, ha="right", fontsize=8)
        ax.set_ylabel(ylabel)
        ax.set_title(ylabel[0].upper() + ylabel[1:] + " (transpiled)")
        ax.grid(axis="y", alpha=0.25)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    h, l = axs[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.01))
    fig.suptitle(f"All cases, transpiled for {backend_name}; dynamic: {vname}", fontsize=13)
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    fig.savefig(f"{OUT}/summary_all_cases.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def replot(backend_name, vname=""):
    """Rebuild the summary plots from an existing results.csv (no backend access needed)."""
    rows = []
    with open(f"{OUT}/results.csv") as f:
        for r in csv.DictReader(f):
            for k, v in r.items():
                if v is not None and v.lstrip("-").isdigit():
                    r[k] = int(v)
            rows.append(r)
    if "gate_count" not in rows[0]:
        raise SystemExit("results.csv predates the gate_count column: re-run compare_depths.py once")
    summary_plots(rows, backend_name, vname)
    print(f"wrote {OUT}/summary_*.png")

if __name__ == "__main__":
    main()
