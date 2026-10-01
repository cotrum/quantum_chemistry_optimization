"""
Aer test: dynamic (constant-depth) Pauli exponential vs. the CNOT-ladder Pauli exponential.

    pip install qiskit-aer            # once
    python test_aer_vs_ladder.py      # all variants, logical sizes 1..4, 1024 shots per dynamic circuit
    python test_aer_vs_ladder.py --variant nisq
    python test_aer_vs_ladder.py --max-n 3 --shots 4096

Variants (separate modules): ft = pauli_exp_dynamic.build_program (paper Fig. 1, |θ> ancilla, ROT rule),
nisq = pauli_exp_nisq.build_nisq_program (θ rotation as a single-qubit gate Rz(±2θ) on q_last),
nisq_compact = pauli_exp_nisq_compact.build_compact_program (nisq with XX layer 1 as a gate and
layers 3+4 as one destructive measurement).
Every check below is run identically for each variant.

1) Dynamic circuit: build_program(...).to_qiskit() (the circuit under test) on a small
   2 x (2n+1) grid chip; the circuit is on the whole chip (6 / 10 / 14 / 18 qubits for
   n = 1..4) and all of it is simulated. Qiskit Aer (AerSimulator, method="statevector")
   runs it natively, with its mid-circuit measurements and feed-forward;
   save_statevector(pershot=True) returns the full statevector after every shot.
2) CNOT ladder: Qiskit's PauliEvolutionGate(P, time=θ) = exp(-iθP), synthesized with
   LieTrotter(cx_structure="chain") -- basis change, CNOT chain, Rz, CNOT chain, basis
   change -- placed on the same data qubits of the same register (all other qubits stay |0>).
   Simulated with Qiskit Aer (no measurements, so the statevector is deterministic).
3) Fidelity: qiskit.quantum_info.state_fidelity between the ladder statevector and the
   dynamic-circuit statevector of EVERY shot, reported separately for the shots where the
   sign correction fired and the shots where it did not (ft: ROT correction, P⊗Z_θ = -1;
   nisq, nisq_compact: sign of Rz on q_last, ZZ parity m = 1); a circuit fails if either branch was never
   exercised (circuits without any such correction, e.g. a NISQ weight-1 term, have one branch).
4) Negative control (single-exponential cases): the same circuit built WITHOUT the sign
   correction. It passes only if the shots where the correction would fire give exactly the
   wrong-sign state exp(+iθP)|ψ> (fidelity cos²2θ + sin²2θ <P>², <P> from
   Statevector.expectation_value) and all other shots are exact -- i.e. the test does detect a
   missing correction, and the correction fixes exactly the sign.

Both circuits start from the same random input state (qiskit.quantum_info.random_statevector),
loaded with QuantumCircuit.initialize on the data qubits.

Exit code 0 only if every shot of every circuit has fidelity >= 1 - 1e-9 and every control behaves
as predicted.
Report: test_results/aer_vs_ladder_<variant>.md  (<variant> = ft, nisq, nisq_compact or all)
"""
from __future__ import annotations

import argparse
import math
import os
import sys
import time

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.quantum_info import Pauli, random_statevector, state_fidelity
from qiskit.synthesis import LieTrotter
from qiskit_aer import AerSimulator

from pauli_exp_dynamic import GridDevice, PaperGridLayout, build_program
from pauli_exp_nisq import build_nisq_program
from pauli_exp_nisq_compact import build_compact_program

TOL = 1e-9
OUT = "test_results"
SIM = AerSimulator(method="statevector")
BUILDERS = {"ft": build_program, "nisq": build_nisq_program, "nisq_compact": build_compact_program}


def test_device(n):
    """Small square-grid chip of 2 x (2n+1) qubits; the whole chip is simulated."""
    dev = GridDevice(2, 2 * n + 1)
    return dev, PaperGridLayout(dev, n, shape=(1, n))


def dynamic_circuit(prog, data, psi):
    """to_qiskit() with |ψ> loaded on the data qubits (all device qubits kept)."""
    circ = prog.to_qiskit()
    qc = circ.copy_empty_like()
    qc.initialize(psi.data, data)
    qc.compose(circ, inplace=True)
    return qc


def ladder_statevector(num_qubits, data, psi, spec):
    """CNOT-ladder exponentials (Qiskit PauliEvolutionGate, chain synthesis) on `data`, via Aer."""
    qc = QuantumCircuit(num_qubits)
    qc.initialize(psi.data, data)
    for label, theta in spec:  # label: rightmost character acts on data[0]
        qc.append(PauliEvolutionGate(Pauli(label), time=theta, synthesis=LieTrotter(cx_structure="chain")), data)
    qc = qc.decompose(gates_to_decompose=["PauliEvolution"])  # -> basis change, CX chain, Rz, CX chain
    qc = transpile(qc, SIM, optimization_level=0)  # only translates gates for Aer; no optimization
    qc.save_statevector()
    return SIM.run(qc).result().get_statevector(), qc.count_ops()


def dynamic_statevectors(qc, shots, seed):
    """Dynamic circuit run natively in Aer; yields (full statevector, mid-circuit outcomes) per shot."""
    qc = qc.copy()
    qc.save_statevector(pershot=True)
    batch = max(1, min(shots, (1 << 30) // (16 << qc.num_qubits)))  # keep saved statevectors ~1 GB
    done = 0
    while done < shots:
        k = min(batch, shots - done)
        res = SIM.run(qc, shots=k, seed_simulator=seed + done, memory=True).result()
        mem = res.get_memory(0) if qc.num_clbits else [""] * k  # no mid-circuit measurements: no memory
        yield from zip(res.data(0)["statevector"], mem)
        done += k


FIXED = ["Z", "X", "Y", "ZZ", "XY", "ZZZ", "XYZ", "YIX", "ZIZ", "ZZZZ", "XZZX", "ZIIZ", "YXIZ", "XYZXY", "ZIXIY"]


def make_cases(rng, max_n, n_random):
    cases = [(lab, [(lab, float(rng.uniform(-math.pi, math.pi)))]) for lab in FIXED if len(lab) <= max_n]
    for i in range(n_random):
        n = int(rng.integers(1, max_n + 1))
        spec = []
        for _ in range(int(rng.integers(1, 4))):  # products of 1-3 exponentials
            lab = "".join(rng.choice(list("IXYZ"), n))
            if set(lab) == {"I"}:
                lab = "Z" + lab[1:]
            spec.append((lab, float(rng.uniform(-math.pi, math.pi))))
        cases.append((f"rand{i}", spec))
    return cases


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=4, help="largest number of logical qubits")
    ap.add_argument("--random", type=int, default=12, help="number of random cases")
    ap.add_argument("--shots", type=int, default=1024, help="Aer shots per dynamic circuit")
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--variant", choices=tuple(BUILDERS) + ("all",), default="all",
                    help="dynamic-circuit variant to test (default: all)")
    args = ap.parse_args()
    variants = tuple(BUILDERS) if args.variant == "all" else (args.variant,)
    rng = np.random.default_rng(args.seed)
    os.makedirs(OUT, exist_ok=True)

    rows, t0 = [], time.time()
    for case, spec in make_cases(rng, args.max_n, args.random):
        n = len(spec[0][0])
        dev, layout = test_device(n)
        data = [int(q) for q in layout.physical_qubits]
        psi = random_statevector(2 ** n, seed=int(rng.integers(1 << 30)))
        seed = int(rng.integers(1 << 30))
        print(f"\n{case}: " + " · ".join(f"exp(-i({th:+.4f}) {lab})" for lab, th in spec)
              + f"   device {dev.num_qubits} qubits, data qubits {data}")

        for variant in variants:
            build = BUILDERS[variant]
            for corrections in ("end", "each"):
                prog = build(spec, layout=layout, corrections=corrections, barriers=False)
                r = run_grouped(prog, data, psi, spec, args.shots, seed)
                ok = r["worst"] >= 1 - TOL and (not r["branches"] or (r["fired"] > 0 and r["plain"] > 0))
                record(rows, case, variant, f"corrections={corrections}", prog, r, ok)

            # negative control: same circuit WITHOUT the sign correction. Shots where the correction
            # would fire must now give exp(+iθP)|ψ>, i.e. fidelity exactly F = cos²2θ + sin²2θ <P>²
            # (Qiskit: psi.expectation_value(P)); all other shots must still be exact.
            if len(spec) == 1:
                label, th = spec[0]
                p = float(np.real(psi.expectation_value(Pauli(label))))
                f_wrong = math.cos(2 * th) ** 2 + math.sin(2 * th) ** 2 * p ** 2
                if 1 - f_wrong < 1e-4:
                    print(f"  [skip] {variant} control without sign correction: θ={th:+.4f} gives "
                          f"1-F = {1 - f_wrong:.1e}, too small to distinguish the two signs")
                    continue
                if not any(info["rot_parity_mask"] for info in prog.term_info):
                    print(f"  [skip] {variant} control: this circuit has no sign correction (no measurements)")
                    continue
                prog = build(spec, layout=layout, barriers=False, rot_correction=False)
                r = run_grouped(prog, data, psi, spec, args.shots, seed)
                ok = (r["fired"] > 0 and r["plain"] > 0 and r["worst_plain"] >= 1 - TOL
                      and r["max_dev_fired"](f_wrong) < 1e-9)
                record(rows, case, variant, "CONTROL: no sign correction", prog, r, ok,
                       note=f"expected F on corrected branch = {f_wrong:.12f}")

    fails = [r for r in rows if not r["ok"]]
    lines = [f"# Aer: dynamic circuit vs CNOT ladder ({time.time() - t0:.0f}s)", "",
             f"{len(rows)} checks, {args.shots} shots each; {len(fails)} failed.", "",
             "Variants: ft = paper Fig. 1 with the |θ> ancilla (pauli_exp_dynamic.py); nisq = θ rotation as a "
             "single-qubit gate (pauli_exp_nisq.py); nisq_compact = nisq with XX layer 1 as a gate and layers 3+4 "
             "as one measurement (pauli_exp_nisq_compact.py). Sign correction fired = on that shot, for at least one "
             "exponential, P⊗Z_θ = -1 (ft) or the ZZ parity m = 1 (nisq, nisq_compact). CONTROL rows use the same circuit "
             "without the sign correction: they pass only if the corrected branch fails with exactly the fidelity "
             "predicted for the wrong sign, exp(+iθP), and every other shot is exact.", "",
             "| case | variant | check | status | qubits | shots | shots with sign correction | min F (correction fired) "
             "| min F (no correction) | distinct outcomes | note |",
             "|---|---|---|---|--:|--:|--:|--:|--:|--:|---|"]
    for r in rows:
        lines.append(f"| {r['case']} | {r['variant']} | {r['check']} | {'ok' if r['ok'] else 'FAIL'} | {r['qubits']} | "
                     f"{r['shots']} | {r['fired']} | {r['worst_fired']:.15f} | {r['worst_plain']:.15f} | "
                     f"{r['outcomes']} | {r['note']} |")
    report = f"{OUT}/aer_vs_ladder_{args.variant}.md"
    open(report, "w").write("\n".join(lines) + "\n")
    print("\n" + lines[2] + f"  report: {report}")
    sys.exit(1 if fails else 0)


def rot_fired(mem: str, masks) -> bool:
    """True if the sign correction fired for at least one exponential on this shot: the parity of the
    mid-circuit bits in that term's rot_parity_mask is 1 (ft: P⊗Z_θ = -1; nisq: ZZ parity m = 1).
    Aer memory: rightmost = mid[0]."""
    bits = mem.replace(" ", "")[::-1]
    return any(sum(int(bits[i]) for i in range(len(bits)) if (mask >> i) & 1) % 2 for mask in masks)


def run_grouped(prog, data, psi, spec, shots, seed):
    """Aer run of the dynamic circuit and of the CNOT ladder on the same register; fidelities of
    every shot, grouped by whether the ROT correction fired."""
    circ = dynamic_circuit(prog, data, psi)
    ref, _ = ladder_statevector(circ.num_qubits, data, psi, spec)
    masks = [info["rot_parity_mask"] for info in prog.term_info]
    fired, plain, outcomes = [], [], set()
    if not prog.num_bits:  # no mid-circuit measurements (NISQ weight-1 term): one deterministic run
        shots = 1
    for sv, mem in dynamic_statevectors(circ, shots, seed):
        (fired if rot_fired(mem, masks) else plain).append(state_fidelity(sv, ref))
        outcomes.add(mem)
    nan = float("nan")
    return dict(qubits=circ.num_qubits, shots=len(fired) + len(plain), fired=len(fired), plain=len(plain),
                branches=any(masks),
                worst=min(fired + plain), worst_fired=min(fired) if fired else nan,
                worst_plain=min(plain) if plain else nan, outcomes=len(outcomes),
                max_dev_fired=lambda f: max(abs(x - f) for x in fired) if fired else nan)


def record(rows, case, variant, name, prog, r, ok, note=""):
    rows.append(dict(case=case, variant=variant, check=name, ok=ok, qubits=r["qubits"], shots=r["shots"],
                     fired=r["fired"], worst_fired=r["worst_fired"], worst_plain=r["worst_plain"],
                     outcomes=r["outcomes"], note=note))
    print(f"  [{'ok' if ok else 'FAIL'}] {variant:12s} {name:28s} {r['shots']} shots: sign correction fired on {r['fired']}, "
          f"min F there {r['worst_fired']:.15f}; min F elsewhere {r['worst_plain']:.15f}"
          + (f"   ({note})" if note else ""))

if __name__ == "__main__":
    main()
