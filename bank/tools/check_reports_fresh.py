#!/usr/bin/env python3
"""Committed reports must MATCH what their generator produces now.

form_readiness.py was broken by the tiered blueprint and its stale CSV was
committed anyway, because the regeneration ran with output suppressed and its
exit code was never read. A committed report that its own generator can no
longer produce is a claim about the artifact that nothing backs.

AND THIS GATE DID NOT CHECK THAT. Until 2026-10-05 it ran each generator and
failed only on a traceback — so it proved the generator did not CRASH, which is
a different claim from the one its own name and its own pass message make. A
stale STATUS.md went through it and was committed: it recorded
`review-provenance` at 19 findings when the code produced 3.

Worse than missing it, the gate DESTROYED THE EVIDENCE. Each generator writes
to the committed path, so running it overwrote the stale file, and the only
remaining trace was a dirty working tree that reads like noise after a suite
run. A freshness check that silently refreshes is not a check.

It now COMPARES, and fails on a difference. The regenerated file is left in
place, because that is the version the author wants to commit — the difference
from before is that the gate says so out loud instead of laundering it.

Comparison normalises the REPOSITORY ROOT. STATUS.md embeds the binding
declaration, which carries an absolute output path, so a byte comparison would
fail on a different checkout for a portability reason rather than a staleness
one — the same trap as a deck HTML carrying the absolute path of the machine
that rendered it. ⚠ That absolute path in a committed report is a real smell
and is NOT fixed here; it is reported, because changing what
`binding.declaration()` prints reaches every tool that prints it.

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


def _norm(text):
    """Content, independent of where this checkout lives."""
    return text.replace(BANK, "<BANK>").replace(os.path.dirname(BANK), "<REPO>")


def main():
    problems = []
    for path, cmd in REPORTS.items():
        full = os.path.join(BANK, path)
        if not os.path.exists(full):
            problems.append(f"{path}: committed report is missing"); continue
        with open(full, encoding="utf-8") as fh:
            committed = fh.read()
        r = subprocess.run([sys.executable] + cmd, cwd=BANK,
                           capture_output=True, text=True)
        # status_report exits non-zero when gates fail; that is a finding about
        # the BANK, not about the generator. A generator that crashed prints a
        # traceback, and that is what makes a report unbackable.
        if "Traceback" in r.stderr:
            tail = r.stderr.strip().splitlines()[-1]
            problems.append(f"{path}: its generator CRASHED — {tail}")
            continue
        with open(full, encoding="utf-8") as fh:
            fresh = fh.read()
        if _norm(committed) != _norm(fresh):
            a = _norm(committed).splitlines()
            b = _norm(fresh).splitlines()
            moved = [f"line {n + 1}: committed {x.strip()!r} -> now {y.strip()!r}"
                     for n, (x, y) in enumerate(zip(a, b)) if x != y][:3]
            if len(a) != len(b):
                moved.append(f"length {len(a)} -> {len(b)} line(s)")
            problems.append(
                f"{path}: the committed report does NOT match what its generator produces "
                f"now — it has been regenerated in place, so COMMIT IT. "
                + "; ".join(moved))
    print(f"checked {len(REPORTS)} committed report(s)")
    if problems:
        print(f"\n[FAIL] check-reports-fresh — {len(problems)} problem(s):")
        for p in problems:
            print("  -", p)
        return 1
    print("[PASS] check-reports-fresh — every committed report MATCHES what its generator "
          "produces now")
    return 0


if __name__ == "__main__":
    sys.exit(main())
