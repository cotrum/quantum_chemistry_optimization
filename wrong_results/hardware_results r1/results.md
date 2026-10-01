# Hardware comparison on ibm_rensselaer (job datkmq3ojkfs738qte0g)

θ = 0.4, 4000 shots. Ideal: P(0..0) = 0.848, P(1_S) = 0.152, leakage 0.

| case | w | circuit | Hellinger fidelity | P(0..0) | P(1_S) | leakage | 2q depth | 2q gates | depth | measurements |
|---|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|
| Z3 | 3 | dynamic | 0.619 | 0.527 | 0.092 | 0.380 | 4 | 8 | 26 | 7 |
| Z3 | 3 | ladder | 0.974 | 0.824 | 0.149 | 0.026 | 4 | 4 | 19 | 3 |
| Z5 | 5 | dynamic | 0.392 | 0.332 | 0.060 | 0.607 | 4 | 16 | 28 | 13 |
| Z5 | 5 | ladder | 0.945 | 0.821 | 0.125 | 0.054 | 8 | 8 | 34 | 5 |
| Z8 | 8 | dynamic | 0.321 | 0.281 | 0.041 | 0.679 | 4 | 28 | 32 | 22 |
| Z8 | 8 | ladder | 0.861 | 0.742 | 0.119 | 0.139 | 14 | 14 | 54 | 8 |
| Z12 | 12 | dynamic | 0.202 | 0.171 | 0.032 | 0.797 | 4 | 44 | 35 | 34 |
| Z12 | 12 | ladder | 0.772 | 0.684 | 0.090 | 0.226 | 22 | 22 | 82 | 12 |
| XYZXYZXY | 8 | dynamic | 0.316 | 0.283 | 0.034 | 0.683 | 4 | 28 | 34 | 22 |
| XYZXYZXY | 8 | ladder | 0.861 | 0.737 | 0.124 | 0.139 | 14 | 14 | 54 | 8 |
| ZIIXIYIZ_gapped | 4 | dynamic | 0.280 | 0.243 | 0.037 | 0.720 | 4 | 36 | 26 | 26 |
| ZIIXIYIZ_gapped | 4 | ladder | 0.948 | 0.818 | 0.131 | 0.052 | 6 | 6 | 26 | 8 |
