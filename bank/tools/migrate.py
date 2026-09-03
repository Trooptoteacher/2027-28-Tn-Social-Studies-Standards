#!/usr/bin/env python3
"""Migrate a 2026-27 item bank onto the 2027-28 standards.

A code is NOT a stable identifier between the two years: 84 of the 94 US codes
changed meaning. So nothing is carried forward BY CODE. Every item is routed
through the published crosswalk and lands in one of three places:

  migrated     the standard's content checklist is intact for this item
  provisional  recoded, but something needs a human: the standard's verb rose,
               or elements were added that this item does not yet cover
  quarantined  the standard retired, or THIS ITEM tests an element the 2027-28
               standard dropped — NOT servable, NOT coverage

Routing is by ELEMENT, not by text similarity. Measurement showed the
character ratio is anti-correlated with alignment: US.16->US.17 scores 0.79
and is a pure bullet reorder, while US.12 scores 0.89 having deleted the
Clayton Antitrust Act of 1914. See tools/alignment.py.

Quarantine is the point. An item whose standard moved out from under it is not
a coverage number, and calling it one is how a bank ends up testing the wrong
standards while every structural gate passes.

The old code is never silently dropped: it moves to provenance.priorStandardCodes.

Usage: python3 tools/migrate.py <source-bank-dir> [--apply]
"""
from __future__ import annotations

import argparse
import collections
import csv
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import alignment
import binding as binding_mod
import itemio

PRIOR_YEAR = "2026-27"

# Old bank's tier vocabulary conflates audience with content type. Map to
# AUDIENCE, conservatively: anything not explicitly student-facing becomes
# teacher-side until a human says otherwise. Answer keys are teacher-side only.
TIER_MAP = {"student": "student", "teacher": "teacher", "retired": "retired",
            "primary-source": "teacher", "standard": "teacher", "stimulus-based": "teacher"}
TYPE_MAP = {"mcq": "mcq", "MCQ": "mcq", "constructed-response": "constructed-response",
            "document-based": "document-based", "extended-response": "extended-response",
            "short-answer": "short-answer"}


def load_crosswalk(path):
    by26 = collections.defaultdict(list)
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["code_2026_27"]:
                by26[r["code_2026_27"]].append(r)
    return by26


def item_text(old):
    """What the item ASKS and KEYS — stem, correct choice, key explanation.

    Distractors are deliberately excluded. A wrong choice mentioning a dropped
    element is not evidence the item tests it.
    """
    bits = [old.get("stem") or "", old.get("explanation") or ""]
    key = old.get("correctAnswer")
    for c in (old.get("choices") or []):
        if isinstance(c, dict) and c.get("id") == key:
            bits.append(c.get("text") or "")
    return " ".join(bits)


def route(old, by26):
    """Return (new_codes, disposition, reasons, review).

    Most conservative disposition wins. The old code is never dropped; it moves
    to provenance.
    """
    codes = old.get("standardCodes") or []
    text = item_text(old)
    new, reasons, review = [], [], {}
    rank = {"migrated": 0, "provisional": 1, "quarantined": 2}
    worst = "migrated"

    def worsen(v):
        nonlocal worst
        if rank[v] > rank[worst]:
            worst = v

    for c in codes:
        rows = by26.get(c)
        if not rows:
            reasons.append(f"{c}: not in crosswalk"); worsen("quarantined"); continue
        for r in rows:
            tgt, disp = r["code_2027_28"], r["disposition"]
            if not tgt or disp == "retired":
                reasons.append(f"{c}: {disp} — no 2027-28 home"); worsen("quarantined"); continue
            d = alignment.delta(r["text_2026_27"], r["text_2027_28"])
            hits = alignment.tests_dropped_element(text, d["dropped"])
            if hits:
                reasons.append(f"{c}->{tgt}: item tests element(s) dropped from the "
                               f"2027-28 standard: {hits}")
                review.setdefault("droppedElementsTested", []).extend(hits)
                worsen("quarantined")
                continue
            new.append(tgt)
            if d["verbChanged"]:
                review["verbChange"] = f"{d['oldVerb']} -> {d['newVerb']}"
                if d["verbRaised"]:
                    review["dokReviewRequired"] = True
                    reasons.append(f"{c}->{tgt}: standard verb RAISED "
                                   f"{d['oldVerb']}->{d['newVerb']}; item may be under-levelled")
                    worsen("provisional")
                else:
                    reasons.append(f"{c}->{tgt}: verb changed {d['oldVerb']}->{d['newVerb']}")
            if d["added"]:
                review.setdefault("elementsAddedToStandard", []).extend(d["added"])
                reasons.append(f"{c}->{tgt}: standard ADDED {d['added']} — coverage gap "
                               f"at the standard, not a defect in this item")
            if not d["verbChanged"] and not d["added"]:
                reasons.append(f"{c}->{tgt}: checklist intact ({len(d['retained'])} element(s))")
    return sorted(set(new)), worst, reasons, review


def convert(old, new_codes, disposition, reasons, review, b):
    """Rebuild the record on the new schema. Absent fields stay absent and are
    reported — never invented."""
    ch = []
    for c in (old.get("choices") or []):
        if not isinstance(c, dict):
            continue
        ch.append({"id": c.get("id"), "text": c.get("text"), "textEs": c.get("textEs"),
                   # These two do not exist in the 2026-27 bank. Left null on purpose:
                   # the distractor-coverage gate reports them as the gap they are.
                   "explanation": None, "misconception": None})
    return {
        "id": old.get("id"),
        "stem": old.get("stem"), "stemEs": old.get("stemEs"),
        "itemType": TYPE_MAP.get(old.get("itemType"), old.get("itemType")),
        "correctAnswer": old.get("correctAnswer"),
        "choices": ch,
        "dokLevel": old.get("dokLevel"),
        "dokRationale": old.get("dokRationale"),
        "standardCodes": new_codes,
        "standardsYear": b.standards_year,
        "reportingCategory": None,
        "reportingCategorySource": "UNMAPPED",
        "explanation": old.get("explanation"), "explanationEs": old.get("explanationEs"),
        "translationStatus": old.get("translationStatus"),
        "irtParameters": old.get("irtParameters"),
        # Parameters that have never met a student are estimates.
        "calibrationStatus": "pre-field-test",
        "bankTier": TIER_MAP.get(old.get("bankTier"), "teacher"),
        "status": disposition,
        "image": None,
        "provenance": {
            "migratedFrom": old.get("_file"),
            "priorStandardsYear": PRIOR_YEAR,
            "priorStandardCodes": old.get("standardCodes"),
            "priorBankTier": old.get("bankTier"),
            "crosswalkReasons": reasons,
            "alignmentReview": review or None,
        },
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--apply", action="store_true", help="write files (default: dry run)")
    a = ap.parse_args(argv)

    b = binding_mod.load()
    print(b.declaration())
    print("Routing by ELEMENT-level alignment, not text similarity "
          "(see tools/alignment.py).\n")

    by26 = load_crosswalk(b.crosswalk_file)
    src = itemio.load_dir(a.source)
    if not src:
        print(f"EMPTY SCAN — no items found under {a.source}. Refusing to report a "
              f"successful migration of nothing.")
        return 1

    buckets = collections.defaultdict(list)
    for old in src:
        new_codes, disp, reasons, review = route(old, by26)
        if disp != "quarantined" and not new_codes:
            disp = "quarantined"
        buckets[disp].append(convert(old, new_codes, disp, reasons, review, b))

    # THE ASSERTION. Every generator fails if a code outside the declared
    # prefix appears anywhere in the output — including quarantine.
    for disp, rows in buckets.items():
        codes = [c for r in rows for c in r["standardCodes"]]
        b.assert_codes(codes, where=f"migration output ({disp})")
        for r in rows:
            b.assert_year(r["standardsYear"], where=f"migration output ({disp}) item {r['id']}")
    print(f"Binding assertion passed on {sum(len(v) for v in buckets.values())} migrated records.\n")

    total = sum(len(v) for v in buckets.values())
    for disp in ("migrated", "provisional", "quarantined"):
        n = len(buckets[disp])
        print(f"  {disp:12s} {n:5d}  ({100*n/total:4.1f}%)")

    live = buckets["migrated"] + buckets["provisional"]
    covered = {c for r in live for c in r["standardCodes"]}
    allc = b.valid_codes()
    print(f"\n  standards with >=1 servable migrated item: {len(covered)}/{len(allc)}")
    print(f"  standards receiving NOTHING: {len(allc - covered)}")
    print("   ", ", ".join(sorted(allc - covered)))

    gaps = {"no dokRationale": sum(1 for r in live if not r["dokRationale"]),
            "no stemEs": sum(1 for r in live if not r["stemEs"]),
            "no explanationEs": sum(1 for r in live if not r["explanationEs"]),
            "distractors with no explanation":
                sum(1 for r in live for c in r["choices"]
                    if c["id"] != r["correctAnswer"] and not c["explanation"])}
    print("\n  Authoring debt carried in by the migration (servable items only):")
    for k, v in gaps.items():
        print(f"    {v:6d}  {k}")

    if not a.apply:
        print("\nDRY RUN — nothing written. Re-run with --apply.")
        return 0

    for disp, rows in buckets.items():
        root = b.quarantine_dir if disp == "quarantined" else b.output_dir
        by_code = collections.defaultdict(list)
        for r in rows:
            by_code[r["standardCodes"][0] if r["standardCodes"] else "_unrouted"].append(r)
        for code, rs in by_code.items():
            d = os.path.join(root, code)
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, f"{disp}.json"), "w", encoding="utf-8") as fh:
                json.dump({"course": b.course, "standardsYear": b.standards_year,
                           "standard": code, "status": disp,
                           "disclosure": b.disclosure_line, "items": rs},
                          fh, indent=2, ensure_ascii=False)
    print(f"\nWrote {total} records to {os.path.relpath(b.output_dir, itemio.BANK_ROOT)} "
          f"and {os.path.relpath(b.quarantine_dir, itemio.BANK_ROOT)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
