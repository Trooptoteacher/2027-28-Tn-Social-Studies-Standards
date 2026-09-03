# Handoff — TN Assessment Item Bank

**Written 2026-09-03.** Numbers here were measured, not remembered. They will drift; the
live ones come from `bash tools/run_all.sh` and `reports/STATUS.md`.

---

## 1. The binding — read this first

```
course          United States History and Geography (us-history-geography)
prefix          US
standards year  2027-28
standards file  ../standards/us-history-geography.json   (94 standards, verbatim TDOE)
output          bank/items/us-history-geography/
```

Declared in `binding.json`, asserted by every generator before it writes and re-checked on
the artifact after. **A standard code is not stable across years** — 84 of the 94 US codes
changed meaning between 2026-27 and 2027-28, which is why the year is pinned and a
superseded code is a hard failure.

To add a course, add a binding. Never widen this one.

## 2. What exists

**5,045 items** migrated from the 2026-27 `history-hack-web-app` bank. Nothing was ever
deleted; `quarantine/` is retention, not a bin.

| | |
|---|---|
| servable | 3,956 |
| aligned (counts toward coverage) | 1,890 |
| quarantined, with stated reasons | 1,059 |
| authored by Claude | 24 |
| reviewed and approved by you | 19 |
| **awaiting your review** | **5** |

Alignment: 1,548 `evidenced` · 342 `rehomed` · 1,931 `unverified` · 135 `not-applicable`.
`unverified` means **kept and usable**, alignment simply not established — it is excluded
from standards coverage and from standards-aligned forms, nothing more.

**Two green forms**, both enforced by the pipeline:
- `forms/FORM-A/` — US.46 · US.60 · US.23, tier `full`
- `forms/FORM-B/` — US.59, tier `full`

## 3. How to run it

```bash
bash tools/run_all.sh                       # everything, ledger first
python3 tools/run_gates.py                  # gates against the bank
python3 tools/run_gates.py --form FORM-A    # one form, scoped
python3 tools/form_readiness.py --csv reports/form-readiness.csv
```

Eleven stages. The ledger runs **first**: if a guard has gone missing, nothing below it
can be trusted.

## 4. The rules that matter

1. **Measure the artifact, never the instruction.** Gates read the built bank and the
   rendered PDF. Reading a builder tells you what was *supposed* to happen.
2. **A gate green against nothing is the most dangerous result there is.** Every gate
   fails on an empty scan.
3. **A gate that judged nothing is not a pass.** `scanned` is the population; `judged` is
   what it formed an opinion about. `NOT MEASURED` is never counted as passing. The one
   exception, `N/A`, requires a stated reason and cannot be claimed while the population
   exists.
4. **Prove every gate, then neuter it.** Defect fails, clean passes, empty fails — then
   replace the gate with an always-green stub and confirm the proofs go red.
5. **Every mistake gets a guard.** `lessons.json` — **50 lessons, 109 guards**.
   `tools/check_lessons.py` fails the build if a lesson has no guard, if a named guard no
   longer exists, or if a suite exists that nothing runs. **It has caught six guard
   strings that my own rewrites deleted.**

## 5. Decisions taken — all reversible, all in a file

| Decision | Where | Why |
|---|---|---|
| Migration routes by **element delta**, not text similarity | `tools/alignment.py` | `difflib` similarity is anti-correlated with alignment: 0.79 was a pure bullet reorder; 0.89 had deleted the Clayton Antitrust Act |
| `reportingCategory` left **UNMAPPED** | `reporting-categories/*.json` | TDOE has published no blueprint for 2027-28. Authoring an interim mapping would be fabrication dressed as data |
| Form blueprint is **tiered** | `blueprints/*.json` | DOK-4 is impossible in a four-option item, so a DOK-4 slot *is* a requirement for an extended item. A lower tier prints its own ceiling |
| Bank measured on **minimum depth + DOK proportion**; forms on **exact tier** | `gates/coverage.py` | "Too many items" is depth, not drift — but 7 items where a tier says 6 is a defective form |
| Relevance reads **stem + key only** | `alignment.subject_text` | Distractors are deliberately wrong; authored explanations are written by this system. Neither may prove where an item belongs |

## 6. Blocked on you

**a. Review FORM-B's authoring — 5 items.**
`q-us59-dok1-4`, `PSTIM-0166`, `U7-DOK2-0005`, `PSTIM-0167`, `q-us6-dok4-cr1`.
Read `authoring/form-b.json` — that is what was written, as data. Then:

```bash
# add an entry to reviewed/historian-approvals.json, then:
python3 tools/apply_review.py <record-id> --apply
```

`review-provenance` will not let an item claim review that no record names, and will not
let authored content be silently settled.

**b. Verify 7 primary-source citations.** `reviewed/citation-corrections.json`. A bulk
edit had replaced publication titles with repository names — Langston Hughes's *"The Negro
Speaks of Rivers"* read *"first published in Library of Congress, NAACP Records
(loc.gov)"* when it was published in ***The Crisis***. The items are held out of service.
Proposals are there; I could not reach loc.gov to verify, so nothing was rewritten.

**c. Spanish.** Everything I wrote sits at `translationStatus: needs-review`. 1,563 items
across the bank are `not-started` because their "Spanish" was English, and 594 need review
because it was word-substitution pseudo-translation. A Spanish reader is required.

## 7. Known limits — not bugs

- **19 standards are identifiable by fewer than two signals; 9 by none.** US.25's only
  signal is "World War I", so an essay on American imperialism matched it. For these,
  "is this item about this standard?" needs a teacher, not a matcher. Flagged in
  `reports/form-readiness.csv` as `weaklyIdentifiable`.
- **39 standards can fill no tier.** They need new items authored, not repairs.
- **No gate can check historical accuracy.** Every authored rationale is a claim. That is
  what `requiresHistorianReview` is for.

## 8. Standard-first generation — the answer to "repair or rebuild"

The old bank was written **item-first** and filed against standards afterward. That is why
42% of it names nothing that identifies its standard. Authoring **from** the standard makes
alignment true by construction, and removes that entire class of defect.

```bash
python3 tools/generation_brief.py US.05          # the brief: standard, signals, slots, rules
# author generation/US.05.draft.json
python3 tools/submit_items.py generation/US.05.draft.json --apply
```

**Generation is gated BEFORE admission, not reviewed after.** `submit_items.py` runs twelve
item-level gates plus an id/stem collision check against the whole bank, and a draft that
fails any of them **does not enter**. It names what to fix and you regenerate.

This matters because the migrated bank *was* built to a real specification — IRT parameters
on 100% of 5,045 items, DOK levels on 100%, blueprint structure, item-writing conventions —
and still shipped the key as the longest choice 53% of the time, 920 explanations restating
the key, and DOK rationales on 8.7%. **The spec was satisfied in form and not in substance,
and nothing measured the difference.** A parameter present in a field looks identical to a
parameter that means something.

What reaches you afterward is only what no gate can judge: **is the history right, and is
this a question you would give your students?** Everything else is enforced.

## 9. To continue the loop

**55 of 94 standards can build a form. 1,539 authoring units to green them all.**
Cheapest next: US.25 (23) · US.26 (24) · US.27 (24) · US.38 (24) · US.61 (24).

Per form, the recipe that produced both green ones:

1. `python3 tools/form_readiness.py` — pick a standard, read its cost
2. Read the items the builder would select. **Read them before authoring** — every round,
   this is where the real defects were found
3. Write `authoring/<form>.json` as data: distractor rationale + misconception per wrong
   choice, DOK rationale, any missing Spanish
4. `python3 tools/apply_authoring.py authoring/<form>.json --apply`
5. `python3 tools/forms.py <FORM-ID> --standards US.xx` — never a wildcard
6. `python3 tools/run_gates.py --form <FORM-ID>` until green
7. Add the form to `tools/run_all.sh` so it stays green
8. Any defect found becomes a lesson **and a guard** in `lessons.json`

The skill `.claude/skills/tn-assessment-bank/SKILL.md` carries this discipline into a new
session.

## 10. Honest note

Four consecutive rounds each found a defect that invalidated an earlier "green". They
narrowed — from *the system measures the wrong thing* to *which text counts as evidence* —
but they did not stop. **Expect the next round to find something too.** That is the
process working; it is also why forms are authored one at a time and reviewed as they go,
rather than in a batch that would outrun your ability to check it.
