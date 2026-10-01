# Dynamic vs CNOT ladder on ibm_phoenix (job datvctlvr3kc73em43eg), 4000 shots per circuit

Dynamic circuits: {'variant': 'nisq', 'construction': 'paper Fig. 1, θ rotation as a single-qubit gate (NISQ): XX / ZZ / Rz(±2θ) on q_last + XX / Z, no |θ> ancilla', 'corrections': 'end', 'pauli_exp_nisq_md5': '862580ff757319de22b342366ab6c877', 'pauli_exp_dynamic_md5': '551635cc1b0dd654f0f9e0194e72e475'}

Ideal: P(0..0) = cos²θ, P(1_S) = sin²θ, leakage 0. θ_est = arcsin√(P(1_S)/(P(0..0)+P(1_S))).

DD = client-side dynamical decoupling (X-X, qiskit-ibm-runtime dynamic-circuit passes); gate metrics are for the circuit before DD padding.

Aer = noise-free Qiskit Aer check of the submitted circuit before submission (ok / skipped if more than 20 active qubits).

Wall-clock / shot = time per shot from the job's execution spans (circuit, readout, reset and the delay before the next shot). how: own = the circuit had execution spans to itself (exact); lsq = least-squares split of spans shared with other circuits; avg = spans always shared with the same circuits, so only their average is known. T2 = median T2 of the qubits the circuit uses. Job average: 46.4 µs per shot; QPU usage 4 s.

Wall-clock times extracted afterwards from the execution spans of job datvctlvr3kc73em43eg (patch_timing.py); T1/T2: calibration at 2026-09-29 13:33 (time of the job).

| case | w | θ | circuit | DD | DD pulses | Aer | Hellinger | P(0..0) (ideal) | P(1_S) (ideal) | leakage | θ_est | θ_est − θ | 2q depth | 2q gates | depth | measurements | wall-clock / shot (µs) | how | T2 (µs) | wall-clock / T2 |
|---|--:|--:|---|---|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|--:|--:|
| Z3 | 3 | 0.400 | dynamic | off | 0 | ok | 0.836 | 0.710 (0.848) | 0.126 (0.152) | 0.164 | 0.399 | -0.001 | 6 | 12 | 39 | 11 | 46.44 | avg | 172 | 0.270 |
| Z3 | 3 | 0.400 | ladder | off | 0 | ok | 0.672 | 0.606 (0.848) | 0.070 (0.152) | 0.324 | 0.328 | -0.072 | 4 | 4 | 20 | 3 | 46.44 | avg | 160 | 0.291 |
| Z5 | 5 | 0.400 | dynamic | off | 0 | ok | 0.575 | 0.482 (0.848) | 0.092 (0.152) | 0.425 | 0.413 | +0.013 | 6 | 24 | 41 | 21 | 46.44 | avg | 172 | 0.270 |
| Z5 | 5 | 0.400 | ladder | off | 0 | ok | 0.535 | 0.472 (0.848) | 0.064 (0.152) | 0.464 | 0.353 | -0.047 | 8 | 8 | 34 | 5 | 46.44 | avg | 160 | 0.289 |
| Z8 | 8 | 0.400 | dynamic | off | 0 | ok | 0.109 | 0.096 (0.848) | 0.013 (0.152) | 0.891 | 0.353 | -0.047 | 6 | 42 | 44 | 36 | 46.44 | avg | 149 | 0.312 |
| Z8 | 8 | 0.400 | ladder | off | 0 | ok | 0.471 | 0.418 (0.848) | 0.054 (0.152) | 0.528 | 0.346 | -0.054 | 14 | 14 | 54 | 8 | 46.44 | avg | 160 | 0.290 |
| Z12 | 12 | 0.400 | dynamic | off | 0 | skipped | 0.035 | 0.032 (0.848) | 0.004 (0.152) | 0.965 | 0.319 | -0.081 | 6 | 66 | 47 | 56 | 46.44 | avg | 166 | 0.279 |
| Z12 | 12 | 0.400 | ladder | off | 0 | ok | 0.441 | 0.398 (0.848) | 0.046 (0.152) | 0.556 | 0.327 | -0.073 | 22 | 22 | 82 | 12 | 46.44 | avg | 177 | 0.263 |
| XYZXYZXY | 8 | 0.400 | dynamic | off | 0 | ok | 0.121 | 0.108 (0.848) | 0.013 (0.152) | 0.879 | 0.340 | -0.060 | 6 | 42 | 42 | 36 | 46.44 | avg | 149 | 0.312 |
| XYZXYZXY | 8 | 0.400 | ladder | off | 0 | ok | 0.543 | 0.496 (0.848) | 0.051 (0.152) | 0.453 | 0.310 | -0.090 | 14 | 14 | 52 | 8 | 46.44 | avg | 160 | 0.290 |
| XZIY_gapped | 3 | 0.400 | dynamic | off | 0 | ok | 0.658 | 0.563 (0.848) | 0.095 (0.152) | 0.342 | 0.389 | -0.011 | 6 | 24 | 37 | 20 | 46.44 | avg | 192 | 0.242 |
| XZIY_gapped | 3 | 0.400 | ladder | off | 0 | ok | 0.675 | 0.562 (0.848) | 0.114 (0.152) | 0.325 | 0.422 | +0.022 | 4 | 4 | 18 | 4 | 46.44 | avg | 199 | 0.233 |
| XYIZIX_gapped | 4 | 0.400 | dynamic | off | 0 | ok | 0.459 | 0.391 (0.848) | 0.068 (0.152) | 0.541 | 0.394 | -0.006 | 6 | 48 | 38 | 38 | 46.44 | avg | 160 | 0.291 |
| XYIZIX_gapped | 4 | 0.400 | ladder | off | 0 | ok | 0.969 | 0.821 (0.848) | 0.148 (0.152) | 0.031 | 0.402 | +0.002 | 6 | 6 | 26 | 6 | 46.44 | avg | 198 | 0.235 |
| ZIIXIYIZ_gapped | 4 | 0.400 | dynamic | off | 0 | skipped | 0.259 | 0.245 (0.848) | 0.018 (0.152) | 0.736 | 0.268 | -0.132 | 6 | 54 | 37 | 44 | 46.44 | avg | 151 | 0.309 |
| ZIIXIYIZ_gapped | 4 | 0.400 | ladder | off | 0 | ok | 0.526 | 0.459 (0.848) | 0.068 (0.152) | 0.473 | 0.368 | -0.032 | 6 | 6 | 26 | 8 | 46.44 | avg | 199 | 0.233 |
