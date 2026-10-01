"""
Shared helpers for comparing the constant-depth dynamic Pauli exponentials with the textbook
CNOT-ladder construction. Two variants of the dynamic circuits, kept in separate modules:

    ft            pauli_exp_dynamic.py        paper Fig. 1, fault-tolerant form (|θ> ancilla, ROT rule)
    nisq          pauli_exp_nisq.py           paper Fig. 1 with the θ rotation as a single-qubit gate
    nisq_compact  pauli_exp_nisq_compact.py   nisq + XX layer 1 as a gate, layers 3+4 as one measurement

Used by compare_depths.py (static depth / diagram study), hardware_compare.py (runs on the
real device) and test_aer_vs_ladder.py (Aer test).
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple


from pauli_exp_dynamic import GridDevice, PaperGridLayout, build_program, parse_terms
from pauli_exp_nisq import build_nisq_program
from pauli_exp_nisq_compact import build_compact_program

BACKEND_NAME = "ibm_rensselaer"
VARIANTS = ("ft", "nisq", "nisq_compact")
VARIANT_NAMES = {"ft": "fault-tolerant (|θ> ancilla)", "nisq": "NISQ (θ as a single-qubit gate)",
                 "nisq_compact": "NISQ compact (θ gate, XX gate, merged XX+Z readout)"}


def builder(variant: str):
    """build_program of the chosen variant (same arguments for both)."""
    return {"ft": build_program, "nisq": build_nisq_program, "nisq_compact": build_compact_program}[variant]


def add_variant_args(ap) -> None:
    ap.add_argument("--variant", choices=VARIANTS, default="ft",
                    help="dynamic-circuit variant: ft = paper Fig. 1 with the |θ> ancilla (pauli_exp_dynamic.py, "
                         "default); nisq = θ rotation as a single-qubit gate (pauli_exp_nisq.py); nisq_compact = "
                         "nisq with XX layer 1 as a gate and layers 3+4 as one measurement (pauli_exp_nisq_compact.py)")


# ----------------------------------------------------------------------------
# Backend / device
# ----------------------------------------------------------------------------
def get_service(instance: Optional[str] = None):
    """QiskitRuntimeService from the SAVED account (same API key), optionally on another
    instance: ``instance`` is a CRN (or instance name). Falls back to $QISKIT_IBM_INSTANCE."""
    import os
    from qiskit_ibm_runtime import QiskitRuntimeService

    instance = instance or os.environ.get("QISKIT_IBM_INSTANCE") or None
    return QiskitRuntimeService(instance=instance) if instance else QiskitRuntimeService()


def get_backend(name: str = BACKEND_NAME, instance: Optional[str] = None):
    return get_service(instance).backend(name)


def add_service_args(ap) -> None:
    """--backend / --instance, shared by every script."""
    ap.add_argument("--backend", default=BACKEND_NAME, help=f"backend name (default {BACKEND_NAME})")
    ap.add_argument("--instance", default=None,
                    help="CRN of the IBM Quantum instance to use; the API key comes from your saved "
                         "account (default: the saved account's instance, or $QISKIT_IBM_INSTANCE)")


def twoq_gate_name(backend) -> Optional[str]:
    ops = backend.target.operation_names
    return next((g for g in ("cz", "ecr", "cx") if g in ops), None)


def patch_cost(layout: PaperGridLayout, device: GridDevice, backend) -> float:
    """Summed readout + two-qubit error over the block of the chip a layout uses."""
    tgt = backend.target
    twoq = twoq_gate_name(backend)
    cost = 0.0
    for rc in layout.block:
        q = layout.device.qubit_at[rc]  # block coords are in layout.device's frame
        try:
            cost += tgt["measure"][(q,)].error or 0.0
        except (KeyError, TypeError):
            cost += 1.0
        for nb in ((rc[0] + 1, rc[1]), (rc[0], rc[1] + 1)):
            if nb in layout.block and twoq:
                pair = (q, layout.device.qubit_at[nb])
                props = tgt[twoq].get(pair) or tgt[twoq].get(pair[::-1])
                cost += props.error if (props is not None and props.error is not None) else 1.0
    return cost


def best_layout(device: GridDevice, backend, n: int) -> PaperGridLayout:
    """Lowest-error patch of the chip that holds n logical qubits (both orientations)."""
    cands = []
    for transposed, dev in ((False, device), (True, device.transposed())):
        for r0 in range(dev.rows):
            for c0 in range(dev.cols):
                try:
                    lay = PaperGridLayout(dev, n, origin=(r0, c0))
                except ValueError:
                    continue
                lay.transposed = transposed
                cands.append(lay)
    if not cands:
        raise ValueError(f"no layout for {n} logical qubits")
    # prefer the most compact shape first, then the lowest error
    min_block = min(len(l.block) for l in cands)
    cands = [l for l in cands if len(l.block) == min_block]
    return min(cands, key=lambda l: patch_cost(l, device, backend))


LAYOUT_FILE = "layouts.json"  # shared by compare_depths.py and hardware_compare.py


def get_layout(device: GridDevice, backend, n: int, path: str = LAYOUT_FILE,
               refresh: bool = False) -> PaperGridLayout:
    """The layout for n logical qubits on this backend, chosen ONCE and then frozen.

    The first call picks the lowest-error patch (best_layout, using the calibration data
    of that moment) and stores it in ``path``; every later call, from any script, rebuilds
    exactly that layout, so the depth study, the diagrams and the hardware runs all use the
    same physical qubits. ``refresh=True`` re-chooses from the current calibration.
    """
    import json
    import os

    db = json.load(open(path)) if os.path.exists(path) else {}
    recs = db.setdefault(backend.name, {})
    rec = recs.get(str(n))
    if rec is not None and "offset" not in rec and not refresh:
        dev = device.transposed() if rec["transposed"] else device
        lay = PaperGridLayout(dev, n, shape=tuple(rec["shape"]), origin=tuple(rec["origin"]))
        lay.transposed = rec["transposed"]
        if [int(q) for q in lay.physical_qubits] != rec["physical_qubits"]:
            raise RuntimeError(f"{path}: stored layout for n={n} no longer matches the device")
        return lay
    lay = best_layout(device, backend, n)
    recs[str(n)] = dict(transposed=bool(lay.transposed), shape=[lay.nr, lay.nc], origin=[lay.r0, lay.c0],
                        physical_qubits=[int(q) for q in lay.physical_qubits])
    with open(path, "w") as f:
        json.dump(db, f, indent=1)
    return lay


# ----------------------------------------------------------------------------
# Circuits
# ----------------------------------------------------------------------------
def terms_label(terms) -> str:
    out = []
    for t, th in terms:
        s = " ".join(f"{v}{k}" for k, v in sorted(t.items())) or "I"
        out.append(f"{s}")
    return " · ".join(out)


def pauli_label(term: dict, n: int) -> str:
    """Qiskit Pauli label of a term {logical qubit: 'X'|'Y'|'Z'} (rightmost character = qubit 0)."""
    return "".join(term.get(q, "I") for q in reversed(range(n)))


def ladder_circuit(terms, n: int, name: str = "cnot_ladder"):
    """CNOT-ladder exp(-iθP): Qiskit's PauliEvolutionGate(P, time=θ) synthesized with
    LieTrotter(cx_structure="chain") -- basis change, CNOT chain, Rz, CNOT chain, basis change --
    decomposed into those gates. Logical (all-to-all) circuit on n qubits; terms act in order."""
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import PauliEvolutionGate
    from qiskit.quantum_info import Pauli
    from qiskit.synthesis import LieTrotter

    qc = QuantumCircuit(n, name=name)
    for term, th in terms:
        if not term:
            qc.global_phase -= th
            continue
        qc.append(PauliEvolutionGate(Pauli(pauli_label(term, n)), time=th,
                                     synthesis=LieTrotter(cx_structure="chain")), range(n))
    return qc.decompose(gates_to_decompose=["PauliEvolution"])


def aer_probabilities(qc) -> Dict[str, float]:
    """Exact outcome probabilities of a measurement-free circuit, from its Qiskit Aer statevector
    (keys: bitstrings, qubit 0 rightmost)."""
    from qiskit import transpile
    from qiskit_aer import AerSimulator

    sim = AerSimulator(method="statevector")
    c = transpile(qc, sim, optimization_level=0)
    c.save_statevector()
    sv = sim.run(c).result().get_statevector()
    return {k: float(v) for k, v in sv.probabilities_dict().items() if v > 1e-12}


AER_TOL = 1e-8


def aer_check(isa, ideal: Dict[str, float], rot_masks: Sequence[int] = (), shots: int = 256,
              max_qubits: int = 20, seed: int = 1234) -> Dict[str, object]:
    """Noise-free Qiskit Aer run of a circuit exactly as it will be submitted (ISA, with DD if any).

    The final readout into register "meas" is replaced by Aer's save_probabilities_dict on the same
    physical qubits (bit j = logical qubit j), saved after EVERY shot (pershot=True): each shot's exact
    outcome distribution is compared with ``ideal`` (no sampling noise). Qubits the circuit never
    touches are dropped first (DAGCircuit.remove_qubits), so only the active qubits are simulated.
    rot_masks: rot_parity_mask of each exponential (dynamic circuits) -- counts the shots on which the
    ROT correction fired; both branches must occur. Circuits without mid-circuit measurements
    (ladders) are deterministic and run with one shot.

    Returns dict(status "ok" | "FAIL" | "skipped" (more than max_qubits active), qubits, shots, fired,
    max_dev = max over shots and outcomes of |p - p_ideal|).
    """
    from qiskit.circuit import Qubit
    from qiskit.converters import circuit_to_dag, dag_to_circuit
    from qiskit_aer import AerSimulator

    meas = next(r for r in isa.cregs if r.name == "meas")
    pos = {b: j for j, b in enumerate(meas)}
    readout, body = {}, isa.copy_empty_like()
    for ins in isa.data:
        if ins.operation.name == "measure" and ins.clbits[0] in pos:
            readout[pos[ins.clbits[0]]] = ins.qubits[0]
        else:
            body.append(ins.operation, ins.qubits, ins.clbits)
    dag = circuit_to_dag(body)
    keep = set(readout.values())  # read-out qubits stay even if idle (e.g. an I position without DD)
    dag.remove_qubits(*[w for w in dag.idle_wires() if isinstance(w, Qubit) and w not in keep])
    small = dag_to_circuit(dag)
    out = dict(status="skipped", qubits=small.num_qubits, shots=0, fired=0, max_dev=float("nan"))
    if small.num_qubits > max_qubits:
        return out

    n = len(meas)
    small.save_probabilities_dict([readout[j] for j in range(n)], label="probs", pershot=True)
    dynamic = bool(rot_masks)
    res = AerSimulator(method="statevector").run(small, shots=shots if dynamic else 1, seed_simulator=seed,
                                                 memory=dynamic).result()
    per_shot = res.data(0)["probs"]
    if isinstance(per_shot, dict):
        per_shot = [per_shot]

    def bits(key):  # Aer key (int, or hex / binary string) -> n-bit string, qubit 0 rightmost
        if isinstance(key, str):
            key = int(key, 16) if key.startswith("0x") else int(key, 2)
        return format(int(key), f"0{n}b")

    max_dev = 0.0
    for p in per_shot:
        p = {bits(k): float(v) for k, v in p.items()}
        max_dev = max(max_dev, max(abs(p.get(k, 0.0) - ideal.get(k, 0.0)) for k in set(p) | set(ideal)))
    fired = 0
    if dynamic:
        k_mid = [r.name for r in small.cregs].index("mid")
        for mem in res.get_memory(0):  # registers appear in reverse order; rightmost char = bit 0
            mid = mem.split()[len(small.cregs) - 1 - k_mid][::-1]
            fired += any(sum(int(mid[i]) for i in range(len(mid)) if (m >> i) & 1) % 2 for m in rot_masks)
    ok = max_dev < AER_TOL and (not dynamic or 0 < fired < len(per_shot))
    out.update(status="ok" if ok else "FAIL", shots=len(per_shot), fired=fired, max_dev=max_dev)
    return out


def construction_info(corrections: str = "end", variant: str = "ft") -> Dict[str, object]:
    """Provenance stored with every result: which construction and which code produced it."""
    import hashlib
    import os

    here = os.path.dirname(os.path.abspath(__file__))

    def md5(fname):
        with open(os.path.join(here, fname), "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    if variant == "ft":
        return dict(variant="ft", construction="paper Fig. 1: XX / ZZ(+θ) / X(θ)+XX / Z, |θ> ancilla",
                    corrections=corrections, pauli_exp_dynamic_md5=md5("pauli_exp_dynamic.py"))
    if variant == "nisq":
        return dict(variant="nisq", construction="paper Fig. 1, θ rotation as a single-qubit gate (NISQ): "
                                                 "XX / ZZ / Rz(±2θ) on q_last + XX / Z, no |θ> ancilla",
                    corrections=corrections, pauli_exp_nisq_md5=md5("pauli_exp_nisq.py"),
                    pauli_exp_dynamic_md5=md5("pauli_exp_dynamic.py"))
    return dict(variant="nisq_compact", construction="NISQ compact: XX as gate (H-CX-H) / ZZ measured / "
                                                     "Rz(±2θ) on q_last / XX+Z(a) as one measurement",
                corrections=corrections, pauli_exp_nisq_compact_md5=md5("pauli_exp_nisq_compact.py"),
                pauli_exp_dynamic_md5=md5("pauli_exp_dynamic.py"))


def parity_prep_post(terms, n: int):
    """Prep / post circuits for the 'GHZ-parity' check of a single Pauli term P:

        |psi> = B |+>^S |0>^rest,  with P = B Z..Z B^dag  (B = H for X, S H for Y)
        post  = H B^dag  on the support

    so that the ideal outcome is 0..0 with prob cos^2θ and 1 on every support qubit
    with prob sin^2θ (for a single term). Works for any list of terms too; the ideal
    distribution is then computed by statevector simulation.
    """
    from qiskit import QuantumCircuit

    term = terms[0][0]
    prep, post = QuantumCircuit(n), QuantumCircuit(n)
    for l in sorted(term):
        prep.h(l)
        if term[l] == "X":
            prep.h(l)
        elif term[l] == "Y":
            prep.h(l)
            prep.s(l)
    for l in sorted(term):
        if term[l] == "X":
            post.h(l)
        elif term[l] == "Y":
            post.sdg(l)
            post.h(l)
        post.h(l)
    return prep, post


# ----------------------------------------------------------------------------
# Metrics
# ----------------------------------------------------------------------------
def _is_directive(ins) -> bool:
    return getattr(ins.operation, "_directive", False) or ins.operation.name == "barrier"


NON_GATES = ("measure", "reset", "barrier", "delay", "if_else")


def metrics(qc) -> Dict[str, int]:
    """Circuit metrics from standard QuantumCircuit methods.

    2q_depth   : qc.depth(lambda instr: len(instr.qubits) == 2)
    2q_count   : qc.num_nonlocal_gates()
    gate_count : QuantumCircuit.count_ops(), all operations except measure/reset/barrier/delay/if_else
                 (gates inside if_else blocks are not included; if_else is reported separately)
    depth      : qc.depth()
    """
    ops = qc.count_ops()
    return {
        "2q_depth": qc.depth(lambda instr: len(instr.qubits) == 2),
        "2q_count": qc.num_nonlocal_gates(),
        "gate_count": int(sum(v for k, v in ops.items() if k not in NON_GATES)),
        "depth": qc.depth(),
        "meas_layers": qc.depth(lambda instr: instr.operation.name == "measure"),
        "measurements": int(ops.get("measure", 0)),
        "if_else": int(ops.get("if_else", 0)),
        "active_qubits": len({q for instr in qc.data for q in instr.qubits}),
    }


# ----------------------------------------------------------------------------
# Transpilation
# ----------------------------------------------------------------------------
def transpile_dynamic(qc, backend, optimization_level: int = 3, seed: int = 1234):
    """Dynamic circuit is already on physical qubits / couplers: pin the trivial layout."""
    from qiskit import transpile

    return transpile(qc, backend=backend, initial_layout=list(range(backend.num_qubits)),
                     optimization_level=optimization_level, seed_transpiler=seed)


def transpile_ladder(qc, backend, initial_layout: Optional[Sequence[int]] = None,
                     optimization_level: int = 3, seeds: Sequence[int] = (1, 2, 3, 4, 5)):
    """Ladder circuit transpiled for the backend.

    initial_layout: physical qubit for each logical qubit. Pass the dynamic program's
    ``layout.physical_qubits`` so both implementations start on the same qubits; the
    transpiler then only adds routing (SWAPs). Keeps the best of several routing seeds
    (lowest 2q depth, then lowest 2q count).
    """
    from qiskit import transpile

    best = None
    for s in seeds:
        isa = transpile(qc, backend=backend, initial_layout=list(initial_layout) if initial_layout else None,
                        optimization_level=optimization_level, seed_transpiler=s)
        if initial_layout is not None:
            got = list(isa.layout.initial_index_layout(filter_ancillas=True))
            if got != list(initial_layout):
                raise RuntimeError(f"transpiler changed the pinned layout: {got} != {list(initial_layout)}")
        m = metrics(isa)
        key = (m["2q_depth"], m["2q_count"])
        if best is None or key < best[0]:
            best = (key, isa)
    return best[1]


def apply_dd(isa, backend):
    """Client-side dynamical decoupling (X-X sequence) on an ISA circuit, dynamic circuits included.

    IBM's server-side DD (Sampler options.dynamical_decoupling) is documented as incompatible
    with dynamic circuits, so DD is inserted here with qiskit-ibm-runtime's dynamic-circuit-aware
    scheduling passes (ALAPScheduleAnalysis + PadDynamicalDecoupling). They pad idle windows,
    including the ones around mid-circuit measurements and feed-forward, with X - X pulses
    (X is native on the backend, so the result stays an ISA circuit). Only qubits the circuit
    already uses are padded; never-used qubits are left alone.
    """
    from qiskit.circuit.library import XGate
    from qiskit.transpiler import PassManager
    from qiskit_ibm_runtime.transpiler.passes.scheduling import ALAPScheduleAnalysis, PadDynamicalDecoupling

    seq = [XGate(), XGate()]
    try:  # qiskit-ibm-runtime >= 0.43: passes take the backend target directly
        pm = PassManager([ALAPScheduleAnalysis(target=backend.target),
                          PadDynamicalDecoupling(target=backend.target, dd_sequences=seq)])
    except TypeError:  # older releases: durations object
        from qiskit_ibm_runtime.transpiler.passes.scheduling import DynamicCircuitInstructionDurations
        durations = DynamicCircuitInstructionDurations.from_backend(backend)
        pm = PassManager([ALAPScheduleAnalysis(durations),
                          PadDynamicalDecoupling(durations, dd_sequences=seq)])
    out = pm.run(isa)
    out.name = isa.name
    return out


def add_dd_args(ap) -> None:
    ap.add_argument("--dd", choices=("on", "off", "both"), default="on",
                    help="dynamical decoupling: on (default), off, or both (every circuit with and "
                         "without DD, in the same job, for a direct comparison)")


def dd_variants(mode: str):
    return {"on": [True], "off": [False], "both": [False, True]}[mode]


def check_trivial_layout(isa, num_qubits: int) -> None:
    """The dynamic circuit is built on physical qubits: its ISA layout must be the identity."""
    got = list(isa.layout.initial_index_layout())
    if got != list(range(num_qubits)):
        raise RuntimeError("transpiler moved the dynamic circuit off its chosen physical qubits")


# ----------------------------------------------------------------------------
# Drawing helpers
# ----------------------------------------------------------------------------
def _chip_axes(device: GridDevice, ax, title: str):
    for a, b in device.edges():
        (r1, c1), (r2, c2) = device.coord_of[a], device.coord_of[b]
        ax.plot([c1, c2], [r1, r2], color="#e3e3e3", lw=1, zorder=0)
    for q, (r, c) in device.coord_of.items():  # physical qubit numbers, to match the hardware
        ax.text(c + 0.18, r + 0.36, str(q), fontsize=5, color="#8c8c8c", zorder=5)
    ax.set_xlim(-0.8, device.cols - 0.2)
    ax.set_ylim(device.rows - 0.2, -0.8)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=9)


def draw_dynamic_layout(device: GridDevice, layout: PaperGridLayout, info: dict, title: str, ax=None):
    """Chain of one term of the dynamic program, drawn in the CHIP's frame (same orientation
    and physical numbering as draw_grid_usage), whatever orientation the layout was built in."""
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots(figsize=(device.cols * 0.62 + 1.5, device.rows * 0.62 + 1.6))
    block = {layout.device.qubit_at[rc] for rc in layout.block}
    data = [int(q) for q in layout.physical_qubits]
    support = {data[l] for l in info["term"]}
    anc, fill = set(info["ancillas"]), set(info["fillers"])
    tq = info.get("theta_qubit")  # paper's |θ> ancilla (ROT rule); None for the NISQ variant
    chain = list(info["chain"]) + ([tq] if tq is not None else [])
    ax.plot([device.coord_of[q][1] for q in chain], [device.coord_of[q][0] for q in chain],
            color="#2f6fb3", lw=2.5, zorder=1)
    for q, (r, c) in device.coord_of.items():
        if q in data:
            l = data.index(q)
            fc = "#e8743b" if q in support else "#f6d2bf"
            ax.scatter(c, r, s=330, color=fc, edgecolor="#8a3b12", zorder=3)
            ax.text(c, r, str(l), ha="center", va="center", fontsize=8,
                    color="white" if q in support else "#8a3b12", zorder=4)
        elif q == tq:
            ax.scatter(c, r, s=260, color="#3a9a4f", edgecolor="#1f5e2c", zorder=3)
            ax.text(c, r, "θ", ha="center", va="center", fontsize=8, color="white", zorder=4)
        elif q in anc:
            ax.scatter(c, r, s=150, color="#2f6fb3", zorder=2)
        elif q in fill:
            ax.scatter(c, r, s=150, color="white", edgecolor="#2f6fb3", lw=1.5, zorder=2)
        else:
            ax.scatter(c, r, s=60 if q in block else 40, color="#bdbdbd" if q in block else "#e6e6e6", zorder=2)
    _chip_axes(device, ax, title)
    return ax


def draw_grid_usage(device: GridDevice, isa, title: str, ax=None, logical_names=None, placement=None):
    """Chip picture for a transpiled circuit: initial placement of each logical qubit,
    final placement (if routing moved it) and every coupler used, thickness ∝ #2q gates.

    placement: logical -> physical list to mark instead of the circuit's own layout
    (needed for the dynamic circuit, whose virtual qubits already are physical qubits)."""
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots(figsize=(device.cols * 0.62 + 1.5, device.rows * 0.62 + 1.6))
    use: Dict[Tuple[int, int], int] = {}

    def walk(circ, qmap):
        for ins in circ.data:
            op = ins.operation
            qs = [qmap[circ.find_bit(q).index] for q in ins.qubits]
            if getattr(op, "blocks", None):
                for b in op.blocks:  # block qubits are ordered like ins.qubits
                    walk(b, qs)
            elif op.num_qubits == 2 and not _is_directive(ins):
                e = tuple(sorted(qs))
                use[e] = use.get(e, 0) + 1

    walk(isa, list(range(isa.num_qubits)))
    mx = max(use.values()) if use else 1
    for (a, b), k in use.items():
        if a in device.coord_of and b in device.coord_of:
            (r1, c1), (r2, c2) = device.coord_of[a], device.coord_of[b]
            ax.plot([c1, c2], [r1, r2], color="#2f6fb3", lw=1.5 + 4.0 * k / mx, zorder=1, alpha=0.85)
    init = final = None
    if placement is not None:
        init = list(placement)
    elif isa.layout is not None:
        init = isa.layout.initial_index_layout(filter_ancillas=True)
        try:
            final = isa.layout.final_index_layout(filter_ancillas=True)
        except Exception:
            final = None
    used_q = {q for e in use for q in e}
    placed = set(init or [])
    for q, (r, c) in device.coord_of.items():
        if q in placed:
            continue
        ax.scatter(c, r, s=110 if q in used_q else 40, color="#2f6fb3" if q in used_q else "#c8c8c8", zorder=2)
    if init:
        for l, q in enumerate(init):
            r, c = device.coord_of[q]
            ax.scatter(c, r, s=330, color="#e8743b", edgecolor="#8a3b12", zorder=3)
            ax.text(c, r, str(l if logical_names is None else logical_names[l]), ha="center", va="center",
                    fontsize=8, color="white", zorder=4)
    if final and init and list(final) != list(init):
        for l, q in enumerate(final):
            if q != init[l]:
                r, c = device.coord_of[q]
                ax.scatter(c, r, s=330, facecolor="none", edgecolor="#8a3b12", lw=1.5, ls="--", zorder=3)
                ax.text(c + 0.32, r - 0.32, f"→{l}", fontsize=7, color="#8a3b12", zorder=4)
    _chip_axes(device, ax, title)
    return ax
