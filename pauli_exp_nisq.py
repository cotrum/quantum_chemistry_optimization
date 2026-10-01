"""
NISQ variant of the constant-depth Pauli exponential of

    I. Moflic & A. Paler, "On the constant depth implementation of Pauli exponentials",
    npj Quantum Information 12:82 (2026), https://doi.org/10.1038/s41534-026-01226-x

The paper (Methods, "Measurement-based implementation") says that on NISQ machines "the θ rotation
is a single-qubit gate". This module is the Fig. 1 construction of pauli_exp_dynamic.py (the
fault-tolerant variant: |θ> ancilla, ROT rule) with exactly that one change -- no |θ> ancilla:

    q_1 - a_1 - q_2 - a_2 - ... - a_L - q_last

    basis change (H / S^dag H) on the support         P = C Z..Z C^dag
    layer 1   XX(a_i, q_{i+1})
    layer 2   ZZ(q_i, a_i)                           outcomes m_i, m = XOR_i m_i
    rotation  Rz(2θ (-1)^m) on q_last                = exp(-iθP), see below
    layer 3   XX(a_i, q_{i+1})
    layer 4   Z measurement of the a_i
    basis change back

Why the rotation is a single-qubit gate on q_last: with every a_i in |0>, P equals
P' = Z(q_1)..Z(q_last) Z(a_1)..Z(a_L) on the input. P' commutes with every XX(a_i, q_{i+1}) and
ZZ(q_i, a_i) of layers 1-2, so exp(-iθP') can be applied after them. There the ZZ outcomes fix
Z(q_1)Z(a_1) .. Z(q_L)Z(a_L) = (-1)^m, hence P' = (-1)^m Z(q_last) and
exp(-iθP') = exp(-iθ (-1)^m Z(q_last)) = Rz(2θ (-1)^m) on q_last (Qiskit Rz(φ) = exp(-iφZ/2)).
Layers 3-4 and the Pauli byproducts are those of the fault-tolerant variant, without the Z
byproduct of the θ-ancilla's X measurement.

Everything else -- device, layout and routing (PaperGridLayout), Pauli frame, corrections
"end"/"each", Qiskit export -- is shared with pauli_exp_dynamic.py, which this module does not modify.
Correctness is tested with Qiskit Aer only (test_aer_vs_ladder.py --variant nisq).
"""
from __future__ import annotations

from typing import Optional

from pauli_exp_dynamic import DynamicPauliProgram, GridDevice, PaperGridLayout, Term, _LABEL, parse_terms

__all__ = ["NisqPauliProgram", "build_nisq_program"]


class NisqPauliProgram(DynamicPauliProgram):
    """DynamicPauliProgram with the NISQ exponential: no |θ> ancilla, Rz(±2θ) on q_last.

    rot_correction=False applies the rotation without the sign (-1)^m; the circuit is then WRONG
    on the shots with m = 1. It exists only as the negative control in test_aer_vs_ladder.py.
    term_info[k]["rot_parity_mask"]: parity of these mid-circuit bits = m.
    """

    variant = "nisq"

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

        # chain  q_1 - a_1 - q_2 - ... - a_L - q_last  (same routing as the fault-tolerant variant)
        path = [self.device.qubit_at[rc] for rc in lay.route(support, strategy)]
        string, anc = path[0::2], path[1::2]
        L = len(anc)
        last = string[-1]
        fillers = [q for q in string if q not in self._data]

        # layer 1: XX(a_i, q_{i+1})
        if L:
            self._barrier("XX", path)
        ex = [self._mxx(string[i + 1], anc[i]) for i in range(L)]

        # layer 2: ZZ(q_i, a_i); the product of the outcomes is (-1)^m with P = (-1)^m Z(q_last)
        if L:
            self._barrier("ZZ", path)
        m_mask = 0
        for i in range(L):
            m_mask ^= self._mzz(string[i], anc[i])

        # the θ rotation as a single-qubit gate: Rz(2θ (-1)^m) on q_last. The X frame of q_last flips
        # the sign again (Rz(φ) X = X Rz(-φ)); IR op ("rz", q, φ, mask) = rz(φ) if parity(mask) == 0 else rz(-φ).
        self._barrier("Rz, XX", path)
        sign_mask = (m_mask if self.rot_correction else 0) ^ self.fx.get(last, 0)
        self.ops.append(("rz", last, 2.0 * theta, sign_mask))

        # layer 3: XX(a_i, q_{i+1})
        ey = [self._mxx(string[i + 1], anc[i]) for i in range(L)]

        # layer 4: Z measurement of the link ancillas
        if L:
            self._barrier("Z(a)", anc)
        em = []
        for a in anc:
            raw, eff = self._measure(a)
            em.append(eff)
            self._reset(a, raw)

        # Pauli byproducts of the XX / ZZ measurements (as in the fault-tolerant variant):
        #   Z on string[i] with parity XOR_{j>=i} (x_j ^ y_j),   X on string[i+1] with m_i
        c = 0
        for i in reversed(range(L)):
            c ^= ex[i] ^ ey[i]
            self.fz[string[i]] = self.fz.get(string[i], 0) ^ c
        for i in range(L):
            self.fx[string[i + 1]] = self.fx.get(string[i + 1], 0) ^ em[i]
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


def build_nisq_program(paulis, theta: Optional[float] = None, layout: Optional[PaperGridLayout] = None,
                       device: Optional[GridDevice] = None, num_logical: Optional[int] = None,
                       corrections: str = "end", barriers: bool = True,
                       strategy: str = "auto", rot_correction: bool = True) -> NisqPauliProgram:
    """NISQ program for prod_k exp(-i theta_k P_k) (first term acts first). Same arguments as
    pauli_exp_dynamic.build_program."""
    terms = parse_terms(paulis, theta)
    if layout is None:
        need = max([max(t) + 1 for t, _ in terms if t] + [1])
        if isinstance(paulis, str):
            m = _LABEL.match(paulis.strip().replace(" ", "").replace("_", ""))
            need = max(need, len(m.group(3)) if m else 0)
        layout = PaperGridLayout.auto(device or GridDevice.nighthawk(), max(need, num_logical or 0))
    prog = NisqPauliProgram(layout, corrections=corrections, barriers=barriers, rot_correction=rot_correction)
    for term, ang in terms:
        prog.add_exponential(term, ang, strategy=strategy)
    return prog.finalize()
