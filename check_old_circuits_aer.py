"""
One-off check: were the OLD dynamic circuits correct?

The old circuits are the ones saved by the earlier compare_depths.py run in
wrong_results/depth_comparison/circuits/<case>.qpy (= [dynamic, dynamic ISA, ladder, ladder ISA]);
the same construction ran on hardware this morning (hardware_results r1, r2, sweeps).

For every saved case whose dynamic circuit touches at most 20 qubits:
  1) the old dynamic circuit (qpy[0], untranspiled) with a random |ψ> loaded on its data qubits,
     simulated with Qiskit Aer (mid-circuit measurements and feed-forward run natively); after
     every shot Aer saves the density matrix of the data qubits (save_density_matrix, pershot=True);
  2) reference: Qiskit's PauliEvolutionGate exp(-iθP) for the same terms (read from the circuit's
     metadata), applied to the same |ψ>, Aer statevector;
  3) state_fidelity of every shot against the reference.
Only the data qubits are compared (Aer traces out the helper qubits), so this checks the
operation on the logical qubits whatever state the old circuits leave their helpers in.

    python check_old_circuits_aer.py
Report: test_results/old_circuits_aer.md
"""
from __future__ import annotations

import glob
import os

import numpy as np
from qiskit import QuantumCircuit, qpy, transpile
from qiskit.circuit import Qubit
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit.quantum_info import DensityMatrix, Pauli, random_statevector, state_fidelity
from qiskit.synthesis import LieTrotter
from qiskit_aer import AerSimulator

SRC = "wrong_results/depth_comparison/circuits"
MAX_QUBITS = 20
SHOTS = 1024
TOL = 1e-9
SIM = AerSimulator(method="statevector")


def pauli_label(term: str, n: int) -> str:
    """Metadata term 'X0 Z1 Y2' -> Qiskit label on n qubits (rightmost character = logical qubit 0)."""
    chars = ["I"] * n
    for tok in term.split():
        chars[n - 1 - int(tok[1:])] = tok[0]
    return "".join(chars)


def reference(psi, terms, n):
    """exp(-iθ_k P_k) ... exp(-iθ_1 P_1)|ψ> with Qiskit's PauliEvolutionGate (first term acts first), via Aer."""
    qc = QuantumCircuit(n)
    qc.initialize(psi.data, range(n))
    for term, th in terms:
        if term != "I":
            qc.append(PauliEvolutionGate(Pauli(pauli_label(term, n)), time=th,
                                         synthesis=LieTrotter(cx_structure="chain")), range(n))
    qc = transpile(qc.decompose(gates_to_decompose=["PauliEvolution"]), SIM, optimization_level=0)
    qc.save_statevector()
    return SIM.run(qc).result().get_statevector()


def check(name, dyn, seed):
    data_phys = [int(p) for p in dyn.metadata["logical_to_physical"]]
    terms = [(t, float(th)) for t, th in dyn.metadata["terms"]]
    n = len(data_phys)
    data = [dyn.qubits[p] for p in data_phys]
    active = {q for ins in dyn.data for q in ins.qubits} | set(data)
    if len(active) > MAX_QUBITS:
        return dict(case=name, n=n, qubits=len(active), status="skipped")

    rng = np.random.default_rng(seed)
    psi = random_statevector(2 ** n, seed=int(rng.integers(1 << 30)))
    qc = dyn.copy_empty_like()
    qc.initialize(psi.data, data)
    qc.compose(dyn, inplace=True)
    dag = circuit_to_dag(qc)  # drop qubits the circuit never touches (keep the data qubits)
    dag.remove_qubits(*[w for w in dag.idle_wires() if isinstance(w, Qubit) and w not in set(data)])
    small = dag_to_circuit(dag)
    if small.num_qubits > MAX_QUBITS:
        return dict(case=name, n=n, qubits=small.num_qubits, status="skipped")

    ref = reference(psi, terms, n)
    small.save_density_matrix(data, label="rho", pershot=True)
    batch = max(1, min(SHOTS, (1 << 30) // (16 * 4 ** n)))  # keep the saved density matrices ~1 GB
    fids, outcomes, done = [], set(), 0
    while done < SHOTS:
        k = min(batch, SHOTS - done)
        res = SIM.run(small, shots=k, seed_simulator=seed + done, memory=True).result()
        fids += [state_fidelity(DensityMatrix(np.asarray(r)), ref) for r in res.data(0)["rho"]]
        outcomes |= set(res.get_memory(0))
        done += k
    bad = sum(f < 1 - TOL for f in fids)
    return dict(case=name, n=n, qubits=small.num_qubits, status="correct" if bad == 0 else "WRONG",
                shots=len(fids), bad=bad, min_f=min(fids), mean_f=float(np.mean(fids)), outcomes=len(outcomes),
                terms=" · ".join(f"exp(-i {th:g} {t})" for t, th in terms))


def main():
    rows = []
    for i, path in enumerate(sorted(glob.glob(f"{SRC}/*.qpy"))):
        name = os.path.basename(path)[:-4]
        with open(path, "rb") as f:
            dyn = qpy.load(f)[0]
        r = check(name, dyn, seed=2026 + 1000 * i)
        rows.append(r)
        if r["status"] == "skipped":
            print(f"{name:18s} skipped ({r['qubits']} active qubits > {MAX_QUBITS})")
        else:
            print(f"{name:18s} {r['status']:8s} {r['qubits']:2d} qubits, {r['shots']} shots, "
                  f"{r['outcomes']} distinct mid-circuit outcomes: min F {r['min_f']:.15f}, mean F {r['mean_f']:.15f}, "
                  f"{r['bad']} shots with F < 1-{TOL:g}   [{r['terms']}]")

    os.makedirs("test_results", exist_ok=True)
    lines = ["# Old dynamic circuits (wrong_results/depth_comparison) vs Qiskit PauliEvolutionGate, Qiskit Aer", "",
             f"Random input state on the data qubits, {SHOTS} shots, per-shot density matrix of the data qubits "
             f"(helpers traced out). Correct = every shot has fidelity >= 1 - {TOL:g}.", "",
             "| case | logical qubits | active qubits | status | shots with F < 1-tol | min F | mean F | distinct outcomes |",
             "|---|--:|--:|---|--:|--:|--:|--:|"]
    for r in rows:
        if r["status"] == "skipped":
            lines.append(f"| {r['case']} | {r['n']} | {r['qubits']} | skipped (> {MAX_QUBITS} qubits) | | | | |")
        else:
            lines.append(f"| {r['case']} | {r['n']} | {r['qubits']} | {r['status']} | {r['bad']} / {r['shots']} | "
                         f"{r['min_f']:.15f} | {r['mean_f']:.15f} | {r['outcomes']} |")
    open("test_results/old_circuits_aer.md", "w").write("\n".join(lines) + "\n")
    print("report: test_results/old_circuits_aer.md")


if __name__ == "__main__":
    main()
