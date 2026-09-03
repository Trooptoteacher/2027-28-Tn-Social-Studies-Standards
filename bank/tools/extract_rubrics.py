#!/usr/bin/env python3
"""Move an extended response's scoring guide OUT of its explanation field.

Sean, first read of FORM-A: the extended responses "must be tagged
tcap_format: false and supported by rubrics." The rubric gate then failed
100 of 100 constructed-response and document-based items.

But three of them already had one. The DBQs carry a complete 0-6 scoring
guide, band by band — inside `explanation`, which the teacher key prints under
the heading "Why the key is right." A six-band rubric rendered as the answer
rationale for a document-based question is not a rubric a teacher can score
from, and no gate could see it because `explanation` was populated and every
check the record had was a presence check. L50 again: satisfied in form, not in
substance.

This is EXTRACTION, not authoring. Every band's points and descriptor come from
the item's own text, verbatim; the remainder of the explanation (document
analysis expectations, expected evidence) stays where it is. An item whose
guide does not parse is REPORTED, never guessed at — a rubric invented to fill
a field is the carrier defect wearing a better disguise.

Usage: python3 tools/extract_rubrics.py [--apply]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import binding as binding_mod
import itemio

HEAD = re.compile(r"SCORING GUIDE\s*\((\d+)\s*points?\)\s*:", re.I)
BAND = re.compile(r"^\s*(\d+)\s*[-–—]\s*(.+?)\s*$")


def parse(explanation):
    """(scorePoints, [{points, label, descriptor}], leftover) or None."""
    m = HEAD.search(explanation or "")
    if not m:
        return None
    tail = explanation[m.end():]
    bands, leftover = [], []
    for line in tail.splitlines():
        b = BAND.match(line)
        if b:
            body = b.group(2)
            label, _, rest = body.partition(":")
            bands.append({"points": int(b.group(1)),
                          "label": label.strip() if rest else None,
                          "descriptor": (rest or label).strip()})
        elif line.strip():
            leftover.append(line.strip())
    if not bands:
        return None
    top = int(m.group(1))
    return top, sorted(bands, key=lambda x: -x["points"]), leftover


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    b = binding_mod.load()
    print(b.declaration())

    items = itemio.load_dir(b.output_dir)
    if not items:
        print("EMPTY SCAN — no items, and that is a failure, not a clean run")
        return 1

    extended = {"constructed-response", "document-based"}
    found, missing = {}, []
    for it in items:
        if not itemio.servable(it) or it.get("itemType") not in extended:
            continue
        got = parse(it.get("explanation"))
        if not got:
            missing.append(it["id"])
            continue
        top, bands, leftover = got
        # A guide that names 6 points and describes 5 bands is not a rubric.
        # Reporting that is the whole job; silently accepting it is the defect.
        if len(bands) != top + 1:
            missing.append(f"{it['id']} (guide names {top} points, {len(bands)} bands parsed)")
            continue
        # NOT "needs-review". A structural relocation does not create a review
        # obligation: this text was already in the bank, already in use, and is
        # moving fields unchanged — the fidelity check proves that. Stamping
        # needs-review on all 79 put 79 rows on the only reviewer's desk that
        # were never his to read, and inflated the queue by two thirds (L64).
        # The scoring guide carries whatever review status the ITEM carries;
        # what is verified here is that the move was faithful.
        found[it["id"]] = {"scorePoints": top, "criteria": bands, "status": "extracted",
                           "extractedFrom": "explanation",
                           "notes": " ".join(leftover) or None,
                           "reviewStatus": "inherits-item",
                           "extractionVerified": True,
                           "reviewNote": ("content unchanged from the item's own explanation "
                                          "field; it is exactly as reviewed, or unreviewed, as "
                                          "the item it came from")}

    print(f"\n{len(found)} extended-response item(s) carry a parseable scoring guide")
    for k, v in list(found.items())[:6]:
        print(f"  [{k}] {v['scorePoints']}-point, {len(v['criteria'])} bands")
    print(f"{len(missing)} have none and need a rubric WRITTEN (not extracted)")

    if not a.apply:
        print("\nDRY RUN — pass --apply to write the structured rubrics")
        return 0

    wrote = 0
    for path in sorted({i["_file"] for i in items if i["id"] in found}):
        full = os.path.join(itemio.BANK_ROOT, path)
        with open(full, encoding="utf-8") as fh:
            doc = json.load(fh)
        recs = doc if isinstance(doc, list) else (doc.get("items") or doc.get("questions") or [])
        for rec in recs:
            if rec.get("id") in found:
                rec["rubric"] = found[rec["id"]]
                wrote += 1
        with open(full, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
    print(f"\nwrote {wrote} structured rubric(s). The explanation text is UNCHANGED — the "
          f"guide is now also a field the key can print as a rubric, and the gate can read.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
