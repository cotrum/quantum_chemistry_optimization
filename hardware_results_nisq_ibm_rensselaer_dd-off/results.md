# Dynamic vs CNOT ladder on ibm_rensselaer (job dato16jojkfs738r20r0), 4000 shots per circuit

Dynamic circuits: {'variant': 'nisq', 'construction': 'paper Fig. 1, θ rotation as a single-qubit gate (NISQ): XX / ZZ / Rz(±2θ) on q_last + XX / Z, no |θ> ancilla', 'corrections': 'end', 'pauli_exp_nisq_md5': '862580ff757319de22b342366ab6c877', 'pauli_exp_dynamic_md5': '551635cc1b0dd654f0f9e0194e72e475'}

Ideal: P(0..0) = cos²θ, P(1_S) = sin²θ, leakage 0. θ_est = arcsin√(P(1_S)/(P(0..0)+P(1_S))).

DD = client-side dynamical decoupling (X-X, qiskit-ibm-runtime dynamic-circuit passes); gate metrics are for the circuit before DD padding.

Aer = noise-free Qiskit Aer check of the submitted circuit before submission (ok / skipped if more than 20 active qubits).

Wall-clock / shot = time per shot from the job's execution spans (circuit, readout, reset and the delay before the next shot). how: own = the circuit had execution spans to itself (exact); lsq = least-squares split of spans shared with other circuits; avg = spans always shared with the same circuits, so only their average is known. T2 = median T2 of the qubits the circuit uses. Job average: 284.6 µs per shot; QPU usage 19 s.

Wall-clock times extracted afterwards from the execution spans of job dato16jojkfs738r20r0 (patch_timing.py); T1/T2: calibration at 2026-09-29 05:10 (time of the job).

| case | w | θ | circuit | DD | DD pulses | Aer | Hellinger | P(0..0) (ideal) | P(1_S) (ideal) | leakage | θ_est | θ_est − θ | 2q depth | 2q gates | depth | measurements | wall-clock / shot (µs) | how | T2 (µs) | wall-clock / T2 |
|---|--:|--:|---|---|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|--:|--:|
| Z3 | 3 | 0.400 | dynamic | off | 0 | ok | 0.328 | 0.276 (0.848) | 0.052 (0.152) | 0.672 | 0.410 | +0.010 | 6 | 12 | 37 | 11 | 284.57 | avg | 168 | 1.697 |
| Z3 | 3 | 0.400 | ladder | off | 0 | ok | 0.960 | 0.818 (0.848) | 0.143 (0.152) | 0.040 | 0.396 | -0.004 | 4 | 4 | 19 | 3 | 284.57 | avg | 237 | 1.201 |
| Z5 | 5 | 0.400 | dynamic | off | 0 | ok | 0.261 | 0.239 (0.848) | 0.025 (0.152) | 0.737 | 0.310 | -0.090 | 6 | 24 | 41 | 21 | 284.57 | avg | 189 | 1.509 |
| Z5 | 5 | 0.400 | ladder | off | 0 | ok | 0.942 | 0.818 (0.848) | 0.125 (0.152) | 0.057 | 0.372 | -0.028 | 8 | 8 | 34 | 5 | 284.57 | avg | 316 | 0.900 |
| Z8 | 8 | 0.400 | dynamic | off | 0 | ok | 0.293 | 0.249 (0.848) | 0.043 (0.152) | 0.707 | 0.396 | -0.004 | 6 | 42 | 42 | 36 | 284.57 | avg | 170 | 1.671 |
| Z8 | 8 | 0.400 | ladder | off | 0 | ok | 0.864 | 0.756 (0.848) | 0.109 (0.152) | 0.135 | 0.363 | -0.037 | 14 | 14 | 54 | 8 | 284.57 | avg | 215 | 1.321 |
| Z12 | 12 | 0.400 | dynamic | off | 0 | skipped | 0.088 | 0.077 (0.848) | 0.011 (0.152) | 0.912 | 0.358 | -0.042 | 6 | 66 | 47 | 56 | 284.57 | avg | 167 | 1.704 |
| Z12 | 12 | 0.400 | ladder | off | 0 | ok | 0.783 | 0.684 (0.848) | 0.099 (0.152) | 0.216 | 0.364 | -0.036 | 22 | 22 | 82 | 12 | 284.57 | avg | 291 | 0.978 |
| XYZXYZXY | 8 | 0.400 | dynamic | off | 0 | ok | 0.332 | 0.289 (0.848) | 0.043 (0.152) | 0.668 | 0.366 | -0.034 | 6 | 42 | 42 | 36 | 284.57 | avg | 170 | 1.671 |
| XYZXYZXY | 8 | 0.400 | ladder | off | 0 | ok | 0.854 | 0.740 (0.848) | 0.115 (0.152) | 0.146 | 0.375 | -0.025 | 14 | 14 | 52 | 8 | 284.57 | avg | 329 | 0.865 |
| XZIY_gapped | 3 | 0.400 | dynamic | off | 0 | ok | 0.522 | 0.449 (0.848) | 0.074 (0.152) | 0.477 | 0.386 | -0.014 | 6 | 24 | 40 | 20 | 284.57 | avg | 217 | 1.312 |
| XZIY_gapped | 3 | 0.400 | ladder | off | 0 | ok | 0.952 | 0.800 (0.848) | 0.152 (0.152) | 0.048 | 0.411 | +0.011 | 4 | 4 | 18 | 4 | 284.57 | avg | 245 | 1.163 |
| XYIZIX_gapped | 4 | 0.400 | dynamic | off | 0 | ok | 0.353 | 0.309 (0.848) | 0.045 (0.152) | 0.646 | 0.365 | -0.035 | 6 | 48 | 40 | 38 | 284.57 | avg | 207 | 1.378 |
| XYIZIX_gapped | 4 | 0.400 | ladder | off | 0 | ok | 0.951 | 0.816 (0.848) | 0.135 (0.152) | 0.049 | 0.387 | -0.013 | 6 | 6 | 26 | 6 | 284.57 | avg | 165 | 1.727 |
| ZIIXIYIZ_gapped | 4 | 0.400 | dynamic | off | 0 | skipped | 0.304 | 0.251 (0.848) | 0.053 (0.152) | 0.696 | 0.433 | +0.033 | 6 | 54 | 37 | 44 | 284.57 | avg | 170 | 1.671 |
| ZIIXIYIZ_gapped | 4 | 0.400 | ladder | off | 0 | ok | 0.953 | 0.810 (0.848) | 0.142 (0.152) | 0.047 | 0.397 | -0.003 | 6 | 6 | 25 | 8 | 284.57 | avg | 173 | 1.641 |
