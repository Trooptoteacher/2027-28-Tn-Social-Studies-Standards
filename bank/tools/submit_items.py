#!/usr/bin/env python3
"""Admit generated items into the bank — only if every gate passes FIRST.

This is the difference between the old bank and this one. The old bank was
generated against a real specification: IRT parameters on 100% of items, DOK
levels on 100%, blueprint structure, item-writing conventions. Every parameter
was present. And the key was still the longest choice 53% of the time, 920
explanations still restated the key, and 8.7% of items had a DOK rationale.

The spec was satisfied in FORM and not in SUBSTANCE, and nothing measured the
difference. So generation is not reviewed after the fact here — it is gated
before admission, and a draft that fails does not enter the bank at all.

Usage: python3 tools/submit_items.py generation/US.05.draft.json [--apply]
"""
from __future__ import annotations

import argparse, collections, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import alignment
import binding as binding_mod
import itemio
from gates import content, record

# Item-level gates a draft must clear before admission. Bank- and form-level
# gates are not applicable to a draft in isolation.
ADMISSION_GATES = [
    record.gate_record_complete,
    record.gate_binding,
    record.gate_key_integrity,
    record.gate_distractor_coverage,
    record.gate_truncation,
    content.gate_standard_relevance,
    content.gate_translation_claim,
    content.gate_explanation_quality,
    content.gate_embedded_key,
    content.gate_citation_integrity,
    content.gate_duplicate_stems,
    content.gate_choice_length_cue,
    # review-provenance is deliberately NOT here: a draft has no authoring
    # provenance until it is admitted, and submit_items sets
    # requiresHistorianReview on everything it admits. It runs on the bank.
]


def dedupe_against_bank(draft, bank):
    """A generated item must not repeat a stem the bank already carries."""
    import re
    norm = lambda s: re.sub(r"[^a-z0-9 ]", "", (s or "").lower()).strip()
    have = {norm(i.get("stem")): i["id"] for i in bank if itemio.servable(i)}
    return [(d["id"], have[norm(d.get("stem"))]) for d in draft
            if norm(d.get("stem")) in have]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft"); ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    b = binding_mod.load(); print(b.declaration())

    with open(a.draft, encoding="utf-8") as fh:
        draft = json.load(fh)["items"]
    if not draft:
        print("EMPTY DRAFT — refusing to report a successful submission of nothing.")
        return 1
    for d in draft:
        d.setdefault("_file", os.path.relpath(a.draft, itemio.BANK_ROOT))

    codes = sorted({c for d in draft for c in (d.get("standardCodes") or [])})
    b.assert_codes(codes, where=f"draft {os.path.basename(a.draft)}")
    for d in draft:
        b.assert_year(d.get("standardsYear"), where=f"draft item {d.get('id')}")
    print(f"\nbinding assertion passed — {len(draft)} item(s), standards {codes}")

    bank = itemio.load_dir(b.output_dir)
    existing = {i["id"] for i in bank}
    clashes = [d["id"] for d in draft if d["id"] in existing]
    dupes = dedupe_against_bank(draft, bank)

    results = [g(draft, b) for g in ADMISSION_GATES]
    print()
    failed = []
    for r in results:
        print(r.report(limit=4))
        if not r.counts_as_pass and not r.inapplicable:
            failed.append(r)
    if clashes:
        print(f"\n[FAIL] id-collision — {len(clashes)} id(s) already in the bank: {clashes[:5]}")
        failed.append("id-collision")
    if dupes:
        print(f"\n[FAIL] stem already in the bank — {len(dupes)}:")
        for new, old in dupes[:4]:
            print(f"          {new} repeats {old}")
        failed.append("stem-duplicate")

    print()
    if failed:
        print(f"REFUSED — {len(failed)} gate(s) failed. The draft does NOT enter the bank.")
        print("Fix the findings above and resubmit. Generation is gated before admission, "
              "not reviewed after it.")
        return 1
    print(f"All {len(results)} admission gates pass.")

    if not a.apply:
        print("DRY RUN — nothing admitted. Re-run with --apply.")
        return 0

    by_std = collections.defaultdict(list)
    for d in draft:
        d.pop("_file", None)
        d.setdefault("provenance", {})["generated"] = {
            "mode": "standard-first",
            "brief": f"generation/{d['standardCodes'][0]}.brief.md",
            "note": "authored FROM the standard; alignment true by construction",
        }
        d["requiresHistorianReview"] = True
        by_std[d["standardCodes"][0]].append(d)
    for code, rows in by_std.items():
        dst = os.path.join(b.output_dir, code)
        os.makedirs(dst, exist_ok=True)
        p = os.path.join(dst, "generated.json")
        doc = {"items": []}
        if os.path.exists(p):
            with open(p, encoding="utf-8") as fh:
                doc = json.load(fh)
        doc.update({"course": b.course, "standardsYear": b.standards_year,
                    "standard": code, "status": "authored",
                    "disclosure": b.disclosure_line})
        doc["items"] = doc.get("items", []) + rows
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
        print(f"  admitted {len(rows)} item(s) -> {os.path.relpath(p, itemio.BANK_ROOT)}")
    print("\nEvery admitted item carries requiresHistorianReview. The gates verified the "
          "ITEM; only a person can verify the HISTORY.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
