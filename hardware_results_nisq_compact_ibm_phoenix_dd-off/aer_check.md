# Aer check of the circuits for ibm_phoenix

Dynamic circuits: {'variant': 'nisq_compact', 'construction': 'NISQ compact: XX as gate (H-CX-H) / ZZ measured / Rz(±2θ) on q_last / XX+Z(a) as one measurement', 'corrections': 'end', 'pauli_exp_nisq_compact_md5': '354346d2f62743a2c519c7b657960305', 'pauli_exp_dynamic_md5': '551635cc1b0dd654f0f9e0194e72e475'}

Noise-free Qiskit Aer run of every circuit exactly as submitted (transpiled, with DD if on). ok = on every shot the logical-qubit outcome probabilities equal the ideal ones (max |p - p_ideal| < 1e-8) and, for dynamic circuits, both branches of the sign correction occurred; skipped = more than 20 active qubits.

| case | θ | circuit | DD | Aer | active qubits | shots | sign correction fired | max abs(p − p_ideal) | 2q depth | 2q gates | depth | measurements | layout |
|---|--:|---|---|---|--:|--:|--:|--:|--:|--:|--:|--:|---|
| Z3 | 0.400 | dynamic | off | ok | 5 | 256 | 118 | 6.7e-16 | 4 | 8 | 26 | 7 | 58 78 98 |
| Z3 | 0.400 | ladder | off | ok | 3 | 1 | – | 6.7e-16 | 4 | 4 | 20 | 3 | 97 96 86 |
| Z5 | 0.400 | dynamic | off | ok | 9 | 256 | 138 | 1.0e-15 | 4 | 16 | 28 | 13 | 18 38 58 78 98 |
| Z5 | 0.400 | ladder | off | ok | 5 | 1 | – | 6.7e-16 | 8 | 8 | 34 | 5 | 95 85 86 96 97 |
| Z8 | 0.400 | dynamic | off | ok | 15 | 256 | 122 | 2.9e-15 | 4 | 28 | 32 | 22 | 82 84 86 88 108 106 104 102 |
| Z8 | 0.400 | ladder | off | ok | 8 | 1 | – | 4.4e-16 | 14 | 14 | 54 | 8 | 97 96 86 85 95 105 104 103 |
| Z12 | 0.400 | dynamic | off | skipped | 23 | – | – | – | 4 | 44 | 38 | 34 | 44 64 84 104 106 86 66 46 48 68 88 108 |
| Z12 | 0.400 | ladder | off | ok | 12 | 1 | – | 6.7e-16 | 22 | 22 | 82 | 12 | 97 96 86 85 95 105 115 114 104 103 102 101 |
| XYZXYZXY | 0.400 | dynamic | off | ok | 15 | 256 | 122 | 7.8e-16 | 4 | 28 | 34 | 22 | 82 84 86 88 108 106 104 102 |
| XYZXYZXY | 0.400 | ladder | off | ok | 8 | 1 | – | 8.3e-17 | 14 | 14 | 52 | 8 | 103 104 105 95 85 86 96 97 |
| XZIY_gapped | 0.400 | dynamic | off | ok | 10 | 256 | 138 | 1.0e-15 | 4 | 16 | 27 | 12 | 48 68 88 108 |
| XZIY_gapped | 0.400 | ladder | off | ok | 4 | 1 | – | 1.4e-16 | 4 | 4 | 18 | 4 | 96 101 86 85 |
| XYIZIX_gapped | 0.400 | dynamic | off | ok | 19 | 256 | 129 | 1.4e-15 | 4 | 32 | 27 | 22 | 84 86 88 108 106 104 |
| XYIZIX_gapped | 0.400 | ladder | off | ok | 6 | 1 | – | 2.2e-16 | 6 | 6 | 26 | 6 | 103 89 113 101 114 115 |
| ZIIXIYIZ_gapped | 0.400 | dynamic | off | skipped | 23 | – | – | – | 4 | 36 | 26 | 26 | 82 84 86 88 108 106 104 102 |
| ZIIXIYIZ_gapped | 0.400 | ladder | off | ok | 8 | 1 | – | 5.6e-17 | 6 | 6 | 26 | 8 | 85 3 86 103 96 89 101 97 |
