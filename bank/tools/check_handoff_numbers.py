#!/usr/bin/env python3
"""The handoff's numbers must still be true.

HANDOFF.md opens by saying its numbers were MEASURED. That is only worth
saying if something re-measures them. They went stale the first time the bank
changed underneath them: a single change moved aligned items 1,890 -> 2,006,
buildable standards 55 -> 66 and the ledger 50/109 -> 53/125, and every one of
those numbers sat in the handoff reading like a current fact.

This is the same defect the repo has caught before in other clothes — a
reference build named in prose and never re-measured, a coverage claim written
into a memory file. A number in prose is a CLAIM, and an unmeasured claim rots
silently while continuing to look authoritative.

So the handoff's headline figures are derived here and compared against the
committed text. Update the file, or explain why the tool is wrong; do not
delete the check.

Usage: python3 tools/check_handoff_numbers.py
"""
from __future__ import annotations

import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import binding as binding_mod
import itemio

HANDOFF = os.path.join(itemio.BANK_ROOT, "HANDOFF.md")
LESSONS = os.path.join(itemio.BANK_ROOT, "lessons.json")


def _n(v) -> str:
    return f"{v:,}"


def live():
    """Every figure the handoff states, computed from the artifact."""
    b = binding_mod.load()
    bank = itemio.load_dir(b.output_dir)
    quar = itemio.load_dir(b.quarantine_dir)
    st = collections.Counter(i.get("alignmentStatus") for i in bank)
    with open(LESSONS, encoding="utf-8") as fh:
        led = json.load(fh)

    # Call the TOOL's own computation. This re-derived it and got 1,763
    # against the tool's 1,867, because the copy pooled items by standardCodes
    # and skipped the per-standard relevance rule. A checker written to catch
    # drift, drifting (L22, L54).
    import form_readiness as fr
    rws = fr.rows(b)
    ok = [r for r in rws if r["buildable"]]
    buildable = len(ok)
    units = sum(r["totalAuthoringUnits"] for r in ok)

    return {
        "servable":     (_n(sum(1 for i in bank if itemio.servable(i))),
                         r"\|\s*servable\s*\|\s*([\d,]+)\s*\|"),
        "aligned":      (_n(sum(1 for i in bank if itemio.aligned(i))),
                         r"\|\s*aligned \(counts toward coverage\)\s*\|\s*([\d,]+)\s*\|"),
        "quarantined":  (_n(len(quar)),
                         r"\|\s*quarantined, with stated reasons\s*\|\s*([\d,]+)\s*\|"),
        "evidenced":    (_n(st["evidenced"]), r"Alignment:\s*([\d,]+)\s*`evidenced`"),
        "rehomed":      (_n(st["rehomed"]), r"`evidenced`\s*·\s*([\d,]+)\s*`rehomed`"),
        "unverified":   (_n(st["unverified"]), r"`rehomed`\s*·\s*([\d,]+)\s*`unverified`"),
        "lessons":      (_n(len(led["lessons"])), r"\*\*([\d,]+) lessons,"),
        "guards":       (_n(sum(len(l["guards"]) for l in led["lessons"])),
                         r"lessons,\s*([\d,]+) guards\*\*"),
        "buildable":    (_n(buildable), r"\*\*([\d,]+) of 94 standards can build a form"),
        "authoringUnits": (_n(units), r"can build a form\.\s*([\d,]+) authoring units"),
    }


def main():
    if not os.path.exists(HANDOFF):
        print("[FAIL] check-handoff-numbers — HANDOFF.md is missing")
        return 1
    text = open(HANDOFF, encoding="utf-8").read()
    problems, checked = [], 0
    for label, (value, pattern) in live().items():
        m = re.search(pattern, text)
        if not m:
            problems.append(f"{label}: the handoff no longer states this figure — the line was "
                            f"reworded or removed, so nothing measures it (live value {value})")
            continue
        checked += 1
        if m.group(1) != value:
            problems.append(f"{label}: handoff says {m.group(1)}, the artifact says {value}")
    print(f"checked {checked} headline figure(s) in HANDOFF.md")
    if problems:
        print(f"\n[FAIL] check-handoff-numbers — {len(problems)} stale or missing figure(s):")
        for p in problems:
            print("  -", p)
        print("\nRegenerate the numbers and edit HANDOFF.md. A number in prose is a claim; "
              "an unmeasured claim rots while still reading as authoritative.")
        return 1
    print("[PASS] check-handoff-numbers — every stated figure still matches the artifact")
    return 0


if __name__ == "__main__":
    sys.exit(main())
