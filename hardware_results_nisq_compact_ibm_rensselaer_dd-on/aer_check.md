# Aer check of the circuits for ibm_rensselaer

Dynamic circuits: {'variant': 'nisq_compact', 'construction': 'NISQ compact: XX as gate (H-CX-H) / ZZ measured / Rz(±2θ) on q_last / XX+Z(a) as one measurement', 'corrections': 'end', 'pauli_exp_nisq_compact_md5': '354346d2f62743a2c519c7b657960305', 'pauli_exp_dynamic_md5': '551635cc1b0dd654f0f9e0194e72e475'}

Noise-free Qiskit Aer run of every circuit exactly as submitted (transpiled, with DD if on). ok = on every shot the logical-qubit outcome probabilities equal the ideal ones (max |p - p_ideal| < 1e-8) and, for dynamic circuits, both branches of the sign correction occurred; skipped = more than 20 active qubits.

| case | θ | circuit | DD | Aer | active qubits | shots | sign correction fired | max abs(p − p_ideal) | 2q depth | 2q gates | depth | measurements | layout |
|---|--:|---|---|---|--:|--:|--:|--:|--:|--:|--:|--:|---|
| Z3 | 0.400 | dynamic | on | ok | 5 | 256 | 118 | 6.7e-16 | 4 | 8 | 26 | 7 | 94 96 98 |
| Z3 | 0.400 | ladder | on | ok | 3 | 1 | – | 6.7e-16 | 4 | 4 | 19 | 3 | 22 12 2 |
| Z5 | 0.400 | dynamic | on | ok | 9 | 256 | 138 | 7.8e-16 | 4 | 16 | 28 | 13 | 18 38 58 78 98 |
| Z5 | 0.400 | ladder | on | ok | 5 | 1 | – | 6.7e-16 | 8 | 8 | 34 | 5 | 117 116 106 96 86 |
| Z8 | 0.400 | dynamic | on | ok | 15 | 256 | 122 | 2.9e-15 | 4 | 28 | 32 | 22 | 72 74 76 78 98 96 94 92 |
| Z8 | 0.400 | ladder | on | ok | 8 | 1 | – | 4.4e-16 | 14 | 14 | 54 | 8 | 65 75 85 86 96 106 116 117 |
| Z12 | 0.400 | dynamic | on | skipped | 23 | – | – | – | 4 | 44 | 35 | 34 | 62 64 66 68 88 86 84 82 102 104 106 108 |
| Z12 | 0.400 | ladder | on | ok | 12 | 1 | – | 6.7e-16 | 22 | 22 | 82 | 12 | 117 116 106 96 97 98 99 89 88 78 79 69 |
| XYZXYZXY | 0.400 | dynamic | on | ok | 15 | 256 | 122 | 7.8e-16 | 4 | 28 | 34 | 22 | 72 74 76 78 98 96 94 92 |
| XYZXYZXY | 0.400 | ladder | on | ok | 8 | 1 | – | 4.4e-16 | 14 | 14 | 52 | 8 | 117 116 106 96 97 98 99 89 |
| XZIY_gapped | 0.400 | dynamic | on | ok | 10 | 256 | 138 | 8.9e-16 | 4 | 16 | 27 | 12 | 28 48 68 88 |
| XZIY_gapped | 0.400 | ladder | on | ok | 4 | 1 | – | 4.4e-16 | 4 | 4 | 18 | 4 | 2 119 12 22 |
| XYIZIX_gapped | 0.400 | dynamic | on | ok | 19 | 256 | 129 | 1.9e-15 | 4 | 32 | 27 | 22 | 74 76 78 98 96 94 |
| XYIZIX_gapped | 0.400 | ladder | on | ok | 6 | 1 | – | 2.2e-16 | 6 | 6 | 26 | 6 | 96 0 106 9 116 117 |
| ZIIXIYIZ_gapped | 0.400 | dynamic | on | skipped | 23 | – | – | – | 4 | 36 | 26 | 26 | 72 74 76 78 98 96 94 92 |
| ZIIXIYIZ_gapped | 0.400 | ladder | on | ok | 8 | 1 | – | 2.2e-16 | 6 | 6 | 25 | 8 | 117 2 116 69 106 0 9 96 |
