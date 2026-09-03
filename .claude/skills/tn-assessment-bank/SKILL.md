---
name: tn-assessment-bank
description: Build, migrate, gate and render Tennessee assessment item banks and test forms in this repo's bank/ tree. Use for any work on items, blueprints, item migration across standards years, test-form rendering, or the quality gates — including adding a new course, adding a gate, or investigating a gate that reads green. Encodes the build discipline and the ledger of defects this system has already made.
---

# TN Assessment Bank — build discipline

Everything lives in `bank/`. Run `bash bank/tools/run_all.sh` before claiming anything.

## 1. Declare the binding before you build

First message of any build session states: **the course, its standard-code prefix, the
standards file you are reading, and the output directory.** `bank/binding.json` holds it;
`Binding.declaration()` prints it; every generator calls `assert_codes()` **before it
writes** and the `binding` gate re-checks the artifact **after**.

One shared toolchain, many walled courses. To add a course, add a binding — never widen
an existing one. A generator that will happily emit another course's prefix will
eventually do it.

The assertion checks three things because each catches a different failure: a foreign
prefix (`GC.01` in a US bank), a well-shaped code the standards file never defines
(`US.99`), and a **superseded standards year**. That last one is not theoretical here:
84 of the 94 US codes changed meaning between 2026-27 and 2027-28.

## 2. Backward design or the bank is worthless

Nothing is written until a blueprint exists as a committed file: per standard, how many
items, at what DOK spread, in what item types, against which reporting category. The
bank is measured against it and **drift fails in either direction**. Writing items first
and describing coverage afterward produces a bank that is 70% DOK-1 recall and reads as
complete.

Keep the target modest at first. Conformance fails in both directions, so a target set
too high can never go green.

## 3. Gates: the four rules

1. **Measure the artifact, never the instruction.** Gates read the built bank and the
   rendered PDF. Reading a builder tells you what was *supposed* to happen.
2. **A gate green against nothing is the most dangerous result there is.** Every gate
   fails on an empty scan (`empty_scan_guard`).
3. **A gate that judged nothing is not a pass.** `scanned` is the outer population;
   `judged` is what the gate formed an opinion about. Report `NOT MEASURED` when
   `judged == 0`, never PASS. `all-gates-measured` holds the release while any gate is
   unmeasured. *(This is L11: a gate reported PASS over 3,986 items while judging zero.)*
4. **Prove every gate before trusting it.** Build a fixture carrying exactly its defect
   and watch it fail; a clean fixture and watch it pass; an empty set and watch it fail.
   Then neuter the gate (`tests/test_mutation.py`) and confirm its proofs go red. A test
   that has never failed is worth nothing.

Fixtures must reproduce the real record's structure — every required field, bilingual
twins, per-distractor rationales. A simplified fixture proves only that the gate can read
a simplified fixture.

## 4. Measure before you choose a threshold

Do not pick a number for a metric you have not examined. Migration was nearly routed on
`difflib` character similarity, which turned out to be **anti-correlated** with alignment:
0.79 was a pure bullet reorder, 0.89 had deleted the Clayton Antitrust Act, 0.94 had
changed its verb from *Explain* to *Analyze*. Routing is by **element delta** — the
standard's content checklist, the words after "including" — in `tools/alignment.py`.

And judge on **effect size, not p-value alone**. At n=3,844 a chi-square test flags a
27/25/24/24 key split no student could exploit. An alarm that fires on the harmless
trains people to ignore the word FAIL.

## 5. Never let an extractor's silence count as evidence

Use `tools/extraction.py`. An extractor must prove itself against control strings known
to be present before any "not found" it reports may be believed. A PDF scan once returned
zero hits for "reporting category" — and zero for "Compromise of 1877", which is
certainly in that document.

## 6. Source of truth only

Standard text verbatim from the standards file, never typed from memory. If a fact cannot
be sourced, the item does not ship — an unsourced item is worse than a missing one.

`reportingCategory` is **not** in the standards document, and TDOE has published no
blueprint for 2027-28. It is sourced in a reviewable mapping file with per-row provenance;
the gate checks **provenance, not plausibility**. A plausibility check built on strand
letters was measured and it *passed* the known-bad item. **Do not author an interim
mapping to make a column go green** — that is fabrication dressed as data.

## 7. Forms

Student form and teacher key render from **one assembly with one deterministic choice
ordering**, so a key letter cannot drift between surfaces. The student surface is built by
**omission at assembly time**, not by hiding at render time.

Page numbering goes in the `@page` margin box. A fixed footer div freezes at
**"Page 1 of 5" on every page** — measured, not assumed. Print gates read the rendered
PDF: pagination, the 9 pt floor glyph by glyph, key leakage, disclosure.

Readability over page-fit: never shrink type to save a page. Add the page.

## 8. Scaffolding is not authoring

A bank scaffolded from another and code-substituted renders perfectly while testing the
wrong standards — every structural gate passes because they measure how it was made, not
what it is about. Mark an unauthored bank `"_unauthored"` and refuse to render it.
**Never build a unit with a wildcard** — name the standards actually authored.

## 8b. Structure gates cannot see content

Sixteen gates measuring binding, keys, blueprint, truncation, pagination and print
floor all passed a bank in which **42% of items name no element of the standard they
are filed under**. Structural gates measure how an artifact was made. Add gates that
measure what it is about:

- `standard-relevance` — the item names something its standard actually asks for
- `choice-length-cue` — the key is not reliably the longest option (it was, 53.3% against
  25% by chance: beatable without reading)
- `duplicate-stems` — one question is not filed twice

And know the ceiling: **no gate can tell you whether a stem's history is right.** A wrong
date, a key that is defensible but not best, a distractor that happens to be true — those
need a historian. Build the review QUEUE, never fake the verdict.

## 9. Every mistake gets a guard

Standing instruction from the owner. When you make or find a mistake:

1. Fix it.
2. Pin it — a test named in the words the defect was found in.
3. Add it to `bank/lessons.json` with the guard that prevents its return.

`tools/check_lessons.py` **fails the build** if a lesson has no guard, if a named guard no
longer exists in the code, if a guard lives in an unregistered suite, or if a test file
exists that nothing runs. It also fails on an empty ledger — the same defect it exists to
prevent. It has already caught a refactor that silently deleted a guard.

A lesson written down but not enforced is a promise. A lesson with a guard is a fact about
the code.

## 10. Report honestly

**done · held · gap.** Grade A means all quality controls pass, not a majority. One
unresolved Critical or High holds the whole artifact. "Close" is not "A."

Every surface that shows an item discloses `classroom-formative · pre-field-test`.
Parameters that have never met a student are estimates.
