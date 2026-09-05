#!/usr/bin/env python3
"""Measure the six-course assessment scope. The checklist's numbers come from here.

ASSESSMENT-BUILD-CHECKLIST.md states standard counts, per-standard depth and authoring volume.
Every one of those is a claim that rots the moment an item is written — the same defect
check_handoff_numbers.py exists to catch, one document over. Run this and compare.

Parallelism is measured on DOK-MATCHED depth, not raw depth. Five items on one standard at
DOK 1, 2, 2, 3, 3 do not build five equal forms; they build one form and four different ones.
US reads 72/94 on raw depth and 65/94 on the measure that matters.

Usage: python3 tools/course_scope.py [--per-form 2]
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import alignment
import itemio

REPO = os.path.dirname(itemio.BANK_ROOT)
COURSES = ["grade-06", "grade-07", "grade-08", "us-history-geography",
           "world-history-geography", "tennessee-history"]
FORMS = 5


def standards_of(slug):
    with open(os.path.join(REPO, "standards", f"{slug}.json"), encoding="utf-8") as fh:
        d = json.load(fh)
    return d, {s["code"]: s for s in d.get("standards") or []}


def dok_matched_depth(pool):
    """The largest set of items on one standard sharing a DOK level."""
    d = collections.Counter(i.get("dokLevel") for i in pool)
    return max(d.values()) if d else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-form", type=int, default=2,
                    help="MCQ items per standard per form (the checklist's one decision)")
    a = ap.parse_args()
    target = FORMS * a.per_form

    banks = {}
    for root in (os.path.join(itemio.BANK_ROOT, "items"),):
        for sub in sorted(os.listdir(root)) if os.path.isdir(root) else []:
            banks[sub] = itemio.load_dir(os.path.join(root, sub))

    print(f"SIX-COURSE SCOPE — {FORMS} parallel forms, {a.per_form} item(s) per standard per "
          f"form (target depth {target} DOK-matched)\n")
    print(f"{'course':<30}{'prefix':<8}{'stds':>6}{'bank':>8}{'ready':>8}{'to author':>11}")
    tot_std = tot_author = tot_ready = 0
    for slug in COURSES:
        doc, stds = standards_of(slug)
        pre = doc.get("standardsPrefix") or "?"
        items = [i for i in banks.get(slug, [])
                 if itemio.aligned(i) and i.get("itemType") in ("mcq", "multiple-select")]
        pool = collections.defaultdict(list)
        for it in items:
            hay = alignment.subject_text(it)
            for c in it.get("standardCodes") or []:
                t = (stds.get(c) or {}).get("text")
                if t and alignment.relevant_to(hay, t):
                    pool[c].append(it)
        ready = sum(1 for c in stds if dok_matched_depth(pool.get(c, [])) >= target)
        author = sum(max(0, target - dok_matched_depth(pool.get(c, []))) for c in stds)
        tot_std += len(stds); tot_author += author; tot_ready += ready
        print(f"{doc.get('title', slug)[:29]:<30}{pre:<8}{len(stds):>6}{len(items):>8}"
              f"{ready:>8}{author:>11,}")
    print(f"{'TOTAL':<38}{tot_std:>6}{'':>8}{tot_ready:>8}{tot_author:>11,}")
    print(f"\n{tot_ready}/{tot_std} standard(s) can already fill {FORMS} parallel forms; "
          f"{tot_author:,} MCQ item(s) still to author.")

    # The stimulus gap is part of the scope, not a footnote.
    import re
    rx = re.compile(r"use the (image|photograph|cartoon|chart|graph|map|table)", re.I)
    phantom = carried = 0
    for name, items in banks.items():
        for i in items:
            if not itemio.servable(i):
                continue
            if i.get("image"):
                carried += 1
            elif rx.search(i.get("stem") or ""):
                phantom += 1
    print(f"\nstimulus: {carried} item(s) carry one; {phantom} instruct the student to use a "
          f"stimulus that is not there")
    return 0


if __name__ == "__main__":
    sys.exit(main())
