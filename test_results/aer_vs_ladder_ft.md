# Aer: dynamic circuit vs CNOT ladder (316s)

68 checks, 1024 shots each; 0 failed.

Variants: ft = paper Fig. 1 with the |θ> ancilla (pauli_exp_dynamic.py); nisq = θ rotation as a single-qubit gate (pauli_exp_nisq.py); nisq_compact = nisq with XX layer 1 as a gate and layers 3+4 as one measurement (pauli_exp_nisq_compact.py). Sign correction fired = on that shot, for at least one exponential, P⊗Z_θ = -1 (ft) or the ZZ parity m = 1 (nisq, nisq_compact). CONTROL rows use the same circuit without the sign correction: they pass only if the corrected branch fails with exactly the fidelity predicted for the wrong sign, exp(+iθP), and every other shot is exact.

| case | variant | check | status | qubits | shots | shots with sign correction | min F (correction fired) | min F (no correction) | distinct outcomes | note |
|---|---|---|---|--:|--:|--:|--:|--:|--:|---|
| Z | ft | corrections=end | ok | 6 | 1024 | 494 | 1.000000000000000 | 1.000000000000000 | 4 |  |
| Z | ft | corrections=each | ok | 6 | 1024 | 494 | 1.000000000000000 | 1.000000000000000 | 4 |  |
| Z | ft | CONTROL: no sign correction | ok | 6 | 1024 | 494 | 0.396823303905656 | 1.000000000000000 | 4 | expected F on corrected branch = 0.396823303906 |
| X | ft | corrections=end | ok | 6 | 1024 | 540 | 1.000000000000000 | 1.000000000000000 | 4 |  |
| X | ft | corrections=each | ok | 6 | 1024 | 540 | 1.000000000000000 | 1.000000000000000 | 4 |  |
| X | ft | CONTROL: no sign correction | ok | 6 | 1024 | 540 | 0.408362806429777 | 1.000000000000000 | 4 | expected F on corrected branch = 0.408362806430 |
| Y | ft | corrections=end | ok | 6 | 1024 | 522 | 1.000000000000000 | 1.000000000000000 | 4 |  |
| Y | ft | corrections=each | ok | 6 | 1024 | 522 | 1.000000000000000 | 1.000000000000000 | 4 |  |
| Y | ft | CONTROL: no sign correction | ok | 6 | 1024 | 522 | 0.844660127208226 | 1.000000000000000 | 4 | expected F on corrected branch = 0.844660127208 |
| ZZ | ft | corrections=end | ok | 10 | 1024 | 512 | 1.000000000000000 | 1.000000000000000 | 64 |  |
| ZZ | ft | corrections=each | ok | 10 | 1024 | 512 | 1.000000000000000 | 1.000000000000000 | 64 |  |
| ZZ | ft | CONTROL: no sign correction | ok | 10 | 1024 | 512 | 0.003263568932211 | 1.000000000000000 | 64 | expected F on corrected branch = 0.003263568932 |
| XY | ft | corrections=end | ok | 10 | 1024 | 509 | 0.999999999999999 | 0.999999999999999 | 64 |  |
| XY | ft | corrections=each | ok | 10 | 1024 | 509 | 0.999999999999999 | 0.999999999999999 | 64 |  |
| XY | ft | CONTROL: no sign correction | ok | 10 | 1024 | 509 | 0.281597185770082 | 0.999999999999999 | 64 | expected F on corrected branch = 0.281597185770 |
| ZZZ | ft | corrections=end | ok | 14 | 1024 | 537 | 0.999999999999999 | 1.000000000000000 | 644 |  |
| ZZZ | ft | corrections=each | ok | 14 | 1024 | 537 | 0.999999999999999 | 1.000000000000000 | 644 |  |
| ZZZ | ft | CONTROL: no sign correction | ok | 14 | 1024 | 537 | 0.768734602819835 | 1.000000000000000 | 644 | expected F on corrected branch = 0.768734602820 |
| XYZ | ft | corrections=end | ok | 14 | 1024 | 485 | 0.999999999999999 | 0.999999999999999 | 646 |  |
| XYZ | ft | corrections=each | ok | 14 | 1024 | 485 | 1.000000000000000 | 1.000000000000000 | 646 |  |
| XYZ | ft | CONTROL: no sign correction | ok | 14 | 1024 | 485 | 0.146768793500691 | 1.000000000000000 | 646 | expected F on corrected branch = 0.146768793501 |
| YIX | ft | corrections=end | ok | 14 | 1024 | 540 | 0.999999999999999 | 1.000000000000000 | 983 |  |
| YIX | ft | corrections=each | ok | 14 | 1024 | 540 | 0.999999999999999 | 0.999999999999999 | 983 |  |
| YIX | ft | CONTROL: no sign correction | ok | 14 | 1024 | 540 | 0.392613206276835 | 1.000000000000000 | 983 | expected F on corrected branch = 0.392613206277 |
| ZIZ | ft | corrections=end | ok | 14 | 1024 | 490 | 0.999999999999999 | 1.000000000000000 | 993 |  |
| ZIZ | ft | corrections=each | ok | 14 | 1024 | 490 | 1.000000000000000 | 1.000000000000000 | 993 |  |
| ZIZ | ft | CONTROL: no sign correction | ok | 14 | 1024 | 490 | 0.303019477930118 | 1.000000000000000 | 993 | expected F on corrected branch = 0.303019477930 |
| ZZZZ | ft | corrections=end | ok | 18 | 1024 | 523 | 1.000000000000000 | 1.000000000000000 | 995 |  |
| ZZZZ | ft | corrections=each | ok | 18 | 1024 | 523 | 1.000000000000000 | 1.000000000000000 | 995 |  |
| ZZZZ | ft | CONTROL: no sign correction | ok | 18 | 1024 | 523 | 0.688472285576884 | 1.000000000000000 | 995 | expected F on corrected branch = 0.688472285577 |
| XZZX | ft | corrections=end | ok | 18 | 1024 | 520 | 1.000000000000000 | 1.000000000000000 | 989 |  |
| XZZX | ft | corrections=each | ok | 18 | 1024 | 520 | 1.000000000000000 | 1.000000000000000 | 989 |  |
| XZZX | ft | CONTROL: no sign correction | ok | 18 | 1024 | 520 | 0.838631604998899 | 1.000000000000000 | 989 | expected F on corrected branch = 0.838631604999 |
| ZIIZ | ft | corrections=end | ok | 18 | 1024 | 507 | 1.000000000000000 | 1.000000000000000 | 1019 |  |
| ZIIZ | ft | corrections=each | ok | 18 | 1024 | 507 | 1.000000000000000 | 1.000000000000000 | 1019 |  |
| ZIIZ | ft | CONTROL: no sign correction | ok | 18 | 1024 | 507 | 0.325914061575904 | 1.000000000000000 | 1019 | expected F on corrected branch = 0.325914061576 |
| YXIZ | ft | corrections=end | ok | 18 | 1024 | 497 | 1.000000000000000 | 1.000000000000000 | 1023 |  |
| YXIZ | ft | corrections=each | ok | 18 | 1024 | 497 | 1.000000000000000 | 1.000000000000000 | 1023 |  |
| YXIZ | ft | CONTROL: no sign correction | ok | 18 | 1024 | 497 | 0.108542327389369 | 1.000000000000000 | 1023 | expected F on corrected branch = 0.108542327389 |
| rand0 | ft | corrections=end | ok | 14 | 1024 | 896 | 0.999999999999999 | 0.999999999999999 | 1021 |  |
| rand0 | ft | corrections=each | ok | 14 | 1024 | 887 | 0.999999999999999 | 0.999999999999999 | 1021 |  |
| rand1 | ft | corrections=end | ok | 14 | 1024 | 465 | 1.000000000000000 | 1.000000000000000 | 64 |  |
| rand1 | ft | corrections=each | ok | 14 | 1024 | 465 | 1.000000000000000 | 1.000000000000000 | 64 |  |
| rand1 | ft | CONTROL: no sign correction | ok | 14 | 1024 | 465 | 0.632927604398248 | 1.000000000000000 | 64 | expected F on corrected branch = 0.632927604398 |
| rand2 | ft | corrections=end | ok | 18 | 1024 | 759 | 0.999999999999999 | 0.999999999999999 | 1019 |  |
| rand2 | ft | corrections=each | ok | 18 | 1024 | 780 | 0.999999999999999 | 0.999999999999999 | 1019 |  |
| rand3 | ft | corrections=end | ok | 18 | 1024 | 886 | 0.999999999999999 | 0.999999999999999 | 1024 |  |
| rand3 | ft | corrections=each | ok | 18 | 1024 | 891 | 0.999999999999999 | 0.999999999999999 | 1024 |  |
| rand4 | ft | corrections=end | ok | 6 | 1024 | 517 | 1.000000000000000 | 1.000000000000000 | 4 |  |
| rand4 | ft | corrections=each | ok | 6 | 1024 | 517 | 1.000000000000000 | 1.000000000000000 | 4 |  |
| rand4 | ft | CONTROL: no sign correction | ok | 6 | 1024 | 517 | 0.927246375089300 | 1.000000000000000 | 4 | expected F on corrected branch = 0.927246375089 |
| rand5 | ft | corrections=end | ok | 14 | 1024 | 755 | 1.000000000000000 | 1.000000000000000 | 1017 |  |
| rand5 | ft | corrections=each | ok | 14 | 1024 | 757 | 1.000000000000000 | 1.000000000000000 | 1017 |  |
| rand6 | ft | corrections=end | ok | 14 | 1024 | 544 | 1.000000000000000 | 1.000000000000000 | 650 |  |
| rand6 | ft | corrections=each | ok | 14 | 1024 | 544 | 1.000000000000000 | 1.000000000000000 | 650 |  |
| rand6 | ft | CONTROL: no sign correction | ok | 14 | 1024 | 544 | 0.996194051786638 | 1.000000000000000 | 650 | expected F on corrected branch = 0.996194051787 |
| rand7 | ft | corrections=end | ok | 18 | 1024 | 770 | 0.999999999999999 | 1.000000000000000 | 1024 |  |
| rand7 | ft | corrections=each | ok | 18 | 1024 | 754 | 0.999999999999999 | 0.999999999999999 | 1024 |  |
| rand8 | ft | corrections=end | ok | 18 | 1024 | 514 | 0.999999999999999 | 0.999999999999999 | 661 |  |
| rand8 | ft | corrections=each | ok | 18 | 1024 | 514 | 0.999999999999999 | 0.999999999999999 | 661 |  |
| rand8 | ft | CONTROL: no sign correction | ok | 18 | 1024 | 514 | 0.152047059121166 | 0.999999999999999 | 661 | expected F on corrected branch = 0.152047059121 |
| rand9 | ft | corrections=end | ok | 10 | 1024 | 902 | 1.000000000000000 | 1.000000000000000 | 993 |  |
| rand9 | ft | corrections=each | ok | 10 | 1024 | 890 | 1.000000000000000 | 1.000000000000000 | 993 |  |
| rand10 | ft | corrections=end | ok | 6 | 1024 | 887 | 1.000000000000000 | 1.000000000000000 | 64 |  |
| rand10 | ft | corrections=each | ok | 6 | 1024 | 910 | 1.000000000000000 | 1.000000000000000 | 64 |  |
| rand11 | ft | corrections=end | ok | 6 | 1024 | 504 | 1.000000000000000 | 1.000000000000000 | 4 |  |
| rand11 | ft | corrections=each | ok | 6 | 1024 | 504 | 1.000000000000000 | 1.000000000000000 | 4 |  |
| rand11 | ft | CONTROL: no sign correction | ok | 6 | 1024 | 504 | 0.720649950276750 | 0.999999999999999 | 4 | expected F on corrected branch = 0.720649950277 |
