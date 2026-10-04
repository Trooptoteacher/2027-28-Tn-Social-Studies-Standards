# Provenance

## The document

| | |
|---|---|
| **Title** | Tennessee Social Studies Standards |
| **File** | `source/TN-Social-Studies-Standards-2027-28.pdf` |
| **Pages** | 269 |
| **Supplied by** | Sean Reynolds, 2026-08-28, as *"2027-28 NEW Adoption TN Academic Social Studies Standards.pdf"* |
| **Scope** | K–12, 20 courses, 1,012 standards, SSP.01–SSP.06 per course |
| **Status** | **Source of truth for all 2027-28 building** (Sean, 2026-08-28) |
| **Bytes** | 1,888,686 |
| **SHA-256** | `f62fd21f6a1854e48d9dc3b07c90b4607a95a23efeaa7edfb53595c19e297100` |

The SHA-256 above is the fingerprint of the exact file Sean supplied. Everything in this repository
is derived from it, so the chain is only checkable if the document itself can be identified — and
until 2026-08-30 nothing recorded it. `tools/check_provenance.py` recomputes the hash and fails if
the PDF in `source/` is not byte-for-byte that file, which is what makes every claim below testable
rather than asserted.

Every standard in `standards/` is parsed verbatim from this file. Nothing is summarised, reworded,
reordered, or invented. `tools/validate_standards.py --verbatim` re-opens the PDF and requires every
standard's text to still appear in it character for character; it exits non-zero if any does not.

## What the document says about itself

The Introduction (page 2) gives its own review and adoption timeline. Quoted here verbatim because a
source of truth should carry its own account rather than a summary of one:

> The Tennessee State Social Studies Standards were reviewed and developed by Tennessee educators,
> historians, and advocates for social studies education for Tennessee students. […] began with a
> public review of the then-current standards during summer 2022. After receiving more than 114,000
> comments, a committee comprised of 21 Tennessee social studies educators spanning elementary
> through higher education reviewed each standard. […] The revised standards were posted online a
> second time for public review during spring 2023. Over 80,800 reviews were submitted […] the
> standards were reviewed by the Social Studies Standards Recommendation Committee (SRC). The
> 10-member SRC, appointed by the Governor, Lieutenant Governor, and Speaker of the House of
> Representatives […] finished all of their work on September 28, 2023. These proposed standards
> will go before the Tennessee State Board of Education on first reading at their November 3. 2023
> board meeting.
>
> The final reading and adoption of the revised social studies standards is expected to occur during
> the state board's February 2024 meeting, and the revised social studies standards will be
> implemented in the 2027-2028 school year.

Two things follow from that paragraph, and they are recorded here rather than argued:

1. **The 2027-28 implementation date is the document's own.** It is not an inference. This is the
   standards set that takes effect in the 2027-28 school year.
2. **The document was written before the State Board's February 2024 final reading.** It describes
   itself in the future tense with respect to adoption. It is being treated as final for building
   purposes (Sean's call, 2026-08-28, made with this paragraph in front of him).

### If a Board-adopted PDF is obtained later

Do not hand-patch individual standards, and do not diff by eye. Re-run the pipeline:

```bash
# replace the file in place, keeping the same name
python3 tools/parse_standards.py source/TN-Social-Studies-Standards-2027-28.pdf standards/
python3 tools/validate_standards.py --verbatim
python3 tools/build_crosswalk.py ../2026-27-Tn.-Social-Studies-Standards
git diff --stat standards/ crosswalk/
```

The parse is deterministic and idempotent, so `git diff` is the difference between the two documents —
exact, per standard, with nothing missed. Anything the diff touches must then be re-checked
downstream through the crosswalk, because a re-coded standard invalidates every asset pointing at
the old code. `2026-27-Tn.-Social-Studies-Standards` is untouched by any of this.

## Parse method

`tools/parse_standards.py`. The PDF has a real text layer (it is not a vector export), and it styles
every element distinctly, so the parser classifies by font metadata rather than by guessing at line
order:

| Style | Element |
|---|---|
| bold, matches a header token | table header cell (`Standard`, `Number`, `Content Standard`, `Content`, `Strand`) |
| bold ≥ 14pt | era or topic heading above a standards table |
| bold, starts `Overview:` | the era's overview paragraph |
| plain 14pt | a standard code (`US.01`) or a practice code (`SSP.01`) |
| plain 12pt | standard text, or a course-description / overview continuation |
| plain 11–12pt, strand letters only | the Content Strand cell |

Five details are load-bearing, each one a bug that was found and fixed rather than a precaution:

- **Lines are read in the PDF's own order and are never re-sorted by y-coordinate.** A code cell is
  vertically centred against a wrapped text cell, so a y-sort detaches the first line of every
  two-line standard and silently hands it to the previous standard.
- **Header cells are matched before headings.** Most headings are 18pt, but Grade 7 sets its three
  Renaissance/Reformation topic headings at 14pt — the same size the header cells use.
- **A strand cell frequently shares a line with the prose**, sometimes even a single text span. It is
  split off at the column gap, found adaptively: a fixed x-threshold cuts mid-sentence, because the
  strand column's left edge moves with the cell's width.
- **A strand cell can wrap** (`C, G, H, P, T,` / `TCA`). Consuming only the first line drops the TCA
  flag from the standard and leaves `TCA` sitting at the end of the standard's text.
- **The era Overview must survive from its heading to the first standard code beneath it.** The
  document prints the heading, then `Overview:`, then the table — so the paragraph is read *before*
  the first code that has to carry it. `apply_heads()`, which installs the pending heading, also
  cleared `overview`, and it runs at exactly that code. **491 of the 1,012 standards shipped with an
  empty `eraOverview`**, every standard of grade-04, grade-08, tennessee-history,
  us-history-geography and world-history-geography among them, with five further courses partial.
  Nothing was red: the key was *present*, so the required-field check passed, and an empty string is
  verbatim by construction, so `--verbatim` passed too. The Overview is now cleared only when a
  genuinely **new** era heading appears — not by a heading already pending and not by a running head
  repeating the current era, both of which sit between the paragraph and the code it belongs to.

## Era overviews, and the provenance that travels with them

Each standard carries `eraOverview` (the state's own paragraph, verbatim) and
`eraOverviewSourcePage` (the page it is printed on — normally *not* the standard's own
`sourcePage`, because the paragraph is printed once at the head of an era and the standards run for
pages after it). Each course file carries an `eraOverviews` table: one row per distinct
`(era, overview, page)`, with the heading it sits under and the span of codes it governs, so a
reader can check a value against the document without re-deriving it.

The document's identity travels with every derived value: `source.sha256` on every course file and
`sourceSha256` in `index.json`, both the hash of the exact PDF the values were read from. A page
number is only correct *about a particular document*; recorded without the hash it is a claim that
rots the moment TDOE re-issues the file. The extraction event's own timestamp is `extractedAt` in
`index.json`, recorded **once** rather than on each of the 1,012 standards — the re-parse workflow
above reads `git diff standards/` as the difference between two *documents*, and a wall-clock field
repeated per course would put a line of churn in every file on every run and bury that signal.

`tools/validate_standards.py` blocks on: an empty overview, an overview with no cited page, two
different overviews under one heading, a non-contiguous run of standards sharing one overview, a
standard whose `(era, overview, page)` is absent from its course's table, a table row no standard
uses, a wrong row count, a missing or malformed hash, and a course hash disagreeing with
`index.json`. Under `--verbatim` it additionally requires each overview to appear character for
character **on the page it cites** — deliberately not anywhere in the document, because a paragraph
found on some other page is a wrong page reference — and re-hashes the PDF on disk.

`tools/validate_standards_selftest.py` proves each of those fires. **Seven of its thirty cases are
negative controls**, because a blocker that rejects legitimate work looks identical to one that
works, and two of the document's own shapes are exactly the kind that get wrongly rejected:

- **TDOE prints one Overview paragraph verbatim under two different headings** — Sociology p194
  *"Self and Socialization"* and p195 *"Functions and Structures of Social Institutions"*. Keyed on
  the text alone the second printing gets no table row, and all thirteen standards citing p195 then
  point at a triple their table does not carry. The duplication is recorded as a
  `documentAnomalies` entry, not resolved: it is what TDOE published.
- **Where the era heading is only a course banner** (`S | SOCIOLOGY`, `WG | WORLD GEOGRAPHY`) or a
  Domain, the document prints an Overview per **topic** heading beneath it. The first version of the
  agreement check was scoped to the era and blocked **12 of the 20 courses**. The scope is the
  cluster — a refinement of the era, and the weaker claim that is true of all twenty courses
  (measured: 0 disagreements across 1,012 standards).

Two independent checks run on every course, and the parser exits non-zero on either:

- an independent **table-geometry parse** must not find a standard code the line parse missed
- codes must be **gapless** from `.01` to the course maximum, with no duplicates

The parser also detects and records source-document defects rather than silently normalising them —
see `documentAnomalies` in `index.json`.

## Related repositories

| Repository | Role |
|---|---|
| `Trooptoteacher/2026-27-Tn.-Social-Studies-Standards` | Standards in force **through 2026-27**. Still current for this year's teaching. Not superseded, not edited. |
| `Trooptoteacher/-2026-27-Social-Studies-Primary-Sources` | Primary-source library keyed to **2026-27** codes. Re-point through the crosswalk before any 2027-28 use. |
| `Trooptoteacher/history-hack-web-app` | Where 2027-28 courses are **built and delivered**, under a separate `2027-28` namespace. See `GOVERNANCE.md`. |
