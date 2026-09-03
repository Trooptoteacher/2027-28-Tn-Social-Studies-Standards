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
| `all-gates-measured` | any gate that formed no opinion (see below) |

**Content gates — what the bank is ABOUT, not how it was made.** Sixteen structural
gates all passed a bank in which **1,680 items (42%) name no element of the standard
they are filed under**: a Vietnam anti-war question under *the founding of the United
Nations*, a Korea question under *prosperity and consumerism in the 1950s*. Those are
pre-existing misfiles in the 2026-27 bank, verified against provenance — the migration
carried the code faithfully. Structure gates are constitutionally unable to see this.

| Gate | Catches | Found on the migrated bank |
|---|---|---|
| `alignment-claim` | an item CLAIMING an alignment nothing backs | **0** — all honestly labelled |
| `choice-length-cue` | the key is the longest choice far above chance | **53.3%** vs 25% |
| `duplicate-stems` | one question filed twice under two ids | **21 groups → fixed** |
| `citation-integrity` | a citation naming a REPOSITORY where a PUBLICATION belongs | **7 held** |

### Content quality and alignment confidence are separate axes

Collapsing them let an unverified label read as a verdict on the question. It is not:
1,320 items had fully intact stems, choices, explanations and bilingual fields and were
nonetheless described as unsaveable. **Nothing has ever been deleted from this bank —
all 5,045 migrated items are retained, and `quarantine/` is retention, not a bin.**

`alignmentStatus` is its own field:

| value | meaning |
|---|---|
| `evidenced` | the item names something that identifies its standard |
| `rehomed` | moved on stem evidence, carrying that evidence, awaiting sign-off |
| `human-verified` | a person confirmed it |
| `unverified` | **kept and usable.** Alignment not established, so excluded from standards coverage and from standards-aligned forms — nothing more |
| `not-applicable` | the standard names nothing matchable |

The gate fails a **dishonest claim**, never the existence of an unverified item. An
item may say "I don't know what standard this tests"; it may not say "I test US.05"
when nothing supports that. `reviewed/relevance-allowlist.json` records human
verification, one committed decision per item.

**Citations.** A bulk edit had replaced publication titles with repository names across
the primary-source items — Langston Hughes's "The Negro Speaks of Rivers" read *"first
published in Library of Congress, NAACP Records (loc.gov), June 1921"* when it was
published in ***The Crisis***. The date survived; the publication did not. A repository
is where a scan lives, not where a work was published, and these are the DBQ items an
adoption reviewer reads first.

Those 7 items are **held** — content retained, not servable — and
`reviewed/citation-corrections.json` proposes the real publication for each as a claim
**a person must confirm**. Nothing was silently rewritten: this session cannot reach
loc.gov, and a confidently wrong citation is the defect being fixed.

**What these do NOT do:** they cannot tell you whether a stem's history is right. A
wrong date, a key that is defensible but not best, a distractor that is accidentally
also true — those need a historian, and no gate substitutes for one.

Print gates, run per rendered form, reading the **PDF**:

| Gate | Catches |
|---|---|
| `form-pagination` | `Page N of M` missing, frozen, or disagreeing with the real page count |
| `form-type-size` | any glyph below the 9 pt print floor |
| `form-key-leakage` | key material on a student PDF |
| `form-disclosure` | a surface showing items without the calibration disclosure |
| `teacher-side-isolation` | teacher-only fields on a rendered student surface |

Run: `python3 tools/run_gates.py` · regenerate the status file with
`python3 tools/status_report.py` (it is a measurement, never hand-edited).

### A gate that judged nothing is not a pass

`teacher-side-isolation` once reported **PASS over 3,986 items while judging
zero** — its inner filter removed every record, and the empty-scan guard only
watched the outer scan. Results now carry a `judged` count and report
`NOT MEASURED`, which the runner does not count as a pass, and
`all-gates-measured` holds the release while any gate formed no opinion.

### Every gate is proven

`python3 tests/test_gates.py` — **53 proofs**: for each gate, a clean fixture passes, a
fixture carrying exactly that defect fails *and the finding names the broken record*,
and an empty set fails.

`python3 tests/test_mutation.py` — replaces each gate with an always-green stub and
confirms its proofs go red. A test that has never failed is worth nothing.

`python3 tests/test_alignment.py` — pins migration routing against real standard
pairs, each one a case the similarity floor got wrong.

`python3 tests/test_regressions.py` — one pin per defect found in this build, named in
the words the defect was found in, so a future failure reads as "you reintroduced X".

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

## Forms

`python3 tools/forms.py <form-id> --standards US.05 US.15 …`

**Never a wildcard** — name the standards actually authored.

The student form and the teacher key render from **one assembly with one
deterministic choice ordering**, seeded from the item id and form id. A key
letter therefore cannot drift between the two surfaces. The student surface is
built by **omission at assembly time**, not by hiding anything at render time.

Page numbering lives in the `@page` margin box. Rendering the same content with
a fixed footer div was measured, and it freezes at **"Page 1 of 5" on every
page** — the total is right and the counter is stuck. That is why
`form-pagination` reads the rendered PDF rather than the template.

Rendered with WeasyPrint; measured with pdfminer, glyph by glyph.

## Every mistake gets a guard

Standing rule: when a mistake is made or found, it is fixed, **pinned**, and recorded
in [`lessons.json`](lessons.json) with the guard that prevents its return.

`python3 tools/check_lessons.py` **fails the build** if a lesson has no guard, if a
named guard no longer exists in the code, if a guard lives in a suite nothing runs, or
if a test file exists that is not registered. It fails on an empty ledger too — the
same defect it exists to prevent.

It has already earned its place: it caught a refactor that silently deleted an
invariant comment `run_gates.py` was cited for, and three ledger entries pointing at
strings that did not exist.

**35 lessons, 71 guards** — among them:

| | |
|---|---|
| `L06` | migration routed on a similarity metric that is anti-correlated with alignment |
| `L07` | element matching read the item's *distractors*, quarantining a 17th Amendment question for the 18th |
| `L11` | a gate reported **PASS over 3,986 items while judging zero** |
| `L13` | a PDF scan's zero hits treated as evidence, when the extractor was simply broken |
| `L14` | a gate designed that would have **passed the very defect it existed to catch** |
| `L15` | a pass tally reported that included a vacuous pass |
| `L17` | sixteen gates measured how the bank was made; **none measured what it is about** |
| `L18` | the key is the longest choice 53.3% of the time — beatable without reading |
| `L27` | 1,144 items' "Spanish" was English; 408 were pseudo-translated by word swap |
| `L32` | a de-bias gate existed for commits that the **builder could not satisfy** |
| `L33` | fixing the length cue **over-corrected to 0%**, which a one-sided gate passed |
| `L34` | a bank gate run over a form measured a distribution **no student ever sees** |

A lesson written down but not enforced is a promise. A lesson with a guard is a fact
about the code.

## The pilot: one form proven green

`python3 tools/run_gates.py --form FORM-A`

**FORM-A (US.46 · US.60 · US.23) passes every gate that applies to it** — 21 of 21
applicable, 1 N/A. It is the existence proof that Grade A is reachable, and the cost of
getting there for one form of 18 items was:

| | |
|---|---|
| distractor rationales authored | 36 |
| DOK rationales authored | 15 |
| Spanish pairs authored (marked `needs-review`) | 5 |
| explanations rewritten | 1 |
| choice sets rebalanced for the length cue | 11 |

Authored content is committed as DATA in [`authoring/`](authoring/) so a reviewer reads
what was written, not the script that wrote it. `tools/apply_authoring.py` refuses to
write a distractor rationale onto the key, to name a choice the item does not have, or to
let two distractors on one item claim the same misconception — it validates the whole
record before writing anything, because a partial content write is worse than none.

Every authored item carries `requiresHistorianReview: true`. A rationale explaining a
misconception is still a historical claim.

## Run everything

```
bash tools/run_all.sh
```

Ledger first — if a guard has gone missing, nothing below it can be trusted — then the
gate proofs, the mutation check, alignment routing, regression pins, print-gate proofs,
and finally the gates against the built artifact.

## Release gate — Grade A only

An item bank or form ships only when it passes **all** quality controls: build/print
QC, accessibility at **zero Critical and zero High**, the state's adoption rubric at
Sean's bar, and content accuracy. One unresolved Critical or High holds the whole
artifact. Status is reported as **done · held · gap**. "Close" is not "A."

Every surface that shows an item discloses **`classroom-formative · pre-field-test`**.
Parameters that have never met a student are estimates; a bank that presents them as
calibrated is making a psychometric claim it cannot support.

**Current status: HELD.** See [`reports/STATUS.md`](reports/STATUS.md).
