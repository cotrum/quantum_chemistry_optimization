# Aer: dynamic circuit vs CNOT ladder (292s)

63 checks, 1024 shots each; 0 failed.

Variants: ft = paper Fig. 1 with the |θ> ancilla (pauli_exp_dynamic.py); nisq = θ rotation as a single-qubit gate (pauli_exp_nisq.py); nisq_compact = nisq with XX layer 1 as a gate and layers 3+4 as one measurement (pauli_exp_nisq_compact.py). Sign correction fired = on that shot, for at least one exponential, P⊗Z_θ = -1 (ft) or the ZZ parity m = 1 (nisq, nisq_compact). CONTROL rows use the same circuit without the sign correction: they pass only if the corrected branch fails with exactly the fidelity predicted for the wrong sign, exp(+iθP), and every other shot is exact.

| case | variant | check | status | qubits | shots | shots with sign correction | min F (correction fired) | min F (no correction) | distinct outcomes | note |
|---|---|---|---|--:|--:|--:|--:|--:|--:|---|
| Z | nisq | corrections=end | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
| Z | nisq | corrections=each | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
| X | nisq | corrections=end | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
| X | nisq | corrections=each | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
| Y | nisq | corrections=end | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
| Y | nisq | corrections=each | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
| ZZ | nisq | corrections=end | ok | 10 | 1024 | 497 | 1.000000000000000 | 1.000000000000000 | 16 |  |
| ZZ | nisq | corrections=each | ok | 10 | 1024 | 497 | 1.000000000000000 | 1.000000000000000 | 16 |  |
| ZZ | nisq | CONTROL: no sign correction | ok | 10 | 1024 | 497 | 0.003263568932211 | 1.000000000000000 | 16 | expected F on corrected branch = 0.003263568932 |
| XY | nisq | corrections=end | ok | 10 | 1024 | 507 | 0.999999999999999 | 0.999999999999999 | 16 |  |
| XY | nisq | corrections=each | ok | 10 | 1024 | 507 | 0.999999999999999 | 0.999999999999999 | 16 |  |
| XY | nisq | CONTROL: no sign correction | ok | 10 | 1024 | 507 | 0.281597185770082 | 0.999999999999999 | 16 | expected F on corrected branch = 0.281597185770 |
| ZZZ | nisq | corrections=end | ok | 14 | 1024 | 504 | 1.000000000000000 | 1.000000000000000 | 252 |  |
| ZZZ | nisq | corrections=each | ok | 14 | 1024 | 504 | 1.000000000000000 | 1.000000000000000 | 252 |  |
| ZZZ | nisq | CONTROL: no sign correction | ok | 14 | 1024 | 504 | 0.768734602819835 | 1.000000000000000 | 252 | expected F on corrected branch = 0.768734602820 |
| XYZ | nisq | corrections=end | ok | 14 | 1024 | 510 | 1.000000000000000 | 0.999999999999999 | 250 |  |
| XYZ | nisq | corrections=each | ok | 14 | 1024 | 510 | 1.000000000000000 | 1.000000000000000 | 250 |  |
| XYZ | nisq | CONTROL: no sign correction | ok | 14 | 1024 | 510 | 0.146768793500691 | 1.000000000000000 | 250 | expected F on corrected branch = 0.146768793501 |
| YIX | nisq | corrections=end | ok | 14 | 1024 | 555 | 0.999999999999999 | 1.000000000000000 | 902 |  |
| YIX | nisq | corrections=each | ok | 14 | 1024 | 555 | 0.999999999999999 | 0.999999999999999 | 902 |  |
| YIX | nisq | CONTROL: no sign correction | ok | 14 | 1024 | 555 | 0.392613206276835 | 1.000000000000000 | 902 | expected F on corrected branch = 0.392613206277 |
| ZIZ | nisq | corrections=end | ok | 14 | 1024 | 505 | 1.000000000000000 | 1.000000000000000 | 914 |  |
| ZIZ | nisq | corrections=each | ok | 14 | 1024 | 505 | 1.000000000000000 | 1.000000000000000 | 914 |  |
| ZIZ | nisq | CONTROL: no sign correction | ok | 14 | 1024 | 505 | 0.303019477930118 | 1.000000000000000 | 914 | expected F on corrected branch = 0.303019477930 |
| ZZZZ | nisq | corrections=end | ok | 18 | 1024 | 500 | 1.000000000000000 | 1.000000000000000 | 907 |  |
| ZZZZ | nisq | corrections=each | ok | 18 | 1024 | 500 | 1.000000000000000 | 1.000000000000000 | 907 |  |
| ZZZZ | nisq | CONTROL: no sign correction | ok | 18 | 1024 | 500 | 0.688472285576884 | 1.000000000000000 | 907 | expected F on corrected branch = 0.688472285577 |
| XZZX | nisq | corrections=end | ok | 18 | 1024 | 506 | 1.000000000000000 | 1.000000000000000 | 908 |  |
| XZZX | nisq | corrections=each | ok | 18 | 1024 | 506 | 1.000000000000000 | 1.000000000000000 | 908 |  |
| XZZX | nisq | CONTROL: no sign correction | ok | 18 | 1024 | 506 | 0.838631604998899 | 1.000000000000000 | 908 | expected F on corrected branch = 0.838631604999 |
| ZIIZ | nisq | corrections=end | ok | 18 | 1024 | 496 | 1.000000000000000 | 1.000000000000000 | 1012 |  |
| ZIIZ | nisq | corrections=each | ok | 18 | 1024 | 496 | 1.000000000000000 | 1.000000000000000 | 1012 |  |
| ZIIZ | nisq | CONTROL: no sign correction | ok | 18 | 1024 | 496 | 0.325914061575904 | 1.000000000000000 | 1012 | expected F on corrected branch = 0.325914061576 |
| YXIZ | nisq | corrections=end | ok | 18 | 1024 | 505 | 1.000000000000000 | 1.000000000000000 | 1022 |  |
| YXIZ | nisq | corrections=each | ok | 18 | 1024 | 505 | 1.000000000000000 | 1.000000000000000 | 1022 |  |
| YXIZ | nisq | CONTROL: no sign correction | ok | 18 | 1024 | 505 | 0.108542327389369 | 1.000000000000000 | 1022 | expected F on corrected branch = 0.108542327389 |
| rand0 | nisq | corrections=end | ok | 14 | 1024 | 768 | 0.999999999999999 | 0.999999999999999 | 897 |  |
| rand0 | nisq | corrections=each | ok | 14 | 1024 | 763 | 0.999999999999999 | 0.999999999999999 | 897 |  |
| rand1 | nisq | corrections=end | ok | 14 | 1024 | 530 | 1.000000000000000 | 1.000000000000000 | 16 |  |
| rand1 | nisq | corrections=each | ok | 14 | 1024 | 530 | 1.000000000000000 | 1.000000000000000 | 16 |  |
| rand1 | nisq | CONTROL: no sign correction | ok | 14 | 1024 | 530 | 0.632927604398248 | 1.000000000000000 | 16 | expected F on corrected branch = 0.632927604398 |
| rand2 | nisq | corrections=end | ok | 18 | 1024 | 746 | 0.999999999999999 | 0.999999999999999 | 905 |  |
| rand2 | nisq | corrections=each | ok | 18 | 1024 | 746 | 0.999999999999999 | 0.999999999999999 | 905 |  |
| rand3 | nisq | corrections=end | ok | 18 | 1024 | 887 | 0.999999999999999 | 0.999999999999999 | 1024 |  |
| rand3 | nisq | corrections=each | ok | 18 | 1024 | 920 | 0.999999999999999 | 0.999999999999999 | 1024 |  |
| rand4 | nisq | corrections=end | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
| rand4 | nisq | corrections=each | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
| rand5 | nisq | corrections=end | ok | 14 | 1024 | 782 | 1.000000000000000 | 1.000000000000000 | 911 |  |
| rand5 | nisq | corrections=each | ok | 14 | 1024 | 781 | 1.000000000000000 | 1.000000000000000 | 911 |  |
| rand6 | nisq | corrections=end | ok | 14 | 1024 | 509 | 1.000000000000000 | 1.000000000000000 | 250 |  |
| rand6 | nisq | corrections=each | ok | 14 | 1024 | 509 | 1.000000000000000 | 1.000000000000000 | 250 |  |
| rand6 | nisq | CONTROL: no sign correction | ok | 14 | 1024 | 509 | 0.996194051786638 | 1.000000000000000 | 250 | expected F on corrected branch = 0.996194051787 |
| rand7 | nisq | corrections=end | ok | 18 | 1024 | 765 | 1.000000000000000 | 1.000000000000000 | 1024 |  |
| rand7 | nisq | corrections=each | ok | 18 | 1024 | 753 | 0.999999999999999 | 0.999999999999999 | 1024 |  |
| rand8 | nisq | corrections=end | ok | 18 | 1024 | 520 | 0.999999999999999 | 0.999999999999999 | 247 |  |
| rand8 | nisq | corrections=each | ok | 18 | 1024 | 520 | 0.999999999999999 | 0.999999999999999 | 247 |  |
| rand8 | nisq | CONTROL: no sign correction | ok | 18 | 1024 | 520 | 0.152047059121166 | 0.999999999999999 | 247 | expected F on corrected branch = 0.152047059121 |
| rand9 | nisq | corrections=end | ok | 10 | 1024 | 758 | 1.000000000000000 | 1.000000000000000 | 247 |  |
| rand9 | nisq | corrections=each | ok | 10 | 1024 | 756 | 1.000000000000000 | 1.000000000000000 | 247 |  |
| rand10 | nisq | corrections=end | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
| rand10 | nisq | corrections=each | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
| rand11 | nisq | corrections=end | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
| rand11 | nisq | corrections=each | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
