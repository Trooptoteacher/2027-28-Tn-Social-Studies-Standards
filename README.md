# 2027-28 Tennessee Social Studies Academic Standards — Source of Truth

Canonical, machine-readable copies of the Tennessee Academic Standards for Social Studies that take
effect in the **2027-28 school year**, parsed **verbatim from the official TDOE PDF**. One place, so
every skill, build, crosswalk and app surface references the same standards.

**Valid year:** 2027-28 — the revised standards. The standards in force *through* 2026-27 live in
[`Trooptoteacher/2026-27-Tn.-Social-Studies-Standards`](https://github.com/Trooptoteacher/2026-27-Tn.-Social-Studies-Standards)
and are **not** superseded there. The two years run side by side: 2026-27 stays current for this
school year's teaching, 2027-28 is what all new course building targets.

> **Read [`GOVERNANCE.md`](GOVERNANCE.md) before building anything from this repo.** A standard code
> is **not** a stable identifier across the two years — 84 of the 94 U.S. History codes now mean
> something different — and reusing an asset by code is the one mistake that silently ships the
> wrong lesson under the right-looking label.

## Contents — 1,012 standards across 20 courses

| Level | File (`standards/…`) | Prefix | Codes | Standards | Geo | TCA | vs 2026-27 |
|---|---|---|---|---|---|---|---|
| Elementary | `kindergarten.json` | `K` | K.01–K.18 | 18 | 0 | 0 | **new course** |
| Elementary | `grade-01.json` | `1` | 1.01–1.24 | 24 | 0 | 0 | **new course** |
| Elementary | `grade-02.json` | `2` | 2.01–2.28 | 28 | 0 | 0 | **new course** |
| Elementary | `grade-03.json` | `3` | 3.01–3.33 | 33 | 23 | 5 | **new course** |
| Elementary | `grade-04.json` | `4` | 4.01–4.43 | 43 | 27 | 5 | **new course** |
| Elementary | `grade-05.json` | `5` | 5.01–5.46 | 46 | 33 | 8 | **new course** |
| Middle | `grade-06.json` | `6` | 6.01–6.62 | 62 | 45 | 0 | revised |
| Middle | `grade-07.json` | `7` | 7.01–7.65 | 65 | 58 | 0 | revised |
| Middle | `grade-08.json` | `8` | 8.01–8.74 | 74 | 39 | 10 | revised |
| High School | `african-american-history.json` | `AAH` | AAH.01–AAH.56 | 56 | 25 | 0 | **new course** |
| High School | `ancient-history.json` | `AH` | AH.01–AH.60 | 60 | 45 | 0 | **new course** |
| High School | `contemporary-issues.json` | `CI` | CI.01–CI.22 | 22 | 15 | 0 | **new course** |
| High School | `economics.json` | `E` | E.01–E.47 | 47 | 9 | 0 | **new course** |
| High School | `psychology.json` | `P` | P.01–P.61 | 61 | 0 | 0 | **new course** |
| High School | `sociology.json` | `S` | S.01–S.43 | 43 | 13 | 1 | **new course** |
| High School | `tennessee-history.json` | `TN` | TN.01–TN.67 | 67 | 35 | 6 | revised |
| High School | `us-government-civics.json` | `GC` | GC.01–GC.47 | 47 | 4 | 1 | revised |
| High School | `us-history-geography.json` | `US` | US.01–US.94 | 94 | 50 | 18 | revised |
| High School | `world-geography.json` | `WG` | WG.01–WG.46 | 46 | 46 | 0 | **new course** |
| High School | `world-history-geography.json` | `W` | W.01–W.76 | 76 | 72 | 0 | revised |

**13 of the 20 courses have no 2026-27 counterpart in our libraries** — all of K–5, plus African
American History, Ancient History, Contemporary Issues, Economics, Psychology, Sociology and World
Geography. Those are new builds with nothing to carry forward. The other 7 are revisions of courses
we already build for, and every one of them re-coded.

## Schema

Each `standards/<course>.json`:

```jsonc
{
  "course": "us-history-geography",
  "title": "United States History and Geography",
  "printedTitle": "UNITED STATES HISTORY AND GEOGRAPHY",  // as printed in the PDF
  "level": "High School",
  "standardsPrefix": "US",
  "standardsYear": "2027-28",          // every record is year-stamped
  "description": "…",                  // the course description, verbatim
  "source": { "document": "…", "file": "…", "pages": [222, 243] },
  "provenance": "Official TDOE PDF — verbatim",
  "practices": [ { "code": "SSP.01", "text": "verbatim" } … SSP.06 ],
  "standardCount": 94, "geoCount": 50, "tcaCount": 18,
  "hasContentStrand": true,
  "standards": [
    {
      "code": "US.01",
      "text": "verbatim, including any bulleted sub-items",
      "strand": ["C","G","H","P","T","TCA"],
      "strandRaw": "C, G, H, P, T, TCA",   // exactly as printed, typos included
      "geo": true,                          // strand includes G
      "tca": true,                          // legally required to be taught
      "era": "The Rise of Industrialization (1877-1900)",
      "eraOverview": "the era's Overview paragraph, verbatim",
      "cluster": "Reconstruction",          // the topic heading over this table
      "sourcePage": 225                     // page in the source PDF
    }
  ]
}
```

`index.json` is the manifest, and also carries `documentAnomalies` — see below.

Strand letters: **C**-Culture, **E**-Economics, **G**-Geography, **H**-History,
**P**-Politics/Government, **T**-Tennessee, **TCA**-Tennessee Code Annotated (legally required).
Four courses — Kindergarten, Grade 1, Grade 2 and Psychology — have **no Content Strand column** in
the source document at all; their `strand` arrays are empty and `hasContentStrand` is `false`. That
is the document's own shape, not missing data.

## How to consume

Raw URL pattern:

```
https://raw.githubusercontent.com/Trooptoteacher/2027-28-Tn-Social-Studies-Standards/main/standards/<course>.json
```

Always read `standardsYear` and carry it with the code. `US.12` on its own is ambiguous;
`US.12 (2027-28)` is not.

## Tools

```bash
pip install pymupdf

# rebuild every course file from the PDF (idempotent)
python3 tools/parse_standards.py source/TN-Social-Studies-Standards-2027-28.pdf standards/

# gate: schema, code integrity, index agreement, and the verbatim check
python3 tools/validate_standards.py --verbatim      # exit 0 only at zero blockers

# rebuild the 2026-27 -> 2027-28 crosswalk
python3 tools/build_crosswalk.py ../2026-27-Tn.-Social-Studies-Standards
```

`--verbatim` re-opens the source PDF and requires every standard's text to still appear in it,
character for character. It is the anti-fabrication gate: a standard that has been reworded,
truncated or invented cannot pass.

The parser classifies by the PDF's own font metadata rather than by line order, and cross-checks its
result against an independent table-geometry parse. Both must agree on the set of standard codes, and
codes must be gapless, or it exits non-zero.

## Crosswalk — `crosswalk/`

| File | Contents |
|---|---|
| `collisions.csv` | **416 codes that exist in both years and mean different things.** Start here. |
| `<course>.csv` | Every 2026-27 standard → its 2027-28 counterpart, plus every new standard |
| `summary.json` | Per-course counts |

| Course | 2026-27 | 2027-28 | unchanged | revised | retired | new | code moved |
|---|---|---|---|---|---|---|---|
| U.S. History | 95 | 94 | 23 | 53 | 19 | 18 | **68** |
| World History | 89 | 76 | 27 | 24 | 38 | 25 | 48 |
| Government & Civics | 35 | 47 | 9 | 14 | 12 | 24 | 23 |
| Tennessee History | 64 | 67 | 37 | 21 | 6 | 9 | 58 |
| Grade 6 | 62 | 62 | 22 | 33 | 7 | 7 | 34 |
| Grade 7 | 65 | 65 | 30 | 27 | 8 | 8 | 43 |
| Grade 8 | 75 | 74 | 12 | 27 | 36 | 35 | 37 |

`unchanged` means the text is the same standard, **which does not mean the code is the same** —
that is what the `code_moved` column is for. Matching is one-to-one and greedy by text similarity, so
no 2026-27 standard is claimed as the origin of two successors.

## Document anomalies

`index.json` → `documentAnomalies` records defects in the **source document**, so nobody spends an
afternoon deciding the parser is broken:

| Code | Page | Issue |
|---|---|---|
| `5.18` | 72 | Content Strand printed as `C. H.P, T` — periods where commas belong |
| `TN.03` | 200 | Content Strand printed as `C. E, G, H, P, T` — period after `C` |

Both are parsed to the letters clearly intended; `strandRaw` keeps what was actually printed. The
standards' own text is untouched in both cases.

## Provenance

Parsed verbatim from the official TDOE PDF, stored here at
`source/TN-Social-Studies-Standards-2027-28.pdf`. See [`PROVENANCE.md`](PROVENANCE.md) for the
document's own account of its review, adoption and implementation timeline, and for what still has
to be confirmed against the State Board's adopted text.
