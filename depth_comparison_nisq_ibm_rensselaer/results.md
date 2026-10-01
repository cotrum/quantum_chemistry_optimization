# Dynamic vs CNOT-ladder Pauli exponentials on ibm_rensselaer

Dynamic circuits: {'variant': 'nisq', 'construction': 'paper Fig. 1, θ rotation as a single-qubit gate (NISQ): XX / ZZ / Rz(±2θ) on q_last + XX / Z, no |θ> ancilla', 'corrections': 'end', 'pauli_exp_nisq_md5': '862580ff757319de22b342366ab6c877', 'pauli_exp_dynamic_md5': '551635cc1b0dd654f0f9e0194e72e475'}

2q depth = qc.depth(lambda instr: len(instr.qubits) == 2); 2q gates = qc.num_nonlocal_gates(); gates = count_ops() without measure/reset/barrier/delay/if_else. Ladder = Qiskit PauliEvolutionGate with LieTrotter(cx_structure='chain'). Transpiled = ISA circuit for the backend (dynamic: preselected layout from layouts.json enforced, opt 3; ladder: layout + routing chosen by the transpiler, opt 3, best of 5 seeds). All diagrams use fold=-1.

| case | w | N | 2q depth dyn (untr) | 2q depth dyn (tr) | 2q depth ladder (untr) | 2q depth ladder (tr) | 2q gates dyn (tr) | 2q gates ladder (tr) | gates dyn (tr) | gates ladder (tr) | depth dyn (tr) | depth ladder (tr) | mid-circ. meas layers (dyn) | mid-circ. meas (dyn) | if_else (dyn) | ISA gates dyn | ISA gates ladder |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|---|
| Z2 | 2 | 2 | 6 | 6 | 1 | 2 | 6 | 2 | 41 | 11 | 36 | 11 | 4 | 4 | 4 | rz:20 sx:12 cz:6 measure:4 if_else:4 x:3 | rz:5 sx:4 cz:2 |
| Z3 | 3 | 3 | 6 | 6 | 4 | 4 | 12 | 4 | 72 | 22 | 35 | 17 | 4 | 8 | 7 | rz:33 sx:24 cz:12 measure:8 if_else:7 x:3 | rz:10 sx:8 cz:4 |
| Z4 | 4 | 4 | 6 | 6 | 6 | 6 | 18 | 6 | 103 | 33 | 37 | 23 | 4 | 12 | 10 | rz:46 sx:36 cz:18 measure:12 if_else:10 x:3 | rz:15 sx:12 cz:6 |
| Z5 | 5 | 5 | 6 | 6 | 8 | 8 | 24 | 8 | 144 | 44 | 37 | 29 | 4 | 16 | 13 | rz:65 sx:48 cz:24 measure:16 if_else:13 x:7 | rz:20 sx:16 cz:8 |
| Z6 | 6 | 6 | 6 | 6 | 10 | 10 | 30 | 10 | 179 | 55 | 39 | 35 | 4 | 20 | 16 | rz:80 sx:60 cz:30 measure:20 if_else:16 x:9 | rz:25 sx:20 cz:10 |
| Z8 | 8 | 8 | 6 | 6 | 14 | 14 | 42 | 14 | 248 | 77 | 40 | 47 | 4 | 28 | 22 | rz:110 sx:84 cz:42 measure:28 if_else:22 x:12 | rz:35 sx:28 cz:14 |
| Z10 | 10 | 10 | 6 | 6 | 18 | 18 | 54 | 18 | 317 | 99 | 44 | 59 | 4 | 36 | 28 | rz:140 sx:108 cz:54 measure:36 if_else:28 x:15 | rz:45 sx:36 cz:18 |
| Z12 | 12 | 12 | 6 | 6 | 22 | 22 | 66 | 22 | 393 | 121 | 45 | 71 | 4 | 44 | 34 | rz:174 sx:132 cz:66 measure:44 if_else:34 x:21 | rz:55 sx:44 cz:22 |
| Z16 | 16 | 16 | 6 | 6 | 30 | 30 | 90 | 30 | 531 | 165 | 50 | 95 | 4 | 60 | 46 | rz:234 sx:180 cz:90 measure:60 if_else:46 x:27 | rz:75 sx:60 cz:30 |
| Z20 | 20 | 20 | 6 | 6 | 38 | 38 | 114 | 38 | 668 | 209 | 53 | 119 | 4 | 76 | 58 | rz:294 sx:228 cz:114 measure:76 if_else:58 x:32 | rz:95 sx:76 cz:38 |
| Z25 | 25 | 25 | 6 | 6 | 48 | 48 | 144 | 48 | 833 | 264 | 58 | 149 | 4 | 96 | 73 | rz:365 sx:288 cz:144 measure:96 if_else:73 x:36 | rz:120 sx:96 cz:48 |
| XYZXYZXY | 8 | 8 | 6 | 6 | 14 | 14 | 42 | 14 | 219 | 72 | 41 | 47 | 4 | 28 | 23 | rz:95 sx:76 cz:42 measure:28 if_else:23 x:6 | rz:31 sx:24 cz:14 x:3 |
| ZIIXIYIZ_gapped | 4 | 8 | 6 | 6 | 6 | 6 | 54 | 6 | 297 | 31 | 36 | 20 | 4 | 36 | 22 | rz:130 sx:104 cz:54 measure:36 if_else:22 x:9 | rz:13 sx:10 cz:6 x:2 |
| XZZZX+YZZZY | 5 | 5 | 12 | 12 | 16 | 15 | 48 | 15 | 255 | 73 | 69 | 52 | 8 | 32 | 15 | rz:110 sx:89 cz:48 measure:32 if_else:15 x:8 | rz:30 sx:28 cz:15 |
