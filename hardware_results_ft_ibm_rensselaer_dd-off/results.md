# Dynamic vs CNOT ladder on ibm_rensselaer (job dato1plvr3kc73elraug), 4000 shots per circuit

Dynamic circuits: {'variant': 'ft', 'construction': 'paper Fig. 1: XX / ZZ(+θ) / X(θ)+XX / Z, |θ> ancilla', 'corrections': 'end', 'pauli_exp_dynamic_md5': '551635cc1b0dd654f0f9e0194e72e475'}

Ideal: P(0..0) = cos²θ, P(1_S) = sin²θ, leakage 0. θ_est = arcsin√(P(1_S)/(P(0..0)+P(1_S))).

DD = client-side dynamical decoupling (X-X, qiskit-ibm-runtime dynamic-circuit passes); gate metrics are for the circuit before DD padding.

Aer = noise-free Qiskit Aer check of the submitted circuit before submission (ok / skipped if more than 20 active qubits).

Wall-clock / shot = time per shot from the job's execution spans (circuit, readout, reset and the delay before the next shot). how: own = the circuit had execution spans to itself (exact); lsq = least-squares split of spans shared with other circuits; avg = spans always shared with the same circuits, so only their average is known. T2 = median T2 of the qubits the circuit uses. Job average: 283.9 µs per shot; QPU usage 20 s.

Wall-clock times extracted afterwards from the execution spans of job dato1plvr3kc73elraug (patch_timing.py); T1/T2: calibration at 2026-09-29 05:12 (time of the job).

| case | w | θ | circuit | DD | DD pulses | Aer | Hellinger | P(0..0) (ideal) | P(1_S) (ideal) | leakage | θ_est | θ_est − θ | 2q depth | 2q gates | depth | measurements | wall-clock / shot (µs) | how | T2 (µs) | wall-clock / T2 |
|---|--:|--:|---|---|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|--:|--:|
| Z3 | 3 | 0.400 | dynamic | off | 0 | ok | 0.297 | 0.240 (0.848) | 0.058 (0.152) | 0.702 | 0.458 | +0.058 | 6 | 14 | 40 | 13 | 283.94 | avg | 178 | 1.594 |
| Z3 | 3 | 0.400 | ladder | off | 0 | ok | 0.965 | 0.807 (0.848) | 0.158 (0.152) | 0.035 | 0.417 | +0.017 | 4 | 4 | 19 | 3 | 283.94 | avg | 237 | 1.198 |
| Z5 | 5 | 0.400 | dynamic | off | 0 | ok | 0.293 | 0.255 (0.848) | 0.038 (0.152) | 0.706 | 0.370 | -0.030 | 6 | 26 | 40 | 23 | 283.94 | avg | 201 | 1.414 |
| Z5 | 5 | 0.400 | ladder | off | 0 | ok | 0.935 | 0.824 (0.848) | 0.114 (0.152) | 0.063 | 0.355 | -0.045 | 8 | 8 | 34 | 5 | 283.94 | avg | 316 | 0.898 |
| Z8 | 8 | 0.400 | dynamic | off | 0 | ok | 0.316 | 0.242 (0.848) | 0.077 (0.152) | 0.680 | 0.514 | +0.114 | 6 | 44 | 44 | 38 | 283.94 | avg | 179 | 1.583 |
| Z8 | 8 | 0.400 | ladder | off | 0 | ok | 0.854 | 0.735 (0.848) | 0.120 (0.152) | 0.146 | 0.384 | -0.016 | 14 | 14 | 54 | 8 | 283.94 | avg | 215 | 1.318 |
| Z12 | 12 | 0.400 | dynamic | off | 0 | skipped | 0.107 | 0.085 (0.848) | 0.022 (0.152) | 0.893 | 0.470 | +0.070 | 6 | 68 | 49 | 58 | 283.94 | avg | 174 | 1.629 |
| Z12 | 12 | 0.400 | ladder | off | 0 | ok | 0.797 | 0.704 (0.848) | 0.096 (0.152) | 0.201 | 0.353 | -0.047 | 22 | 22 | 82 | 12 | 283.94 | avg | 291 | 0.976 |
| XYZXYZXY | 8 | 0.400 | dynamic | off | 0 | ok | 0.352 | 0.276 (0.848) | 0.079 (0.152) | 0.646 | 0.491 | +0.091 | 6 | 44 | 44 | 38 | 283.94 | avg | 179 | 1.583 |
| XYZXYZXY | 8 | 0.400 | ladder | off | 0 | ok | 0.864 | 0.745 (0.848) | 0.119 (0.152) | 0.136 | 0.381 | -0.019 | 14 | 14 | 52 | 8 | 283.94 | avg | 329 | 0.863 |
| XZIY_gapped | 3 | 0.400 | dynamic | off | 0 | ok | 0.536 | 0.451 (0.848) | 0.086 (0.152) | 0.463 | 0.411 | +0.011 | 6 | 26 | 40 | 22 | 283.94 | avg | 221 | 1.286 |
| XZIY_gapped | 3 | 0.400 | ladder | off | 0 | ok | 0.955 | 0.811 (0.848) | 0.144 (0.152) | 0.045 | 0.399 | -0.001 | 4 | 4 | 18 | 4 | 283.94 | avg | 245 | 1.161 |
| XYIZIX_gapped | 4 | 0.400 | dynamic | off | 0 | ok | 0.335 | 0.253 (0.848) | 0.089 (0.152) | 0.659 | 0.535 | +0.135 | 6 | 50 | 41 | 40 | 283.94 | avg | 210 | 1.353 |
| XYIZIX_gapped | 4 | 0.400 | ladder | off | 0 | ok | 0.946 | 0.819 (0.848) | 0.128 (0.152) | 0.053 | 0.377 | -0.023 | 6 | 6 | 26 | 6 | 283.94 | avg | 165 | 1.723 |
| ZIIXIYIZ_gapped | 4 | 0.400 | dynamic | off | 0 | skipped | 0.309 | 0.239 (0.848) | 0.073 (0.152) | 0.688 | 0.506 | +0.106 | 6 | 56 | 39 | 46 | 283.94 | avg | 179 | 1.583 |
| ZIIXIYIZ_gapped | 4 | 0.400 | ladder | off | 0 | ok | 0.952 | 0.815 (0.848) | 0.137 (0.152) | 0.048 | 0.388 | -0.012 | 6 | 6 | 25 | 8 | 283.94 | avg | 173 | 1.637 |
