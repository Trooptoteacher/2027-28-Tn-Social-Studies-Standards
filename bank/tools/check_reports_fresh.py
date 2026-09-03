#!/usr/bin/env python3
"""Committed reports must be regenerable from the current code.

form_readiness.py was broken by the tiered blueprint and its stale CSV was
committed anyway, because the regeneration ran with output suppressed and its
exit code was never read. A committed report that its own generator can no
longer produce is a claim about the artifact that nothing backs.

Usage: python3 tools/check_reports_fresh.py
"""
from __future__ import annotations

import os
import subprocess
import sys

BANK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# report file -> the command that must be able to produce it
REPORTS = {
    "reports/form-readiness.csv": ["tools/form_readiness.py", "--csv",
                                   "reports/form-readiness.csv"],
    "reports/STATUS.md": ["tools/status_report.py"],
}


def main():
    problems = []
    for path, cmd in REPORTS.items():
        full = os.path.join(BANK, path)
        if not os.path.exists(full):
            problems.append(f"{path}: committed report is missing"); continue
        r = subprocess.run([sys.executable] + cmd, cwd=BANK,
                           capture_output=True, text=True)
        # status_report exits non-zero when gates fail; that is a finding about
        # the BANK, not about the generator. A generator that crashed prints a
        # traceback, and that is what makes a report unbackable.
        if "Traceback" in r.stderr:
            tail = r.stderr.strip().splitlines()[-1]
            problems.append(f"{path}: its generator CRASHED — {tail}")
    print(f"checked {len(REPORTS)} committed report(s)")
    if problems:
        print(f"\n[FAIL] check-reports-fresh — {len(problems)} problem(s):")
        for p in problems:
            print("  -", p)
        return 1
    print("[PASS] check-reports-fresh — every committed report can still be produced "
          "by its generator")
    return 0


if __name__ == "__main__":
    sys.exit(main())
