#!/usr/bin/env python3
"""Write the generation brief for ONE standard — standard-first authoring.

The old bank was written item-first and filed against standards afterward,
which is why 42% of its items name nothing that identifies the standard they
sit under, and why an entire relevance-matching apparatus had to exist to find
out. Authoring FROM the standard makes alignment true by construction.

The brief carries everything an author needs and nothing they have to remember:
the standard verbatim, what identifies it, the tier's slots, the item-writing
constraints the gates will enforce, and the exact record shape to fill.

Usage: python3 tools/generation_brief.py US.05 [--tier selected-response]
"""
from __future__ import annotations

import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import alignment
import binding as binding_mod
import itemio

OUT = os.path.join(itemio.BANK_ROOT, "generation")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("standard"); ap.add_argument("--tier")
    a = ap.parse_args()
    b = binding_mod.load(); print(b.declaration())
    b.assert_codes([a.standard], where="generation brief")
    stds = b.standards()
    std = stds[a.standard]
    with open(b.blueprint_file, encoding="utf-8") as fh:
        form = json.load(fh)["form"]
    tier = next((t for t in form["tiers"] if t["id"] == a.tier), None) if a.tier else None

    # What already exists, so generation fills gaps rather than duplicating.
    have = [i for i in itemio.load_dir(b.output_dir)
            if a.standard in (i.get("standardCodes") or []) and itemio.aligned(i)]
    sigs = alignment.identifying_signals(std["text"])

    if not tier:
        # Highest tier the EXISTING pool cannot already fill — generate for that.
        import form_readiness as fr
        reached, _ = fr.reachable_tier(sorted(have, key=lambda i: i["id"]), form)
        idx = next((n for n, t in enumerate(form["tiers"]) if reached and t["id"] == reached["id"]),
                   len(form["tiers"]))
        tier = form["tiers"][max(idx - 1, 0)] if reached else form["tiers"][-1]

    L = []
    L.append(f"# Generation brief — {a.standard}\n")
    L.append(f"**Course** {b.course_title} · **Standards year** {b.standards_year} · "
             f"**Tier** `{tier['id']}` (DOK ceiling {tier['dokCeiling']})\n")
    L.append("## The standard, verbatim\n")
    L.append(f"> {std['text']}\n")
    L.append(f"*Era: {std.get('era','—')} · Strands: {', '.join(std.get('strand') or [])}*\n")

    L.append("## What identifies this standard\n")
    if sigs:
        L.append("Every generated item MUST name at least one of these in its **stem or its "
                 "correct answer**. This is checked at submission, not afterward.\n")
        for s in sorted(set(sigs)):
            L.append(f"- `{s}`")
    else:
        L.append("**This standard names nothing matchable.** Alignment cannot be verified "
                 "mechanically here — a human must confirm every item belongs. "
                 "(One of the 19 weakly identifiable standards.)")
    L.append("")

    L.append("## Slots to fill\n")
    L.append("| # | item type | DOK |\n|---|---|---|")
    for n, sl in enumerate(tier["slots"], 1):
        L.append(f"| {n} | {' or '.join(sl['types'])} | {sl['dok']} |")
    L.append("")

    L.append("## Constraints the gates enforce at submission\n")
    L.append("""
- **Alignment** — stem or key names an identifying signal above. Nothing else counts:
  not the distractors (they are deliberately wrong), not the explanation (it is authored).
- **Distractors** — every wrong choice carries its own `explanation` and a `misconception`
  naming the specific student error it catches. No two distractors on one item may name the
  same misconception. A distractor written only to be wrong is noise.
- **Choice length** — the key must NOT be reliably the longest option. Measured across the
  standard's items: key-is-longest between 15% and 35%. The migrated bank runs at 53%
  against 25% by chance, with a median margin of 17 characters, which a student can beat
  without reading the stem. Write distractors as specific as the key.
- **Key position** — spread across the set; the form builder balances the rendered letters.
- **DOK rationale** — required, and it is the check on the number. A DOK-2 label on a recall
  stem is the most common defect in this bank and the number alone never reveals it.
  DOK-4 is impossible in a four-option item: it needs a constructed or document-based response.
- **Explanation** — says WHY the key is right, never restates it. 920 items in the migrated
  bank open by repeating the correct answer verbatim.
- **Truncation** — nothing ends mid-sentence. A stem may end on a colon or dash (completion
  style); an explanation may not.
- **Citations** — name where a work was PUBLISHED, never where a scan lives. "The Crisis,
  June 1921", not "Library of Congress, NAACP Records (loc.gov)".
- **Bilingual** — `stemEs` / `explanationEs` / `textEs`. If it is not real Spanish, say so:
  `translationStatus` must match what the fields actually contain.
- **Calibration** — `calibrationStatus: "pre-field-test"`. Parameters that have never met a
  student are estimates.
""")
    L.append(f"## Existing items for {a.standard}\n")
    L.append(f"{len(have)} aligned item(s) already exist. Generate to FILL THE SLOTS above, "
             f"not to duplicate. Existing stems:\n")
    for i in sorted(have, key=lambda i: i["id"])[:12]:
        L.append(f"- `{i['id']}` ({i['itemType']} DOK{i['dokLevel']}) {(i.get('stem') or '')[:90]}")
    if len(have) > 12:
        L.append(f"- … and {len(have)-12} more")
    L.append("")

    L.append("## Record shape\n")
    L.append("Write `generation/" + a.standard + ".draft.json` as `{\"items\": [ … ]}`. "
             "Each item:\n")
    L.append("```json\n" + json.dumps({
        "id": f"{a.standard}-GEN-01", "stem": "…", "stemEs": "…",
        "itemType": "mcq", "correctAnswer": "B",
        "choices": [{"id": "A", "text": "…", "textEs": "…",
                     "explanation": "why this is wrong",
                     "misconception": "the specific error it catches"},
                    {"id": "B", "text": "…", "textEs": "…",
                     "explanation": None, "misconception": None}],
        "dokLevel": 2, "dokRationale": "why this level and not the one below",
        "standardCodes": [a.standard], "standardsYear": b.standards_year,
        "reportingCategory": None, "reportingCategorySource": "UNMAPPED",
        "explanation": "why the key is right — not a restatement",
        "explanationEs": "…", "translationStatus": "needs-review",
        "irtParameters": None, "calibrationStatus": "pre-field-test",
        "bankTier": "teacher", "status": "authored",
        "alignmentStatus": "evidenced", "requiresHistorianReview": True,
    }, indent=2) + "\n```\n")
    L.append("Then: `python3 tools/submit_items.py generation/" + a.standard +
             ".draft.json` — it refuses anything that fails a gate and names what to fix.\n")

    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"{a.standard}.brief.md")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print(f"\nwrote {os.path.relpath(p, itemio.BANK_ROOT)} — tier {tier['id']}, "
          f"{len(tier['slots'])} slots, {len(set(sigs))} identifying signal(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
