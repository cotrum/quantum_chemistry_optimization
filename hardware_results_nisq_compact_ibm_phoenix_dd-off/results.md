# Dynamic vs CNOT ladder on ibm_phoenix (job datvcg2hcrkc73duq4h0), 4000 shots per circuit

Dynamic circuits: {'variant': 'nisq_compact', 'construction': 'NISQ compact: XX as gate (H-CX-H) / ZZ measured / Rz(±2θ) on q_last / XX+Z(a) as one measurement', 'corrections': 'end', 'pauli_exp_nisq_compact_md5': '354346d2f62743a2c519c7b657960305', 'pauli_exp_dynamic_md5': '551635cc1b0dd654f0f9e0194e72e475'}

Ideal: P(0..0) = cos²θ, P(1_S) = sin²θ, leakage 0. θ_est = arcsin√(P(1_S)/(P(0..0)+P(1_S))).

DD = client-side dynamical decoupling (X-X, qiskit-ibm-runtime dynamic-circuit passes); gate metrics are for the circuit before DD padding.

Aer = noise-free Qiskit Aer check of the submitted circuit before submission (ok / skipped if more than 20 active qubits).

Wall-clock / shot = time per shot from the job's execution spans (circuit, readout, reset and the delay before the next shot). how: own = the circuit had execution spans to itself (exact); lsq = least-squares split of spans shared with other circuits; avg = spans always shared with the same circuits, so only their average is known. T2 = median T2 of the qubits the circuit uses. Job average: 30.4 µs per shot; QPU usage 4 s.

Wall-clock times extracted afterwards from the execution spans of job datvcg2hcrkc73duq4h0 (patch_timing.py); T1/T2: calibration at 2026-09-29 13:32 (time of the job).

| case | w | θ | circuit | DD | DD pulses | Aer | Hellinger | P(0..0) (ideal) | P(1_S) (ideal) | leakage | θ_est | θ_est − θ | 2q depth | 2q gates | depth | measurements | wall-clock / shot (µs) | how | T2 (µs) | wall-clock / T2 |
|---|--:|--:|---|---|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|--:|--:|
| Z3 | 3 | 0.400 | dynamic | off | 0 | ok | 0.886 | 0.753 (0.848) | 0.133 (0.152) | 0.114 | 0.398 | -0.002 | 4 | 8 | 26 | 7 | 30.43 | avg | 172 | 0.177 |
| Z3 | 3 | 0.400 | ladder | off | 0 | ok | 0.652 | 0.584 (0.848) | 0.070 (0.152) | 0.345 | 0.334 | -0.066 | 4 | 4 | 20 | 3 | 30.43 | avg | 160 | 0.191 |
| Z5 | 5 | 0.400 | dynamic | off | 0 | ok | 0.680 | 0.572 (0.848) | 0.107 (0.152) | 0.320 | 0.409 | +0.009 | 4 | 16 | 28 | 13 | 30.43 | avg | 172 | 0.177 |
| Z5 | 5 | 0.400 | ladder | off | 0 | ok | 0.483 | 0.436 (0.848) | 0.049 (0.152) | 0.514 | 0.324 | -0.076 | 8 | 8 | 34 | 5 | 30.43 | avg | 160 | 0.190 |
| Z8 | 8 | 0.400 | dynamic | off | 0 | ok | 0.180 | 0.169 (0.848) | 0.014 (0.152) | 0.817 | 0.283 | -0.117 | 4 | 28 | 32 | 22 | 30.43 | avg | 149 | 0.205 |
| Z8 | 8 | 0.400 | ladder | off | 0 | ok | 0.478 | 0.434 (0.848) | 0.048 (0.152) | 0.518 | 0.320 | -0.080 | 14 | 14 | 54 | 8 | 30.43 | avg | 160 | 0.190 |
| Z12 | 12 | 0.400 | dynamic | off | 0 | skipped | 0.083 | 0.076 (0.848) | 0.007 (0.152) | 0.916 | 0.304 | -0.096 | 4 | 44 | 38 | 34 | 30.43 | avg | 166 | 0.183 |
| Z12 | 12 | 0.400 | ladder | off | 0 | ok | 0.439 | 0.402 (0.848) | 0.041 (0.152) | 0.557 | 0.307 | -0.093 | 22 | 22 | 82 | 12 | 30.43 | avg | 177 | 0.172 |
| XYZXYZXY | 8 | 0.400 | dynamic | off | 0 | ok | 0.186 | 0.166 (0.848) | 0.021 (0.152) | 0.813 | 0.340 | -0.060 | 4 | 28 | 34 | 22 | 30.43 | avg | 149 | 0.205 |
| XYZXYZXY | 8 | 0.400 | ladder | off | 0 | ok | 0.409 | 0.375 (0.848) | 0.037 (0.152) | 0.587 | 0.306 | -0.094 | 14 | 14 | 52 | 8 | 30.43 | avg | 160 | 0.190 |
| XZIY_gapped | 3 | 0.400 | dynamic | off | 0 | ok | 0.717 | 0.612 (0.848) | 0.105 (0.152) | 0.283 | 0.393 | -0.007 | 4 | 16 | 27 | 12 | 30.43 | avg | 192 | 0.159 |
| XZIY_gapped | 3 | 0.400 | ladder | off | 0 | ok | 0.717 | 0.585 (0.848) | 0.134 (0.152) | 0.281 | 0.447 | +0.047 | 4 | 4 | 18 | 4 | 30.43 | avg | 199 | 0.153 |
| XYIZIX_gapped | 4 | 0.400 | dynamic | off | 0 | ok | 0.574 | 0.487 (0.848) | 0.087 (0.152) | 0.426 | 0.400 | +0.000 | 4 | 32 | 27 | 22 | 30.43 | avg | 160 | 0.191 |
| XYIZIX_gapped | 4 | 0.400 | ladder | off | 0 | ok | 0.971 | 0.823 (0.848) | 0.147 (0.152) | 0.029 | 0.400 | +0.000 | 6 | 6 | 26 | 6 | 30.43 | avg | 198 | 0.154 |
| ZIIXIYIZ_gapped | 4 | 0.400 | dynamic | off | 0 | skipped | 0.277 | 0.246 (0.848) | 0.032 (0.152) | 0.722 | 0.345 | -0.055 | 4 | 36 | 26 | 26 | 30.43 | avg | 151 | 0.202 |
| ZIIXIYIZ_gapped | 4 | 0.400 | ladder | off | 0 | ok | 0.551 | 0.486 (0.848) | 0.066 (0.152) | 0.448 | 0.354 | -0.046 | 6 | 6 | 26 | 8 | 30.43 | avg | 199 | 0.153 |
