# Hardware comparison on ibm_phoenix (job datktd5vr3kc73eln58g)

θ = 0.4, 4000 shots. Ideal: P(0..0) = 0.848, P(1_S) = 0.152, leakage 0.

| case | w | circuit | Hellinger fidelity | P(0..0) | P(1_S) | leakage | 2q depth | 2q gates | depth | measurements |
|---|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|
| Z3 | 3 | dynamic | 0.882 | 0.751 | 0.131 | 0.118 | 4 | 8 | 26 | 7 |
| Z3 | 3 | ladder | 0.985 | 0.838 | 0.147 | 0.015 | 4 | 4 | 20 | 3 |
| Z5 | 5 | dynamic | 0.730 | 0.625 | 0.105 | 0.270 | 4 | 16 | 28 | 13 |
| Z5 | 5 | ladder | 0.979 | 0.835 | 0.144 | 0.021 | 8 | 8 | 34 | 5 |
| Z8 | 8 | dynamic | 0.488 | 0.419 | 0.069 | 0.512 | 4 | 28 | 32 | 22 |
| Z8 | 8 | ladder | 0.918 | 0.788 | 0.130 | 0.082 | 14 | 14 | 54 | 8 |
| Z12 | 12 | dynamic | 0.283 | 0.242 | 0.041 | 0.717 | 4 | 44 | 38 | 34 |
| Z12 | 12 | ladder | 0.824 | 0.710 | 0.115 | 0.175 | 22 | 22 | 83 | 12 |
| XYZXYZXY | 8 | dynamic | 0.469 | 0.407 | 0.062 | 0.531 | 4 | 28 | 34 | 22 |
| XYZXYZXY | 8 | ladder | 0.920 | 0.791 | 0.129 | 0.080 | 14 | 14 | 54 | 8 |
| ZIIXIYIZ_gapped | 4 | dynamic | 0.493 | 0.417 | 0.076 | 0.507 | 4 | 36 | 26 | 26 |
| ZIIXIYIZ_gapped | 4 | ladder | 0.980 | 0.841 | 0.139 | 0.020 | 6 | 6 | 26 | 8 |
