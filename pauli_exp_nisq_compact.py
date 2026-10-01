"""
NISQ-compact variant of the constant-depth Pauli exponential of

    I. Moflic & A. Paler, "On the constant depth implementation of Pauli exponentials",
    npj Quantum Information 12:82 (2026), https://doi.org/10.1038/s41534-026-01226-x

This is the NISQ variant (pauli_exp_nisq.py: paper Fig. 1 with the θ rotation as a single-qubit
gate) with two standard circuit identities applied to the link ancillas. They are NOT steps written
out in the paper; the construction is the one that ran on hardware earlier as the "old" dynamic
circuits (Aer-checked with check_old_circuits_aer.py):

    q_1 - a_1 - q_2 - ... - a_L - q_last          (no |θ> ancilla)

    basis change (H / S^dag H) on the support         P = C Z..Z C^dag
    layer 1   XX(a_i, q_{i+1}) as a GATE:  H(q) CX(q->a) H(a) H(q)
              a_i starts in |0>, so this deterministically prepares the +1 outcome of the XX
              measurement (no measurement, no byproduct)
    layer 2   ZZ(q_i, a_i) measured: CX(q->a), measure a, CX(q->a)        outcomes m_i, m = XOR m_i
    rotation  Rz(2θ (-1)^m) on q_last                                    (as in the NISQ variant)
    layer 3+4 XX(a_i, q_{i+1}) followed by the Z readout of a_i, merged into ONE destructive
              measurement: H(a) H(q) CX(q->a), measure a (outcome y_i), H(q)
              a_i is left in |y_i> and is returned to |0> (frame or feed-forward)
    Pauli byproducts: Z on q_i with parity XOR_{j>=i} y_j (no X byproducts)
    basis change back

Per link ancilla: 4 CX and 2 measurements (NISQ variant: 6 CX, 4 measurements; fault-tolerant
variant: the same plus the |θ> ancilla). Device, layout and routing, Pauli frame, corrections
"end"/"each" and the Qiskit export are shared with pauli_exp_dynamic.py, which this module does
not modify. Correctness is tested with Qiskit Aer only (test_aer_vs_ladder.py --variant nisq_compact).
"""
from __future__ import annotations

from typing import Optional

from pauli_exp_dynamic import DynamicPauliProgram, GridDevice, PaperGridLayout, Term, _LABEL, parse_terms

__all__ = ["CompactNisqPauliProgram", "build_compact_program"]


class CompactNisqPauliProgram(DynamicPauliProgram):
    """DynamicPauliProgram with the NISQ-compact exponential (see module docstring).

    rot_correction=False applies the rotation without the sign (-1)^m; the circuit is then WRONG
    on the shots with m = 1. It exists only as the negative control in test_aer_vs_ladder.py.
    term_info[k]["rot_parity_mask"]: parity of these mid-circuit bits = m.
    """

    variant = "nisq_compact"

    def add_exponential(self, term: Term, theta: float, strategy: str = "auto") -> None:
        if self._finalized:
            raise RuntimeError("program already finalized")
        term = {int(k): v for k, v in term.items() if v != "I"}
        self.terms.append((dict(term), float(theta)))
        if not term:
            self.global_phase -= theta
            return
        lay = self.layout
        support = sorted(term)
        phys = {l: lay.physical_qubits[l] for l in support}

        # rotate the term to Z-type:  P = C Z..Z C^dag, apply C^dag first
        for l in support:
            if term[l] == "X":
                self._h(phys[l])
            elif term[l] == "Y":
                self._s(phys[l], dag=True)
                self._h(phys[l])

        # chain  q_1 - a_1 - q_2 - ... - a_L - q_last  (same routing as the other variants)
        path = [self.device.qubit_at[rc] for rc in lay.route(support, strategy)]
        string, anc = path[0::2], path[1::2]
        L = len(anc)
        last = string[-1]
        fillers = [q for q in string if q not in self._data]

        # layer 1: XX(a_i, q_{i+1}) as a gate (a_i is |0>: deterministic +1 outcome)
        if L:
            self._barrier("XX (gate)", path)
        for i in range(L):
            q, a = string[i + 1], anc[i]
            self._h(q)
            self._cx(q, a)
            self._h(a)
            self._h(q)

        # layer 2: ZZ(q_i, a_i) measured; the product of the outcomes is (-1)^m with P = (-1)^m Z(q_last)
        if L:
            self._barrier("ZZ", path)
        m_mask = 0
        for i in range(L):
            m_mask ^= self._mzz(string[i], anc[i])

        # the θ rotation as a single-qubit gate: Rz(2θ (-1)^m) on q_last (X frame of q_last flips the sign)
        self._barrier("Rz, XX+Z(a)", path)
        sign_mask = (m_mask if self.rot_correction else 0) ^ self.fx.get(last, 0)
        self.ops.append(("rz", last, 2.0 * theta, sign_mask))

        # layers 3+4 merged: XX(a_i, q_{i+1}) and the Z readout of a_i as one destructive measurement
        ey = []
        for i in range(L):
            q, a = string[i + 1], anc[i]
            self._h(a)
            self._h(q)
            self._cx(q, a)
            raw, eff = self._measure(a)
            self._h(q)
            ey.append(eff)
            self._reset(a, raw)

        # Pauli byproducts: Z on string[i] with parity XOR_{j>=i} y_j
        c = 0
        for i in reversed(range(L)):
            c ^= ey[i]
            self.fz[string[i]] = self.fz.get(string[i], 0) ^ c
        for q in fillers:  # fillers are |0> in the ideal frame: Z frame is irrelevant
            self.fz[q] = 0

        # undo the basis change
        for l in support:
            if term[l] == "X":
                self._h(phys[l])
            elif term[l] == "Y":
                self._h(phys[l])
                self._s(phys[l])

        self.term_info.append(dict(
            term=dict(term), theta=float(theta), weight=len(support), chain=path,
            string_qubits=string, ancillas=anc, fillers=fillers, theta_qubit=None,
            rot_parity_mask=m_mask,  # parity of these mid-circuit bits = m (sign of the rotation flipped)
        ))
        if self.corrections == "each":
            self._flush(path)

    def to_qiskit(self, *args, **kwargs):
        qc = super().to_qiskit(*args, **kwargs)
        qc.metadata["variant"] = self.variant
        return qc


def build_compact_program(paulis, theta: Optional[float] = None, layout: Optional[PaperGridLayout] = None,
                          device: Optional[GridDevice] = None, num_logical: Optional[int] = None,
                          corrections: str = "end", barriers: bool = True,
                          strategy: str = "auto", rot_correction: bool = True) -> CompactNisqPauliProgram:
    """NISQ-compact program for prod_k exp(-i theta_k P_k) (first term acts first). Same arguments as
    pauli_exp_dynamic.build_program."""
    terms = parse_terms(paulis, theta)
    if layout is None:
        need = max([max(t) + 1 for t, _ in terms if t] + [1])
        if isinstance(paulis, str):
            m = _LABEL.match(paulis.strip().replace(" ", "").replace("_", ""))
            need = max(need, len(m.group(3)) if m else 0)
        layout = PaperGridLayout.auto(device or GridDevice.nighthawk(), max(need, num_logical or 0))
    prog = CompactNisqPauliProgram(layout, corrections=corrections, barriers=barriers, rot_correction=rot_correction)
    for term, ang in terms:
        prog.add_exponential(term, ang, strategy=strategy)
    return prog.finalize()
