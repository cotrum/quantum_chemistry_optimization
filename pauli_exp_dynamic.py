"""
Constant-depth dynamic circuits for Pauli exponentials on square-lattice hardware.

Implements the decomposition of

    I. Moflic & A. Paler, "On the constant depth implementation of Pauli
    exponentials", npj Quantum Information 12:82 (2026),
    https://doi.org/10.1038/s41534-026-01226-x

for IBM's square-lattice processors (e.g. Nighthawk, 120 qubits = 10 x 12 grid).

What it builds (paper Fig. 1)
-----------------------------
For each Pauli term P and angle theta, exp(-i theta P) is realised on a chain

    q_1 - a_1 - q_2 - a_2 - ... - a_L - q_last - θ

of string qubits q (support qubits, or |0> fillers for I terms), |0> link ancillas a,
and the |θ> ancilla next to the last string qubit:

    basis change (H / S^dag H) on the support   P = C Z..Z C^dag
    |θ> = Rz(2θ)|+>                              paper: |θ> = Rz(θ)|+> -> exp(-iθ/2 P)
    layer 1  XX(a_i, q_{i+1})
    layer 2  ZZ(q_i, a_i), ZZ(q_last, θ)         product of outcomes = P ⊗ Z_θ
    layer 3  X measurement of θ, XX(a_i, q_{i+1})
    layer 4  Z measurement of the a_i
    basis change back

Every XX / ZZ two-body interaction is a parity measurement between the two neighbouring
qubits of the chain (ZZ: CX, measure the second qubit, CX; XX: the same between H layers).
Corrections (paper Supplementary Material): Pauli byproducts of the measurements are
tracked in a Pauli frame; for P ⊗ Z_θ = -1 the negative angle is corrected with
Rz(θ) = Rz(2θ)Rz(-θ), applied to |θ> before its X measurement.

Layout (paper Fig. 7 and the "bi-linear" layout of the Methods)
---------------------------------------------------------------
Logical qubits sit on every other site of every other row of the grid:

        c0  .   .   .   .   .   .  E        Q = logical (data) qubit
    r0   .  Q   .   Q   .   Q   .  .        . = ancilla / routing qubit
         .  .   .   .   .   .   .  .   <- routing lane under each data row
         .  Q   .   Q   .   Q   .  .
         .  .   .   .   .   .   .  .

All logical qubits lie on the same sublattice of the (bipartite) grid, so any
path between two of them alternates  data-colour / other-colour  sites. A chain
for a term is a simple path that visits every qubit in the term's support and
avoids every other logical qubit. Odd path positions are the XX/ZZ ancillas;
even positions are either support qubits or spare qubits held in |0>
("fillers"). A filler contributes a Z on |0>, i.e. the identity -- this is the
paper's trick for strings with I terms (Fig. 11 and the |0>-padding identity
exp(iθ Z..I..Z)|A..B..C> -> exp(iθ Z..Z..Z)|A..0..C>). The lanes and the two
edge columns guarantee such a path exists for every support. The |θ> ancilla is placed
on a free qubit next to one end of the chain (PaperGridLayout.extend_for_theta).

On a 12 x 10 (or 10 x 12) grid this holds up to 25 logical qubits (5 rows x 5 columns).

Pauli-frame handling
--------------------
Byproduct Paulis are tracked symbolically as parities of mid-circuit
measurement bits. ``corrections="each"`` applies them (feed-forward) after every
term; ``corrections="end"`` (default) carries them through the whole sequence
and applies them once at the very end, so the only mid-circuit feed-forward of each
term is the corrective rotation on its θ-ancilla. Either way the returned circuit implements
the exact unitary on the logical qubits and returns every helper qubit to |0>.

Conventions
-----------
* Pauli labels use Qiskit order: the rightmost character acts on logical qubit 0.
  A leading "-" negates the angle. Dicts like {0: "Z", 5: "X"} are also accepted,
  as are qiskit.quantum_info.Pauli / SparsePauliOp objects.
* A term (P, theta) means exp(-i * theta * P). A list of terms is applied in list
  order (first term acts first). For a SparsePauliOp H and time t the terms are
  exp(-i t c_k P_k) (a first-order Trotter step).

Building a program needs only the standard library; ``to_qiskit`` needs Qiskit.
Correctness is tested with Qiskit Aer only (test_aer_vs_ladder.py: full statevectors
compared with the CNOT-ladder exponential).
"""
from __future__ import annotations

import math
import re
from collections import deque
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


__all__ = [
    "GridDevice",
    "PaperGridLayout",
    "DynamicPauliProgram",
    "build_program",
    "parse_terms",
]

Coord = Tuple[int, int]
Term = Dict[int, str]  # logical qubit -> "X" | "Y" | "Z"


# ----------------------------------------------------------------------------
# Device
# ----------------------------------------------------------------------------
class GridDevice:
    """A rows x cols square lattice with a map (row, col) -> physical qubit index."""

    def __init__(self, rows: int, cols: int, qubit_at: Optional[Dict[Coord, int]] = None):
        self.rows, self.cols = rows, cols
        if qubit_at is None:
            qubit_at = {(r, c): r * cols + c for r in range(rows) for c in range(cols)}
        self.qubit_at: Dict[Coord, int] = dict(qubit_at)
        self.coord_of: Dict[int, Coord] = {q: rc for rc, q in self.qubit_at.items()}
        self.num_qubits = max(self.coord_of) + 1

    @classmethod
    def nighthawk(cls) -> "GridDevice":
        """10 x 12 grid, row-major qubit numbering (120 qubits, 218 couplers).

        Real backends may number their qubits differently: for hardware runs use
        ``GridDevice.from_coupling_map(backend.coupling_map)`` instead.
        """
        return cls(10, 12)

    @classmethod
    def from_coupling_map(cls, coupling_map) -> "GridDevice":
        """Recover grid coordinates from a coupling map of a full rectangular grid.

        Accepts a qiskit CouplingMap or any iterable of (q1, q2) pairs.
        """
        edges = coupling_map.get_edges() if hasattr(coupling_map, "get_edges") else coupling_map
        adj: Dict[int, set] = {}
        for a, b in edges:
            a, b = int(a), int(b)
            if a == b:
                continue
            adj.setdefault(a, set()).add(b)
            adj.setdefault(b, set()).add(a)
        corners = sorted(q for q, nb in adj.items() if len(nb) == 2)
        if len(corners) != 4:
            raise ValueError(
                f"Expected a full rectangular grid (4 corner qubits), found {len(corners)} "
                "degree-2 qubits. Build GridDevice(rows, cols, qubit_at=...) by hand instead."
            )

        def bfs(src):
            dist = {src: 0}
            dq = deque([src])
            while dq:
                u = dq.popleft()
                for v in adj[u]:
                    if v not in dist:
                        dist[v] = dist[u] + 1
                        dq.append(v)
            return dist

        d0 = bfs(corners[0])
        others = sorted(corners[1:], key=lambda q: d0[q])
        a = others[0]  # nearest other corner: same row
        p = d0[a]  # = cols - 1
        da = bfs(a)
        qubit_at = {}
        for q in adj:
            c2, r2 = d0[q] - da[q] + p, d0[q] + da[q] - p
            if c2 % 2 or r2 % 2:
                raise ValueError("Coupling map is not a square grid.")
            qubit_at[(r2 // 2, c2 // 2)] = q
        rows = max(r for r, _ in qubit_at) + 1
        cols = max(c for _, c in qubit_at) + 1
        dev = cls(rows, cols, qubit_at)
        expected = rows * (cols - 1) + cols * (rows - 1)
        undirected = {tuple(sorted((int(a), int(b)))) for a, b in edges if a != b}
        ok = len(qubit_at) == rows * cols == len(adj) and len(undirected) == expected
        ok = ok and all(
            abs(dev.coord_of[a][0] - dev.coord_of[b][0]) + abs(dev.coord_of[a][1] - dev.coord_of[b][1]) == 1
            for a, b in undirected
        )
        if not ok:
            raise ValueError("Coupling map is not a full rectangular grid (missing qubits or couplers?).")
        return dev

    def transposed(self) -> "GridDevice":
        return GridDevice(self.cols, self.rows, {(c, r): q for (r, c), q in self.qubit_at.items()})

    def edges(self) -> List[Tuple[int, int]]:
        out = []
        for (r, c), q in self.qubit_at.items():
            for rc in ((r + 1, c), (r, c + 1)):
                if rc in self.qubit_at:
                    out.append((q, self.qubit_at[rc]))
        return out


# ----------------------------------------------------------------------------
# Layout + routing
# ----------------------------------------------------------------------------
class PaperGridLayout:
    """Logical qubits on sites (r0 + 2k, c0 + 1 + 2j), k < nr, j < nc.

    The block used on the chip spans rows r0 .. r0+2nr-1 and columns c0 .. c0+2nc.
    Logical indices are assigned in snake order (row 0 left->right, row 1
    right->left, ...), so neighbouring logical indices are neighbours on chip.
    """

    def __init__(self, device: GridDevice, num_logical: int,
                 shape: Optional[Tuple[int, int]] = None, origin: Coord = (0, 0)):
        self.device = device
        self.num_logical = int(num_logical)
        self.r0, self.c0 = origin
        nr_max = (device.rows - self.r0) // 2
        nc_max = (device.cols - self.c0 - 1) // 2
        if shape is None:
            shape = self._auto_shape(self.num_logical, nr_max, nc_max)
        self.nr, self.nc = shape
        if self.nr < 1 or self.nc < 1 or self.nr * self.nc < self.num_logical:
            raise ValueError(f"shape {shape} cannot hold {num_logical} logical qubits")
        if self.nr > nr_max or self.nc > nc_max:
            raise ValueError(
                f"shape {shape} at origin {origin} does not fit the {device.rows}x{device.cols} grid "
                f"(max {nr_max}x{nc_max} from this origin)"
            )
        self.left_edge, self.right_edge = self.c0, self.c0 + 2 * self.nc
        self.block = {(r, c) for r in range(self.r0, self.r0 + 2 * self.nr)
                      for c in range(self.c0, self.c0 + 2 * self.nc + 1)}
        missing = [rc for rc in self.block if rc not in device.qubit_at]
        if missing:
            raise ValueError(f"grid sites {missing[:4]}... are not on the device")
        slots = []
        for k in range(self.nr):
            js = range(self.nc) if k % 2 == 0 else range(self.nc - 1, -1, -1)
            slots += [(k, j) for j in js]
        self.slot: List[Tuple[int, int]] = slots[: self.num_logical]
        self.coord: List[Coord] = [self._rc(k, j) for k, j in self.slot]
        self.logical_at: Dict[Coord, int] = {rc: l for l, rc in enumerate(self.coord)}
        self.physical_qubits: List[int] = [device.qubit_at[rc] for rc in self.coord]

    @staticmethod
    def _auto_shape(n: int, nr_max: int, nc_max: int) -> Tuple[int, int]:
        if nr_max < 1 or nc_max < 1:
            raise ValueError("grid too small")
        nc = max(1, min(nc_max, math.ceil(math.sqrt(n))))
        nr = math.ceil(n / nc)
        if nr > nr_max:
            nr = nr_max
            nc = math.ceil(n / nr)
        if nc > nc_max:
            raise ValueError(f"{n} logical qubits do not fit (max {nr_max * nc_max} here)")
        return nr, nc

    @classmethod
    def auto(cls, device: GridDevice, num_logical: int, origin: Coord = (0, 0)) -> "PaperGridLayout":
        """Pick the grid orientation and block shape that fits ``num_logical`` most compactly."""
        best = None
        for dev in (device, device.transposed()):
            try:
                lay = cls(dev, num_logical, origin=origin)
            except ValueError:
                continue
            cost = (len(lay.block), abs(lay.nr * 2 - lay.nc * 2 - 1))
            if best is None or cost < best[0]:
                best = (cost, lay)
        if best is None:
            raise ValueError(f"{num_logical} logical qubits do not fit on a {device.rows}x{device.cols} grid")
        return best[1]

    @property
    def capacity(self) -> int:
        return self.nr * self.nc

    def _rc(self, k: int, j: int) -> Coord:
        return (self.r0 + 2 * k, self.c0 + 1 + 2 * j)

    # ---- routing ---------------------------------------------------------
    def route(self, support: Sequence[int], strategy: str = "auto") -> List[Coord]:
        """Chain of grid coordinates for a term with the given logical support.

        Even positions: support qubits or |0> fillers; odd positions: ancillas.
        strategy: "auto" (shortest-path greedy, falling back to the constructive
        snake), "greedy", or "snake" (always succeeds on this layout).
        """
        S = sorted(set(int(l) for l in support))
        if not S:
            raise ValueError("empty support")
        for l in S:
            if not 0 <= l < self.num_logical:
                raise ValueError(f"logical qubit {l} not in layout (num_logical={self.num_logical})")
        path = None
        if strategy in ("auto", "greedy"):
            path = self._greedy_route(S)
            if path is None and strategy == "greedy":
                raise RuntimeError("greedy routing failed")
        if path is None:
            path = self._snake_route(S)
        self.check_path(path, S)
        return path

    def _neighbors(self, rc: Coord):
        r, c = rc
        for nb in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if nb in self.block:
                yield nb

    def _greedy_route(self, S: List[int]) -> Optional[List[Coord]]:
        occupied = set(self.coord)
        path = [self.coord[S[0]]]
        used = {path[0]}
        for b in S[1:]:
            tgt = self.coord[b]
            blocked = used | (occupied - {tgt})
            prev = {path[-1]: None}
            dq = deque([path[-1]])
            while dq and tgt not in prev:
                u = dq.popleft()
                for v in self._neighbors(u):
                    if v not in prev and v not in blocked:
                        prev[v] = u
                        dq.append(v)
            if tgt not in prev:
                return None
            seg = []
            v = tgt
            while v != path[-1]:
                seg.append(v)
                v = prev[v]
            seg.reverse()
            path += seg
            used |= set(seg)
        return path

    def _snake_route(self, S: List[int]) -> List[Coord]:
        by_row: Dict[int, List[int]] = {}
        for l in S:
            k, j = self.slot[l]
            by_row.setdefault(k, []).append(j)
        rows = sorted(by_row)
        C = lambda j: self.c0 + 1 + 2 * j
        R = lambda k: self.r0 + 2 * k
        path: List[Coord] = []
        direction = +1
        for idx, k in enumerate(rows):
            js = sorted(by_row[k], reverse=direction < 0)
            r, lane, step = R(k), R(k) + 1, direction
            if idx == 0:
                path.append((r, C(js[0])))
            for ja, jb in zip(js, js[1:]):  # traverse the row, detouring via the lane
                if abs(jb - ja) == 1:
                    path += [(r, C(ja) + step), (r, C(jb))]
                else:
                    path.append((r, C(ja) + step))
                    c = C(ja) + step
                    while True:
                        path.append((lane, c))
                        if c == C(jb) - step:
                            break
                        c += step
                    path += [(r, C(jb) - step), (r, C(jb))]
            if idx + 1 == len(rows):
                break
            # transition to the next used row via this row's lane and an edge column
            k2 = rows[idx + 1]
            r2, lane2 = R(k2), R(k2) + 1
            edge = self.right_edge if direction > 0 else self.left_edge
            first2 = sorted(by_row[k2], reverse=direction > 0)[0]
            entry_col = C(first2) + step
            c = C(js[-1]) + step
            path += [(r, c), (lane, c)]
            while c != edge:
                c += step
                path.append((lane, c))
            target_row = r2 if entry_col == edge else lane2
            rr = lane
            while rr != target_row:
                rr += 1
                path.append((rr, edge))
            if entry_col != edge:
                c = edge
                while c != entry_col:
                    c -= step
                    path.append((lane2, c))
                path.append((r2, entry_col))
            path.append((r2, C(first2)))
            direction = -direction
        return path

    def check_path(self, path: List[Coord], S: Sequence[int]) -> None:
        want = {self.coord[l] for l in S}
        if len(set(path)) != len(path):
            raise AssertionError("path is not simple")
        if any(rc not in self.block for rc in path):
            raise AssertionError("path leaves the layout block")
        for u, v in zip(path, path[1:]):
            if abs(u[0] - v[0]) + abs(u[1] - v[1]) != 1:
                raise AssertionError(f"non-adjacent step {u}->{v}")
        if path[0] not in want or path[-1] not in want:
            raise AssertionError("path must start and end on support qubits")
        for i, rc in enumerate(path):
            if rc in self.logical_at and rc not in want:
                raise AssertionError(f"path crosses logical qubit {self.logical_at[rc]} not in the term")
            if rc in want and i % 2:
                raise AssertionError("support qubit on an ancilla position")
        if not want <= set(path[0::2]):
            raise AssertionError("path misses support qubits")

    # ---- paper's |θ> ancilla (ROT rule, Figs. 1 and 9) ------------------------------
    def extend_for_theta(self, path: List[Coord]) -> List[Coord]:
        """Append the |θ> ancilla of Fig. 1 to a routed chain: a free qubit next to the last
        string qubit (joined to it by the ZZ interaction of Fig. 1). If no neighbour of either
        chain end is free, the chain is continued through |0> fillers (link ancilla + filler
        pairs) to the nearest free site. Only qubits that are neither logical qubits nor on
        the chain are used; the layout block is searched first, then the whole device. The
        returned path ends on the θ-ancilla (an even-length path)."""
        occupied = set(self.coord)
        scopes = (self.block, set(self.device.qubit_at))
        for scope in scopes:
            for p in (list(path), list(path)[::-1]):
                ext = self._bfs_extension(p, scope, occupied)
                if ext is not None:
                    full = p + ext
                    self.check_theta_path(full)
                    return full
        raise RuntimeError("no free site next to the chain for the |θ> ancilla")

    def _bfs_extension(self, path, scope, occupied) -> Optional[List[Coord]]:
        start = path[-1]
        used = set(path)
        prev = {start: None}
        dist = {start: 0}
        dq = deque([start])
        while dq:
            u = dq.popleft()
            r, c = u
            for v in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if v in prev or v not in scope or v not in self.device.qubit_at:
                    continue
                if v in used or v in occupied:
                    continue
                prev[v] = u
                dist[v] = dist[u] + 1
                if dist[v] % 2 == 1:  # neighbour of a string qubit (other sublattice)
                    seg = []
                    w = v
                    while w != start:
                        seg.append(w)
                        w = prev[w]
                    return seg[::-1]
                dq.append(v)
        return None

    def check_theta_path(self, path: List[Coord]) -> None:
        if len(set(path)) != len(path):
            raise AssertionError("θ-extended path is not simple")
        for u, v in zip(path, path[1:]):
            if abs(u[0] - v[0]) + abs(u[1] - v[1]) != 1:
                raise AssertionError(f"non-adjacent step {u}->{v}")
        if len(path) % 2 != 0:
            raise AssertionError("θ-ancilla must be the neighbour of the last string qubit")
        if path[-1] in self.logical_at or path[-1] not in self.device.qubit_at:
            raise AssertionError("θ-ancilla must be a free device qubit")

    def draw(self, support: Optional[Sequence[int]] = None, ax=None, title: Optional[str] = None,
             theta_ancilla: bool = True):
        """Matplotlib picture of the chip, the layout block and (optionally) a routed chain."""
        import matplotlib.pyplot as plt

        if ax is None:
            _, ax = plt.subplots(figsize=(self.device.cols * 0.62 + 1, self.device.rows * 0.62 + 1))
        dev = self.device
        for (r, c) in dev.qubit_at:
            for rc in ((r + 1, c), (r, c + 1)):
                if rc in dev.qubit_at:
                    ax.plot([c, rc[1]], [r, rc[0]], color="#d9d9d9", lw=1, zorder=0)
        chain = self.route(support) if support else []
        if chain and theta_ancilla:
            chain = self.extend_for_theta(chain)
        role = {}
        for i, rc in enumerate(chain):
            role[rc] = "anc" if i % 2 else ("data" if rc in self.logical_at else "fill")
        if chain and theta_ancilla:
            role[chain[-1]] = "theta"
        if chain:
            ax.plot([c for _, c in chain], [r for r, _ in chain], color="#2f6fb3", lw=2.5, zorder=1)
        want = {self.coord[l] for l in support} if support else set()
        for (r, c), q in dev.qubit_at.items():
            if (r, c) in self.logical_at:
                fc = "#e8743b" if (r, c) in want or not support else "#f6d2bf"
                ax.scatter(c, r, s=330, color=fc, edgecolor="#8a3b12", zorder=2)
                ax.text(c, r, str(self.logical_at[(r, c)]), ha="center", va="center", fontsize=8,
                        color="white" if fc == "#e8743b" else "#8a3b12", zorder=3)
            elif role.get((r, c)) == "anc":
                ax.scatter(c, r, s=150, color="#2f6fb3", zorder=2)
            elif role.get((r, c)) == "fill":
                ax.scatter(c, r, s=150, color="white", edgecolor="#2f6fb3", lw=1.5, zorder=2)
            elif role.get((r, c)) == "theta":  # paper's |θ> ancilla (green Z term of Fig. 1)
                ax.scatter(c, r, s=260, color="#3a9a4f", edgecolor="#1f5e2c", zorder=2)
                ax.text(c, r, "θ", ha="center", va="center", fontsize=8, color="white", zorder=3)
            else:
                inside = (r, c) in self.block
                ax.scatter(c, r, s=60, color="#bdbdbd" if inside else "#eeeeee", zorder=2)
        ax.set_xlim(-0.8, dev.cols - 0.2)
        ax.set_ylim(dev.rows - 0.2, -0.8)
        ax.set_aspect("equal")
        ax.axis("off")
        if title:
            ax.set_title(title, fontsize=10)
        return ax


# ----------------------------------------------------------------------------
# Parsing Pauli input
# ----------------------------------------------------------------------------
_LABEL = re.compile(r"^([+-]?)([ij]?)([IXYZ]+)$")


def _parse_label(label: str) -> Tuple[Term, int]:
    s = label.strip().replace(" ", "").replace("_", "")
    m = _LABEL.match(s)
    if not m:
        raise ValueError(f"bad Pauli label {label!r} (use characters I, X, Y, Z)")
    if m.group(2):
        raise ValueError(f"Pauli {label!r} has an imaginary phase; exp(-i θ P) needs Hermitian P")
    sign = -1 if m.group(1) == "-" else 1
    chars = m.group(3)
    n = len(chars)
    term = {n - 1 - pos: ch for pos, ch in enumerate(chars) if ch != "I"}
    return term, sign


def _parse_one(p) -> Tuple[Term, int]:
    if isinstance(p, str):
        return _parse_label(p)
    if isinstance(p, dict):
        term = {}
        for k, v in p.items():
            v = str(v).upper()
            if v not in ("I", "X", "Y", "Z"):
                raise ValueError(f"bad Pauli {v!r} on qubit {k}")
            if v != "I":
                term[int(k)] = v
        return term, 1
    if hasattr(p, "to_label"):  # qiskit Pauli
        return _parse_label(p.to_label())
    raise TypeError(f"cannot interpret {p!r} as a Pauli string")


def parse_terms(paulis, theta: Optional[float] = None) -> List[Tuple[Term, float]]:
    """Normalise input into [(term_dict, angle), ...] meaning prod_k exp(-i angle_k P_k)."""
    if hasattr(paulis, "to_list") and hasattr(paulis, "paulis"):  # SparsePauliOp
        t = 1.0 if theta is None else float(theta)
        out = []
        for label, coeff in paulis.to_list():
            coeff = complex(coeff)
            if abs(coeff.imag) > 1e-12:
                raise ValueError("SparsePauliOp coefficients must be real")
            term, sign = _parse_label(label)
            out.append((term, sign * coeff.real * t))
        return out
    items = [paulis] if isinstance(paulis, (str, dict)) or hasattr(paulis, "to_label") else list(paulis)
    out = []
    for it in items:
        if isinstance(it, tuple) and len(it) == 2 and not isinstance(it[1], str):
            p, ang = it
        else:
            if theta is None:
                raise ValueError("give theta, or pass (pauli, theta) pairs")
            p, ang = it, theta
        term, sign = _parse_one(p)
        out.append((term, sign * float(ang)))
    return out


# ----------------------------------------------------------------------------
# Program (IR + Pauli frame)
# ----------------------------------------------------------------------------
def _bits(mask: int) -> List[int]:
    out, i = [], 0
    while mask:
        if mask & 1:
            out.append(i)
        mask >>= 1
        i += 1
    return out


class DynamicPauliProgram:
    """Hardware-level instruction list with a symbolic Pauli frame.

    Instructions (physical qubit indices, classical bit indices):
      ("h"|"s"|"sdg"|"x"|"z", q)   ("cx", c, t)   ("measure", q, bit)
      ("rz", q, phi, mask)   rz(phi) if parity(mask) == 0 else rz(-phi)
      ("x_if"|"z_if", q, mask)   apply if parity(mask) == 1
      ("barrier", label, qubits)
    A mask is an int whose set bits index mid-circuit measurement results.
    """

    def __init__(self, layout: PaperGridLayout, corrections: str = "end", barriers: bool = True,
                 rot_correction: bool = True):
        if corrections not in ("each", "end"):
            raise ValueError('corrections must be "each" or "end"')
        self.layout = layout
        self.device = layout.device
        self.corrections = corrections
        # rot_correction=False leaves out the ROT correction for P⊗Z_θ = -1; the circuit is then
        # WRONG on that branch. It exists only as the negative control in test_aer_vs_ladder.py.
        self.rot_correction = rot_correction
        self.barriers = barriers
        self.ops: List[tuple] = []
        self.num_bits = 0
        self.global_phase = 0.0
        self.terms: List[Tuple[Term, float]] = []
        self.term_info: List[dict] = []
        self.fx: Dict[int, int] = {}
        self.fz: Dict[int, int] = {}
        self._data = set(layout.physical_qubits)
        self._finalized = False

    # -- gates with frame propagation (actual = X^fx Z^fz · ideal) --------
    def _h(self, q):
        self.ops.append(("h", q))
        self.fx[q], self.fz[q] = self.fz.get(q, 0), self.fx.get(q, 0)

    def _s(self, q, dag=False):
        self.ops.append(("sdg" if dag else "s", q))
        self.fz[q] = self.fz.get(q, 0) ^ self.fx.get(q, 0)

    def _cx(self, c, t):
        self.ops.append(("cx", c, t))
        self.fx[t] = self.fx.get(t, 0) ^ self.fx.get(c, 0)
        self.fz[c] = self.fz.get(c, 0) ^ self.fz.get(t, 0)

    def _measure(self, q) -> Tuple[int, int]:
        """Z measurement. Returns (raw_mask, effective_mask = outcome in the ideal frame)."""
        b = self.num_bits
        self.num_bits += 1
        self.ops.append(("measure", q, b))
        raw = 1 << b
        return raw, raw ^ self.fx.get(q, 0)

    def _reset(self, q, raw):
        """Measured qubit q is now |raw>: return it to |0> (physically, or in the Pauli frame)."""
        if self.corrections == "each":
            self.ops.append(("x_if", q, raw))
            self.fx[q] = 0
        else:
            self.fx[q] = raw
        self.fz[q] = 0

    def _mzz(self, u, v):
        """ZZ two-body interaction of neighbours u, v: CX(u->v), measure Z on v, CX(u->v)."""
        self._cx(u, v)
        _, eff = self._measure(v)
        self._cx(u, v)
        return eff

    def _mxx(self, u, v):
        """XX two-body interaction of neighbours u, v: the ZZ circuit between H layers."""
        self._h(u); self._h(v)
        self._cx(u, v)
        _, eff = self._measure(v)
        self._cx(u, v)
        self._h(u); self._h(v)
        return eff

    def _barrier(self, label, qubits):
        if self.barriers:
            self.ops.append(("barrier", label, tuple(sorted(set(qubits)))))

    # -- one exponential ---------------------------------------------------
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

        # 1) rotate the term to Z-type:  P = C Z..Z C^dag, apply C^dag first
        for l in support:
            if term[l] == "X":
                self._h(phys[l])
            elif term[l] == "Y":
                self._s(phys[l], dag=True)
                self._h(phys[l])

        # chain  q_1 - a_1 - q_2 - ... - a_L - q_last  plus the |θ> ancilla next to q_last (Fig. 1)
        coords = lay.extend_for_theta(lay.route(support, strategy))
        nodes = [self.device.qubit_at[rc] for rc in coords]
        tq = nodes[-1]  # the |θ> ancilla
        path = nodes[:-1]
        string, anc = path[0::2], path[1::2]
        L = len(anc)
        last = string[-1]
        fillers = [q for q in string if q not in self._data]

        # |θ> = Rz(θ_paper)|+>, which gives exp(-i θ_paper/2 P) (Supplementary Material, ROT);
        # for exp(-iθP) that is Rz(2θ)|+> (Qiskit convention Rz(φ) = exp(-iφZ/2)).
        self._h(tq)
        self.ops.append(("rz", tq, 2.0 * theta, self.fx.get(tq, 0)))

        # Fig. 1, layer 1: XX(a_i, q_{i+1})
        self._barrier("XX", nodes)
        ex = [self._mxx(string[i + 1], anc[i]) for i in range(L)]

        # layer 2: ZZ(q_i, a_i) and ZZ(q_last, θ); the product of the outcomes is P ⊗ Z_θ
        self._barrier("ZZ", nodes)
        m_mask = 0
        for i in range(L):
            m_mask ^= self._mzz(string[i], anc[i])
        m_mask ^= self._mzz(last, tq)

        # layer 3: X measurement of |θ>, and XX(a_i, q_{i+1})
        #   P⊗Z_θ = -1 gives the negative angle: the ROT correction "Rz(θ) = Rz(2θ)Rz(-θ)" is
        #   applied to |θ> before its X measurement: Rz(-2θ)·Rz(+2θ) = 1 (m = 0),
        #   Rz(-2θ)·Rz(-2θ) = Rz(-4θ) (m = 1).
        #   X outcome -1 leaves the Pauli correction P^c (a Z on q_last here), tracked in the frame.
        self._barrier("X(θ), XX", nodes)
        if self.rot_correction:
            self.ops.append(("rz", tq, -2.0 * theta, self.fx.get(tq, 0)))
            self.ops.append(("rz", tq, 2.0 * theta, m_mask ^ self.fx.get(tq, 0)))
        self._h(tq)
        raw_s, s_eff = self._measure(tq)
        self.fz[last] = self.fz.get(last, 0) ^ s_eff
        self._reset(tq, raw_s)
        ey = [self._mxx(string[i + 1], anc[i]) for i in range(L)]

        # layer 4: Z measurement of the link ancillas
        self._barrier("Z(a)", anc)
        em = []
        for a in anc:
            raw, eff = self._measure(a)
            em.append(eff)
            self._reset(a, raw)

        # Pauli byproducts of the XX / ZZ measurements (tracked in the Pauli frame):
        #   Z on string[i] with parity XOR_{j>=i} (x_j ^ y_j),   X on string[i+1] with m_i
        c = 0
        for i in reversed(range(L)):
            c ^= ex[i] ^ ey[i]
            self.fz[string[i]] = self.fz.get(string[i], 0) ^ c
        for i in range(L):
            self.fx[string[i + 1]] = self.fx.get(string[i + 1], 0) ^ em[i]
        for q in fillers:  # fillers are |0> in the ideal frame: Z frame is irrelevant
            self.fz[q] = 0

        # 4) undo the basis change
        for l in support:
            if term[l] == "X":
                self._h(phys[l])
            elif term[l] == "Y":
                self._h(phys[l])
                self._s(phys[l])

        self.term_info.append(dict(
            term=dict(term), theta=float(theta), weight=len(support), chain=path,
            string_qubits=string, ancillas=anc, fillers=fillers, theta_qubit=tq,
            rot_parity_mask=m_mask,  # parity of these mid-circuit bits = 1  <=>  ROT correction fired
        ))
        if self.corrections == "each":
            self._flush(nodes)

    def _flush(self, qubits: Iterable[int]) -> None:
        todo = sorted(set(qubits))
        if not any(self.fx.get(q, 0) or (q in self._data and self.fz.get(q, 0)) for q in todo):
            return
        self._barrier("Pauli corrections", todo)
        for q in todo:
            if self.fx.get(q, 0):
                self.ops.append(("x_if", q, self.fx[q]))
            if q in self._data and self.fz.get(q, 0):
                self.ops.append(("z_if", q, self.fz[q]))
            self.fx[q] = 0
            self.fz[q] = 0

    def finalize(self) -> "DynamicPauliProgram":
        if not self._finalized:
            # Keep a terminal-readout view before materializing the reusable
            # circuit's data corrections and helper cleanup.
            self._terminal_ops_count = len(self.ops)
            self._terminal_fx, self._terminal_fz = dict(self.fx), dict(self.fz)
            self._flush(list(self.fx) + list(self.fz))
            self._finalized = True
        return self

    # -- Qiskit export -----------------------------------------------------
    def to_qiskit(self, prep=None, post=None, measure: bool = False, name: str = "pauli_exp_dynamic",
                  terminal_frame: bool = False):
        """Return a qiskit QuantumCircuit on all device qubits.

        prep:    optional QuantumCircuit on ``num_logical`` qubits, prepended onto
                 the logical (data) qubits.
        post:    optional QuantumCircuit on ``num_logical`` qubits, appended after
                 the exponentials (e.g. basis rotations before readout).
        measure: append a Z measurement of every logical qubit into register "meas"
                 (bit j = logical qubit j).
        terminal_frame: omit final physical corrections/cleanup, requiring
                 measure=True and a Clifford post circuit. Correct each shot's
                 meas bits with metadata["readout_flip_masks"] and its own mid
                 bits. This mode does not return helpers physically to zero.
        Transpile with ``initial_layout=list(range(backend.num_qubits))``: every
        two-qubit gate is already on a coupler, so no SWAPs are needed.
        """
        from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
        from qiskit.circuit.classical import expr

        self.finalize()
        if terminal_frame and not measure:
            raise ValueError("terminal_frame requires terminal measurement")
        masks = [0] * self.layout.num_logical
        if terminal_frame:
            from qiskit.quantum_info import Clifford, Pauli
            clifford = Clifford(post) if post is not None else None
            for bit in range(self.num_bits):
                x = [bool(self._terminal_fx.get(q, 0) & (1 << bit))
                     for q in self.layout.physical_qubits]
                z = [bool(self._terminal_fz.get(q, 0) & (1 << bit))
                     for q in self.layout.physical_qubits]
                frame = Pauli((z, x))
                if clifford is not None:
                    frame = frame.evolve(clifford, frame="s")
                for j, flip in enumerate(frame.x):
                    if flip:
                        masks[j] |= 1 << bit
        qr = QuantumRegister(self.device.num_qubits, "q")
        qc = QuantumCircuit(qr, name=name)
        if self.num_bits:
            mid = ClassicalRegister(self.num_bits, "mid")
            qc.add_register(mid)
        qc.global_phase = self.global_phase

        def cond(mask):
            bits = [mid[i] for i in _bits(mask)]
            if len(bits) == 1:
                return (bits[0], 1)
            e = expr.lift(bits[0])
            for b in bits[1:]:
                e = expr.bit_xor(e, b)
            return e

        data = [qr[p] for p in self.layout.physical_qubits]
        if prep is not None:
            qc.compose(prep, qubits=data, inplace=True)
        ops = self.ops[:self._terminal_ops_count] if terminal_frame else self.ops
        for op in ops:
            kind = op[0]
            if kind in ("h", "s", "sdg", "x", "z"):
                getattr(qc, kind)(qr[op[1]])
            elif kind == "cx":
                qc.cx(qr[op[1]], qr[op[2]])
            elif kind == "measure":
                qc.measure(qr[op[1]], mid[op[2]])
            elif kind == "rz":
                _, q, phi, mask = op
                if mask == 0:
                    qc.rz(phi, qr[q])
                else:
                    with qc.if_test(cond(mask)) as else_:
                        qc.rz(-phi, qr[q])
                    with else_:
                        qc.rz(phi, qr[q])
            elif kind in ("x_if", "z_if"):
                _, q, mask = op
                with qc.if_test(cond(mask)):
                    (qc.x if kind == "x_if" else qc.z)(qr[q])
            elif kind == "barrier":
                qc.barrier(*[qr[q] for q in op[2]], label=op[1])
        if post is not None:
            qc.compose(post, qubits=data, inplace=True)
        if measure:
            meas = ClassicalRegister(self.layout.num_logical, "meas")
            qc.add_register(meas)
            for j, p in enumerate(self.layout.physical_qubits):
                qc.measure(qr[p], meas[j])
        qc.metadata = {
            "logical_to_physical": [int(p) for p in self.layout.physical_qubits],
            "terms": [[" ".join(f"{v}{k}" for k, v in sorted(t.items())) or "I", float(th)]
                      for t, th in self.terms],
            "corrections": self.corrections,
            "terminal_frame": terminal_frame,
            "readout_flip_masks": masks,
        }
        return qc


def _op_qubits(op) -> Tuple[int, ...]:
    kind = op[0]
    if kind == "barrier":
        return tuple(op[2])
    if kind == "cx":
        return (op[1], op[2])
    return (op[1],)


# ----------------------------------------------------------------------------
# Front door
# ----------------------------------------------------------------------------
def build_program(paulis, theta: Optional[float] = None, layout: Optional[PaperGridLayout] = None,
                  device: Optional[GridDevice] = None, num_logical: Optional[int] = None,
                  corrections: str = "end", barriers: bool = True,
                  strategy: str = "auto", rot_correction: bool = True) -> DynamicPauliProgram:
    """Build the dynamic program for prod_k exp(-i theta_k P_k) (first term acts first)."""
    terms = parse_terms(paulis, theta)
    if layout is None:
        need = max([max(t) + 1 for t, _ in terms if t] + [1])
        if isinstance(paulis, str):
            m = _LABEL.match(paulis.strip().replace(" ", "").replace("_", ""))
            need = max(need, len(m.group(3)) if m else 0)
        n = max(need, num_logical or 0)
        layout = PaperGridLayout.auto(device or GridDevice.nighthawk(), n)
    prog = DynamicPauliProgram(layout, corrections=corrections, barriers=barriers,
                               rot_correction=rot_correction)
    for term, ang in terms:
        prog.add_exponential(term, ang, strategy=strategy)
    return prog.finalize()
