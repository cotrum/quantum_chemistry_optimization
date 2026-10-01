# Dynamic vs CNOT-ladder Pauli exponentials on ibm_rensselaer

Dynamic circuits: {'variant': 'ft', 'construction': 'paper Fig. 1: XX / ZZ(+θ) / X(θ)+XX / Z, |θ> ancilla', 'corrections': 'end', 'pauli_exp_dynamic_md5': '551635cc1b0dd654f0f9e0194e72e475'}

2q depth = qc.depth(lambda instr: len(instr.qubits) == 2); 2q gates = qc.num_nonlocal_gates(); gates = count_ops() without measure/reset/barrier/delay/if_else. Ladder = Qiskit PauliEvolutionGate with LieTrotter(cx_structure='chain'). Transpiled = ISA circuit for the backend (dynamic: preselected layout from layouts.json enforced, opt 3; ladder: layout + routing chosen by the transpiler, opt 3, best of 5 seeds). All diagrams use fold=-1.

| case | w | N | 2q depth dyn (untr) | 2q depth dyn (tr) | 2q depth ladder (untr) | 2q depth ladder (tr) | 2q gates dyn (tr) | 2q gates ladder (tr) | gates dyn (tr) | gates ladder (tr) | depth dyn (tr) | depth ladder (tr) | mid-circ. meas layers (dyn) | mid-circ. meas (dyn) | if_else (dyn) | ISA gates dyn | ISA gates ladder |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|---|
| Z2 | 2 | 2 | 6 | 6 | 1 | 2 | 8 | 2 | 56 | 11 | 39 | 11 | 4 | 6 | 6 | rz:27 sx:18 cz:8 measure:6 if_else:6 x:3 | rz:5 sx:4 cz:2 |
| Z3 | 3 | 3 | 6 | 6 | 4 | 4 | 14 | 4 | 87 | 22 | 39 | 17 | 4 | 10 | 9 | rz:40 sx:30 cz:14 measure:10 if_else:9 x:3 | rz:10 sx:8 cz:4 |
| Z4 | 4 | 4 | 6 | 6 | 6 | 6 | 20 | 6 | 118 | 33 | 39 | 23 | 4 | 14 | 12 | rz:53 sx:42 cz:20 measure:14 if_else:12 x:3 | rz:15 sx:12 cz:6 |
| Z5 | 5 | 5 | 6 | 6 | 8 | 8 | 26 | 8 | 159 | 44 | 39 | 29 | 4 | 18 | 15 | rz:72 sx:54 cz:26 measure:18 if_else:15 x:7 | rz:20 sx:16 cz:8 |
| Z6 | 6 | 6 | 6 | 6 | 10 | 10 | 32 | 10 | 194 | 55 | 41 | 35 | 4 | 22 | 18 | rz:87 sx:66 cz:32 measure:22 if_else:18 x:9 | rz:25 sx:20 cz:10 |
| Z8 | 8 | 8 | 6 | 6 | 14 | 14 | 44 | 14 | 263 | 77 | 42 | 47 | 4 | 30 | 24 | rz:117 sx:90 cz:44 measure:30 if_else:24 x:12 | rz:35 sx:28 cz:14 |
| Z10 | 10 | 10 | 6 | 6 | 18 | 18 | 56 | 18 | 332 | 99 | 44 | 59 | 4 | 38 | 30 | rz:147 sx:114 cz:56 measure:38 if_else:30 x:15 | rz:45 sx:36 cz:18 |
| Z12 | 12 | 12 | 6 | 6 | 22 | 22 | 68 | 22 | 408 | 121 | 47 | 71 | 4 | 46 | 36 | rz:181 sx:138 cz:68 measure:46 if_else:36 x:21 | rz:55 sx:44 cz:22 |
| Z16 | 16 | 16 | 6 | 6 | 30 | 30 | 92 | 30 | 546 | 165 | 52 | 95 | 4 | 62 | 48 | rz:241 sx:186 cz:92 measure:62 if_else:48 x:27 | rz:75 sx:60 cz:30 |
| Z20 | 20 | 20 | 6 | 6 | 38 | 38 | 116 | 38 | 683 | 209 | 55 | 119 | 4 | 78 | 60 | rz:301 sx:234 cz:116 measure:78 if_else:60 x:32 | rz:95 sx:76 cz:38 |
| Z25 | 25 | 25 | 6 | 6 | 48 | 48 | 146 | 48 | 848 | 264 | 60 | 149 | 4 | 98 | 75 | rz:372 sx:294 cz:146 measure:98 if_else:75 x:36 | rz:120 sx:96 cz:48 |
| XYZXYZXY | 8 | 8 | 6 | 6 | 14 | 14 | 44 | 14 | 234 | 72 | 43 | 47 | 4 | 30 | 25 | rz:102 sx:82 cz:44 measure:30 if_else:25 x:6 | rz:31 sx:24 cz:14 x:3 |
| ZIIXIYIZ_gapped | 4 | 8 | 6 | 6 | 6 | 6 | 56 | 6 | 312 | 31 | 39 | 20 | 4 | 38 | 24 | rz:137 sx:110 cz:56 measure:38 if_else:24 x:9 | rz:13 sx:10 cz:6 x:2 |
| XZZZX+YZZZY | 5 | 5 | 12 | 12 | 16 | 15 | 52 | 15 | 285 | 73 | 72 | 52 | 8 | 36 | 17 | rz:124 sx:101 cz:52 measure:36 if_else:17 x:8 | rz:30 sx:28 cz:15 |
