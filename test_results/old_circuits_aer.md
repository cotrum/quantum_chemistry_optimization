# Old dynamic circuits (wrong_results/depth_comparison) vs Qiskit PauliEvolutionGate, Qiskit Aer

Random input state on the data qubits, 1024 shots, per-shot density matrix of the data qubits (helpers traced out). Correct = every shot has fidelity >= 1 - 1e-09.

| case | logical qubits | active qubits | status | shots with F < 1-tol | min F | mean F | distinct outcomes |
|---|--:|--:|---|--:|--:|--:|--:|
| XYZXYZXY | 8 | 15 | correct | 0 / 1024 | 0.999999999999999 | 1.000000000000000 | 994 |
| XZZZX+YZZZY | 5 | 9 | correct | 0 / 1024 | 1.000000000000000 | 1.000000000000000 | 1015 |
| Z10 | 10 | 19 | correct | 0 / 1024 | 0.999999999999998 | 0.999999999999998 | 1022 |
| Z12 | 12 | 23 | skipped (> 20 qubits) | | | | |
| Z16 | 16 | 31 | skipped (> 20 qubits) | | | | |
| Z2 | 2 | 3 | correct | 0 / 1024 | 1.000000000000000 | 1.000000000000000 | 4 |
| Z20 | 20 | 39 | skipped (> 20 qubits) | | | | |
| Z25 | 25 | 49 | skipped (> 20 qubits) | | | | |
| Z3 | 3 | 5 | correct | 0 / 1024 | 1.000000000000000 | 1.000000000000000 | 16 |
| Z4 | 4 | 7 | correct | 0 / 1024 | 1.000000000000000 | 1.000000000000000 | 64 |
| Z5 | 5 | 9 | correct | 0 / 1024 | 1.000000000000000 | 1.000000000000000 | 251 |
| Z6 | 6 | 11 | correct | 0 / 1024 | 1.000000000000000 | 1.000000000000000 | 636 |
| Z8 | 8 | 15 | correct | 0 / 1024 | 1.000000000000000 | 1.000000000000000 | 990 |
| ZIIXIYIZ_gapped | 8 | 23 | skipped (> 20 qubits) | | | | |
