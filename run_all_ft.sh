#!/usr/bin/env bash
# Every test case for the FAULT-TOLERANT variant (pauli_exp_dynamic.py: paper Fig. 1, |θ> ancilla, ROT rule).
#
#     conda activate dynamic_circuits
#     bash run_all_ft.sh                              # ibm_rensselaer, saved account's instance
#     bash run_all_ft.sh <backend_name> "<CRN>"       # another device with its own CRN (same saved API key)
#
# Each hardware line submits ONE job and waits for its result. Before submitting, hardware_compare.py
# runs the Aer check on every circuit exactly as submitted and submits nothing if a check fails.
# A failed step is reported and the script continues with the next one.
# --dd both puts every circuit with AND without DD into one job (i.e. --dd on + --dd off together).
# Note: on ibm_rensselaer, DD-padded dynamic circuits have failed with IBM error 6057 (compiler error).

cd "$(dirname "$0")"

# BACKEND="${1:-ibm_rensselaer}"                             # device name (1st argument)
# CRN="${2:-}"                                                # CRN of its instance (2nd argument); empty = saved default
BACKEND="ibm_phoenix"                                  # ... or set them here instead
CRN="crn:v1:bluemix:public:quantum-computing:us-east:a/b8ff6077c08a4ea9871560ccb827d457:d51a1467-98b7-4f15-8cd9-055a57606194::"

DRY=""                                                     # submit the hardware jobs
# DRY="--dry-run"                                          # build + transpile + Aer check only, no jobs (-> *_dryrun/ folders)

DEVICE=(--backend "$BACKEND")
if [ -n "$CRN" ]; then DEVICE+=(--instance "$CRN"); fi
echo "device: $BACKEND   instance: ${CRN:-(saved account default)}"

run() { echo; echo "=== $*"; "$@" || echo "!!! FAILED (continuing): $*"; }

# 1) correctness: Qiskit Aer, dynamic circuit vs CNOT ladder (local; report in test_results/)
run python test_aer_vs_ladder.py --variant ft

# 2) depth study, untranspiled + transpiled for the device  ->  depth_comparison_ft_<backend>/
run python compare_depths.py --variant ft "${DEVICE[@]}"

# 3) hardware, θ = 0.4  ->  hardware_results_ft_<backend>_dd-<on|off|both>/
run python hardware_compare.py --variant ft --dd off  $DRY "${DEVICE[@]}"
run python hardware_compare.py --variant ft --dd on   $DRY "${DEVICE[@]}"
run python hardware_compare.py --variant ft --dd both $DRY "${DEVICE[@]}"

# 4) hardware, θ sweep π/8, π/4, 3π/8  ->  hardware_theta_sweep_ft_<backend>_dd-<on|off|both>/
run python hardware_compare.py --variant ft --sweep --dd off  $DRY "${DEVICE[@]}"
run python hardware_compare.py --variant ft --sweep --dd on   $DRY "${DEVICE[@]}"
run python hardware_compare.py --variant ft --sweep --dd both $DRY "${DEVICE[@]}"
