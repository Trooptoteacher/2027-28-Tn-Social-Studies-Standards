#!/usr/bin/env python3
"""Every gate that exists is wired, and every gate that is wired exists.

A careless rewrite of tools/gates/coverage.py — replacing from one function to
the END of the file — silently deleted two gates defined after it. The runner
then crashed on an AttributeError, which was luck: had those gates been
referenced only in a branch that did not run, the deletion would have been
invisible and the artifact would simply have stopped being checked for those
defects.

So: the runner's gate lists must resolve, and no gate may exist in the package
without being wired somewhere or explicitly declared unwired.

Usage: python3 tools/check_gates_wired.py
"""
from __future__ import annotations

import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import run_gates
from gates import content, coverage, record
from gates import forms as formgates

# Gates deliberately not in a runner list, with the reason.
UNWIRED = {
    "gate_form_standard_relevance": "called directly by the form scope in collect_form",
    "gate_form_key_position": "called directly by the form scope in collect_form",
    "gate_form_blueprint": "called directly with the form's declared tiers",
    "gate_form_pagination": "print gate, called on rendered PDFs",
    "gate_form_type_size": "print gate, called on rendered PDFs",
    "gate_form_key_leakage": "print gate, called on rendered PDFs",
    "gate_form_disclosure": "print gate, called on rendered PDFs",
    "gate_form_key_contradiction": "print gate, called on rendered PDFs",
    "gate_form_teacher_metadata": "print gate, called on rendered PDFs",
    "gate_teacher_side_isolation": "form scope only — items at rest carry no surface",
}


def main():
    problems = []
    defined = {}
    for mod in (record, coverage, content, formgates):
        for nm, fn in vars(mod).items():
            if nm.startswith("gate_") and inspect.isfunction(fn):
                defined[nm] = mod.__name__

    wired = {g.__name__ for g in run_gates.GATES} | {g.__name__ for g in run_gates.ITEM_GATES}
    src = inspect.getsource(run_gates)

    for nm in sorted(defined):
        if nm in wired:
            continue
        if nm in UNWIRED:
            if nm not in src:
                problems.append(f"{nm}: declared as directly-called but the runner never "
                                f"mentions it — it is not running at all")
            continue
        problems.append(f"{nm} ({defined[nm]}): defined but wired nowhere and not declared "
                        f"unwired — this gate is not measuring anything")

    for nm in sorted(wired | set(UNWIRED)):
        if nm not in defined:
            problems.append(f"{nm}: referenced by the runner but no longer defined — a rewrite "
                            f"may have deleted it")

    print(f"gates defined: {len(defined)}; in a runner list: {len(wired)}; "
          f"directly called: {len(UNWIRED)}")
    if problems:
        print(f"\n[FAIL] check-gates-wired — {len(problems)} problem(s):")
        for p in problems:
            print("  -", p)
        return 1
    print("[PASS] check-gates-wired — every gate defined is running, and every gate "
          "referenced still exists")
    return 0


if __name__ == "__main__":
    sys.exit(main())
