# quantum_chemistry_optimization

The repository includes source code, circuit data, result tables, reports, and
overview plots. Detailed circuit, layout, and per-case PNG plots are generated
locally by the experiment scripts and are excluded from Git to keep the
repository small.

To print the circuits for the fault-tolerant, NISQ, NISQ compact, and CNOT
ladder implementations without connecting to an IBM backend, run
`python print_circuits.py`. Use `--term XYZ:0.4` to choose a Pauli string and
angle, repeat `--term` for a product of exponentials, or add
`--output circuit_comparison.txt` to save the diagrams.
