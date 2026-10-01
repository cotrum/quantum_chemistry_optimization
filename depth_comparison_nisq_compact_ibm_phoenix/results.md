# Dynamic vs CNOT-ladder Pauli exponentials on ibm_phoenix

Dynamic circuits: {'variant': 'nisq_compact', 'construction': 'NISQ compact: XX as gate (H-CX-H) / ZZ measured / Rz(±2θ) on q_last / XX+Z(a) as one measurement', 'corrections': 'end', 'pauli_exp_nisq_compact_md5': '354346d2f62743a2c519c7b657960305', 'pauli_exp_dynamic_md5': '551635cc1b0dd654f0f9e0194e72e475'}

2q depth = qc.depth(lambda instr: len(instr.qubits) == 2); 2q gates = qc.num_nonlocal_gates(); gates = count_ops() without measure/reset/barrier/delay/if_else. Ladder = Qiskit PauliEvolutionGate with LieTrotter(cx_structure='chain'). Transpiled = ISA circuit for the backend (dynamic: preselected layout from layouts.json enforced, opt 3; ladder: layout + routing chosen by the transpiler, opt 3, best of 5 seeds). All diagrams use fold=-1.

| case | w | N | 2q depth dyn (untr) | 2q depth dyn (tr) | 2q depth ladder (untr) | 2q depth ladder (tr) | 2q gates dyn (tr) | 2q gates ladder (tr) | gates dyn (tr) | gates ladder (tr) | depth dyn (tr) | depth ladder (tr) | mid-circ. meas layers (dyn) | mid-circ. meas (dyn) | if_else (dyn) | ISA gates dyn | ISA gates ladder |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|---|
| Z2 | 2 | 2 | 4 | 4 | 1 | 2 | 4 | 2 | 26 | 11 | 21 | 11 | 2 | 2 | 3 | rz:12 sx:10 cz:4 if_else:3 measure:2 | rz:5 sx:4 cz:2 |
| Z3 | 3 | 3 | 4 | 4 | 4 | 4 | 8 | 4 | 49 | 22 | 22 | 17 | 2 | 4 | 5 | rz:21 sx:20 cz:8 if_else:5 measure:4 | rz:10 sx:8 cz:4 |
| Z4 | 4 | 4 | 4 | 4 | 6 | 6 | 12 | 6 | 72 | 33 | 23 | 23 | 2 | 6 | 7 | rz:30 sx:30 cz:12 if_else:7 measure:6 | rz:15 sx:12 cz:6 |
| Z5 | 5 | 5 | 4 | 4 | 8 | 8 | 16 | 8 | 95 | 44 | 24 | 29 | 2 | 8 | 9 | sx:40 rz:39 cz:16 if_else:9 measure:8 | rz:20 sx:16 cz:8 |
| Z6 | 6 | 6 | 4 | 4 | 10 | 10 | 20 | 10 | 118 | 55 | 25 | 35 | 2 | 10 | 11 | sx:50 rz:48 cz:20 if_else:11 measure:10 | rz:25 sx:20 cz:10 |
| Z8 | 8 | 8 | 4 | 4 | 14 | 14 | 28 | 14 | 164 | 77 | 27 | 47 | 2 | 14 | 15 | sx:70 rz:66 cz:28 if_else:15 measure:14 | rz:35 sx:28 cz:14 |
| Z10 | 10 | 10 | 4 | 4 | 18 | 18 | 36 | 18 | 210 | 99 | 29 | 59 | 2 | 18 | 19 | sx:90 rz:84 cz:36 if_else:19 measure:18 | rz:45 sx:36 cz:18 |
| Z12 | 12 | 12 | 4 | 4 | 22 | 22 | 44 | 22 | 256 | 121 | 33 | 71 | 2 | 22 | 23 | sx:110 rz:102 cz:44 if_else:23 measure:22 | rz:55 sx:44 cz:22 |
| Z16 | 16 | 16 | 4 | 4 | 30 | 30 | 60 | 30 | 348 | 165 | 35 | 95 | 2 | 30 | 31 | sx:150 rz:138 cz:60 if_else:31 measure:30 | rz:75 sx:60 cz:30 |
| Z20 | 20 | 20 | 4 | 4 | 38 | 38 | 76 | 38 | 440 | 209 | 39 | 119 | 2 | 38 | 39 | sx:190 rz:174 cz:76 if_else:39 measure:38 | rz:95 sx:76 cz:38 |
| Z25 | 25 | 25 | 4 | 4 | 48 | 48 | 96 | 48 | 555 | 264 | 47 | 149 | 2 | 48 | 49 | sx:240 rz:219 cz:96 if_else:49 measure:48 | rz:120 sx:96 cz:48 |
| XYZXYZXY | 8 | 8 | 4 | 4 | 14 | 14 | 28 | 14 | 155 | 74 | 31 | 49 | 2 | 14 | 18 | rz:63 sx:62 cz:28 if_else:18 measure:14 x:2 | rz:34 sx:26 cz:14 |
| ZIIXIYIZ_gapped | 4 | 8 | 4 | 4 | 6 | 6 | 36 | 6 | 206 | 31 | 26 | 20 | 2 | 18 | 14 | sx:86 rz:83 cz:36 measure:18 if_else:14 x:1 | rz:13 sx:10 cz:6 x:2 |
| XZZZX+YZZZY | 5 | 5 | 8 | 8 | 16 | 15 | 32 | 15 | 173 | 75 | 43 | 51 | 4 | 16 | 11 | sx:73 rz:68 cz:32 measure:16 if_else:11 | rz:30 sx:28 cz:15 x:2 |
