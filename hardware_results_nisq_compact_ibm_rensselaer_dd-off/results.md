# Dynamic vs CNOT ladder on ibm_rensselaer (job dato4trojkfs738r25m0), 4000 shots per circuit

Dynamic circuits: {'variant': 'nisq_compact', 'construction': 'NISQ compact: XX as gate (H-CX-H) / ZZ measured / Rz(±2θ) on q_last / XX+Z(a) as one measurement', 'corrections': 'end', 'pauli_exp_nisq_compact_md5': '354346d2f62743a2c519c7b657960305', 'pauli_exp_dynamic_md5': '551635cc1b0dd654f0f9e0194e72e475'}

Ideal: P(0..0) = cos²θ, P(1_S) = sin²θ, leakage 0. θ_est = arcsin√(P(1_S)/(P(0..0)+P(1_S))).

DD = client-side dynamical decoupling (X-X, qiskit-ibm-runtime dynamic-circuit passes); gate metrics are for the circuit before DD padding.

Aer = noise-free Qiskit Aer check of the submitted circuit before submission (ok / skipped if more than 20 active qubits).

Wall-clock / shot = time per shot from the job's execution spans (circuit, readout, reset and the delay before the next shot). how: own = the circuit had execution spans to itself (exact); lsq = least-squares split of spans shared with other circuits; avg = spans always shared with the same circuits, so only their average is known. T2 = median T2 of the qubits the circuit uses. Job average: 281.0 µs per shot; QPU usage 19 s.

Wall-clock times extracted afterwards from the execution spans of job dato4trojkfs738r25m0 (patch_timing.py); T1/T2: calibration at 2026-09-29 05:18 (time of the job).

| case | w | θ | circuit | DD | DD pulses | Aer | Hellinger | P(0..0) (ideal) | P(1_S) (ideal) | leakage | θ_est | θ_est − θ | 2q depth | 2q gates | depth | measurements | wall-clock / shot (µs) | how | T2 (µs) | wall-clock / T2 |
|---|--:|--:|---|---|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|--:|--:|
| Z3 | 3 | 0.400 | dynamic | off | 0 | ok | 0.646 | 0.552 (0.848) | 0.094 (0.152) | 0.354 | 0.391 | -0.009 | 4 | 8 | 26 | 7 | 281.00 | avg | 168 | 1.676 |
| Z3 | 3 | 0.400 | ladder | off | 0 | ok | 0.967 | 0.817 (0.848) | 0.150 (0.152) | 0.032 | 0.405 | +0.005 | 4 | 4 | 19 | 3 | 281.00 | avg | 237 | 1.186 |
| Z5 | 5 | 0.400 | dynamic | off | 0 | ok | 0.243 | 0.215 (0.848) | 0.028 (0.152) | 0.756 | 0.346 | -0.054 | 4 | 16 | 28 | 13 | 281.00 | avg | 189 | 1.490 |
| Z5 | 5 | 0.400 | ladder | off | 0 | ok | 0.940 | 0.818 (0.848) | 0.123 (0.152) | 0.060 | 0.370 | -0.030 | 8 | 8 | 34 | 5 | 281.00 | avg | 316 | 0.889 |
| Z8 | 8 | 0.400 | dynamic | off | 0 | ok | 0.402 | 0.344 (0.848) | 0.059 (0.152) | 0.598 | 0.392 | -0.008 | 4 | 28 | 32 | 22 | 281.00 | avg | 170 | 1.650 |
| Z8 | 8 | 0.400 | ladder | off | 0 | ok | 0.829 | 0.724 (0.848) | 0.106 (0.152) | 0.170 | 0.366 | -0.034 | 14 | 14 | 54 | 8 | 281.00 | avg | 215 | 1.305 |
| Z12 | 12 | 0.400 | dynamic | off | 0 | skipped | 0.139 | 0.117 (0.848) | 0.022 (0.152) | 0.861 | 0.407 | +0.007 | 4 | 44 | 35 | 34 | 281.00 | avg | 167 | 1.683 |
| Z12 | 12 | 0.400 | ladder | off | 0 | ok | 0.784 | 0.686 (0.848) | 0.099 (0.152) | 0.215 | 0.364 | -0.036 | 22 | 22 | 82 | 12 | 281.00 | avg | 291 | 0.966 |
| XYZXYZXY | 8 | 0.400 | dynamic | off | 0 | ok | 0.407 | 0.343 (0.848) | 0.064 (0.152) | 0.593 | 0.408 | +0.008 | 4 | 28 | 34 | 22 | 281.00 | avg | 170 | 1.650 |
| XYZXYZXY | 8 | 0.400 | ladder | off | 0 | ok | 0.862 | 0.738 (0.848) | 0.124 (0.152) | 0.138 | 0.390 | -0.010 | 14 | 14 | 52 | 8 | 281.00 | avg | 329 | 0.854 |
| XZIY_gapped | 3 | 0.400 | dynamic | off | 0 | ok | 0.585 | 0.508 (0.848) | 0.077 (0.152) | 0.415 | 0.372 | -0.028 | 4 | 16 | 27 | 12 | 281.00 | avg | 217 | 1.295 |
| XZIY_gapped | 3 | 0.400 | ladder | off | 0 | ok | 0.958 | 0.811 (0.848) | 0.147 (0.152) | 0.042 | 0.403 | +0.003 | 4 | 4 | 18 | 4 | 281.00 | avg | 245 | 1.149 |
| XYIZIX_gapped | 4 | 0.400 | dynamic | off | 0 | ok | 0.401 | 0.344 (0.848) | 0.057 (0.152) | 0.599 | 0.387 | -0.013 | 4 | 32 | 27 | 22 | 281.00 | avg | 207 | 1.361 |
| XYIZIX_gapped | 4 | 0.400 | ladder | off | 0 | ok | 0.942 | 0.805 (0.848) | 0.137 (0.152) | 0.058 | 0.391 | -0.009 | 6 | 6 | 26 | 6 | 281.00 | avg | 165 | 1.706 |
| ZIIXIYIZ_gapped | 4 | 0.400 | dynamic | off | 0 | skipped | 0.389 | 0.339 (0.848) | 0.051 (0.152) | 0.610 | 0.371 | -0.029 | 4 | 36 | 26 | 26 | 281.00 | avg | 170 | 1.650 |
| ZIIXIYIZ_gapped | 4 | 0.400 | ladder | off | 0 | ok | 0.951 | 0.820 (0.848) | 0.132 (0.152) | 0.049 | 0.381 | -0.019 | 6 | 6 | 25 | 8 | 281.00 | avg | 173 | 1.621 |
