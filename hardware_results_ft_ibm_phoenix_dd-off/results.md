# Dynamic vs CNOT ladder on ibm_phoenix (job datvd4bg95ks73ehhn6g), 4000 shots per circuit

Dynamic circuits: {'variant': 'ft', 'construction': 'paper Fig. 1: XX / ZZ(+θ) / X(θ)+XX / Z, |θ> ancilla', 'corrections': 'end', 'pauli_exp_dynamic_md5': '551635cc1b0dd654f0f9e0194e72e475'}

Ideal: P(0..0) = cos²θ, P(1_S) = sin²θ, leakage 0. θ_est = arcsin√(P(1_S)/(P(0..0)+P(1_S))).

DD = client-side dynamical decoupling (X-X, qiskit-ibm-runtime dynamic-circuit passes); gate metrics are for the circuit before DD padding.

Aer = noise-free Qiskit Aer check of the submitted circuit before submission (ok / skipped if more than 20 active qubits).

Wall-clock / shot = time per shot from the job's execution spans (circuit, readout, reset and the delay before the next shot). how: own = the circuit had execution spans to itself (exact); lsq = least-squares split of spans shared with other circuits; avg = spans always shared with the same circuits, so only their average is known. T2 = median T2 of the qubits the circuit uses. Job average: 34.7 µs per shot; QPU usage 4 s.

Wall-clock times extracted afterwards from the execution spans of job datvd4bg95ks73ehhn6g (patch_timing.py); T1/T2: calibration at 2026-09-29 13:34 (time of the job).

| case | w | θ | circuit | DD | DD pulses | Aer | Hellinger | P(0..0) (ideal) | P(1_S) (ideal) | leakage | θ_est | θ_est − θ | 2q depth | 2q gates | depth | measurements | wall-clock / shot (µs) | how | T2 (µs) | wall-clock / T2 |
|---|--:|--:|---|---|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|--:|--:|
| Z3 | 3 | 0.400 | dynamic | off | 0 | ok | 0.831 | 0.694 (0.848) | 0.138 (0.152) | 0.168 | 0.420 | +0.020 | 6 | 14 | 40 | 13 | 34.67 | avg | 174 | 0.200 |
| Z3 | 3 | 0.400 | ladder | off | 0 | ok | 0.654 | 0.591 (0.848) | 0.067 (0.152) | 0.342 | 0.325 | -0.075 | 4 | 4 | 20 | 3 | 34.67 | avg | 160 | 0.217 |
| Z5 | 5 | 0.400 | dynamic | off | 0 | ok | 0.635 | 0.528 (0.848) | 0.107 (0.152) | 0.364 | 0.423 | +0.023 | 6 | 26 | 42 | 23 | 34.67 | avg | 174 | 0.200 |
| Z5 | 5 | 0.400 | ladder | off | 0 | ok | 0.537 | 0.495 (0.848) | 0.048 (0.152) | 0.457 | 0.300 | -0.100 | 8 | 8 | 34 | 5 | 34.67 | avg | 160 | 0.216 |
| Z8 | 8 | 0.400 | dynamic | off | 0 | ok | 0.089 | 0.073 (0.848) | 0.016 (0.152) | 0.911 | 0.434 | +0.034 | 6 | 44 | 46 | 38 | 34.67 | avg | 148 | 0.234 |
| Z8 | 8 | 0.400 | ladder | off | 0 | ok | 0.508 | 0.455 (0.848) | 0.055 (0.152) | 0.490 | 0.335 | -0.065 | 14 | 14 | 54 | 8 | 34.67 | avg | 160 | 0.217 |
| Z12 | 12 | 0.400 | dynamic | off | 0 | skipped | 0.041 | 0.035 (0.848) | 0.005 (0.152) | 0.959 | 0.376 | -0.024 | 6 | 68 | 49 | 58 | 34.67 | avg | 169 | 0.205 |
| Z12 | 12 | 0.400 | ladder | off | 0 | ok | 0.455 | 0.410 (0.848) | 0.048 (0.152) | 0.543 | 0.328 | -0.072 | 22 | 22 | 82 | 12 | 34.67 | avg | 177 | 0.196 |
| XYZXYZXY | 8 | 0.400 | dynamic | off | 0 | ok | 0.108 | 0.086 (0.848) | 0.023 (0.152) | 0.891 | 0.477 | +0.077 | 6 | 44 | 44 | 38 | 34.67 | avg | 148 | 0.234 |
| XYZXYZXY | 8 | 0.400 | ladder | off | 0 | ok | 0.393 | 0.357 (0.848) | 0.038 (0.152) | 0.604 | 0.317 | -0.083 | 14 | 14 | 52 | 8 | 34.67 | avg | 160 | 0.217 |
| XZIY_gapped | 3 | 0.400 | dynamic | off | 0 | ok | 0.579 | 0.477 (0.848) | 0.103 (0.152) | 0.420 | 0.435 | +0.035 | 6 | 26 | 37 | 22 | 34.67 | avg | 172 | 0.201 |
| XZIY_gapped | 3 | 0.400 | ladder | off | 0 | ok | 0.733 | 0.613 (0.848) | 0.120 (0.152) | 0.267 | 0.417 | +0.017 | 4 | 4 | 18 | 4 | 34.67 | avg | 199 | 0.174 |
| XYIZIX_gapped | 4 | 0.400 | dynamic | off | 0 | ok | 0.427 | 0.331 (0.848) | 0.101 (0.152) | 0.569 | 0.504 | +0.104 | 6 | 50 | 39 | 40 | 34.67 | avg | 160 | 0.217 |
| XYIZIX_gapped | 4 | 0.400 | ladder | off | 0 | ok | 0.966 | 0.821 (0.848) | 0.146 (0.152) | 0.034 | 0.399 | -0.001 | 6 | 6 | 26 | 6 | 34.67 | avg | 198 | 0.175 |
| ZIIXIYIZ_gapped | 4 | 0.400 | dynamic | off | 0 | skipped | 0.261 | 0.217 (0.848) | 0.045 (0.152) | 0.739 | 0.426 | +0.026 | 6 | 56 | 38 | 46 | 34.67 | avg | 155 | 0.223 |
| ZIIXIYIZ_gapped | 4 | 0.400 | ladder | off | 0 | ok | 0.611 | 0.537 (0.848) | 0.075 (0.152) | 0.388 | 0.357 | -0.043 | 6 | 6 | 26 | 8 | 34.67 | avg | 199 | 0.174 |
