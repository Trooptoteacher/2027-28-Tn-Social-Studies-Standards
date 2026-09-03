#!/usr/bin/env python3
"""Alignment routing, pinned against real 2026-27 -> 2027-28 standard pairs.

Every case here is one the character-similarity floor got WRONG, in one
direction or the other. They are pinned because each was a bug found by
reading output, and each would return silently.
"""
from __future__ import annotations

import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))

import alignment as A

CROSSWALK = os.path.join(os.path.dirname(HERE), "..", "crosswalk",
                         "us-history-geography.csv")
ROWS = {(r["code_2026_27"], r["code_2027_28"]): r
        for r in csv.DictReader(open(CROSSWALK, encoding="utf-8")) if r["code_2026_27"]}

# (old, new, expected dropped, expected added, expected verbRaised, why it is here)
CASES = [
    ("US.16", "US.17", [], [], False,
     "sim 0.79 — a PURE BULLET REORDER. A 0.90 floor quarantined a standard "
     "with identical content."),
    ("US.12", "US.12", ["Clayton Antitrust Act of 1914"], [], False,
     "sim 0.89 — the Clayton Antitrust Act was DELETED. High similarity hid a "
     "real removal; items testing Clayton are out of scope."),
    ("US.60", "US.60", [], [], True,
     "sim 0.94 — verb Explain -> ANALYZE. A DOK shift a text ratio cannot see."),
    ("US.93", "US.92", ["Sandra Day O’Connor"], ["Sonia Sotomayor"], False,
     "a named figure swapped for another; the ratio only saw reordering."),
]

FAILED = []


def check(label, cond, detail=""):
    print(f"    [{'ok  ' if cond else 'FAIL'}] {label}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILED.append(label)


print("=" * 74)
print("ALIGNMENT ROUTING — pinned against real standard pairs")
print("=" * 74)

for old, new, exp_drop, exp_add, exp_raised, why in CASES:
    r = ROWS[(old, new)]
    d = A.delta(r["text_2026_27"], r["text_2027_28"])
    print(f"\n  {old} -> {new}  (sim {r['similarity']})\n    {why}")
    check(f"{old}->{new} dropped == {exp_drop}", d["dropped"] == exp_drop, f"got {d['dropped']}")
    check(f"{old}->{new} added == {exp_add}", d["added"] == exp_add, f"got {d['added']}")
    check(f"{old}->{new} verbRaised == {exp_raised}", d["verbRaised"] == exp_raised)

# Rewording is not deletion.
r = ROWS[("US.18", "US.20")]
d = A.delta(r["text_2026_27"], r["text_2027_28"])
print("\n  US.18 -> US.20   rewording must not read as deletion")
check("Tennessee's role NOT dropped (nickname 'Perfect 36' removed, role kept)",
      not any("Tennessee" in x for x in d["dropped"]), f"got {d['dropped']}")
check("'suffragettes' -> 'suffragists' NOT dropped (reworded)",
      not any("suffrag" in x.lower() for x in d["dropped"]), f"got {d['dropped']}")
check("Susan B. Anthony detected as ADDED",
      any("Anthony" in x for x in d["added"]), f"got {d['added']}")

# Case-citation punctuation is not a deletion.
r = ROWS[("US.86", "US.84")]
d = A.delta(r["text_2026_27"], r["text_2027_28"])
print("\n  US.86 -> US.84   'United States v. Nixon' vs 'United States vs. Nixon'")
check("v. / vs. punctuation not read as a deletion",
      not any("Nixon" in x for x in d["dropped"]), f"got {d['dropped']}")

# A distractor mentioning a dropped element is not evidence the item tests it.
print("\n  item matching")
check("generic demonym 'American' is not a usable signal",
      "american" not in [s.lower() for s in A.signals("desire to spread American democratic")]
      or not any(re.search(r"[A-Z]", s) for s in A.signals("desire to spread American democratic"))
      if (re := __import__("re")) else False)
check("a named act is a usable signal",
      A.signals("Clayton Antitrust Act of 1914") == ["Clayton Antitrust Act"],
      f"got {A.signals('Clayton Antitrust Act of 1914')}")
check("item testing the 17th Amendment does not match dropped '18th Amendment'",
      A.tests_dropped_element("What change did the 17th Amendment make?", ["18th Amendment"]) == [])

print("\n" + "=" * 74)
print(f"{'ALL PASS' if not FAILED else str(len(FAILED)) + ' FAILED'}")
for f in FAILED:
    print("  FAILED:", f)
print("=" * 74)
sys.exit(1 if FAILED else 0)
