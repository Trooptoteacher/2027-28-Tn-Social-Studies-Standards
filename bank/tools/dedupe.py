#!/usr/bin/env python3
"""Retire duplicate stems. Nothing is deleted.

Two ids carrying one stem can land on the same form and are counted twice
toward coverage. The fix is to keep the RICHER copy and retire the other with
a pointer to its survivor — retired items stay in the bank, keep their content,
and are simply not servable. A duplicate is a filing problem, not a reason to
destroy authored work.

Richness, in order: alignment established > has a dokRationale > has both
bilingual fields > longer key explanation. Where copies sit on DIFFERENT
standards the survivor's standard is recorded on the retired copy, so a
cross-listing that mattered can be recovered.

Usage: python3 tools/dedupe.py [--apply]
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import binding as binding_mod
import itemio


def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", (s or "").lower()).strip()


def richness(i):
    return (itemio.aligned(i),
            bool((i.get("dokRationale") or "").strip()),
            bool((i.get("stemEs") or "").strip()) and bool((i.get("explanationEs") or "").strip()),
            len(i.get("explanation") or ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    b = binding_mod.load()
    print(b.declaration())

    items = [i for i in itemio.load_dir(b.output_dir) if itemio.servable(i)]
    if not items:
        print("EMPTY SCAN — nothing to deduplicate."); return 1
    groups = collections.defaultdict(list)
    for i in items:
        if (i.get("stem") or "").strip():
            groups[norm(i["stem"])].append(i)
    dups = {k: v for k, v in groups.items() if len(v) > 1}

    retire = {}
    cross = 0
    for k, group in dups.items():
        ranked = sorted(group, key=richness, reverse=True)
        keeper = ranked[0]
        stds = {c for i in group for c in (i.get("standardCodes") or [])}
        if len(stds) > 1:
            cross += 1
        for loser in ranked[1:]:
            retire[loser["id"]] = {
                "duplicateOf": keeper["id"],
                "survivorStandards": keeper.get("standardCodes"),
                "thisCopyWasFiledUnder": loser.get("standardCodes"),
                "note": "retired as a duplicate stem; content retained, not servable",
            }
    print(f"\n{len(dups)} duplicate group(s), {sum(len(v) for v in dups.values())} items")
    print(f"  {cross} group(s) span more than one standard")
    print(f"  retiring {len(retire)} copy(ies); keeping the richer one in each group")

    if not a.apply:
        print("\nDRY RUN — nothing changed. Re-run with --apply.")
        return 0

    changed = 0
    for path in sorted({i["_file"] for i in items}):
        full = os.path.join(itemio.BANK_ROOT, path)
        with open(full, encoding="utf-8") as fh:
            doc = json.load(fh)
        for rec in doc.get("items", []):
            if rec.get("id") in retire:
                rec["status"] = "retired"
                rec.setdefault("provenance", {})["duplicate"] = retire[rec["id"]]
                changed += 1
        with open(full, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
    print(f"\nretired {changed} duplicate copy(ies). Content retained in place.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
