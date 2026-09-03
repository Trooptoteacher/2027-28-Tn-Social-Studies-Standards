# TN Social Studies — Assessment Item Bank & Test Forms

Builds assessment item banks and test forms against the **2027-28 Tennessee Academic
Standards for Social Studies**. Nothing else ships from here.

---

## Binding — declared before anything is built

| | |
|---|---|
| **Course** | United States History and Geography (`us-history-geography`) |
| **Standard-code prefix** | `US` |
| **Standards year** | **2027-28** |
| **Standards file** | `../standards/us-history-geography.json` (94 standards, verbatim from the TDOE PDF) |
| **Output directory** | `items/us-history-geography/` |
| **Quarantine** | `quarantine/us-history-geography/` — not servable, not coverage |

Declared in [`binding.json`](binding.json). Every generator loads it and calls
`Binding.assert_codes()` **before it writes**; the `binding` gate re-checks the
artifact **after**. A generator that will happily emit another course's prefix will
eventually do it, so the assertion is a hard exception, never a warning.

It checks three things, because each catches a different failure:

1. **Shape** — a foreign prefix (`GC.01` in a US bank).
2. **Existence** — a well-shaped code the standards file never defines (`US.99`).
3. **Year** — a code carrying the superseded 2026-27 year. **84 of the 94 US codes
   changed meaning between the two years.** A code is not a stable identifier across
   them, and carrying an asset forward by code alone is the one mistake that silently
   ships the wrong lesson under the right-looking label.

One shared toolchain, many walled courses. To add a course, add a binding — never
widen this one.

## Backward design

Nothing is written until [`blueprints/us-history-geography.blueprint.json`](blueprints/us-history-geography.blueprint.json)
exists. It is committed, and the bank is **measured against it** per standard, per DOK,
per item type, failing on drift in **either** direction.

Current draft: 6 items per standard · DOK 2/2/1/1 · 4 mcq + 1 constructed-response +
1 document-based · **564 items** across 94 standards. Marked `DRAFT` — proposed by the
build, not yet approved.

## The gates

Each is written against a defect it has actually caught. Each reads the **built
artifact**, never the generator source. Each **fails on an empty scan** — a gate green
against nothing is the most dangerous result there is, and it reads exactly like a
clean pass.

| Gate | Catches |
|---|---|
| `record-complete` | any required field missing |
| `binding` | foreign prefix, undefined code, superseded standards year |
| `key-integrity` | key naming a nonexistent choice, duplicate/orphan choice ids, multi-key single-select |
| `distractor-coverage` | a wrong choice with no explanation, or two distractors naming the same misconception |
| `truncation` | stem/choice/explanation cut mid-sentence by a bulk edit or translation pass |
| `blueprint-conformance` | drift from the committed blueprint, in either direction |
| `key-position-debias` | key positions non-uniform (chi-square, p<0.01) |
| `serveability` | item routes to a standard that does not exist, image that does not resolve, absent bilingual field |
| `reporting-category-provenance` | a category with no declared source, or disagreeing with the mapping |
| `teacher-side-isolation` | key material on a student-facing surface |
| `release-readiness` | the Grade A decision — unsourced categories, unsigned blueprint, unreviewed provisional items, authoring debt |

Run: `python3 tools/run_gates.py`

### Every gate is proven

`python3 tests/test_gates.py` — **53 proofs**: for each gate, a clean fixture passes, a
fixture carrying exactly that defect fails *and the finding names the broken record*,
and an empty set fails.

`python3 tests/test_mutation.py` — replaces each gate with an always-green stub and
confirms its proofs go red. A test that has never failed is worth nothing.

`python3 tests/test_alignment.py` — pins migration routing against real standard
pairs, each one a case the similarity floor got wrong.

Fixtures reproduce the real record's structure — all 17 required fields, bilingual
twins, per-distractor rationales, IRT block. A simplified fixture proves only that the
gate can read a simplified fixture.

## `reportingCategory` — sourced here, not guessed

**Not in the standards document.** TDOE publishes a US History EOC blueprint defining
reporting categories, but it is keyed to the **2026-27** standards, and **no blueprint
exists yet for 2027-28** (adopted Feb 2024, implements 2027-28). So this field cannot
currently claim to be the state's own category.

It is therefore sourced in [`reporting-categories/us-history-geography.json`](reporting-categories/us-history-geography.json),
one reviewable row per standard, each carrying `source` ∈ `tdoe-blueprint` |
`interim-district` | `UNMAPPED`. **All 94 rows are currently `UNMAPPED`, and no
interim mapping has been authored** — inventing one would be fabrication dressed
as data.

The provenance gate reads **green** over all-`UNMAPPED`, because consistency is all
it can check. That is why `release-readiness` exists and **holds on it**: a green
column over 94 unsourced categories is the same trap as a gate green over an empty
set.

The gate checks **provenance, not plausibility.** A plausibility check built on the
standards' strand letters was built and measured against the existing 2026-27 bank: it
flagged 11 items of 4,189 and **passed the known-bad one** — a Bessemer-process stem
filed under *Government and Civics*, whose standard carries strands C and P. A gate
that passes the defect it exists to catch is worse than no gate.

## Migration from the 2026-27 bank

`python3 tools/migrate.py <source-dir> [--apply]`

Nothing is carried forward by code. The old code moves to
`provenance.priorStandardCodes` rather than being dropped.

**Routing is by element, not by text similarity.** A similarity floor was built
first, then measured, and it is *anti-correlated* with alignment:

| pair | similarity | what actually happened |
|---|---|---|
| `US.16 → US.17` | 0.79 | pure bullet reorder — **identical content** |
| `US.12 → US.12` | 0.89 | **Clayton Antitrust Act of 1914 deleted** |
| `US.19 → US.21` | 0.89 | "spread American democratic and moral ideals" → "American nationalism" |
| `US.60 → US.60` | 0.94 | verb **Explain → Analyze** — a DOK shift |

A 0.90 floor quarantines the first and waves through the rest. So
[`tools/alignment.py`](tools/alignment.py) diffs the standard's **content
checklist** — the words after "including" — and its verb:

| Bucket | Rule | Servable |
|---|---|---|
| `migrated` | checklist intact for this item | yes |
| `provisional` | standard's verb rose, or elements were added | yes, flagged for review |
| `quarantined` | standard retired, **or this item tests a dropped element** | **no — not coverage** |

Every quarantine names the element that caused it. Pinned by
[`tests/test_alignment.py`](tests/test_alignment.py), which carries each
false positive found by reading real output: a distractor mentioning the 18th
Amendment quarantining a 17th Amendment item; `United States v. Nixon` vs
`vs. Nixon` reading as a deletion; `suffragettes → suffragists` and Tennessee's
"Perfect 36" reading as deletions when only the wording moved.

Quarantine is the point. An item whose standard moved out from under it is not a
coverage number, and calling it one is how a bank ends up testing the wrong standards
while every structural gate passes.

## Release gate — Grade A only

An item bank or form ships only when it passes **all** quality controls: build/print
QC, accessibility at **zero Critical and zero High**, the state's adoption rubric at
Sean's bar, and content accuracy. One unresolved Critical or High holds the whole
artifact. Status is reported as **done · held · gap**. "Close" is not "A."

Every surface that shows an item discloses **`classroom-formative · pre-field-test`**.
Parameters that have never met a student are estimates; a bank that presents them as
calibrated is making a psychometric claim it cannot support.

**Current status: HELD.** See [`reports/STATUS.md`](reports/STATUS.md).
