#!/usr/bin/env bash
# Everything, in the order that fails fastest and cheapest first.
# Exit non-zero if ANY stage fails. "Close" is not "A".
set -uo pipefail
cd "$(dirname "$0")/.." || exit 2
FAIL=0
stage() {
  printf '\n\033[1m=== %s ===\033[0m\n' "$1"; shift
  if "$@"; then :; else FAIL=1; printf '  ^ STAGE FAILED\n'; fi
}

# The ledger first: if a guard has gone missing, nothing below can be trusted.
stage "lessons ledger"        python3 tools/check_lessons.py
stage "gate proofs"           python3 tests/test_gates.py
stage "gate mutation check"   python3 tests/test_mutation.py
stage "alignment routing"     python3 tests/test_alignment.py
stage "regression pins"       python3 tests/test_regressions.py
stage "content gate proofs"   python3 tests/test_content_gates.py
stage "re-home triage pins"   python3 tests/test_rehome.py
stage "print gate proofs"     python3 tests/test_form_gates.py
stage "gates vs artifact"     python3 tools/run_gates.py
# The pilot form is GREEN. Enforce it: a regression here means something that
# was proven achievable stopped being achievable.
stage "FORM-A (proven green)"  python3 tools/run_gates.py --form FORM-A

printf '\n'
if [ "$FAIL" -eq 0 ]; then
  echo "ALL STAGES PASS"
else
  echo "HELD — at least one stage failed. Grade A requires all of them."
fi
exit "$FAIL"
