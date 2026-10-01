"""
Dynamic (constant-depth) vs CNOT-ladder Pauli exponentials on the real device.

    python hardware_compare.py                        # θ = 0.4, every case, ONE Sampler job
    python hardware_compare.py --sweep                # θ = π/8, π/4, 3π/8, every case, ONE Sampler job
    python hardware_compare.py --dry-run [--sweep]    # build + transpile + Aer check, no job
    python hardware_compare.py --dd both              # every circuit with AND without dynamical decoupling
    python hardware_compare.py --dd off               # no dynamical decoupling
    python hardware_compare.py --backend <name> --instance <CRN>   # other device, same saved API key
    python hardware_compare.py --variant nisq         # NISQ variant of the dynamic circuits
    python hardware_compare.py --variant nisq_compact # NISQ-compact variant

4000 shots per circuit.

Dynamic circuits, three variants in separate modules (--variant):
    ft    (default) pauli_exp_dynamic.build_program: paper Fig. 1, ROT rule with the |θ> ancilla at
          the end of each chain, P⊗Z_θ parity readout, X readout of the θ-ancilla
    nisq  pauli_exp_nisq.build_nisq_program: paper Fig. 1 with the θ rotation as a single-qubit
          gate, Rz(±2θ) on the last chain qubit (no |θ> ancilla)
    nisq_compact  pauli_exp_nisq_compact.build_compact_program: nisq with XX layer 1 as a gate and
          layers 3+4 (XX, Z readout) as one destructive measurement

Test (exact answer known), for each Pauli string P with support S:

    |psi> = B|+>^S |0>^rest,  P = B Z..Z B^dag       (B = H for X, S·H for Y, 1 for Z)
    apply exp(-i θ P), then H·B^dag on S, measure all logical qubits.

Ideal: 0..0 with prob cos^2θ, 1 on every support qubit (1_S) with prob sin^2θ, nothing else.
The same prep/post wrap both implementations, so the only difference is the exponential itself.
Reported per circuit: Hellinger fidelity to the ideal distribution, P(0..0), P(1_S), leakage
(everything else), and the angle implied by the post-selected populations,
    θ_est = arcsin( sqrt( P(1_S) / (P(0..0) + P(1_S)) ) ).

Layouts: dynamic circuits use the preselected layout from layouts.json (written by
compare_depths.py, or chosen now and saved if missing), enforced. The CNOT ladders are NOT
pinned: the transpiler chooses their layout and routing (best of 5 seeds).

Dynamical decoupling (--dd on, default): X-X sequences are inserted client-side into the
transpiled circuits with qiskit-ibm-runtime's dynamic-circuit-aware passes (ALAPScheduleAnalysis
+ PadDynamicalDecoupling). IBM's server-side DD option does not support dynamic circuits.
The same DD is applied to the CNOT ladders.

Aer check (always, also with --dry-run): every circuit exactly as it will be submitted (transpiled,
with DD) that has at most 20 active qubits is run noise-free in Qiskit Aer (pauli_bench.aer_check):
the outcome probabilities of the logical qubits after every shot (256 shots; mid-circuit
measurements and feed-forward run natively) must equal the ideal ones to 1e-8, and for dynamic
circuits both branches of the ROT correction must occur. Larger circuits are reported as skipped.
If any check fails, nothing is submitted.

Submission: every circuit (cases x θ x dynamic/ladder x DD variants) goes into ONE Sampler job.

Outputs: one folder per device and flag combination:
    hardware_results_<variant>_<backend>_dd-<on|off|both>/       (default)
    hardware_theta_sweep_<variant>_<backend>_dd-<on|off|both>/   (--sweep)
    ... + "_dryrun" with --dry-run (simulator outputs only, no job)
    e.g. hardware_results_ft_ibm_rensselaer_dd-on/, hardware_theta_sweep_nisq_ibm_rensselaer_dd-off_dryrun/
  containing
    aer_check.md, aer_check.csv   Aer check of every circuit as submitted (written before submission)
    job_<id>.json            job id, counts + metadata (not with --dry-run)
    results.md, results.csv
    hardware_compare.png     Hellinger fidelity per case (one θ), or, for several θ,
    sweep_fidelity.png, sweep_angle.png, sweep_leakage.png   (vs θ, one panel per case)
    layouts/<case>.png       preselected layout + transpiled layouts of both circuits (first θ)
    circuits/<case>.qpy      every submitted circuit of that case
    circuits/<case>_<kind>_dd.png   DD circuits as submitted (first θ, fold=-1)
    execution_time.png       circuit execution time vs Pauli weight (Z strings), with the T1/T2 of the qubits
    scheduler_timing.json    IBM's instruction-level schedule of every circuit (not with --dry-run)
    execution_spans.json     the job's execution spans (not with --dry-run)

Execution times (real runs only):
  * circuit time, per circuit: the job is submitted with IBM's scheduler timing on (Sampler option
    experimental.execution.scheduler_timing); IBM returns circuit_duration (in dt) of every circuit:
    one shot as scheduled by the control system, from the first gate to the final readout, incl.
    mid-circuit measurements and feed-forward latencies -- the time the qubits must stay coherent.
    Reported next to the median T1 / T2 of the qubits the circuit uses.
  * wall-clock per shot, job average: from the job's execution spans (IBM runs all circuits of a job in
    the same spans, so there is no per-circuit value); it adds readout, reset and the wait between
    shots to the circuit time. Reported once per job, with the QPU usage.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import statistics

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from qiskit import ClassicalRegister, QuantumCircuit, qpy
from qiskit.quantum_info import hellinger_fidelity

from pauli_exp_dynamic import GridDevice, parse_terms
from pauli_bench import (LAYOUT_FILE, VARIANT_NAMES, add_dd_args, add_service_args, add_variant_args, aer_check,
                         aer_probabilities, apply_dd, builder,
                         check_trivial_layout, construction_info, dd_variants, draw_dynamic_layout,
                         draw_grid_usage, get_backend, get_layout, ladder_circuit, metrics,
                         parity_prep_post, terms_label, transpile_dynamic, transpile_ladder)

THETA = 0.4                                             # default (no --sweep)
SWEEP_THETAS = (math.pi / 8, math.pi / 4, 3 * math.pi / 8)  # default with --sweep
SHOTS = 4000
AER_SHOTS = 256       # Aer check: shots per dynamic circuit (each shot checked exactly)
AER_MAX_QUBITS = 20   # Aer check: circuits with more active qubits are skipped
PREFIX = {False: "hardware_results", True: "hardware_theta_sweep"}  # folder: <prefix>_<variant>_<backend>_dd-<mode>

# (name, pauli label, num logical)  -- label: rightmost char = logical qubit 0
CASES = [
    ("Z3", "ZZZ", 3),
    ("Z5", "ZZZZZ", 5),
    ("Z8", "ZZZZZZZZ", 8),
    ("Z12", "Z" * 12, 12),
    ("XYZXYZXY", "XYZXYZXY", 8),
    ("XZIY_gapped", "XZIY", 4),
    ("XYIZIX_gapped", "XYIZIX", 6),
    ("ZIIXIYIZ_gapped", "ZIIXIYIZ", 8),
]


def out_dir(backend_name: str, sweep: bool, dd_mode: str, variant: str, dry_run: bool) -> str:
    """Results folder named after the device and the flags (dry runs get their own folder)."""
    return f"{PREFIX[sweep]}_{variant}_{backend_name}_dd-{dd_mode}" + ("_dryrun" if dry_run else "")


def theta_label(th: float) -> str:
    for k in range(1, 8):
        if abs(th - k * math.pi / 8) < 1e-9:
            return {1: "π/8", 2: "π/4", 3: "3π/8", 4: "π/2", 5: "5π/8", 6: "3π/4", 7: "7π/8"}[k]
    return f"{th:.3f}"


# ----------------------------------------------------------------------------
# Build
# ----------------------------------------------------------------------------
def build(backend, device, cases, thetas, out, dd_mode="on", variant="ft"):
    """Build, transpile and Aer-check every circuit. Returns (circuits, meta, names of failed Aer checks)."""
    build_dynamic = builder(variant)
    circuits, meta, failed = [], [], []
    os.makedirs(f"{out}/circuits", exist_ok=True)
    for name, label, n in cases:
        layout = get_layout(device, backend, n)  # same frozen layout as compare_depths.py
        phys = [int(q) for q in layout.physical_qubits]
        submitted = []
        for t, th in enumerate(thetas):
            terms = parse_terms([(label, th)])
            prep, post = parity_prep_post(terms, n)

            prog = build_dynamic(terms, layout=layout, barriers=False)
            dyn = prog.to_qiskit(prep=prep, post=post, measure=True, name=f"dynamic_{name}_{th:.4f}")

            full = QuantumCircuit(n, name=f"ladder_{name}_{th:.4f}")
            full.compose(prep, inplace=True)
            full.compose(ladder_circuit(terms, n), inplace=True)
            full.compose(post, inplace=True)
            ideal = aer_probabilities(full)  # exact, from the Qiskit Aer statevector of the ladder circuit
            full.add_register(ClassicalRegister(n, "meas"))
            full.measure(range(n), full.cregs[0])

            dyn_isa = transpile_dynamic(dyn, backend)
            check_trivial_layout(dyn_isa, backend.num_qubits)
            lad_isa = transpile_ladder(full, backend)  # free layout: transpiler chooses placement + routing
            lad_phys = [int(q) for q in lad_isa.layout.initial_index_layout(filter_ancillas=True)]
            if t == 0:
                print(f"{name}: dynamic logical->physical {phys} (from {LAYOUT_FILE}, enforced); "
                      f"ladder {lad_phys} (chosen by the transpiler)")
                save_layout_figure(device, backend.name, out, name, th, layout, prog, dyn_isa, lad_isa, variant)
            masks = [info["rot_parity_mask"] for info in prog.term_info]
            for kind, isa, lay in (("dynamic", dyn_isa, phys), ("ladder", lad_isa, lad_phys)):
                mm = metrics(isa)  # gate metrics of the circuit itself (before DD padding)
                t1_us, t2_us = coherence_us(isa, backend)
                for dd in dd_variants(dd_mode):
                    circ = apply_dd(isa, backend) if dd else isa
                    n_dd = circ.count_ops().get("x", 0) - isa.count_ops().get("x", 0)
                    chk = aer_check(circ, ideal, rot_masks=masks if kind == "dynamic" else (),
                                    shots=AER_SHOTS, max_qubits=AER_MAX_QUBITS)
                    circuits.append(circ)
                    submitted.append(circ)
                    meta.append(dict(case=name, pauli=label, support=terms_label(terms), num_logical=n,
                                     circuit=kind, variant=variant if kind == "dynamic" else None, dd=dd, dd_pulses=n_dd, theta=th, ideal=ideal,
                                     logical_to_physical=lay, aer=chk["status"], aer_qubits=chk["qubits"],
                                     aer_shots=chk["shots"], aer_fired=chk["fired"], aer_max_dev=chk["max_dev"],
                                     t1_us=t1_us, t2_us=t2_us, **mm))
                    tag = f"{name} θ={theta_label(th)} {kind} DD {'on' if dd else 'off'}"
                    if chk["status"] == "skipped":
                        aer = f"Aer: skipped ({chk['qubits']} active qubits > {AER_MAX_QUBITS})"
                    else:
                        aer = (f"Aer: {chk['status'].upper()} ({chk['qubits']} qubits, {chk['shots']} shot(s)"
                               + (f", ROT fired on {chk['fired']}" if kind == "dynamic" else "")
                               + f", max |p - p_ideal| = {chk['max_dev']:.1e})")
                        if chk["status"] == "FAIL":
                            failed.append(tag)
                    print(f"{name:16s} θ={theta_label(th):>6s} {kind:8s} DD {'on ' if dd else 'off'} "
                          f"({n_dd:4d} X pulses)  2q depth {mm['2q_depth']:3d}  2q gates {mm['2q_count']:3d}  "
                          f"depth {mm['depth']:4d}  meas {mm['measurements']:3d}   {aer}")
                    if dd and t == 0:
                        draw_submitted(circ, f"{out}/circuits/{name}_{kind}_dd.png",
                                       f"[{name}] {kind.upper()} with dynamical decoupling (X-X), θ={theta_label(th)}, "
                                       f"as submitted to {backend.name}: {n_dd} DD pulses")
        with open(f"{out}/circuits/{name}.qpy", "wb") as f:
            qpy.dump(submitted, f)
    return circuits, meta, failed


def coherence_us(isa, backend):
    """Median T1 and T2 (µs) of the qubits the circuit uses, from the backend target (current calibration)."""
    props = getattr(backend.target, "qubit_properties", None) or []
    used = sorted({isa.find_bit(q).index for ins in isa.data for q in ins.qubits})

    def med(attr):
        v = [getattr(props[q], attr, None) for q in used if q < len(props) and props[q] is not None]
        v = [x for x in v if x]
        return statistics.median(v) * 1e6 if v else float("nan")

    return med("t1"), med("t2")


def circuit_duration_dt(scheduler_timing):
    """Duration of one shot of a circuit in dt, from IBM's scheduler timing: its circuit_duration field, or
    else the latest end time (T0 + Duration) over the instruction rows of the timing table."""
    if not scheduler_timing:
        return None
    if scheduler_timing.get("circuit_duration") is not None:
        return int(scheduler_timing["circuit_duration"])
    timing = scheduler_timing.get("timing") or []
    lines = timing if isinstance(timing, list) else str(timing).splitlines()
    end = None
    for line in lines:
        f = [x.strip() for x in str(line).split(",")]
        try:
            e = int(float(f[3])) + int(float(f[4]))  # Branch, Instruction, Channel, T0, Duration, Pulse
        except (IndexError, ValueError):
            continue  # header or other non-data row
        end = e if end is None else max(end, e)
    return end


def job_wallclock_us(result):
    """Average wall-clock time per shot (µs) over the whole job, from its execution spans (IBM runs all
    circuits of a job in the same spans, so this is a job-level number only)."""
    spans = (result.metadata.get("execution") or {}).get("execution_spans")
    if not spans:
        return float("nan"), []
    raw = [dict(start=str(sp.start), stop=str(sp.stop), duration_s=float(sp.duration), size=int(sp.size))
           for sp in spans]
    shots = sum(r["size"] for r in raw)
    return (sum(r["duration_s"] for r in raw) / shots * 1e6 if shots else float("nan")), raw


def write_aer_report(meta, out, backend_name, construction):
    """<out>/aer_check.md + .csv: the Aer check of every circuit exactly as it is (or would be) submitted."""
    rows = [dict(case=m["case"], theta=theta_label(m["theta"]), circuit=m["circuit"], dd="on" if m["dd"] else "off",
                 aer=m["aer"], active_qubits=m["aer_qubits"], shots=m["aer_shots"], sign_correction_fired=m["aer_fired"],
                 max_dev=m["aer_max_dev"], twoq_depth=m["2q_depth"], twoq_count=m["2q_count"], depth=m["depth"],
                 measurements=m["measurements"], layout=" ".join(map(str, m["logical_to_physical"]))) for m in meta]
    with open(f"{out}/aer_check.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    lines = [f"# Aer check of the circuits for {backend_name}", "",
             f"Dynamic circuits: {construction}", "",
             f"Noise-free Qiskit Aer run of every circuit exactly as submitted (transpiled, with DD if on). "
             f"ok = on every shot the logical-qubit outcome probabilities equal the ideal ones (max |p - p_ideal| "
             f"< 1e-8) and, for dynamic circuits, both branches of the sign correction occurred; skipped = more "
             f"than {AER_MAX_QUBITS} active qubits.", "",
             "| case | θ | circuit | DD | Aer | active qubits | shots | sign correction fired | max abs(p − p_ideal) "
             "| 2q depth | 2q gates | depth | measurements | layout |",
             "|---|--:|---|---|---|--:|--:|--:|--:|--:|--:|--:|--:|---|"]
    for r in rows:
        dev = "–" if r["aer"] == "skipped" else f"{r['max_dev']:.1e}"
        fired = r["sign_correction_fired"] if r["circuit"] == "dynamic" and r["aer"] != "skipped" else "–"
        lines.append(f"| {r['case']} | {r['theta']} | {r['circuit']} | {r['dd']} | {r['aer']} | {r['active_qubits']} | "
                     f"{r['shots'] or '–'} | {fired} | {dev} | {r['twoq_depth']} | {r['twoq_count']} | {r['depth']} | "
                     f"{r['measurements']} | {r['layout']} |")
    open(f"{out}/aer_check.md", "w").write("\n".join(lines) + "\n")
    print(f"wrote {out}/aer_check.md, aer_check.csv")


def draw_submitted(circ, path, title):
    try:
        fig = circ.draw("mpl", idle_wires=False, fold=-1)
    except Exception as e:  # drawing is a convenience; never block the run on it
        print(f"   (could not draw {path}: {e})")
        return
    fig.suptitle(title, fontsize=14, x=0.02, ha="left", y=1.0)
    dpi = min(100, int(60000 / max(fig.get_size_inches())))
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def save_layout_figure(device, backend_name, out, name, th, layout, prog, dyn_isa, lad_isa, variant):
    """<out>/layouts/<case>.png: what is actually submitted, in the chip frame."""
    os.makedirs(f"{out}/layouts", exist_ok=True)
    w, hgt = device.cols * 0.62 + 1.5, device.rows * 0.62 + 2.0
    fig, axs = plt.subplots(1, 3, figsize=(3 * w, hgt))
    phys = [int(q) for q in layout.physical_qubits]
    draw_dynamic_layout(device, layout, prog.term_info[0], ax=axs[0],
                        title=f"DYNAMIC ({VARIANT_NAMES[variant]}): preselected layout + chain"
                              + (" (green θ = |θ> ancilla)" if variant == "ft" else "") + f"\nlogical→physical {phys}")
    draw_grid_usage(device, dyn_isa, ax=axs[1], placement=phys,
                    title="DYNAMIC, transpiled (as submitted):\nqubits + couplers used")
    draw_grid_usage(device, lad_isa, ax=axs[2],
                    title=f"CNOT LADDER, transpiled (as submitted), layout chosen by the transpiler:\n"
                          f"{list(lad_isa.layout.initial_index_layout(filter_ancillas=True))}, dashed = after routing")
    fig.suptitle(f"[{name}] layouts on {backend_name}, θ={theta_label(th)} "
                 f"(small grey numbers = physical qubits)", fontsize=11)
    fig.savefig(f"{out}/layouts/{name}.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------------------
# Analysis
# ----------------------------------------------------------------------------
def analyse(rec, out):
    rows = []
    nan = float("nan")
    dt = rec.get("dt")
    durations = rec.get("circuit_duration_dt") or [None] * len(rec["meta"])
    for m, counts, dur in zip(rec["meta"], rec["counts"], durations):
        tot = sum(counts.values())
        probs = {k: v / tot for k, v in counts.items()}
        n = m["num_logical"]
        zero = "0" * n
        ones = "".join("1" if ch != "I" else "0" for ch in m["pauli"])  # label order == bitstring order
        p0, p1 = probs.get(zero, 0.0), probs.get(ones, 0.0)
        th_est = math.asin(math.sqrt(p1 / (p0 + p1))) if p0 + p1 > 0 else float("nan")
        exec_us = dur * dt * 1e6 if (dur is not None and dt) else nan
        rows.append(dict(case=m["case"], pauli=m["pauli"], circuit=m["circuit"], dd=bool(m["dd"]), dd_pulses=m["dd_pulses"],
                         theta=m["theta"], theta_label=theta_label(m["theta"]),
                         w=sum(ch != "I" for ch in m["pauli"]), n=n,
                         hellinger=hellinger_fidelity(probs, m["ideal"]), p0=p0, p0_ideal=math.cos(m["theta"]) ** 2,
                         p1=p1, p1_ideal=math.sin(m["theta"]) ** 2, leakage=1 - p0 - p1, theta_est=th_est,
                         angle_error=th_est - m["theta"], twoq_depth=m["2q_depth"], twoq_count=m["2q_count"],
                         depth=m["depth"], measurements=m["measurements"], aer=m["aer"],
                         duration_dt=dur, exec_us=exec_us,
                         t1_us=m.get("t1_us", nan), t2_us=m.get("t2_us", nan),
                         exec_over_t2=exec_us / m["t2_us"] if m.get("t2_us", nan) == m.get("t2_us", nan) and m.get("t2_us") else nan,
                         layout=" ".join(map(str, m["logical_to_physical"]))))

    with open(f"{out}/results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    lines = [f"# Dynamic vs CNOT ladder on {rec['backend']} (job {rec['job_id']}), {rec['shots']} shots per circuit", "",
             f"Dynamic circuits: {rec['construction']}", "",
             "Ideal: P(0..0) = cos²θ, P(1_S) = sin²θ, leakage 0. θ_est = arcsin√(P(1_S)/(P(0..0)+P(1_S))).", "",
             "DD = client-side dynamical decoupling (X-X, qiskit-ibm-runtime dynamic-circuit passes); "
             "gate metrics are for the circuit before DD padding.", "",
             f"Aer = noise-free Qiskit Aer check of the submitted circuit before submission (ok / skipped if more "
             f"than {AER_MAX_QUBITS} active qubits).", "",
             "Circuit time = IBM scheduler timing circuit_duration x dt"
             + (f" (dt = {dt * 1e9:.4g} ns)" if dt else " (not available for this job)")
             + ": one shot from the first gate to the final readout, incl. mid-circuit measurements and feed-forward. "
             "T2 = median T2 of the qubits the circuit uses. "
             f"Wall-clock per shot, job average (execution spans; adds readout, reset and the wait between shots): "
             f"{rec.get('wallclock_job_avg_us', nan):.1f} µs"
             + (f"; QPU usage {rec['qpu_seconds']:.0f} s." if rec.get("qpu_seconds") else "."), "",
             "| case | w | θ | circuit | DD | DD pulses | Aer | Hellinger | P(0..0) (ideal) | P(1_S) (ideal) | leakage "
             "| θ_est | θ_est − θ | 2q depth | 2q gates | depth | measurements | circuit time (µs) | T2 (µs) "
             "| circuit time / T2 |",
             "|---|--:|--:|---|---|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|"]
    for r in rows:
        lines.append(f"| {r['case']} | {r['w']} | {r['theta_label']} | {r['circuit']} | {'on' if r['dd'] else 'off'} | "
                     f"{r['dd_pulses']} | {r['aer']} | {r['hellinger']:.3f} | "
                     f"{r['p0']:.3f} ({r['p0_ideal']:.3f}) | {r['p1']:.3f} ({r['p1_ideal']:.3f}) | {r['leakage']:.3f} | "
                     f"{r['theta_est']:.3f} | {r['angle_error']:+.3f} | {r['twoq_depth']} | {r['twoq_count']} | "
                     f"{r['depth']} | {r['measurements']} | {r['exec_us']:.2f} | {r['t2_us']:.0f} | "
                     f"{r['exec_over_t2']:.3f} |")
    open(f"{out}/results.md", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    vname = VARIANT_NAMES[rec["construction"]["variant"]]
    time_plot(rows, rec["backend"], out, vname)
    if len({r["theta"] for r in rows}) == 1:
        bar_plot(rows, rec["backend"], out, vname)
    else:
        sweep_plots(rows, rec["backend"], out, vname)


def bar_plot(rows, backend_name, out, vname):
    names = list(dict.fromkeys(r["case"] for r in rows))
    by = {(r["case"], r["circuit"], r["dd"]): r for r in rows}
    variants = [(k, d) for k in ("dynamic", "ladder") for d in (False, True)
                if any((c, k, d) in by for c in names)]
    width = 0.8 / len(variants)
    fig, ax = plt.subplots(figsize=(max(8, 1.6 * len(names)), 4.4))
    x = list(range(len(names)))
    for j, (kind, dd) in enumerate(variants):
        col = "#e8743b" if kind == "dynamic" else "#2f6fb3"
        off = (j - (len(variants) - 1) / 2) * width
        ax.bar([i + off for i in x], [by[c, kind, dd]["hellinger"] if (c, kind, dd) in by else 0 for c in names],
               width=width * 0.95, color=col, edgecolor="white", linewidth=1, hatch="//" if dd else None,
               label=f"{'dynamic (constant depth)' if kind == 'dynamic' else 'CNOT ladder'}"
                     f"{', with DD' if dd else ', no DD'}")
    ax.set_xticks(x, names, rotation=20)
    ax.set_ylabel("Hellinger fidelity to ideal")
    ax.set_ylim(0, 1)
    ax.set_title(f"exp(-iθP) parity test on {backend_name}, θ={rows[0]['theta_label']}; dynamic: {vname}")
    ax.legend(frameon=False, ncol=2, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    ax.grid(axis="y", alpha=0.3)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.savefig(f"{out}/hardware_compare.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}/results.md, results.csv, hardware_compare.png")


STYLE = {  # colour = implementation, marker fill + line style = DD (identity never colour-only)
    ("dynamic", True): dict(color="#e8743b", marker="o", ls="-", label="dynamic (constant depth), with DD"),
    ("dynamic", False): dict(color="#e8743b", marker="o", ls=":", mfc="white", label="dynamic (constant depth), no DD"),
    ("ladder", True): dict(color="#2f6fb3", marker="s", ls="--", label="CNOT ladder, with DD"),
    ("ladder", False): dict(color="#2f6fb3", marker="s", ls=":", mfc="white", label="CNOT ladder, no DD"),
}


def _panels(rows, key, ylabel, path, title, backend_name, diag=False, ylim=None):
    names = list(dict.fromkeys(r["case"] for r in rows))
    ncol = min(3, len(names))
    nrow = math.ceil(len(names) / ncol)
    fig, axs = plt.subplots(nrow, ncol, figsize=(4.6 * ncol, 3.6 * nrow), squeeze=False, sharey=ylim is not None)
    thetas = sorted({r["theta"] for r in rows})
    for i, c in enumerate(names):
        ax = axs[i // ncol][i % ncol]
        if diag:
            ax.axhline(0, color="#9a9a9a", lw=1, ls=":", label="ideal (no angle error)")
        for (kind, dd), st in STYLE.items():
            pts = sorted((r["theta"], r[key]) for r in rows if r["case"] == c and r["circuit"] == kind and r["dd"] == dd)
            if pts:
                ax.plot([p[0] for p in pts], [p[1] for p in pts], lw=2, ms=6, **st)
        ax.set_xticks(thetas, [theta_label(t) for t in thetas])
        if ylim:
            ax.set_ylim(*ylim)
        ax.set_title(c, fontsize=10)
        ax.set_xlabel("θ")
        if i % ncol == 0:
            ax.set_ylabel(ylabel)
        ax.grid(alpha=0.25)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    for k in range(len(names), nrow * ncol):
        axs[k // ncol][k % ncol].axis("off")
    h, l = axs[0][0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=min(len(l), 2), frameon=False, bbox_to_anchor=(0.5, -0.04))
    fig.suptitle(f"{title} — {backend_name}", fontsize=12)
    fig.tight_layout(rect=(0, 0.05, 1, 0.96))
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def time_plot(rows, backend_name, out, vname):
    """execution_time.png: circuit execution time (IBM scheduler timing) vs Pauli weight for the exp(-iθ Z⊗w)
    cases (mean over θ), dynamic vs CNOT ladder, with the median T2 and T1 of the qubits used as reference
    lines (log scale, since the coherence times are far above the circuit times)."""
    ok = [r for r in rows if r["exec_us"] == r["exec_us"] and set(r["pauli"]) == {"Z"}]
    if not ok:
        print("   (no circuit times for the Z-string cases: execution_time.png not written)")
        return
    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    ws = sorted({r["w"] for r in ok})
    for (kind, dd), st in STYLE.items():
        pts = {}
        for r in ok:
            if r["circuit"] == kind and r["dd"] == dd:
                pts.setdefault(r["w"], []).append(r["exec_us"])
        if not pts:
            continue
        x = sorted(pts)
        y = [statistics.mean(pts[w]) for w in x]
        ax.plot(x, y, lw=2, ms=7, **st)
        ax.annotate(f"{y[-1]:.1f} µs", (x[-1], y[-1]), xytext=(6, 5 if dd else -5), textcoords="offset points",
                    va="center", fontsize=8, color="#444444")
    t2 = statistics.median([r["t2_us"] for r in ok if r["t2_us"] == r["t2_us"]] or [float("nan")])
    t1 = statistics.median([r["t1_us"] for r in ok if r["t1_us"] == r["t1_us"]] or [float("nan")])
    for val, ls, name in ((t2, "--", "T2"), (t1, ":", "T1")):
        if val == val:
            ax.axhline(val, color="#8c8c8c", lw=1.2, ls=ls, zorder=0)
            ax.annotate(f"median {name} of the qubits used: {val:.0f} µs", (ws[0], val), xytext=(0, 4),
                        textcoords="offset points", fontsize=8, color="#444444")
    ax.set_yscale("log")
    ax.set_xticks(ws)
    ax.set_xlim(ws[0] - 0.5, ws[-1] + 2.5)
    ax.set_xlabel("Pauli weight w   (exp(-iθ Z⊗w))")
    ax.set_ylabel("circuit execution time, one shot (µs, log scale)")
    ax.set_title(f"Circuit execution time on {backend_name} (IBM scheduler timing)\ndynamic: {vname}", fontsize=10)
    ax.grid(alpha=0.25, which="both")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2)
    fig.savefig(f"{out}/execution_time.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}/execution_time.png")


def sweep_plots(rows, backend_name, out, vname):
    _panels(rows, "hellinger", "Hellinger fidelity to ideal", f"{out}/sweep_fidelity.png",
            f"exp(-iθP) parity test: fidelity vs θ (dynamic: {vname})", backend_name, ylim=(0, 1))
    _panels(rows, "angle_error", "θ_est − θ  (rad, post-selected)", f"{out}/sweep_angle.png",
            f"Rotation-angle error vs target θ (dynamic: {vname})", backend_name, diag=True)
    _panels(rows, "leakage", "leakage (outside 0..0 and 1_S)", f"{out}/sweep_leakage.png",
            f"Leakage vs θ (dynamic: {vname})", backend_name, ylim=(0, 1))
    print(f"wrote {out}/results.md, results.csv, sweep_fidelity.png, sweep_angle.png, sweep_leakage.png")


# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    add_service_args(ap)  # --backend (device name), --instance (CRN)
    add_dd_args(ap)       # --dd on|off|both
    add_variant_args(ap)  # --variant ft|nisq|nisq_compact
    ap.add_argument("--sweep", action="store_true",
                    help=f"θ sweep (θ = π/8, π/4, 3π/8 instead of {THETA}); results in {PREFIX[True]}_<variant>_<backend>_dd-<mode>/")
    ap.add_argument("--dry-run", action="store_true", help="build + transpile + Aer check only, no job")
    args = ap.parse_args()

    thetas = list(SWEEP_THETAS) if args.sweep else [THETA]
    backend = get_backend(args.backend, args.instance)
    out = out_dir(backend.name, args.sweep, args.dd, args.variant, args.dry_run)
    os.makedirs(out, exist_ok=True)
    print(f"backend {backend.name}, instance {args.instance or '(saved account default)'}, "
          f"θ = {[theta_label(t) for t in thetas]}, {SHOTS} shots, dynamical decoupling: {args.dd}, "
          f"results in {out}/")
    construction = construction_info(variant=args.variant)
    print(f"dynamic circuits: {construction}")
    device = GridDevice.from_coupling_map(backend.coupling_map)
    circuits, meta, failed = build(backend, device, CASES, thetas, out, args.dd, args.variant)
    write_aer_report(meta, out, backend.name, construction)
    n_ok = sum(m["aer"] == "ok" for m in meta)
    print(f"{len(circuits)} circuits, all in one job; Aer check: {n_ok} ok, "
          f"{sum(m['aer'] == 'skipped' for m in meta)} skipped (> {AER_MAX_QUBITS} active qubits), {len(failed)} failed")
    if failed:
        raise SystemExit("Aer check FAILED (nothing submitted):\n  " + "\n  ".join(failed))
    if args.dry_run:
        return
    from qiskit_ibm_runtime import SamplerV2 as Sampler

    sampler = Sampler(mode=backend)
    sampler.options.experimental = {"execution": {"scheduler_timing": True}}  # per-circuit circuit time
    job = sampler.run(circuits, shots=SHOTS)  # ONE job with every circuit
    rec = dict(job_id=job.job_id(), backend=backend.name, instance=args.instance, shots=SHOTS,
               dt=float(getattr(backend.target, "dt", None) or backend.dt),
               sweep=args.sweep, thetas=thetas, construction=construction, meta=meta)
    json.dump(rec, open(f"{out}/job_{job.job_id()}.json", "w"), indent=1)
    print(f"submitted job {job.job_id()}; waiting for results...")

    result = job.result()
    rec["counts"] = [pub.data.meas.get_counts() for pub in result]
    timings = [(pub.metadata.get("compilation") or {}).get("scheduler_timing") for pub in result]
    rec["circuit_duration_dt"] = [circuit_duration_dt(st) for st in timings]
    if not any(d is not None for d in rec["circuit_duration_dt"]):
        print("   (no scheduler timing in the job result metadata: circuit times not available)")
    json.dump([dict(index=i, case=m["case"], theta=m["theta"], circuit=m["circuit"], dd=m["dd"],
                    circuit_duration_dt=d, timing=(st or {}).get("timing"))
               for i, (m, st, d) in enumerate(zip(rec["meta"], timings, rec["circuit_duration_dt"]))],
              open(f"{out}/scheduler_timing.json", "w"), indent=1)
    rec["wallclock_job_avg_us"], spans = job_wallclock_us(result)
    json.dump(spans, open(f"{out}/execution_spans.json", "w"), indent=1)
    try:
        rec["qpu_seconds"] = float(job.usage())
    except Exception:
        pass
    json.dump(rec, open(f"{out}/job_{rec['job_id']}.json", "w"), indent=1)
    analyse(rec, out)


if __name__ == "__main__":
    main()
