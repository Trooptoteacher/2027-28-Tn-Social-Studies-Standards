#!/usr/bin/env python3
"""Enforce the rule: every mistake gets a guard.

Sean's standing instruction — for every mistake made or found, build a guard so
it never happens again. A ledger of lessons is worthless on its own; prose
about a fix decays into a promise. So this checks that each lesson names a
guard, that the guard EXISTS in the code, and that the suite carrying it
actually RUNS.

It also fails on an orphan: a test file nobody registered is a suite that
quietly stops being executed.

Usage: python3 tools/check_lessons.py
"""
from __future__ import annotations

import glob
import json
import os
import sys

BANK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(BANK, "lessons.json")


def main():
    with open(LEDGER, encoding="utf-8") as fh:
        doc = json.load(fh)
    lessons = doc.get("lessons", [])
    suites = doc.get("registeredSuites", [])
    problems = []

    # A ledger with no lessons is the empty-scan failure applied to itself.
    if not lessons:
        problems.append("EMPTY LEDGER — no lessons recorded. This check reporting green "
                        "over zero lessons is the same defect it exists to prevent.")
    if not suites:
        problems.append("no registered suites — nothing would run")

    seen_ids = set()
    for L in lessons:
        lid = L.get("id", "?")
        if lid in seen_ids:
            problems.append(f"{lid}: duplicate lesson id")
        seen_ids.add(lid)
        if not L.get("mistake", "").strip():
            problems.append(f"{lid}: no mistake described")
        guards = L.get("guards") or []
        if not guards:
            problems.append(f"{lid}: NO GUARD — a lesson without a guard is a promise, "
                            f"not a fix")
            continue
        for g in guards:
            path = os.path.join(BANK, g["file"])
            if not os.path.exists(path):
                problems.append(f"{lid}: guard file {g['file']} does not exist")
                continue
            with open(path, encoding="utf-8") as fh:
                body = fh.read()
            if g["contains"] not in body:
                problems.append(
                    f"{lid}: guard {g['file']} no longer contains {g['contains']!r} — "
                    f"the guard was removed or renamed, so the lesson is unenforced")
            is_suite_file = (g["file"].startswith("tests/")
                             and os.path.basename(g["file"]).startswith("test_"))
            if is_suite_file and g["file"] not in suites:
                problems.append(
                    f"{lid}: guard lives in {g['file']}, which is NOT a registered suite — "
                    f"it would never run")

    # Orphan suites: a test file that exists but nothing runs.
    on_disk = {os.path.relpath(p, BANK) for p in
               glob.glob(os.path.join(BANK, "tests", "test_*.py"))}
    for orphan in sorted(on_disk - set(suites)):
        problems.append(f"{orphan} exists but is not a registered suite — it would never run")
    for missing in sorted(set(suites) - on_disk):
        problems.append(f"registered suite {missing} does not exist on disk")

    print(f"Lessons ledger: {len(lessons)} lesson(s), "
          f"{sum(len(L.get('guards') or []) for L in lessons)} guard(s), "
          f"{len(suites)} registered suite(s)")
    if problems:
        print(f"\n[FAIL] check-lessons — {len(problems)} problem(s):")
        for p in problems:
            print("  -", p)
        return 1
    print("[PASS] check-lessons — every lesson names a guard that exists in a suite that runs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
