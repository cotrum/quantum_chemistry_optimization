# Aer: dynamic circuit vs CNOT ladder (191s)

63 checks, 1024 shots each; 0 failed.

Variants: ft = paper Fig. 1 with the |θ> ancilla (pauli_exp_dynamic.py); nisq = θ rotation as a single-qubit gate (pauli_exp_nisq.py); nisq_compact = nisq with XX layer 1 as a gate and layers 3+4 as one measurement (pauli_exp_nisq_compact.py). Sign correction fired = on that shot, for at least one exponential, P⊗Z_θ = -1 (ft) or the ZZ parity m = 1 (nisq, nisq_compact). CONTROL rows use the same circuit without the sign correction: they pass only if the corrected branch fails with exactly the fidelity predicted for the wrong sign, exp(+iθP), and every other shot is exact.

| case | variant | check | status | qubits | shots | shots with sign correction | min F (correction fired) | min F (no correction) | distinct outcomes | note |
|---|---|---|---|--:|--:|--:|--:|--:|--:|---|
| Z | nisq_compact | corrections=end | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
| Z | nisq_compact | corrections=each | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
| X | nisq_compact | corrections=end | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
| X | nisq_compact | corrections=each | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
| Y | nisq_compact | corrections=end | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
| Y | nisq_compact | corrections=each | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
| ZZ | nisq_compact | corrections=end | ok | 10 | 1024 | 509 | 1.000000000000000 | 1.000000000000000 | 4 |  |
| ZZ | nisq_compact | corrections=each | ok | 10 | 1024 | 509 | 1.000000000000000 | 1.000000000000000 | 4 |  |
| ZZ | nisq_compact | CONTROL: no sign correction | ok | 10 | 1024 | 509 | 0.003263568932211 | 1.000000000000000 | 4 | expected F on corrected branch = 0.003263568932 |
| XY | nisq_compact | corrections=end | ok | 10 | 1024 | 527 | 1.000000000000000 | 0.999999999999999 | 4 |  |
| XY | nisq_compact | corrections=each | ok | 10 | 1024 | 527 | 0.999999999999999 | 0.999999999999999 | 4 |  |
| XY | nisq_compact | CONTROL: no sign correction | ok | 10 | 1024 | 527 | 0.281597185770082 | 0.999999999999999 | 4 | expected F on corrected branch = 0.281597185770 |
| ZZZ | nisq_compact | corrections=end | ok | 14 | 1024 | 503 | 1.000000000000000 | 1.000000000000000 | 16 |  |
| ZZZ | nisq_compact | corrections=each | ok | 14 | 1024 | 503 | 1.000000000000000 | 1.000000000000000 | 16 |  |
| ZZZ | nisq_compact | CONTROL: no sign correction | ok | 14 | 1024 | 503 | 0.768734602819835 | 1.000000000000000 | 16 | expected F on corrected branch = 0.768734602820 |
| XYZ | nisq_compact | corrections=end | ok | 14 | 1024 | 522 | 1.000000000000000 | 1.000000000000000 | 16 |  |
| XYZ | nisq_compact | corrections=each | ok | 14 | 1024 | 522 | 1.000000000000000 | 1.000000000000000 | 16 |  |
| XYZ | nisq_compact | CONTROL: no sign correction | ok | 14 | 1024 | 522 | 0.146768793500692 | 1.000000000000000 | 16 | expected F on corrected branch = 0.146768793501 |
| YIX | nisq_compact | corrections=end | ok | 14 | 1024 | 511 | 1.000000000000000 | 1.000000000000000 | 64 |  |
| YIX | nisq_compact | corrections=each | ok | 14 | 1024 | 511 | 1.000000000000000 | 0.999999999999999 | 64 |  |
| YIX | nisq_compact | CONTROL: no sign correction | ok | 14 | 1024 | 511 | 0.392613206276835 | 1.000000000000000 | 64 | expected F on corrected branch = 0.392613206277 |
| ZIZ | nisq_compact | corrections=end | ok | 14 | 1024 | 500 | 1.000000000000000 | 1.000000000000000 | 64 |  |
| ZIZ | nisq_compact | corrections=each | ok | 14 | 1024 | 500 | 1.000000000000000 | 1.000000000000000 | 64 |  |
| ZIZ | nisq_compact | CONTROL: no sign correction | ok | 14 | 1024 | 500 | 0.303019477930118 | 1.000000000000000 | 64 | expected F on corrected branch = 0.303019477930 |
| ZZZZ | nisq_compact | corrections=end | ok | 18 | 1024 | 512 | 1.000000000000000 | 1.000000000000000 | 64 |  |
| ZZZZ | nisq_compact | corrections=each | ok | 18 | 1024 | 512 | 1.000000000000000 | 1.000000000000000 | 64 |  |
| ZZZZ | nisq_compact | CONTROL: no sign correction | ok | 18 | 1024 | 512 | 0.688472285576884 | 1.000000000000000 | 64 | expected F on corrected branch = 0.688472285577 |
| XZZX | nisq_compact | corrections=end | ok | 18 | 1024 | 528 | 1.000000000000000 | 1.000000000000000 | 64 |  |
| XZZX | nisq_compact | corrections=each | ok | 18 | 1024 | 528 | 1.000000000000000 | 1.000000000000000 | 64 |  |
| XZZX | nisq_compact | CONTROL: no sign correction | ok | 18 | 1024 | 528 | 0.838631604998899 | 1.000000000000000 | 64 | expected F on corrected branch = 0.838631604999 |
| ZIIZ | nisq_compact | corrections=end | ok | 18 | 1024 | 522 | 1.000000000000000 | 1.000000000000000 | 251 |  |
| ZIIZ | nisq_compact | corrections=each | ok | 18 | 1024 | 522 | 1.000000000000000 | 1.000000000000000 | 251 |  |
| ZIIZ | nisq_compact | CONTROL: no sign correction | ok | 18 | 1024 | 522 | 0.325914061575904 | 1.000000000000000 | 251 | expected F on corrected branch = 0.325914061576 |
| YXIZ | nisq_compact | corrections=end | ok | 18 | 1024 | 495 | 1.000000000000000 | 1.000000000000000 | 254 |  |
| YXIZ | nisq_compact | corrections=each | ok | 18 | 1024 | 495 | 1.000000000000000 | 1.000000000000000 | 254 |  |
| YXIZ | nisq_compact | CONTROL: no sign correction | ok | 18 | 1024 | 495 | 0.108542327389369 | 1.000000000000000 | 254 | expected F on corrected branch = 0.108542327389 |
| rand0 | nisq_compact | corrections=end | ok | 14 | 1024 | 757 | 0.999999999999999 | 1.000000000000000 | 64 |  |
| rand0 | nisq_compact | corrections=each | ok | 14 | 1024 | 735 | 1.000000000000000 | 0.999999999999999 | 64 |  |
| rand1 | nisq_compact | corrections=end | ok | 14 | 1024 | 506 | 1.000000000000000 | 1.000000000000000 | 4 |  |
| rand1 | nisq_compact | corrections=each | ok | 14 | 1024 | 506 | 1.000000000000000 | 1.000000000000000 | 4 |  |
| rand1 | nisq_compact | CONTROL: no sign correction | ok | 14 | 1024 | 506 | 0.632927604398248 | 1.000000000000000 | 4 | expected F on corrected branch = 0.632927604398 |
| rand2 | nisq_compact | corrections=end | ok | 18 | 1024 | 788 | 0.999999999999999 | 1.000000000000000 | 64 |  |
| rand2 | nisq_compact | corrections=each | ok | 18 | 1024 | 788 | 0.999999999999999 | 0.999999999999999 | 64 |  |
| rand3 | nisq_compact | corrections=end | ok | 18 | 1024 | 892 | 0.999999999999999 | 0.999999999999999 | 1022 |  |
| rand3 | nisq_compact | corrections=each | ok | 18 | 1024 | 881 | 0.999999999999999 | 0.999999999999999 | 1022 |  |
| rand4 | nisq_compact | corrections=end | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
| rand4 | nisq_compact | corrections=each | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
| rand5 | nisq_compact | corrections=end | ok | 14 | 1024 | 745 | 1.000000000000000 | 1.000000000000000 | 64 |  |
| rand5 | nisq_compact | corrections=each | ok | 14 | 1024 | 761 | 1.000000000000000 | 1.000000000000000 | 64 |  |
| rand6 | nisq_compact | corrections=end | ok | 14 | 1024 | 517 | 1.000000000000000 | 1.000000000000000 | 16 |  |
| rand6 | nisq_compact | corrections=each | ok | 14 | 1024 | 517 | 1.000000000000000 | 1.000000000000000 | 16 |  |
| rand6 | nisq_compact | CONTROL: no sign correction | ok | 14 | 1024 | 517 | 0.996194051786638 | 1.000000000000000 | 16 | expected F on corrected branch = 0.996194051787 |
| rand7 | nisq_compact | corrections=end | ok | 18 | 1024 | 747 | 1.000000000000000 | 1.000000000000000 | 900 |  |
| rand7 | nisq_compact | corrections=each | ok | 18 | 1024 | 801 | 1.000000000000000 | 0.999999999999999 | 900 |  |
| rand8 | nisq_compact | corrections=end | ok | 18 | 1024 | 509 | 1.000000000000000 | 0.999999999999999 | 16 |  |
| rand8 | nisq_compact | corrections=each | ok | 18 | 1024 | 509 | 0.999999999999999 | 0.999999999999999 | 16 |  |
| rand8 | nisq_compact | CONTROL: no sign correction | ok | 18 | 1024 | 509 | 0.152047059121166 | 0.999999999999999 | 16 | expected F on corrected branch = 0.152047059121 |
| rand9 | nisq_compact | corrections=end | ok | 10 | 1024 | 783 | 1.000000000000000 | 1.000000000000000 | 16 |  |
| rand9 | nisq_compact | corrections=each | ok | 10 | 1024 | 783 | 1.000000000000000 | 1.000000000000000 | 16 |  |
| rand10 | nisq_compact | corrections=end | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
| rand10 | nisq_compact | corrections=each | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
| rand11 | nisq_compact | corrections=end | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
| rand11 | nisq_compact | corrections=each | ok | 6 | 1 | 0 | nan | 1.000000000000000 | 1 |  |
