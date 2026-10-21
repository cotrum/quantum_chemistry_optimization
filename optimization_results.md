**Optimization pilot — 2026-10-21**

Backend: `ibm_rensselaer`. Independent placement per construction; compact and terminal share placement. No readout mitigation. Hardware results are a small pilot, not process fidelity.

**Recommendation:** Prioritize the local single-ancilla gadget: Z4 uses 4 instead of 12 entanglers, with population fidelity 0.939 versus compact 0.545 (ladder: 0.936). The hybrid reduces Z6 entanglers 20→14 and phase error 0.413→0.211, but the ladder remains better. Keep terminal software corrections experimental: the Z4 regression repeated; learned XX DD recovered performance only to approximately the original compact level. ZNE shows a tentative phase-error reduction with larger uncertainty; the synthesis search does not beat the routed ladder. Placement differences contribute to cross-construction comparisons.

Implemented: terminal Pauli frames, single-ancilla parity rotations, and pairwise parity compression. Paper adaptations: complete-gadget folding/XX DD (Shirgure–Niu), a 48-iteration legal-order UCT/Rustiq search (MonteQ), and bounded empirical data-subregister DD selection (Tong). These are limited adaptations, not full paper reproductions.

Checks: 896 coherent branches and 1792 exact readout-probability branches passed (maximum state infidelity 8.9e-16). Every submitted circuit also passed an ideal Aer sampling check.

| Case | Method | Native 2q / depth | Ancilla measurements | Population fidelity | Phase error |
|---|---|---:|---:|---:|---:|
| XYZ | compact | 8 / 4 | 4 | 0.869 | 0.200 ± 0.027 |
| XYZ | ladder | 4 / 4 | 0 | 0.973 | 0.063 ± 0.024 |
| XYZ | star | 3 / 3 | 1 | 0.959 | 0.032 ± 0.023 |
| XYZ | terminal | 8 / 4 | 4 | 0.898 | 0.206 ± 0.027 |
| ZZZ | compact | 8 / 4 | 4 | 0.873 | 0.239 ± 0.027 |
| ZZZ | ladder | 4 / 4 | 0 | 0.978 | 0.007 ± 0.022 |
| ZZZ | star | 3 / 3 | 1 | 0.975 | 0.069 ± 0.024 |
| ZZZ | terminal | 8 / 4 | 4 | 0.895 | 0.178 ± 0.026 |
| ZZZZ | compact | 12 / 4 | 6 | 0.545 | 0.540 ± 0.031 |
| ZZZZ | hybrid | 8 / 6 | 2 | 0.882 | 0.139 ± 0.025 |
| ZZZZ | ladder | 6 / 6 | 0 | 0.936 | 0.061 ± 0.024 |
| ZZZZ | star | 4 / 4 | 1 | 0.939 | 0.028 ± 0.023 |
| ZZZZ | terminal | 12 / 4 | 6 | 0.268 | 0.733 ± 0.031 |
| ZZZZZZ | compact | 20 / 4 | 10 | 0.689 | 0.413 ± 0.030 |
| ZZZZZZ | hybrid | 14 / 6 | 4 | 0.695 | 0.211 ± 0.027 |
| ZZZZZZ | ladder | 10 / 10 | 0 | 0.890 | 0.102 ± 0.025 |
| ZZZZZZ | terminal | 20 / 4 | 10 | 0.743 | 0.315 ± 0.029 |

Phase error is the absolute error in the Y/X parity expectation; ± is one sampling standard error, not calibration uncertainty.

**Paper experiments**

Shirgure/Niu: full-gadget folds 1/3/5 on Z3. XX is client-scheduled data-qubit DD; the paper's stretch scheduling and spin-model benchmarks are not reproduced.

| DD | Raw phase error | Linear ZNE error | Quadratic ZNE error |
|---|---:|---:|---:|
| off | 0.110 ± 0.025 | 0.082 ± 0.039 | 0.118 ± 0.058 |
| xx | 0.100 ± 0.025 | 0.050 ± 0.039 | 0.022 ± 0.058 |

ZNE uses 2×/3× the raw shot budget, increases variance, and assumes useful noise scaling; estimates are not clipped.

MonteQ adaptation: 48 UCT iterations, 42 legal orders. Logical entanglers: Rustiq 32 → search 30; the final Clifford is retained and the full unitary checked. Rustiq replaces the paper's custom transition heuristic.

| Eight-term circuit | Routed 2q | Population fidelity | Phase error |
|---|---:|---:|---:|
| ladder | 27 | 0.909 | 0.046 ± 0.031 |
| rustiq | 42 | 0.901 | 0.030 ± 0.031 |
| mcts | 38 | 0.866 | 0.105 ± 0.031 |

This search did not beat the routed ladder on the selected workload.

Tong adaptation: selected `xx` from five DD settings using training phase error. This is a small subregister/timing search, not the full interval-specific genetic algorithm. Fresh validation shots use the same physical patch and both angle signs.

| θ | Method / DD | Population fidelity | Phase error |
|---|---|---:|---:|
| -0.4 | compact / off | 0.614 | 0.549 ± 0.022 |
| -0.4 | terminal / off | 0.033 | 0.893 ± 0.022 |
| -0.4 | terminal / xx | 0.569 | 0.554 ± 0.022 |
| +0.4 | compact / off | 0.605 | 0.572 ± 0.022 |
| +0.4 | terminal / off | 0.032 | 0.886 ± 0.022 |
| +0.4 | terminal / xx | 0.589 | 0.581 ± 0.022 |

Existing compact regression suite: 51 checks passed, including noncommuting term sequences and wrong-sign negative controls.

Joint counts, layouts, ideal values, timing, checks, and job IDs: `optimization_results.json`.

- pilot: `dbchgjvi0auc73duvom0` — complete; 51 circuits × 1024 shots.
- validation: `dbchi5vi0auc73duvrv0` — complete; 12 circuits × 2048 shots.
- Reported QPU use: 25 seconds.

Sources: [Shirgure/Niu](https://arxiv.org/abs/2605.05256), [MonteQ](https://arxiv.org/abs/2604.19029), [Tong et al.](https://arxiv.org/abs/2604.18734).

Reproduce: `python optimization_experiment.py --check`; `--submit` submits a new pilot; `--collect` retrieves existing jobs; `--validate-dd` submits the independent DD validation once. Use the `qiskit2_5` environment.
