#!/usr/bin/env python3
"""Apply authored rubrics from a committed authoring record.

Same discipline as apply_authoring.py: the rubric is DATA in authoring/, so a
reviewer reads what was written rather than the script that wrote it. Refuses
before writing anything if a rubric is malformed, because a partial content
write is worse than none.

Every applied item is marked requiresHistorianReview — a rubric band asserts
what a historically strong answer contains, which is a claim about the history.

Usage: python3 tools/apply_rubrics.py authoring/rubrics-forms.json [--apply]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import binding as binding_mod
import itemio

EXTENDED = {"constructed-response", "document-based"}


def validate(rubrics, by_id):
    problems = []
    for iid, r in rubrics.items():
        it = by_id.get(iid)
        if not it:
            problems.append(f"{iid}: not in the bank")
            continue
        if it.get("itemType") not in EXTENDED:
            problems.append(f"{iid}: itemType {it.get('itemType')!r} takes no rubric")
        pts, crit = r.get("scorePoints"), r.get("criteria") or []
        if not isinstance(pts, int) or pts < 1:
            problems.append(f"{iid}: scorePoints {pts!r} is not a scale")
            continue
        if {c.get("points") for c in crit} != set(range(pts + 1)):
            problems.append(f"{iid}: bands are {sorted(c.get('points') for c in crit)}, "
                            f"not 0-{pts}")
        for c in crit:
            d = (c.get("descriptor") or "").strip()
            # The ZERO band is legitimately short: "No response, or off-topic."
            # is the whole descriptor and needs no distinguishing. Requiring 40
            # characters there refused four correctly-written rubrics — an alarm
            # firing on the harmless, which trains you to pass --force.
            floor = 1 if c.get("points") == 0 else 40
            if len(d) < floor:
                problems.append(f"{iid}/{c.get('points')}: descriptor is {len(d)} chars — "
                                f"too short to distinguish this band from the next")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("record")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    b = binding_mod.load()
    print(b.declaration())

    with open(a.record, encoding="utf-8") as fh:
        rec = json.load(fh)
    rubrics = rec["rubrics"]
    items = itemio.load_dir(b.output_dir)
    by_id = {i["id"]: i for i in items}

    if not rubrics:
        print("EMPTY RECORD — refusing to report a successful application of nothing")
        return 1
    problems = validate(rubrics, by_id)
    if problems:
        print(f"\nREFUSED — {len(problems)} problem(s); nothing written:")
        for p in problems:
            print("  -", p)
        return 1

    print(f"\n{len(rubrics)} rubric(s) validate against the bank")
    for iid, r in rubrics.items():
        print(f"  [{iid}] {r['scorePoints']}-point, {len(r['criteria'])} bands, "
              f"{by_id[iid].get('itemType')}")
    if not a.apply:
        print("\nDRY RUN — pass --apply to write")
        return 0

    wrote = 0
    for path in sorted({i["_file"] for i in items if i["id"] in rubrics}):
        full = os.path.join(itemio.BANK_ROOT, path)
        with open(full, encoding="utf-8") as fh:
            doc = json.load(fh)
        recs = doc if isinstance(doc, list) else (doc.get("items") or doc.get("questions") or [])
        for r in recs:
            if r.get("id") in rubrics:
                src = dict(rubrics[r["id"]])
                src.pop("stem", None)
                r["rubric"] = src
                r["requiresHistorianReview"] = True
                wrote += 1
        with open(full, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
    print(f"\nwrote {wrote} rubric(s), each flagged requiresHistorianReview")
    return 0


if __name__ == "__main__":
    sys.exit(main())
