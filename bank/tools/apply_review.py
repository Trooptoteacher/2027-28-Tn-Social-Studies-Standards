#!/usr/bin/env python3
"""Stamp human review onto the items an approval record actually names.

Approval is a fact about specific items on a specific date by a specific
person. Recording it in prose, or as something the build "knows", is how an
unreviewed item ends up looking reviewed. The record is committed data; this
only transcribes it onto the items it names.

Usage: python3 tools/apply_review.py <record-id> [--apply]
"""
from __future__ import annotations

import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import binding as binding_mod
import itemio

RECORD = os.path.join(itemio.BANK_ROOT, "reviewed", "historian-approvals.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("record_id"); ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    b = binding_mod.load(); print(b.declaration())
    with open(RECORD, encoding="utf-8") as fh:
        doc = json.load(fh)
    rec = next((r for r in doc["approvals"] if r["record"] == a.record_id), None)
    if not rec:
        print(f"no approval record named {a.record_id!r}"); return 1

    items = itemio.load_dir(b.output_dir)
    by_id = {i["id"]: i for i in items}
    named = rec["items"]
    missing = [i for i in named if i not in by_id]
    unauthored = [i for i in named
                  if not (by_id.get(i, {}).get("provenance") or {}).get("authoring")]
    if missing:
        print(f"REFUSED: {len(missing)} named item(s) are not in the bank: {missing[:5]}")
        return 1
    if unauthored:
        print(f"REFUSED: {len(unauthored)} named item(s) carry no authoring provenance — an "
              f"approval must name what was actually authored: {unauthored[:5]}")
        return 1
    print(f"\n{rec['reviewer']} ({rec['role']}), {rec['date']}: {rec['statement']!r}")
    print(f"  covers      : {len(rec['scope']['covers'])} categories over {len(named)} items")
    for x in rec["scope"]["doesNotCover"]:
        print(f"  NOT covered : {x[:100]}")
    if not a.apply:
        print("\nDRY RUN — nothing stamped. Re-run with --apply."); return 0

    n = 0
    for path in sorted({by_id[i]["_file"] for i in named}):
        full = os.path.join(itemio.BANK_ROOT, path)
        with open(full, encoding="utf-8") as fh:
            d = json.load(fh)
        for r in d.get("items", []):
            if r.get("id") in named:
                r["historianReview"] = {"status": "approved", "record": rec["record"],
                                        "reviewer": rec["reviewer"], "date": rec["date"]}
                r["requiresHistorianReview"] = False
                n += 1
        with open(full, "w", encoding="utf-8") as fh:
            json.dump(d, fh, indent=2, ensure_ascii=False)
    print(f"\nstamped {n} item(s). translationStatus untouched — see doesNotCover.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
