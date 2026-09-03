# Generation brief — US.05

**Course** United States History and Geography · **Standards year** 2027-28 · **Tier** `extended-dok3` (DOK ceiling 3)

## The standard, verbatim

> Examine federal policies toward American Indians, including the movement to reservations, assimilation, boarding schools, and the Dawes Act.

*Era: The Rise of Industrialization (1877-1900) · Strands: C, G, H, P, T*

## What identifies this standard

Every generated item MUST name at least one of these in its **stem or its correct answer**. This is checked at submission, not afterward.

- `American Indians`
- `Dawes Act`

## Slots to fill

| # | item type | DOK |
|---|---|---|
| 1 | mcq | 1 |
| 2 | mcq | 1 |
| 3 | mcq | 2 |
| 4 | mcq | 2 |
| 5 | mcq | 3 |
| 6 | document-based or constructed-response or extended-response or short-answer | 3 |

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

## Existing items for US.05

8 aligned item(s) already exist. Generate to FILL THE SLOTS above, not to duplicate. Existing stems:

- `US.01-X013` (mcq DOK1) The Dawes Act (1887) attempted to assimilate Native Americans by:
- `US.01-X025` (mcq DOK3) Which evaluation BEST assesses whether the federal government's Native American policy fro
- `US.02-E01` (mcq DOK1) Look at the word assimilation. It means to make people fit into a new culture. The Dawes A
- `US.02-Q01` (mcq DOK1) The Dawes Act of 1887 was primarily designed to:
- `US.02-Q02` (mcq DOK2) Which statement best describes the federal government's assimilation policy toward America
- `US.02-Q05` (mcq DOK3) The Dawes Act resulted in American Indians losing approximately two-thirds of their tribal
- `US.02-Q07` (mcq DOK2) What was the primary difference between the reservation system and the Dawes Act of 1887 i
- `US.07-X026` (mcq DOK2) The Dawes Act (1887) attempted to 'Americanize' Native peoples by:

## Record shape

Write `generation/US.05.draft.json` as `{"items": [ … ]}`. Each item:

```json
{
  "id": "US.05-GEN-01",
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
    "US.05"
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
  "requiresHistorianReview": true
}
```

Then: `python3 tools/submit_items.py generation/US.05.draft.json` — it refuses anything that fails a gate and names what to fix.
