#!/usr/bin/env python3
"""Hold items whose citation names a repository where a publication belongs.

Content is retained in place; the item stops being servable until a person
confirms the real publication. An unsourced item is worse than a missing one,
and these are the DBQ and constructed-response items an adoption reviewer
reads first.

Nothing is rewritten. The correct publication is PROPOSED in a review sheet
and never silently substituted — this session cannot reach loc.gov to verify,
and a confidently wrong citation is exactly the defect being fixed.

Usage: python3 tools/hold_citations.py [--apply]
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
from gates import content

# Proposed corrections, each stated as a claim a person must confirm.
PROPOSALS = [
    (re.compile(r"Negro Speaks of Rivers", re.I),
     "The Crisis (NAACP), June 1921",
     "The date already in the item is June 1921 and The Crisis is the NAACP magazine "
     "whose records the replacement string names — consistent with a title-for-repository "
     "substitution."),
    (re.compile(r'["“]I,\s*Too', re.I),
     "Survey Graphic, March 1925 (the 'Harlem: Mecca of the New Negro' number)",
     "The item's own date is March 1925."),
    (re.compile(r"Jazzonia", re.I),
     "The Crisis (NAACP), August 1923",
     "The item's own date is August 1923; The Weary Blues (1926) is the later collection, "
     "which the item already names separately."),
    (re.compile(r"Garvey[^\n]{0,80}(?:Liberty Hall|Africa for the Africans)", re.I),
     "Negro World (UNIA newspaper)",
     "The item still carries the dangling word 'newspaper' after the repository string."),
]


def citation_line(blob):
    """The line carrying the broken attribution — the only text a proposal may
    be matched against. Matching the whole item tagged a Marcus Garvey speech
    with a Langston Hughes publication, because the Garvey excerpt contains the
    words "I, too" in its prose."""
    m = re.search(r"[^\n]*(?:loc\.gov|archives\.gov|published in)[^\n]*", blob or "")
    return m.group(0) if m else ""


def proposal(blob):
    line = citation_line(blob)
    if not line:
        return None, None
    for rx, pub, why in PROPOSALS:
        if rx.search(line):
            return pub, why
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    b = binding_mod.load()
    print(b.declaration())

    items = itemio.load_dir(b.output_dir)
    r = content.gate_citation_integrity(items, b)
    ids = {str(f).split(" ")[0].rstrip(":") for f in r.findings}
    by_id = {i["id"]: i for i in items}
    if not ids:
        print("No corrupted citations found."); return 0

    sheet = []
    print(f"\n{len(ids)} item(s) held for citation verification:\n")
    for iid in sorted(ids):
        it = by_id.get(iid, {})
        blob = " ".join([it.get("stem") or "", it.get("explanation") or "",
                         str(it.get("correctAnswer") or "")])
        pub, why = proposal(blob)
        m = re.search(r"[^\n]*(?:loc\.gov|archives\.gov|published in)[^\n]*", blob)
        print(f"  {iid}  [{', '.join(it.get('standardCodes') or [])}]")
        print(f"     reads    : {(m.group(0).strip() if m else '')[:120]}")
        print(f"     PROPOSED : {pub or '(needs research)'}")
        sheet.append({"id": iid, "standards": it.get("standardCodes"),
                      "currentCitation": (m.group(0).strip() if m else None),
                      "proposedPublication": pub, "basis": why,
                      "status": "HELD — verify against the source before accepting"})

    out = os.path.join(itemio.BANK_ROOT, "reviewed", "citation-corrections.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"$comment": "Proposed citation corrections. NOT applied. Each names a "
                               "publication a person must confirm against the source before "
                               "the item returns to service.",
                   "items": sheet}, fh, indent=2, ensure_ascii=False)
    print(f"\nwrote {os.path.relpath(out, itemio.BANK_ROOT)}")

    if not a.apply:
        print("\nDRY RUN — nothing held. Re-run with --apply.")
        return 0
    held = 0
    for path in sorted({i["_file"] for i in items if i["id"] in ids}):
        full = os.path.join(itemio.BANK_ROOT, path)
        with open(full, encoding="utf-8") as fh:
            doc = json.load(fh)
        for rec in doc.get("items", []):
            if rec.get("id") in ids:
                rec["citationStatus"] = "corrupted-held"
                rec["status"] = "quarantined"
                rec.setdefault("provenance", {})["citationHold"] = {
                    "reason": "citation names a repository where a publication belongs",
                    "proposedPublication": proposal(
                        " ".join([rec.get("stem") or "", rec.get("explanation") or "",
                                  str(rec.get("correctAnswer") or "")]))[0],
                    "note": "content retained; not servable until a person verifies the source",
                }
                held += 1
        with open(full, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
    print(f"\nheld {held} item(s). Content retained; not servable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
