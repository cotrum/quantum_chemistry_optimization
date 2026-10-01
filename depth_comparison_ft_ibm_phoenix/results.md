# Dynamic vs CNOT-ladder Pauli exponentials on ibm_phoenix

Dynamic circuits: {'variant': 'ft', 'construction': 'paper Fig. 1: XX / ZZ(+θ) / X(θ)+XX / Z, |θ> ancilla', 'corrections': 'end', 'pauli_exp_dynamic_md5': '551635cc1b0dd654f0f9e0194e72e475'}

2q depth = qc.depth(lambda instr: len(instr.qubits) == 2); 2q gates = qc.num_nonlocal_gates(); gates = count_ops() without measure/reset/barrier/delay/if_else. Ladder = Qiskit PauliEvolutionGate with LieTrotter(cx_structure='chain'). Transpiled = ISA circuit for the backend (dynamic: preselected layout from layouts.json enforced, opt 3; ladder: layout + routing chosen by the transpiler, opt 3, best of 5 seeds). All diagrams use fold=-1.

| case | w | N | 2q depth dyn (untr) | 2q depth dyn (tr) | 2q depth ladder (untr) | 2q depth ladder (tr) | 2q gates dyn (tr) | 2q gates ladder (tr) | gates dyn (tr) | gates ladder (tr) | depth dyn (tr) | depth ladder (tr) | mid-circ. meas layers (dyn) | mid-circ. meas (dyn) | if_else (dyn) | ISA gates dyn | ISA gates ladder |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|---|
| Z2 | 2 | 2 | 6 | 6 | 1 | 2 | 8 | 2 | 49 | 11 | 36 | 11 | 4 | 6 | 6 | rz:23 sx:18 cz:8 measure:6 if_else:6 | rz:5 sx:4 cz:2 |
| Z3 | 3 | 3 | 6 | 6 | 4 | 4 | 14 | 4 | 94 | 22 | 39 | 17 | 4 | 10 | 9 | rz:44 sx:30 cz:14 measure:10 if_else:9 x:6 | rz:10 sx:8 cz:4 |
| Z4 | 4 | 4 | 6 | 6 | 6 | 6 | 20 | 6 | 118 | 33 | 40 | 23 | 4 | 14 | 12 | rz:53 sx:42 cz:20 measure:14 if_else:12 x:3 | rz:15 sx:12 cz:6 |
| Z5 | 5 | 5 | 6 | 6 | 8 | 8 | 26 | 8 | 163 | 44 | 41 | 29 | 4 | 18 | 15 | rz:74 sx:54 cz:26 measure:18 if_else:15 x:9 | rz:20 sx:16 cz:8 |
| Z6 | 6 | 6 | 6 | 6 | 10 | 10 | 32 | 10 | 183 | 55 | 39 | 35 | 4 | 22 | 18 | rz:81 sx:66 cz:32 measure:22 if_else:18 x:4 | rz:25 sx:20 cz:10 |
| Z8 | 8 | 8 | 6 | 6 | 14 | 14 | 44 | 14 | 252 | 77 | 44 | 47 | 4 | 30 | 24 | rz:111 sx:90 cz:44 measure:30 if_else:24 x:7 | rz:35 sx:28 cz:14 |
| Z10 | 10 | 10 | 6 | 6 | 18 | 18 | 56 | 18 | 314 | 99 | 44 | 59 | 4 | 38 | 30 | rz:137 sx:114 cz:56 measure:38 if_else:30 x:7 | rz:45 sx:36 cz:18 |
| Z12 | 12 | 12 | 6 | 6 | 22 | 22 | 68 | 22 | 397 | 121 | 47 | 71 | 4 | 46 | 36 | rz:175 sx:138 cz:68 measure:46 if_else:36 x:16 | rz:55 sx:44 cz:22 |
| Z16 | 16 | 16 | 6 | 6 | 30 | 30 | 92 | 30 | 514 | 165 | 51 | 95 | 4 | 62 | 48 | rz:223 sx:186 cz:92 measure:62 if_else:48 x:13 | rz:75 sx:60 cz:30 |
| Z20 | 20 | 20 | 6 | 6 | 38 | 38 | 116 | 38 | 666 | 209 | 55 | 119 | 4 | 78 | 60 | rz:291 sx:234 cz:116 measure:78 if_else:60 x:25 | rz:95 sx:76 cz:38 |
| Z25 | 25 | 25 | 6 | 6 | 48 | 48 | 146 | 48 | 838 | 264 | 60 | 149 | 4 | 98 | 75 | rz:366 sx:294 cz:146 measure:98 if_else:75 x:32 | rz:120 sx:96 cz:48 |
| XYZXYZXY | 8 | 8 | 6 | 6 | 14 | 14 | 44 | 14 | 229 | 74 | 43 | 49 | 4 | 30 | 25 | rz:100 sx:82 cz:44 measure:30 if_else:25 x:3 | rz:34 sx:26 cz:14 |
| ZIIXIYIZ_gapped | 4 | 8 | 6 | 6 | 6 | 6 | 56 | 6 | 324 | 31 | 37 | 20 | 4 | 38 | 24 | rz:143 sx:110 cz:56 measure:38 if_else:24 x:15 | rz:13 sx:10 cz:6 x:2 |
| XZZZX+YZZZY | 5 | 5 | 12 | 12 | 16 | 15 | 52 | 15 | 281 | 75 | 70 | 51 | 8 | 36 | 17 | rz:122 sx:101 cz:52 measure:36 if_else:17 x:6 | rz:30 sx:28 cz:15 x:2 |
