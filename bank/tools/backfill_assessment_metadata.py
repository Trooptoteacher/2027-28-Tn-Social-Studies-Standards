#!/usr/bin/env python3
"""Stamp the three fields the first teacher read of FORM-A found missing.

Sean Reynolds, reading the rendered form: "this is a mixed classroom
assessment, not a TCAP-field-testable form. Six extended responses/DBQs ...
must be tagged tcap_format: false and supported by rubrics; the 12 MC items
also lack the required standards, DOK/Hess, distractor, bias, citation, and
IRT metadata in the supplied form."

Measured before writing anything: tcapFormat on 0 of 3,958 servable items,
rubric on 0 of 100 constructed-response/document-based items, bias review on
0 of everything. Not "thin" — ABSENT, on every item, while every structural
gate read green. Same shape as L50: the spec was satisfied in form and not in
substance, and nothing measured the difference.

This writes only STRUCTURAL fields — a boolean, a review-status stub, a
citation carrier. It never touches a stem, a choice, an explanation or a
rubric's content: that is authoring, and bulk edits to student-facing text are
how the corrupted citations and the swallowed stems entered this bank (L25).

Usage: python3 tools/backfill_assessment_metadata.py [--apply]
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

POLICY = os.path.join(itemio.BANK_ROOT, "policy", "tcap-format.json")


def policy():
    with open(POLICY, encoding="utf-8") as fh:
        return json.load(fh)


def tcap_format(item, pol) -> bool:
    """FALSE unless a human affirmed it against a policy that exists.

    There is no path to True in this tool. Deriving True from the presence of
    fields would be the machine affirming its own field-testability, which is
    the compliance claim the policy exists to forbid.
    """
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    b = binding_mod.load()
    print(b.declaration())
    pol = policy()
    print(f"policy: {POLICY} v{pol['policyVersion']} — sourceOfRecord: {pol['sourceOfRecord']}")
    print(f"        {pol['notTdoe']}\n")

    never = set(pol["neverTcapFormat"]["itemTypes"])
    counts = collections.Counter()
    for root in (b.output_dir, b.quarantine_dir):
        items = itemio.load_dir(root)
        if not items:
            print(f"EMPTY SCAN — nothing under {root}")
            continue
        for path in sorted({i["_file"] for i in items}):
            full = os.path.join(itemio.BANK_ROOT, path)
            with open(full, encoding="utf-8") as fh:
                doc = json.load(fh)
            recs = doc if isinstance(doc, list) else (doc.get("items") or doc.get("questions") or [])
            for rec in recs:
                if "tcapFormat" not in rec:
                    rec["tcapFormat"] = tcap_format(rec, pol)
                    counts["tcapFormat"] += 1
                if rec["tcapFormat"] is False and "tcapFormatReason" not in rec:
                    rec["tcapFormatReason"] = (
                        "item type is never TCAP-format under policy v%d" % pol["policyVersion"]
                        if rec.get("itemType") in never
                        else "not affirmed — no human has judged this item field-testable")
                    counts["tcapFormatReason"] += 1
                if "biasReview" not in rec:
                    rec["biasReview"] = {"status": "not-started", "reviewer": None,
                                         "reviewedAt": None, "notes": None}
                    counts["biasReview"] += 1
                if rec.get("itemType") in never and "rubric" not in rec:
                    # A CARRIER, not a rubric. An empty rubric must never read
                    # as a written one, so the gate fails on scorePoints: null.
                    rec["rubric"] = {"scorePoints": None, "criteria": [], "status": "not-written"}
                    counts["rubric(carrier)"] += 1
            if a.apply:
                with open(full, "w", encoding="utf-8") as fh:
                    json.dump(doc, fh, indent=2, ensure_ascii=False)

    print("fields stamped" + ("" if a.apply else "  (DRY RUN — pass --apply to write)"))
    for k, v in counts.most_common():
        print(f"   {v:5d}  {k}")
    print("\nNo stem, choice, explanation or rubric CONTENT was written. tcapFormat is False "
          "on every item: nothing is field-testable until a person says so.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
