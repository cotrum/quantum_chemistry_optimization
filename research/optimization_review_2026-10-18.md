**Circuit decomposition research for the constant-depth Pauli-exponential experiment**  
Research cutoff: 18 October 2026. Convention throughout: \(U_P(\theta)=e^{-i\theta P}\), so Qiskit uses `Rz(2*theta)` or `RZZ(2*theta)`.

The strongest next experiments are **terminal Pauli-frame processing, a local single-ancilla gadget, and a hybrid of local parity compression with a shorter dynamic chain**. For sequences of exponentials, add **joint Pauli-network synthesis**. These address gate count, measurement errors, and feedback latency together. I did not find a verified newer construction that uniformly beats the existing compact circuit for an isolated arbitrary-angle string while retaining its alternating one-dimensional layout and hardware assumptions.

This review combines inspection of the repository, recent primary papers, current IBM documentation, and independently checked algebra. Paper benchmark improvements are not forecasts for these devices. Proposed resource counts below exclude routing unless explicitly stated. No new hardware performance has been measured.

**What the current experiment establishes**

The reference is Moflic and Paler's *On the constant depth implementation of Pauli exponentials*, published 28 March 2026, with an initial preprint from August 2024. Its constant-depth construction uses auxiliary qubits and pairwise XX/ZZ measurements. On a processor implementing those measurements through entangling gates and readout, physical execution cost must include their decompositions. [Published paper](https://www.nature.com/articles/s41534-026-01226-x), [March 2026 manuscript](https://arxiv.org/html/2408.08265v7).

The code already goes beyond a literal implementation of the paper:

- [pauli_exp_nisq_compact.py](../pauli_exp_nisq_compact.py) replaces the first XX measurement with a gate and combines the final XX interaction and ancilla readout. With \(L\) link ancillas it uses \(4L\) CX gates, two measurement rounds, and \(2L\) individual measurements. For an unpadded string, \(L=w-1\).
- `corrections="end"` already tracks Pauli frames across terms. However, `finalize()` physically flushes them, including helper-qubit cleanup, before the final measurement wrapper.
- [hardware_compare.py](../hardware_compare.py) already builds with `barriers=False`. Removing barriers or introducing frame tracking would therefore not be new optimizations.
- The hardware cases are individual exponentials. The two-term `XZZZX+YZZZY` case occurs in the depth study; it is a useful next hardware workload.
- The ladder is synthesized with `LieTrotter(cx_structure="chain")`, with free placement and the best of five transpiler seeds. Dynamic circuits use a frozen, structurally constrained layout.

The following are actual stored compact-circuit results, not predictions. Hellinger fidelity here compares output probability distributions, not quantum processes.

| Case | Compact 2q gates | Ladder 2q gates | Compact 2q depth | Ladder 2q depth | Phoenix fidelity: compact / ladder, DD off |
|---|---:|---:|---:|---:|---:|
| Z3 | 8 | 4 | 4 | 4 | 0.886 / 0.652 |
| Z5 | 16 | 8 | 4 | 8 | 0.680 / 0.483 |
| Z8 | 28 | 14 | 4 | 14 | 0.180 / 0.478 |
| Z12 | 44 | 22 | 4 | 22 | 0.083 / 0.439 |
| ZIIXIYIZ, weight 4 | 36 | 6 | 4 | 6 | 0.277 / 0.551 |

Sources: [Phoenix hardware results](../hardware_results_nisq_compact_ibm_phoenix_dd-off/results.md), [Rensselaer depth study](../depth_comparison_nisq_compact_ibm_rensselaer/results.md). The last case has nine link ancillas although its Pauli weight is only four. The relevant dynamic resource is **routed chain length**, not just Pauli weight.

The same-job DD comparison also deserves attention. On Rensselaer, compact Z3 improves from 0.650 to 0.853 with DD, while Z8 falls from 0.409 to 0.234 and Z12 from 0.190 to 0.074. Z12 receives 616 added X pulses. Those observations motivate targeted DD experiments; they do not by themselves identify the noise mechanism. [Paired DD results](../hardware_results_nisq_compact_ibm_rensselaer_dd-both/results.csv).

**Recent papers with the most useful consequences**

Dates distinguish preprint revisions from journal publication. Full-text inspection was possible for the central dynamic-circuit and compiler papers. Access limitations for two additional candidates are recorded below.

| Paper and date | Relevant mechanism and evidence | Application to this experiment |
|---|---|---|
| **Tong et al., Learning error suppression strategies for dynamic quantum circuits.** Preprint April 2026; v3 **27 September 2026**. [Paper](https://arxiv.org/abs/2604.18734v3) | Learns DD separately for circuit intervals and qubit groups. Reports a threefold reduction in average dynamic-circuit error measured by randomized benchmarking, and applies the method to QFT with measurement. | A strong companion to decomposition changes: protect the first parity-measurement/feedback interval and the later readout interval separately. The reported reduction is not a Pauli-exponential fidelity prediction. |
| **Luiz, Ferreira and de Oliveira, Hardware-Efficient Hamiltonian Simulation via Trotter-Initialized Variational Optimization with Native Placement.** Preprint April 2026; journal publication **26 September 2026**. [Paper](https://arxiv.org/abs/2604.26663), [publication](https://advanced.onlinelibrary.wiley.com/doi/10.1002/qute.70482) | Combines native placement, adaptive Trotter discretization, and variational refinement. The authors report a 27-CX approximate circuit outperforming a 187-CX exact comparator on Torino. | Relevant when extending to Hamiltonian evolution with an explicit approximation budget. It is not an exact replacement for the present arbitrary-input single-exponential benchmark. |
| **Shirgure and Niu, Error Mitigation in Dynamic Circuits for Hamiltonian Simulation.** **May 2026**, v2 14 May. [Full text](https://arxiv.org/html/2605.05256v2) | Uses dynamic CNOT ladders and an ancilla-mediated two-body rotation gadget on IBM Kingston. Aligns measurements/feedback within each interaction layer and uses stretch-based DD and whole-gadget folding for ZNE. | Particularly relevant to measurement-based rotation variants. The reported gains concern energy-error reduction; they must not be interpreted as process-fidelity gains. DD and ZNE improve execution/estimation rather than algebraic gate count. |
| **Machiya et al., MonteQ: A Monte Carlo Tree Search Based Quantum Circuit Synthesis Framework.** **21 April 2026** preprint. [Full text](https://arxiv.org/html/2604.19029) | Searches Pauli-rotation orderings above a lower-level synthesizer, including a hardware-aware heuristic. Offers a unitary-preserving dependency-graph mode and a relaxed mode. Reports up to 53%, averaging 30%, CNOT reduction against comparators including Rustiq on its synthesis tasks. | High priority for longer sequences, after establishing Rustiq as a baseline. Use the unitary-preserving mode for this experiment; relaxed ordering changes the task for noncommuting terms. |
| **Kuo et al., Unified Pauli-Rotation Synthesis for Relieving CX-Count Overhead in Tableau-Based Quantum Circuit Optimization Flow.** **DATE 2026**. [Conference paper](https://past.date-conference.com/proceedings-archive/2026/DATA/1110.pdf) | Unifies Clifford and rotation tableaux and uses a Pauli minimum-spanning-tree method, accounting for the residual Clifford. Its reported geometric-mean two-qubit count ratio is 1.28 relative to the original circuits, versus larger expansion ratios for comparators. | A useful warning to include the final Clifford when evaluating compilation. This is not a claim of a 28% reduction. Primary conference text was available through indexing; direct full-PDF retrieval failed, so implementation assessment is provisional. |
| **Kaldenbach et al., Improved strategies for fermionic quantum simulation with global interactions.** **March 2026**, npj Quantum Information 12, 54; preprint April 2025. [Publication](https://www.nature.com/articles/s41534-026-01223-0), [preprint](https://arxiv.org/abs/2504.03237) | Exploits global Mølmer–Sørensen interactions for excitation operators and shared decompositions. | Relevant to a future trapped-ion comparison. Its global interaction is not the local CZ primitive used in these saved IBM runs; translating it back to pairwise CZ gates can remove the benefit. |
| **Decker et al., Kernpiler: Compiler Optimization for Quantum Hamiltonian Simulation with Partial Trotterization.** April 2025; revision **18 November 2025**. [Full text](https://arxiv.org/html/2504.07214v2) | Compiles small groups of noncommuting Hamiltonian terms together and uses error analysis to reduce the required Trotter steps. Reports numerical gate/depth improvements up to tenfold on selected tasks. | Useful after moving from individual strings to Hamiltonian simulation. Compare at matched simulation error, not merely matched number of Trotter steps. |
| **Yang et al., PHOENIX: Pauli-Based High-Level Optimization Engine for Instruction Execution on NISQ Devices.** **DAC 2025**, July manuscript revision. [Full text](https://arxiv.org/html/2504.03529v5), [code](https://github.com/iqubit-org/phoenix) | Uses binary symplectic representations, Clifford transformations, and global block ordering that considers cancellation, depth, and routing. | A candidate for jointly compiling chemistry-style term lists. PHOENIX is a compiler name, unrelated to the `ibm_phoenix` backend. Audit term-order semantics when using its scheduling freedom. |
| **Bäumer and Woerner, Measurement-based long-range entangling gates in constant depth.** **6 May 2025**, Physical Review Research 7, 023120; preprint August 2024. [Publication](https://journals.aps.org/prresearch/abstract/10.1103/PhysRevResearch.7.023120), [full text](https://arxiv.org/html/2408.03064v1) | Gives an alternating-line CNOT ladder using two entangling layers, \(2n\) CX gates, and one round of \(n\) measurements. Also develops fan-out, long-range CNOTs, and simultaneous prefix-string rotations. | Two dynamic ladders around one rotation give \(4n\) CX and \(2n\) measurements: the same leading resources as the compact implementation, not an automatic improvement. More promising for shared prefix rotations and long gaps. The preprint hardware protocol applied corrections in postprocessing with an emulated feedback delay. |
| **Dubal et al., Pauli Network Circuit Synthesis with Reinforcement Learning.** **18 March 2025** preprint. [Full text](https://arxiv.org/html/2503.14448) | Resynthesizes small Pauli/Clifford blocks subject to connectivity, including post-routing optimization. Reports average improvements around 20% in two-qubit count and depth across Benchpress, with larger gains for some instances. | Appropriate for unitary blocks before/between measurements and for stronger static baselines. Do not run a unitary optimizer across measurements or conditional branches without preserving the complete quantum instrument. |
| **Liu et al., QuCLEAR: Clifford Extraction and Absorption for Quantum Circuit Optimization.** **HPCA 2025**, February manuscript revision. [Full text](https://arxiv.org/html/2408.13316v2), [artifact](https://github.com/revilooliver/QuCLEAR) | Moves Clifford work through rotations and, when measurement semantics permit, absorbs the final Clifford into observable evaluation or classical processing. Reports benchmark maxima of 77.7% fewer CNOTs and 84.1% less entangling depth. | Particularly useful for multi-term workloads and terminal observables. Keep the residual Clifford for a reusable unitary; arbitrary Clifford removal is not always a bitstring relabeling. These maxima are not expected savings on a single Pauli string. |
| **Kaldenbach and Heller, Mapping quantum circuits to shallow-depth measurement patterns based on graph states.** **QST 10, 015010 (2025)**; online **15 October 2024**. [Publication/full text](https://doi.org/10.1088/2058-9565/ad802b) | Constructs Pauli-unitary measurement patterns, shifts corrections, and exploits commuting groups and graph-state optimization. Some further reductions use known stabilizer input and measurement structure. | The key conceptual reference for local ancilla gadgets and measurement-aware compilation. Separate arbitrary-input channel implementations from optimizations that only preserve a chosen preparation/measurement experiment. Count graph preparation and routing. |

Three older references remain essential comparators rather than being superseded by their publication dates:

- **Goubault de Brugière and Martiel, Faster and shorter synthesis of Hamiltonian simulation circuits (April 2024).** Introduces the Pauli-network heuristics underlying Rustiq, with count/depth objectives and ordering choices. It supplies an accessible baseline for joint synthesis; native-device routing still needs evaluation. [Paper](https://arxiv.org/abs/2404.03280), [repository](https://github.com/qiskit-community/rustiq).
- **Cowtan et al., Phase Gadget Synthesis for Shallow Circuits (2019 preprint; 2020 proceedings).** Provides the phase-gadget/tree and cancellation perspective needed for a stronger baseline than an endpoint chain. Balanced logical trees do not imply logarithmic depth on a one-dimensional nearest-neighbor device. [Paper](https://arxiv.org/abs/1906.01734).
- **Sriluckshmy et al., Optimal, hardware native decomposition of parameterized multi-qubit Pauli gates (2023).** Studies synthesis into native parameterized two-qubit interactions on different hardware graphs. Its optimality statements depend on that gate model; a fixed CZ gate and an arbitrary-angle RZZ gate have different costs. [Paper](https://arxiv.org/abs/2303.04498).

Additional useful context comes from **Bäumer et al., Efficient Long-Range Entanglement Using Dynamic Circuits (PRX Quantum 2024)**: it benchmarks long-distance teleportation and analyzes dynamic-circuit error budgets. This motivates testing routing replacements using measured latency and error, not assuming a distance-independent quantum-layer count implies a hardware win. [Paper](https://arxiv.org/abs/2308.13065).

For a later chemistry application, **Miller, Glos and Zimborás, Treespilation: architecture- and state-optimised fermion-to-qubit mappings** offers optimization before the Pauli strings are fixed. Changing the fermion encoding may shorten routed strings, but it changes the encoding, reference state, and observables together. It is outside the current fixed-string comparison. [Paper](https://arxiv.org/abs/2403.03992), [publication](https://www.nature.com/articles/s41534-025-01170-2).

Two watch-list entries should not drive implementation yet: **PauliForest** (IEEE TCAD, June 2025; [DOI](https://doi.org/10.1109/TCAD.2024.3509794)) could be relevant to joint synthesis/mapping, but I could not retrieve primary full text; and **Meijer-van de Griend and Becker, Pauli Gadget Synthesis for Gatesets with Arbitrary Even-Arity Clifford Gates** is listed in the [QPL 2026 program](https://qplconference.org/accepted/), but a verified accessible paper was not located. No gate-count claims from either are used here.

**Concrete decompositions and adaptations to test**

The following resource analysis is specific to this repository. Algebraic adaptations are identified explicitly; their native-hardware performance remains to be measured.

**1. Keep terminal corrections in software.** This is the smallest change to the existing compact construction. Retain the final data Pauli frame \(F\), conjugate it through the Clifford readout wrapper \(C\), and flip each measured bit whose Z measurement anticommutes with \(CFC^\dagger\). Preserve shot-by-shot correlations with the mid-circuit record. Helpers that will never be reused need no physical cleanup.

For an unpadded Z string, the compact construction's final corrections consist of suffix parities of the second ancilla outcomes. The final Hadamards turn these Z corrections into readout-bit flips. The all-Z decomposition has \(2L+1\) conditional blocks, including helper cleanup; terminal processing can leave only the rotation-sign conditional. This is a count of removed conditionals, not a prediction of proportional latency reduction.

The first parity measurement and its **angle-sign feed-forward must remain**. They affect a non-Clifford rotation. This optimization also requires a terminal-measurement mode: the existing reusable-unitary contract returns helpers physically to zero and cannot silently be changed.

Relevant implementation points are `_flush`, `finalize`, and `to_qiskit` in [pauli_exp_dynamic.py](../pauli_exp_dynamic.py), plus result handling in [hardware_compare.py](../hardware_compare.py). The latter currently saves only final `meas` counts. Save **joint per-shot ancilla and data outcomes** for software frame correction; independent marginal histograms lose the required correlations.

**2. Use one ancilla for a locally connected string.** This is the direct measurement-based parity-gadget alternative. A useful hardware form, derived here in the repository's angle convention, is:

1. Rotate the data Pauli factors into Z.
2. Prepare a connected ancilla in \(|+\rangle\).
3. Apply one CZ from the ancilla to each supported data qubit.
4. Apply \(R_x(2\theta)\) to the ancilla and measure it in Z, obtaining \(s\).
5. Apply/track \((\prod Z_j)^s\), then undo the data basis change.

The unnormalized data branch is

\[
K_s=\frac{1}{\sqrt{2}}P^s e^{-i\theta P}
\]

after translating back to the original Pauli basis. Both outcomes occur with probability one half, independently of the input. Thus this implements the full channel, not just a selected state preparation. The expression follows by expanding the controlled-P interaction into the ancilla's two computational states.

| Local supported weight | CZ gates | Ancillas | Ancilla measurements | Compact-chain comparison |
|---|---:|---:|---:|---|
| 3 | 3 | 1 | 1 | 8 CX, 2 ancillas, 4 measurements |
| 4 | 4 | 1 | 1 | 12 CX, 3 ancillas, 6 measurements |

All CZs share the hub, so their depth is \(w\), not one. A square-lattice hub has at most four neighbors; larger strings require routing or another construction. Moreover, `PaperGridLayout` spaces data on every other row and column: its current data placement does not provide a hub adjacent to three or four data qubits. **A new local layout is required.**

For a single exponential followed only by Clifford readout, all outcomes can be measured at the end and corrected classically. No within-shot feedback is required in that specialized terminal circuit. For arbitrary subsequent operations, retain the correction/frame and adapt later noncommuting rotations. This is the same distinction between channel gadgets and terminal measurement optimization emphasized by the measurement-pattern literature above.

**3. Compress local groups before using a dynamic chain.** This is a proposed combination of parity-tree synthesis and the existing compact gadget, rather than a claim that a paper already benchmarks this exact hybrid.

Partition the support into \(k\) groups. Within each group compute its Z parity into a root using a Clifford circuit \(C\), run the compact exponential on the roots, then uncompute \(C\). In chronological order this is \(C\), root rotation, \(C^\dagger\). Algebraically,

\[
C^\dagger e^{-i\theta\prod_{j=1}^{k} Z_{r_j}}C
=e^{-i\theta\prod_{i=1}^{w}Z_i}.
\]

If each local group uses a tree with one edge per eliminated support qubit, and the roots can use an alternating chain without fillers, the count is

\[
N_{2q}=2(w-k)+4(k-1)=2w+2k-4,
\qquad N_{\rm MCM}=2(k-1).
\]

For \(k\ge2\), entangling depth is at most \(2d_C+4\), where \(d_C\) is the depth of the parallel local compression circuits.

| Example | Compact gates / measurements | Hybrid gates / measurements | Hybrid assumption |
|---|---:|---:|---|
| Weight 8, four groups of 2 | 28 / 14 | 20 / 6 | Four locally computed roots with three direct links |
| Weight 12, three groups of 4 | 44 / 22 | 26 / 4 | Three locally computed roots with two direct links |
| Weight 25, five groups of 5 | 96 / 48 | 56 / 8 | Five locally computed roots with four direct links |

These are **pre-routing design targets**. The current spaced layout does not give adjacent data within the groups. Count all bridging/filler operations in an actual embedding. The attraction is a tunable trade-off: modest additional coherent depth can remove many measured ancillas and their error channels. Search group size and geometry together instead of fixing the grouping by logical index.

**4. Share the Clifford circuit in `XZZZX + YZZZY`.** Write the endpoints as qubits 0 and 4 and define

\[
C=\mathrm{CZ}_{0,1}\mathrm{CZ}_{0,2}\mathrm{CZ}_{0,3}.
\]

Then \(CX_0X_4C=X_0Z_1Z_2Z_3X_4\), and the analogous identity holds for Y. Therefore, for arbitrary independent angles,

\[
e^{-i\beta YZZZY}e^{-i\alpha XZZZX}
=C\left[e^{-i\beta Y_0Y_4}e^{-i\alpha X_0X_4}\right]C.
\]

This reduces the problem to six shared CZs and a two-qubit core. Generic exact KAK synthesis needs at most three CX-equivalent entanglers for that core: a conservative target is **at most nine entanglers before routing**, versus 16 for two separate logical ladders and 32 for two compact dynamic gadgets. The saved transpiled ladder already reduces 16 to 15, which should be the actual comparator. A five-site square-lattice cross can embed this construction with qubit 0 at its center and qubits 1–4 on its neighbors. More specialized synthesis may improve the core further; the nine-gate target does not depend on that improvement.

This derivation is specific to the existing benchmark. Recent hardware work also uses exact two-qubit KAK compression for overlapping Pauli terms, demonstrating its practical role, but does not establish the performance of this five-qubit proposal. [2026 hardware paper, implementation section](https://www.nature.com/articles/s41467-026-75904-x).

**5. Add stronger unitary baselines and joint compilation.** For isolated strings, compare the current endpoint ladder against a balanced logical parity tree and a tree built directly on the coupling graph. On a connected line, inward accumulation from both ends is another useful baseline. A balanced tree's ideal \(2\lceil\log_2 w\rceil\) compute/uncompute depth requires suitable connectivity; report the routed result.

For term lists, feed the **whole sequence** to Rustiq, QuCLEAR, PHOENIX, or MonteQ. Calling a sophisticated synthesizer separately for each string discards the main optimization opportunity. Start with the two-term case and a set of nested Z prefixes, then short mixed commuting/noncommuting lists. Preserve noncommuting order.

Qiskit's current Rustiq high-level synthesis plugin exposes `optimize_count`, `preserve_order`, and `upto_clifford`. For the reusable exact-unitary comparison, preserve order up to commutation and retain the final Clifford. Test count and depth objectives independently, then route and rank their physical circuits. [Current plugin documentation](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.transpiler.passes.synthesis.hls_plugins.PauliEvolutionSynthesisRustiq).

**6. Test native parameterized gates where available.** A straightforward exact alternative computes parity down to two qubits, applies native \(R_{ZZ}(2\theta)\), then uncomputes. Without routing, this takes \(2(w-2)+1=2w-3\) entangling operations, versus \(2w-2\) for a CX-based ladder. The improvement for one long string is modest, but two-body-heavy term lists benefit more.

IBM's current fractional-gate guide documents native RZZ/RX on supported Heron systems; it does not establish support on the two backends in the saved experiment. The repository's `get_backend()` does not request fractional gates. Inspect the target on each device, including angle restrictions, before using this option. At \(\theta=0.4\), the required RZZ angle 0.8 lies in the documented direct range \((0,\pi/2]\). [Fractional-gate guide](https://quantum.cloud.ibm.com/docs/en/guides/fractional-gates).

Current Sampler documentation explicitly permits fractional gates with dynamic circuits with runtime client v0.42 or later. Older documentation stating they are incompatible is outdated. Other feature combinations, including gate twirling with fractional gates, remain restricted. [Current compatibility documentation](https://quantum.cloud.ibm.com/docs/en/guides/sampler-options). Native-unitary RZZ gates must not be confused with the project's projective ZZ measurements.

**How to make the hardware comparison decisive**

First, add a phase-sensitive observable. After the present preparation/postprocessing, a single-string ideal output is

\[
|\psi_\theta\rangle=\cos\theta|0\cdots0\rangle-i\sin\theta|1_S\rangle.
\]

Its computational-basis distribution is unchanged under \(\theta\mapsto-\theta\). Consequently, Hellinger fidelity and `theta_est` cannot detect every incorrect sign branch or loss of coherence. The separate [full-statevector tests](../test_aer_vs_ladder.py) do check the sign; the probability-only pre-submission check and the present hardware observable do not provide that same guarantee.

Measure Y on one support qubit and X on the other supported qubits, in the effective output basis. Its ideal expectation is \(-\sin(2\theta)\). At \(\theta=0.4\), the correct and wrong-sign values are approximately -0.71736 and +0.71736; an equal mixture gives zero. Keep the existing population/leakage measurement as a separate diagnostic. Use several non-Clifford positive and negative angles. This is also a direct way to validate terminal frame processing experimentally.

Second, use two placement comparisons: (a) the same physical data assignment when both constructions support it, and (b) independently optimized placement for each construction. The first isolates implementation cost; the second asks which approach delivers the best device result. Neither alone answers both questions. Repeat across several comparable patches and interleave circuit order within jobs.

Third, report actual scheduled circuit duration and idle intervals, alongside native two-qubit counts, measurement count, measurement rounds, and feed-forward dependencies. The stored execution-span wall-clock values include inter-shot overhead and often average multiple circuits; dividing those numbers by T2 does not measure coherent exposure. The code already requests scheduler timing, so first inspect why it was unavailable in older records. IBM documents returning actual dynamic-circuit timing in Sampler metadata. [Timing documentation](https://quantum.cloud.ibm.com/docs/en/guides/qiskit-runtime-circuit-timing).

Fourth, distinguish the first parity measurements from terminal ancilla readouts. Current code emits ordinary `measure`. On targets that support it, evaluate the optimized `MidCircuitMeasure` instruction through `ConvertToMidCircuitMeasure` after routing. Verify support on the actual physical qubits. Update operation metrics and simulation handling for its instruction name; existing code counts only `measure`. [Conversion-pass documentation](https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/transpiler-passes-convert-to-mid-circuit-measure).

Fifth, optimize layouts against the actual repeated operations. `patch_cost()` currently sums errors over the whole layout block and `best_layout()` prioritizes smallest block size. A better experimental heuristic would weight used edges by multiplicity, link-ancilla measurement quality, and actual idle time. Measure spectator disturbance and parity-measurement quality rather than treating terminal readout errors as a complete MCM noise model.

For intuition only, if \(L\) independent parity bits each flip with probability \(p\), their XOR is incorrect with probability

\[
p_{\rm parity}=\frac{1-(1-2p)^L}{2}.
\]

The model omits correlations, relaxation, and measurement backaction, but explains why shortening the measured chain can matter even when its quantum depth is already constant. Fit any cost model to measured hardware behavior rather than treating this expression as a fidelity predictor.

Finally, treat DD and ZNE as separately budgeted experiments. Tune DD to the relevant idle intervals, and report added pulses and actual scheduling. If exploring ZNE, repeat complete logical gadgets and their logical inverses with fresh/reinitialized ancillas; a physical projective measurement has no ordinary unitary inverse. Account for the additional shots and compare observable-estimation error separately from raw circuit performance.

**Recommended experiment order**

| Priority | Experiment | Initial cases | Decision criterion |
|---|---|---|---|
| 1 | Compact circuit with terminal frame processing; appropriate MCM instruction; phase-sensitive readout | Z3, Z5, XYZ strings | Same ideal corrected statistics and phase; fewer physical conditionals; measured duration/fidelity change |
| 2 | One-ancilla local gadget, with terminal and reusable modes distinguished | Three- and four-leaf local stars | Does reduced entangling/readout cost survive the hub's noise and placement constraints? |
| 3 | Static trees and local-compression/dynamic hybrids | Weights 8 and 12, groups of 2–4 | Find the measured optimum between coherent depth and measurement overhead |
| 4 | Shared exact synthesis and compiler comparison | XZZZX+YZZZY; nested Z prefixes; short term lists | Native routed resources and coherent accuracy against the existing ladder |
| 5 | Native RZZ where supported; interval-specific DD | Best candidates from 1–4 | Improvement at matched target, calibration window, and shot budget |
| 6 | Approximate synthesis, partial Trotterization, or alternative fermion encodings | Actual chemistry/time-evolution workload | Total observable error at matched simulation accuracy and execution budget |

Include special-angle checks: \(\theta=0\) is identity and \(\theta=\pi/2\) gives \(-iP\), requiring only local Paulis up to global phase. \(\theta=\pi/4\) is Clifford but can still be entangling. Main hardware conclusions should include generic non-Clifford angles so these simplifications do not dominate the result.

**Independent checks and practical limits**

The companion [verification script](verify_candidate_identities.py) uses only Python's standard library. It compares complex amplitudes for every computational-basis column of its selected small instances, so it checks coherent linear maps rather than only probability distributions. [Saved results](identity_check_results_2026-10-18.json):

- Single-ancilla gadget: 2,156 branch/column checks, including mixed X/Y/Z strings and both ancilla outcomes; maximum amplitude discrepancy \(4.45\times10^{-16}\).
- Group-compression identity: 7,168 column checks through eight data qubits; zero observed discrepancy.
- Shared five-qubit pair: 96 column checks with independent angles; zero observed discrepancy.
- Sign diagnostic: identical computational-basis probabilities for opposite angles, with the expected opposite Y/X correlators.

These checks establish the stated identities for the tested instances. They do not test native KAK synthesis, routing, Qiskit export, noisy measurements, or hardware performance. The hybrid check uses an ideal root rotation; the actual compact gadget and frame propagation must be validated again when integrated. The active Python environment lacks Qiskit/Aer, so no new transpilation or Aer results are claimed.

The review's highest-confidence conclusion is that **measurement and correction cost, routed support length, and opportunities shared across terms are the next useful optimization targets**. The current compact circuit is already a strong constant-depth implementation; a portfolio selected by geometry and measurement context is more promising than assuming one decomposition will win for every string.
