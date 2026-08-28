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

The parse is deterministic and idempotent, so `git diff` is the difference between the editions —
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

Four details are load-bearing, each one a bug that was found and fixed rather than a precaution:

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
