# Generation brief — US.10

**Course** United States History and Geography · **Standards year** 2027-28 · **Tier** `tcap-floor` (DOK ceiling 2)

## The standard, verbatim

> Determine the impacts of increased immigration on American society, including: • Competition for jobs • Rise of Nativism • Chinese Exclusion Act and Gentleman’s Agreement

*Era: The Rise of Industrialization (1877-1900) · Strands: C, E, H, P*

## What identifies this standard

Every generated item MUST name at least one of these in its **stem or its correct answer**. This is checked at submission, not afterward.

- `Chinese Exclusion Act`
- `Chinese Exclusion Act and Gentleman’s Agreement`
- `Gentleman’s Agreement`
- `Rise of Nativism`

## Slots to fill

| # | item type | DOK |
|---|---|---|
| 1 | mcq or multiple-select | 1 |
| 2 | mcq or multiple-select | 2 |
| 3 | mcq or multiple-select | 2 |

## Constraints the gates enforce at submission


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
- **Field-testability** — `tcapFormat: false` AND `tcapFormatReason`. Every item must SAY
  whether it is field-testable; a form built from an item that does not say cannot state what
  it is. These are classroom-formative and pre-field-test, so `false` is the honest value —
  and saying nothing is not the same as saying false. The REASON is required too: "no"
  without one is indistinguishable from "nobody looked".
- **Dangling words** — the truncation gate holds a closed list of words an explanation may
  not end on (`that`, `for`, `and`, `in`, `by`, …). It cannot tell a stranded preposition
  from a real truncation, so a complete sentence ending "…is what the practice was for." is
  refused. Rewrite the sentence; do not argue with the gate. US.01 lost two explanations
  to this and both read better afterwards.
- **A distractor may not assert history that never happened** (`plausible-fabrication` is an
  ITEM FLAW). Wrong means wrong BY THE HISTORY, because the distractor outlives the item.
  Anchor every wrong option in something real that does not answer THIS stem: a true fact
  about a different question (`partial-truth`, `right-answer-wrong-question`), or a real
  event in the wrong period or attributed to the wrong actor (`common-misconception` with a
  family). "Forty acres and a mule as federal policy" is the kind of option this forbids.
- **A stimulus you reference, you carry.** If the stem says "use the photograph", the item
  needs an `image` record with `src`, `alt`, `altEs`, `citationChicago`, `rightsLabel`,
  `rightsStatementVerbatim`, `hostingInstitution` and `commercialUse: "permitted"`. 111
  items in the migrated bank tell a student to read an image that is not there. Do not
  write the 112th: either attach the source or write a text-only stem.

## Existing items for US.10

3 aligned item(s) already exist. Generate to FILL THE SLOTS above, not to duplicate. Existing stems:

- `q-tcap-us10-1` (mcq DOK2) The Chinese Exclusion Act of 1882 was significant because it —
- `q-us10-dok2-1` (mcq DOK1) The Chinese Exclusion Act of 1882 was a response to which concern?
- `q-us10-dok3-1` (short-answer DOK3) How did the Chinese Exclusion Act of 1882 contradict American ideals?

## Record shape

Write `generation/US.10.draft.json` as `{"items": [ … ]}`. Each item:

```json
{
  "id": "US.10-GEN-01",
  "stem": "\u2026",
  "stemEs": "\u2026",
  "itemType": "mcq",
  "correctAnswer": "B",
  "choices": [
    {
      "id": "A",
      "text": "\u2026",
      "textEs": "\u2026",
      "explanation": "why this is wrong",
      "misconception": "the specific error it catches"
    },
    {
      "id": "B",
      "text": "\u2026",
      "textEs": "\u2026",
      "explanation": null,
      "misconception": null
    }
  ],
  "dokLevel": 2,
  "dokRationale": "why this level and not the one below",
  "standardCodes": [
    "US.10"
  ],
  "standardsYear": "2027-28",
  "reportingCategory": null,
  "reportingCategorySource": "UNMAPPED",
  "explanation": "why the key is right \u2014 not a restatement",
  "explanationEs": "\u2026",
  "translationStatus": "needs-review",
  "irtParameters": null,
  "calibrationStatus": "pre-field-test",
  "bankTier": "teacher",
  "status": "authored",
  "alignmentStatus": "evidenced",
  "requiresHistorianReview": true,
  "tcapFormat": false,
  "tcapFormatReason": "not affirmed \u2014 no human has judged this item field-testable"
}
```

Then: `python3 tools/submit_items.py generation/US.10.draft.json` — it refuses anything that fails a gate and names what to fix.
