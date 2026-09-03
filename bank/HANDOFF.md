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
| servable | 3,928 |
| aligned (counts toward coverage) | 1,989 |
| quarantined, with stated reasons | 1,059 |
| authored by Claude | 24 |
| reviewed and approved by you | 19 |
| **awaiting your review** | **5** |

Alignment: 1,693 `evidenced` · 343 `rehomed` · 1,952 `unverified`. (`not-applicable` is now
empty: every standard is judgeable — see §11.) **30 items are `held`** because their key
explanation calls the key wrong — see §12.
`unverified` means **kept and usable**, alignment simply not established — it is excluded
from standards coverage and from standards-aligned forms, nothing more.

**Assessment forms are SELECTED RESPONSE ONLY** (Sean, 2026-09-03) — TCAP-style multiple
choice, with multiple-select allowed. The blueprint declares `surface: assessment` and
`allowedItemTypes`, and `form-surface` fails anything else. Tiers `tcap-standard` (6 items,
DOK 1-3), `tcap-short` (4), `tcap-floor` (3, DOK 1-2). A selected-response form cannot reach
DOK-4 and says so on the page instead of carrying an extended item to pretend otherwise.
- `forms/FORM-A/` — US.46 · US.60 · US.23, tier `tcap-standard`
- `forms/FORM-B/` — US.59, tier `tcap-standard`

**34 DBQ activities**, `deliverables/dbq/<item-id>/` — student activity + teacher edition, in
the America 250 brand. Every document is a source card with its own citation, a HIPP sourcing
scaffold, a planning frame and writing space; the teacher edition adds the scoring guide. Built
by `python3 tools/dbq_activity.py --all`. See §13.

## 3. How to run it

```bash
bash tools/run_all.sh                       # everything, ledger first
python3 tools/run_gates.py                  # gates against the bank
python3 tools/run_gates.py --form FORM-A    # one form, scoped
python3 tools/form_readiness.py --csv reports/form-readiness.csv
```

Twelve stages. The ledger runs **first**: if a guard has gone missing, nothing below it
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
5. **Every mistake gets a guard.** `lessons.json` — **62 lessons, 161 guards**.
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

- **1 standard is identifiable by a single signal (US.65, "baby boomer generation").**
  For it, "is this item about this standard?" needs a teacher, not a matcher. The
  `signal-coverage` gate discloses it on every run; `reports/form-readiness.csv` carries
  `identifyingSignals` and `weaklyIdentifiable` per standard.
  *This line used to read "19 standards below two signals; 9 by none" — see §11.*
- **28 standards can fill no tier.** They need new items authored, not repairs.
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

**73 of 94 standards can build a form. 2,281 authoring units to green them all.**
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

## 11. The nine standards nothing could judge (2026-09-03)

The relevance matcher required a **capitalised name**. Nine of the 94 standards do not
contain one — they are about common-noun content:

> US.13 *working conditions ... women and children as a labor source* · US.21 *imperialism,
> raw materials, yellow journalism* · US.22 *imperialists and non-imperialists* ·
> US.31 *radio and movies ... popular culture* · US.33 *air travel, electricity* ·
> US.36 *flappers, birth control, office jobs* · US.65 *the baby boomer generation* ·
> US.67 *television and mass media* · US.69 *atomic testing, civil defense, mutual assured
> destruction, fallout shelters*

For those, `identifying_signals()` returned an **empty set**, and `relevance_scan` did the
worst possible thing with it: `continue`. **331 servable items were skipped — not judged,
not flagged, not counted.** The relevance gate reported PASS across 3,600 other items while
never looking at these, and `form-readiness.csv` printed those standards at **0 aligned**,
which reads as *"no items exist"* rather than *"no item here can ever be checked."* Two very
different statements, and only one of them is true.

This is the vacuous-pass defect (L11/L15) **one level down** — per standard, where the
`judged` counter cannot see it. It is exactly what you named at the outset: *a gate green
against nothing is the most dangerous result there is, and it reads exactly like a clean
pass.*

**What changed**

1. **`signal-coverage`** — a new gate that measures the *standards file*, not the items, and
   **fails** if any standard has nothing the matcher can match on. It discloses
   single-signal standards in its note.
2. **`relevance_scan` returns what it cannot judge** instead of dropping it, and the
   relevance gate fails on those items rather than passing over them.
3. **Topic signals** (`alignment.topic_signals`) — common-noun phrases read from the
   *whole* sentence, because three of those standards have no "including" clause at all and
   therefore no elements. A common noun is looser than a name, so the bar is higher: **one
   multi-word phrase, or two distinct single words.** One word alone is never evidence —
   "radio" in a Fireside Chats item must not claim the popular-culture standard.
4. **`backfill_alignment` no longer overwrites `human-verified`.** It rewrote every status
   unconditionally, so the first backfill after your review pass would have erased it. No
   item carries that status yet, which is the only reason it had not already happened.

**Measured, not asserted.** Topic signals claim **fewer** standards per item than the
proper-noun matcher already accepted — 0.77 vs 1.22 across 400 sampled items — so this is
not a loosening of the alignment bar. Every stoplist word in it was curated from what was
observed leaking, not from intuition: `civil` alone matched civil war, civil rights and
civil defense indiscriminately, while `civil defense` and `civil rights act` are precise.

**Result, with nothing new authored:**

| | before | after |
|---|---|---|
| standards the matcher can judge | 85 / 94 | **94 / 94** |
| items silently skipped | 331 | **0** |
| aligned items | 1,890 | **2,036** |
| standards that can fill a form tier | 55 | **66** |
| bank gates passing | 21 / 32 | **22 / 33** |

Recorded as **L51, L52, L53** with 14 guards. Both forms remain green (24/24).

## 13. Selected response only, and the DBQs as their own activity (2026-09-03)

Two instructions from your first teacher read, and they are one decision:

> "all the questions on the assessment builder need to be TCAP-style multiple choice, maybe
> multiple select" · "let's turn those larger DBQ questions into actual separate DBQ questions.
> We'll put the primary source of the context in my brand. Make sure we have the citations and
> sourcing. Make sure it's easily read, and then just turn that into an activity."

**Why the builder was producing a mixed packet.** The old blueprint's top tier *required* a
constructed response and a document-based question. The builder was structurally obliged to put
them on a test form. That ladder existed to answer a real problem — DOK-4 is impossible in a
four-option item — but it answered it by smuggling an extended item onto an assessment instead
of saying on the page that a selected-response form cannot reach DOK-4. It now says it.

| | before | after |
|---|---|---|
| assessment item types | mcq + CR + DBQ | **mcq, multiple-select** |
| tiers | full / extended / extended-dok3 / selected-response | **tcap-standard / tcap-short / tcap-floor** |
| DOK ceiling | 4 (via an extended item) | **3, printed on the form** |
| standards that can build a form | 66 | **73** |

The DBQ requirement was what most standards could not meet; removing it was worth seven
standards on its own.

**The DBQs did not go away — they became what they always were.** A document-based question
crammed into slot 6 of 6 is three primary sources, a three-part prompt and a six-band scoring
guide, printed with a KEY line and a paragraph headed *"Why the key is right."* All 34 now build
as standalone activities: `deliverables/dbq/<item-id>/student-activity.pdf` + `teacher-edition.pdf`.

Each source is a card in the America 250 palette — Heritage Blue border, warm tint, its citation
on a gold rule, the excerpt in 12 pt serif at 1.65 leading because it is the thing being read.
Under each card, a HIPP sourcing scaffold with ruled lines. Then the prompt broken into its own
numbered parts, a planning frame (claim → evidence per document → why it supports the claim →
outside knowledge), and writing space. The teacher edition adds the scoring guide as a real
table and the expected-evidence notes.

**Nothing was rewritten.** Documents, citations and prompts are the items' own text; the scoring
guides were extracted from the `explanation` field where they had been buried (§L58).

**Four gates measure the new surface**, all on the rendered PDF: pagination, the 9 pt print
floor, `activity-sourcing` (every document card carries a citation between its heading and its
excerpt), `activity-teacher-isolation` (no scoring guide on a student sheet). 172 source cards
and 220 student pages measured, all passing.

**Three of my own gates false-positived on my own clean output** before they were trusted —
`activity-teacher-isolation` failed all 34 student sheets on their own footer line *"its scoring
guide is not calibrated"*, and `activity-sourcing` read `George Kennan, "The Long Telegram,"` as
a 15-character citation. That is the third time in this repo an over-eager matcher has failed
clean work (L49, L59, L62). A gate is now run against known-clean output *before* it is trusted,
not only against a defect.

**What this cost.** Rebuilding FORM-A and FORM-B as pure selected response pulled in different
items — the old DOK-3/4 slots were the CR and DBQ. The new items carry the usual authoring debt
(6 items on FORM-A need DOK rationales, distractor misconceptions and Spanish; the key-longest
cue sits at 50%). **Neither form is green right now.** That is the honest cost of the change and
it is one authoring pass, not a redesign.
