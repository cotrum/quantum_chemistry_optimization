"""Print the three dynamic implementations and their CNOT-ladder reference.

Examples:
    python print_circuits.py
    python print_circuits.py --term XYZ:0.4 --output circuit_comparison.txt
    python print_circuits.py --term ZZ:0.4 --term XX:-0.2

Pauli labels follow Qiskit's convention: the rightmost letter acts on logical
qubit 0. The dynamic circuits use a small local grid, without an IBM account.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from pauli_bench import VARIANTS, builder, ladder_circuit
from pauli_exp_dynamic import GridDevice, PaperGridLayout, parse_terms


def term_arg(value: str) -> tuple[str, float]:
    try:
        label, angle = value.rsplit(":", 1)
        theta = float(angle)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("use LABEL:ANGLE, for example XYZ:0.4") from exc
    label = label.upper()
    if not label or set(label) - set("IXYZ"):
        raise argparse.ArgumentTypeError("LABEL must contain only I, X, Y, and Z")
    return label, theta


def render(spec: list[tuple[str, float]], fold: int) -> str:
    n = max(len(label) for label, _ in spec)
    if any(len(label) != n for label, _ in spec):
        raise ValueError("all Pauli labels must have the same length")

    device = GridDevice(2, 2 * n + 1)
    layout = PaperGridLayout(device, n, shape=(1, n))
    terms = parse_terms(spec)
    sections = [
        "Pauli exponentials (applied in the order shown): "
        + " · ".join(f"exp(-i {angle:g} {label})" for label, angle in spec),
        f"Logical qubits: {n}; dynamic grid: {device.rows}x{device.cols}; "
        f"data qubits: {list(map(int, layout.physical_qubits))}",
        "Qiskit labels are little-endian: the rightmost Pauli acts on logical qubit 0.",
    ]

    for variant in VARIANTS:
        circuit = builder(variant)(spec, layout=layout, barriers=False).to_qiskit()
        sections.extend((
            f"\n=== {variant} dynamic circuit ({circuit.num_qubits} qubits, "
            f"{circuit.num_clbits} classical bits) ===",
            str(circuit.draw(output="text", fold=fold, idle_wires=False)),
        ))

    ladder = ladder_circuit(terms, n)
    # Qiskit can leave a two-qubit Pauli rotation as RXX/RYY/RZZ.
    # Expand it so the printed reference shows the actual CX chain.
    ladder = ladder.decompose(gates_to_decompose=["rxx", "ryy", "rzz"])
    sections.extend((
        f"\n=== CNOT ladder reference ({ladder.num_qubits} logical qubits) ===",
        str(ladder.draw(output="text", fold=fold, idle_wires=False)),
    ))
    return "\n".join(line.rstrip() for line in "\n".join(sections).splitlines()) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--term", type=term_arg, action="append", metavar="LABEL:ANGLE",
                        help="Pauli exponential to append; repeat for products (default: ZZ:0.4)")
    parser.add_argument("--fold", type=int, default=100, help="diagram width (default: 100)")
    parser.add_argument("--output", type=Path, help="also save the printed circuits to this text file")
    args = parser.parse_args()
    if args.fold <= 0:
        parser.error("--fold must be positive")
    try:
        result = render(args.term or [("ZZ", 0.4)], args.fold)
    except ValueError as exc:
        parser.error(str(exc))
    print(result, end="")
    if args.output:
        args.output.write_text(result, encoding="utf-8")


if __name__ == "__main__":
    main()
