# Dynamic vs CNOT ladder on ibm_rensselaer (job dato5uahcrkc73duhivg), 4000 shots per circuit

Dynamic circuits: {'variant': 'nisq_compact', 'construction': 'NISQ compact: XX as gate (H-CX-H) / ZZ measured / Rz(±2θ) on q_last / XX+Z(a) as one measurement', 'corrections': 'end', 'pauli_exp_nisq_compact_md5': '354346d2f62743a2c519c7b657960305', 'pauli_exp_dynamic_md5': '551635cc1b0dd654f0f9e0194e72e475'}

Ideal: P(0..0) = cos²θ, P(1_S) = sin²θ, leakage 0. θ_est = arcsin√(P(1_S)/(P(0..0)+P(1_S))).

DD = client-side dynamical decoupling (X-X, qiskit-ibm-runtime dynamic-circuit passes); gate metrics are for the circuit before DD padding.

Aer = noise-free Qiskit Aer check of the submitted circuit before submission (ok / skipped if more than 20 active qubits).

Wall-clock / shot = time per shot from the job's execution spans (circuit, readout, reset and the delay before the next shot). how: own = the circuit had execution spans to itself (exact); lsq = least-squares split of spans shared with other circuits; avg = spans always shared with the same circuits, so only their average is known. T2 = median T2 of the qubits the circuit uses. Job average: 277.4 µs per shot; QPU usage 37 s.

Wall-clock times extracted afterwards from the execution spans of job dato5uahcrkc73duhivg (patch_timing.py); T1/T2: calibration at 2026-09-29 05:20 (time of the job).

| case | w | θ | circuit | DD | DD pulses | Aer | Hellinger | P(0..0) (ideal) | P(1_S) (ideal) | leakage | θ_est | θ_est − θ | 2q depth | 2q gates | depth | measurements | wall-clock / shot (µs) | how | T2 (µs) | wall-clock / T2 |
|---|--:|--:|---|---|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|--:|--:|
| Z3 | 3 | 0.400 | dynamic | off | 0 | ok | 0.650 | 0.548 (0.848) | 0.102 (0.152) | 0.350 | 0.408 | +0.008 | 4 | 8 | 26 | 7 | 277.37 | avg | 168 | 1.654 |
| Z3 | 3 | 0.400 | dynamic | on | 38 | ok | 0.853 | 0.722 (0.848) | 0.132 (0.152) | 0.147 | 0.404 | +0.004 | 4 | 8 | 26 | 7 | 277.37 | avg | 168 | 1.654 |
| Z3 | 3 | 0.400 | ladder | off | 0 | ok | 0.967 | 0.825 (0.848) | 0.143 (0.152) | 0.033 | 0.394 | -0.006 | 4 | 4 | 19 | 3 | 277.37 | avg | 237 | 1.170 |
| Z3 | 3 | 0.400 | ladder | on | 8 | ok | 0.964 | 0.817 (0.848) | 0.147 (0.152) | 0.036 | 0.401 | +0.001 | 4 | 4 | 19 | 3 | 277.37 | avg | 237 | 1.170 |
| Z5 | 5 | 0.400 | dynamic | off | 0 | ok | 0.239 | 0.209 (0.848) | 0.030 (0.152) | 0.761 | 0.362 | -0.038 | 4 | 16 | 28 | 13 | 277.37 | avg | 189 | 1.471 |
| Z5 | 5 | 0.400 | dynamic | on | 118 | ok | 0.310 | 0.277 (0.848) | 0.035 (0.152) | 0.688 | 0.341 | -0.059 | 4 | 16 | 28 | 13 | 277.37 | avg | 189 | 1.471 |
| Z5 | 5 | 0.400 | ladder | off | 0 | ok | 0.938 | 0.827 (0.848) | 0.113 (0.152) | 0.060 | 0.354 | -0.046 | 8 | 8 | 34 | 5 | 277.37 | avg | 316 | 0.877 |
| Z5 | 5 | 0.400 | ladder | on | 16 | ok | 0.928 | 0.810 (0.848) | 0.119 (0.152) | 0.071 | 0.366 | -0.034 | 8 | 8 | 34 | 5 | 277.37 | avg | 316 | 0.877 |
| Z8 | 8 | 0.400 | dynamic | off | 0 | ok | 0.409 | 0.358 (0.848) | 0.051 (0.152) | 0.591 | 0.363 | -0.037 | 4 | 28 | 32 | 22 | 277.37 | avg | 170 | 1.629 |
| Z8 | 8 | 0.400 | dynamic | on | 284 | ok | 0.234 | 0.199 (0.848) | 0.035 (0.152) | 0.766 | 0.398 | -0.002 | 4 | 28 | 32 | 22 | 277.37 | avg | 170 | 1.629 |
| Z8 | 8 | 0.400 | ladder | off | 0 | ok | 0.846 | 0.734 (0.848) | 0.114 (0.152) | 0.153 | 0.375 | -0.025 | 14 | 14 | 54 | 8 | 277.37 | avg | 215 | 1.288 |
| Z8 | 8 | 0.400 | ladder | on | 28 | ok | 0.873 | 0.747 (0.848) | 0.126 (0.152) | 0.127 | 0.390 | -0.010 | 14 | 14 | 54 | 8 | 277.37 | avg | 215 | 1.288 |
| Z12 | 12 | 0.400 | dynamic | off | 0 | skipped | 0.190 | 0.160 (0.848) | 0.030 (0.152) | 0.810 | 0.407 | +0.007 | 4 | 44 | 35 | 34 | 277.37 | avg | 167 | 1.661 |
| Z12 | 12 | 0.400 | dynamic | on | 616 | skipped | 0.074 | 0.063 (0.848) | 0.011 (0.152) | 0.926 | 0.397 | -0.003 | 4 | 44 | 35 | 34 | 277.37 | avg | 167 | 1.661 |
| Z12 | 12 | 0.400 | ladder | off | 0 | ok | 0.783 | 0.687 (0.848) | 0.097 (0.152) | 0.216 | 0.359 | -0.041 | 22 | 22 | 82 | 12 | 277.37 | avg | 291 | 0.953 |
| Z12 | 12 | 0.400 | ladder | on | 44 | ok | 0.789 | 0.684 (0.848) | 0.105 (0.152) | 0.210 | 0.374 | -0.026 | 22 | 22 | 82 | 12 | 277.37 | avg | 291 | 0.953 |
| XYZXYZXY | 8 | 0.400 | dynamic | off | 0 | ok | 0.418 | 0.359 (0.848) | 0.059 (0.152) | 0.582 | 0.386 | -0.014 | 4 | 28 | 34 | 22 | 277.37 | avg | 170 | 1.629 |
| XYZXYZXY | 8 | 0.400 | dynamic | on | 284 | ok | 0.286 | 0.239 (0.848) | 0.047 (0.152) | 0.714 | 0.418 | +0.018 | 4 | 28 | 34 | 22 | 277.37 | avg | 170 | 1.629 |
| XYZXYZXY | 8 | 0.400 | ladder | off | 0 | ok | 0.861 | 0.734 (0.848) | 0.127 (0.152) | 0.139 | 0.395 | -0.005 | 14 | 14 | 52 | 8 | 277.37 | avg | 329 | 0.843 |
| XYZXYZXY | 8 | 0.400 | ladder | on | 26 | ok | 0.876 | 0.764 (0.848) | 0.113 (0.152) | 0.123 | 0.366 | -0.034 | 14 | 14 | 52 | 8 | 277.37 | avg | 329 | 0.843 |
| XZIY_gapped | 3 | 0.400 | dynamic | off | 0 | ok | 0.587 | 0.496 (0.848) | 0.091 (0.152) | 0.413 | 0.405 | +0.005 | 4 | 16 | 27 | 12 | 277.37 | avg | 217 | 1.278 |
| XZIY_gapped | 3 | 0.400 | dynamic | on | 108 | ok | 0.490 | 0.403 (0.848) | 0.087 (0.152) | 0.509 | 0.436 | +0.036 | 4 | 16 | 27 | 12 | 277.37 | avg | 217 | 1.278 |
| XZIY_gapped | 3 | 0.400 | ladder | off | 0 | ok | 0.956 | 0.804 (0.848) | 0.152 (0.152) | 0.044 | 0.410 | +0.010 | 4 | 4 | 18 | 4 | 277.37 | avg | 245 | 1.134 |
| XZIY_gapped | 3 | 0.400 | ladder | on | 8 | ok | 0.958 | 0.816 (0.848) | 0.142 (0.152) | 0.042 | 0.395 | -0.005 | 4 | 4 | 18 | 4 | 277.37 | avg | 245 | 1.134 |
| XYIZIX_gapped | 4 | 0.400 | dynamic | off | 0 | ok | 0.400 | 0.340 (0.848) | 0.059 (0.152) | 0.600 | 0.396 | -0.004 | 4 | 32 | 27 | 22 | 277.37 | avg | 207 | 1.343 |
| XYIZIX_gapped | 4 | 0.400 | dynamic | on | 218 | ok | 0.494 | 0.424 (0.848) | 0.070 (0.152) | 0.506 | 0.384 | -0.016 | 4 | 32 | 27 | 22 | 277.37 | avg | 207 | 1.343 |
| XYIZIX_gapped | 4 | 0.400 | ladder | off | 0 | ok | 0.941 | 0.798 (0.848) | 0.142 (0.152) | 0.059 | 0.399 | -0.001 | 6 | 6 | 26 | 6 | 277.37 | avg | 165 | 1.684 |
| XYIZIX_gapped | 4 | 0.400 | ladder | on | 10 | ok | 0.941 | 0.792 (0.848) | 0.149 (0.152) | 0.059 | 0.409 | +0.009 | 6 | 6 | 26 | 6 | 277.37 | avg | 165 | 1.684 |
| ZIIXIYIZ_gapped | 4 | 0.400 | dynamic | off | 0 | skipped | 0.388 | 0.333 (0.848) | 0.056 (0.152) | 0.612 | 0.388 | -0.012 | 4 | 36 | 26 | 26 | 277.37 | avg | 170 | 1.629 |
| ZIIXIYIZ_gapped | 4 | 0.400 | dynamic | on | 284 | skipped | 0.448 | 0.383 (0.848) | 0.065 (0.152) | 0.551 | 0.391 | -0.009 | 4 | 36 | 26 | 26 | 277.37 | avg | 170 | 1.629 |
| ZIIXIYIZ_gapped | 4 | 0.400 | ladder | off | 0 | ok | 0.949 | 0.815 (0.848) | 0.134 (0.152) | 0.051 | 0.386 | -0.014 | 6 | 6 | 25 | 8 | 277.37 | avg | 173 | 1.600 |
| ZIIXIYIZ_gapped | 4 | 0.400 | ladder | on | 12 | ok | 0.940 | 0.812 (0.848) | 0.128 (0.152) | 0.059 | 0.378 | -0.022 | 6 | 6 | 25 | 8 | 277.37 | avg | 173 | 1.600 |
