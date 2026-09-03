#!/usr/bin/env python3
"""Make every translationStatus match what the Spanish fields actually contain.

DOWNGRADE ONLY. This never promotes an item to a better status — it cannot
tell a good translation from a lucky one — it only stops the bank claiming a
bilingual capability it does not have. A bilingual claim is an accessibility
claim, and 93 items claimed 'complete' while their Spanish was English with a
word swapped.

No Spanish is written or altered. Only the CLAIM changes.

Usage: python3 tools/fix_translation_claims.py [--apply]
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import binding as binding_mod
import itemio
from gates import content

# Evidence -> the strongest status the item may honestly claim.
CEILING = {"untranslated-copy": "not-started", "pseudo-translation": "needs-review"}
RANK = {"not-started": 0, "pending": 1, "needs-review": 2, "complete": 3}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    b = binding_mod.load()
    print(b.declaration())

    items = itemio.load_dir(b.output_dir)
    if not items:
        print("EMPTY SCAN — nothing to correct."); return 1

    moves = collections.Counter()
    plan = {}
    for it in items:
        if not itemio.servable(it):
            continue
        d = content.worst_translation_defect(it)
        if not d:
            continue
        claimed = it.get("translationStatus") or "not-started"
        ceiling = CEILING[d]
        if RANK.get(claimed, 0) > RANK[ceiling]:
            plan[it["id"]] = ceiling
            moves[(claimed, ceiling, d)] += 1

    print(f"\n{len(plan)} item(s) claim more than their Spanish supports:")
    for (was, now, why), n in moves.most_common():
        print(f"   {n:5d}  {was} -> {now}   ({why})")
    if not plan:
        print("   none — every claim already matches its evidence")
        return 0

    if not a.apply:
        print("\nDRY RUN — nothing changed. Re-run with --apply.")
        return 0

    changed = 0
    for path in sorted({i["_file"] for i in items if i["id"] in plan}):
        full = os.path.join(itemio.BANK_ROOT, path)
        with open(full, encoding="utf-8") as fh:
            doc = json.load(fh)
        for rec in doc.get("items", []):
            if rec.get("id") in plan:
                rec.setdefault("provenance", {})["translationClaimCorrected"] = {
                    "was": rec.get("translationStatus"), "now": plan[rec["id"]],
                    "basis": "Spanish fields measured; no Spanish text was written or altered",
                }
                rec["translationStatus"] = plan[rec["id"]]
                changed += 1
        with open(full, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
    print(f"\ncorrected {changed} claim(s). No Spanish text was written or altered.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
