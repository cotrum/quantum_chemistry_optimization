# Aer check of the circuits for ibm_phoenix

Dynamic circuits: {'variant': 'ft', 'construction': 'paper Fig. 1: XX / ZZ(+θ) / X(θ)+XX / Z, |θ> ancilla', 'corrections': 'end', 'pauli_exp_dynamic_md5': '551635cc1b0dd654f0f9e0194e72e475'}

Noise-free Qiskit Aer run of every circuit exactly as submitted (transpiled, with DD if on). ok = on every shot the logical-qubit outcome probabilities equal the ideal ones (max |p - p_ideal| < 1e-8) and, for dynamic circuits, both branches of the sign correction occurred; skipped = more than 20 active qubits.

| case | θ | circuit | DD | Aer | active qubits | shots | sign correction fired | max abs(p − p_ideal) | 2q depth | 2q gates | depth | measurements | layout |
|---|--:|---|---|---|--:|--:|--:|--:|--:|--:|--:|--:|---|
| Z3 | 0.400 | dynamic | off | ok | 6 | 256 | 127 | 7.8e-16 | 6 | 14 | 40 | 13 | 58 78 98 |
| Z3 | 0.400 | ladder | off | ok | 3 | 1 | – | 6.7e-16 | 4 | 4 | 20 | 3 | 97 96 86 |
| Z5 | 0.400 | dynamic | off | ok | 10 | 256 | 139 | 7.8e-16 | 6 | 26 | 42 | 23 | 18 38 58 78 98 |
| Z5 | 0.400 | ladder | off | ok | 5 | 1 | – | 6.7e-16 | 8 | 8 | 34 | 5 | 95 85 86 96 97 |
| Z8 | 0.400 | dynamic | off | ok | 16 | 256 | 133 | 1.7e-15 | 6 | 44 | 46 | 38 | 82 84 86 88 108 106 104 102 |
| Z8 | 0.400 | ladder | off | ok | 8 | 1 | – | 4.4e-16 | 14 | 14 | 54 | 8 | 97 96 86 85 95 105 104 103 |
| Z12 | 0.400 | dynamic | off | skipped | 24 | – | – | – | 6 | 68 | 49 | 58 | 44 64 84 104 106 86 66 46 48 68 88 108 |
| Z12 | 0.400 | ladder | off | ok | 12 | 1 | – | 6.7e-16 | 22 | 22 | 82 | 12 | 97 96 86 85 95 105 115 114 104 103 102 101 |
| XYZXYZXY | 0.400 | dynamic | off | ok | 16 | 256 | 133 | 8.9e-16 | 6 | 44 | 44 | 38 | 82 84 86 88 108 106 104 102 |
| XYZXYZXY | 0.400 | ladder | off | ok | 8 | 1 | – | 8.3e-17 | 14 | 14 | 52 | 8 | 103 104 105 95 85 86 96 97 |
| XZIY_gapped | 0.400 | dynamic | off | ok | 11 | 256 | 139 | 1.0e-15 | 6 | 26 | 37 | 22 | 48 68 88 108 |
| XZIY_gapped | 0.400 | ladder | off | ok | 4 | 1 | – | 1.4e-16 | 4 | 4 | 18 | 4 | 96 101 86 85 |
| XYIZIX_gapped | 0.400 | dynamic | off | ok | 20 | 256 | 115 | 1.8e-15 | 6 | 50 | 39 | 40 | 84 86 88 108 106 104 |
| XYIZIX_gapped | 0.400 | ladder | off | ok | 6 | 1 | – | 2.2e-16 | 6 | 6 | 26 | 6 | 103 89 113 101 114 115 |
| ZIIXIYIZ_gapped | 0.400 | dynamic | off | skipped | 24 | – | – | – | 6 | 56 | 38 | 46 | 82 84 86 88 108 106 104 102 |
| ZIIXIYIZ_gapped | 0.400 | ladder | off | ok | 8 | 1 | – | 5.6e-17 | 6 | 6 | 26 | 8 | 85 3 86 103 96 89 101 97 |
