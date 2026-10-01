# Dynamic vs CNOT ladder on ibm_rensselaer (job dato5c3g95ks73eh926g), 4000 shots per circuit

Dynamic circuits: {'variant': 'nisq_compact', 'construction': 'NISQ compact: XX as gate (H-CX-H) / ZZ measured / Rz(±2θ) on q_last / XX+Z(a) as one measurement', 'corrections': 'end', 'pauli_exp_nisq_compact_md5': '354346d2f62743a2c519c7b657960305', 'pauli_exp_dynamic_md5': '551635cc1b0dd654f0f9e0194e72e475'}

Ideal: P(0..0) = cos²θ, P(1_S) = sin²θ, leakage 0. θ_est = arcsin√(P(1_S)/(P(0..0)+P(1_S))).

DD = client-side dynamical decoupling (X-X, qiskit-ibm-runtime dynamic-circuit passes); gate metrics are for the circuit before DD padding.

Aer = noise-free Qiskit Aer check of the submitted circuit before submission (ok / skipped if more than 20 active qubits).

Wall-clock / shot = time per shot from the job's execution spans (circuit, readout, reset and the delay before the next shot). how: own = the circuit had execution spans to itself (exact); lsq = least-squares split of spans shared with other circuits; avg = spans always shared with the same circuits, so only their average is known. T2 = median T2 of the qubits the circuit uses. Job average: 288.0 µs per shot; QPU usage 20 s.

Wall-clock times extracted afterwards from the execution spans of job dato5c3g95ks73eh926g (patch_timing.py); T1/T2: calibration at 2026-09-29 05:19 (time of the job).

| case | w | θ | circuit | DD | DD pulses | Aer | Hellinger | P(0..0) (ideal) | P(1_S) (ideal) | leakage | θ_est | θ_est − θ | 2q depth | 2q gates | depth | measurements | wall-clock / shot (µs) | how | T2 (µs) | wall-clock / T2 |
|---|--:|--:|---|---|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|--:|--:|
| Z3 | 3 | 0.400 | dynamic | on | 38 | ok | 0.843 | 0.715 (0.848) | 0.129 (0.152) | 0.157 | 0.401 | +0.001 | 4 | 8 | 26 | 7 | 287.98 | avg | 168 | 1.717 |
| Z3 | 3 | 0.400 | ladder | on | 8 | ok | 0.956 | 0.818 (0.848) | 0.139 (0.152) | 0.043 | 0.391 | -0.009 | 4 | 4 | 19 | 3 | 287.98 | avg | 237 | 1.215 |
| Z5 | 5 | 0.400 | dynamic | on | 118 | ok | 0.306 | 0.263 (0.848) | 0.043 (0.152) | 0.694 | 0.382 | -0.018 | 4 | 16 | 28 | 13 | 287.98 | avg | 189 | 1.527 |
| Z5 | 5 | 0.400 | ladder | on | 16 | ok | 0.927 | 0.801 (0.848) | 0.126 (0.152) | 0.073 | 0.377 | -0.023 | 8 | 8 | 34 | 5 | 287.98 | avg | 316 | 0.911 |
| Z8 | 8 | 0.400 | dynamic | on | 284 | ok | 0.272 | 0.228 (0.848) | 0.044 (0.152) | 0.728 | 0.416 | +0.016 | 4 | 28 | 32 | 22 | 287.98 | avg | 170 | 1.691 |
| Z8 | 8 | 0.400 | ladder | on | 28 | ok | 0.873 | 0.755 (0.848) | 0.118 (0.152) | 0.127 | 0.377 | -0.023 | 14 | 14 | 54 | 8 | 287.98 | avg | 215 | 1.337 |
| Z12 | 12 | 0.400 | dynamic | on | 616 | skipped | 0.075 | 0.062 (0.848) | 0.013 (0.152) | 0.925 | 0.434 | +0.034 | 4 | 44 | 35 | 34 | 287.98 | avg | 167 | 1.725 |
| Z12 | 12 | 0.400 | ladder | on | 44 | ok | 0.772 | 0.673 (0.848) | 0.100 (0.152) | 0.227 | 0.367 | -0.033 | 22 | 22 | 82 | 12 | 287.98 | avg | 291 | 0.990 |
| XYZXYZXY | 8 | 0.400 | dynamic | on | 284 | ok | 0.315 | 0.266 (0.848) | 0.050 (0.152) | 0.684 | 0.407 | +0.007 | 4 | 28 | 34 | 22 | 287.98 | avg | 170 | 1.691 |
| XYZXYZXY | 8 | 0.400 | ladder | on | 26 | ok | 0.872 | 0.753 (0.848) | 0.119 (0.152) | 0.127 | 0.379 | -0.021 | 14 | 14 | 52 | 8 | 287.98 | avg | 329 | 0.875 |
| XZIY_gapped | 3 | 0.400 | dynamic | on | 108 | ok | 0.484 | 0.396 (0.848) | 0.089 (0.152) | 0.515 | 0.443 | +0.043 | 4 | 16 | 27 | 12 | 287.98 | avg | 217 | 1.327 |
| XZIY_gapped | 3 | 0.400 | ladder | on | 8 | ok | 0.956 | 0.828 (0.848) | 0.129 (0.152) | 0.043 | 0.376 | -0.024 | 4 | 4 | 18 | 4 | 287.98 | avg | 245 | 1.177 |
| XYIZIX_gapped | 4 | 0.400 | dynamic | on | 218 | ok | 0.498 | 0.424 (0.848) | 0.074 (0.152) | 0.502 | 0.395 | -0.005 | 4 | 32 | 27 | 22 | 287.98 | avg | 207 | 1.394 |
| XYIZIX_gapped | 4 | 0.400 | ladder | on | 10 | ok | 0.939 | 0.793 (0.848) | 0.145 (0.152) | 0.061 | 0.405 | +0.005 | 6 | 6 | 26 | 6 | 287.98 | avg | 165 | 1.748 |
| ZIIXIYIZ_gapped | 4 | 0.400 | dynamic | on | 284 | skipped | 0.480 | 0.407 (0.848) | 0.073 (0.152) | 0.520 | 0.401 | +0.001 | 4 | 36 | 26 | 26 | 287.98 | avg | 170 | 1.691 |
| ZIIXIYIZ_gapped | 4 | 0.400 | ladder | on | 12 | ok | 0.951 | 0.808 (0.848) | 0.142 (0.152) | 0.049 | 0.398 | -0.002 | 6 | 6 | 25 | 8 | 287.98 | avg | 173 | 1.661 |
