# Handoff — TN Assessment Item Bank

**Written 2026-09-03.** Numbers here were measured, not remembered. They will drift; the
live ones come from `bash tools/run_all.sh` and `reports/STATUS.md`.

---

## 0. ⛔ A SESSION'S WORK WAS LOST — AND WHY THE BRANCH IS NOW PUSHED

**2026-10-04.** A session authored 12 standards, applied 130 re-homes, repaired 6 standards to
zero and fixed 8 tools. It committed each piece as instructed and, as instructed, **pushed
nothing**. The container was then reclaimed, the repository was re-cloned from `origin`, and
every one of those commits went with it. `origin/claude/tn-social-studies-bank-d2iz2u` was at
`337e13e` ("Phase 3"); there was no reflog, no stash, no dangling object and no newer ref on
the remote. **It was not recoverable, and nothing in this branch is a reconstruction of it** —
the history here is the Phase-3 state plus what has been rebuilt since, and the rebuilt pieces
say so in their own commit messages.

**The instruction and the environment were individually reasonable and jointly lossy.** "Do
not push, merge, or open a pull request unless explicitly instructed" protects the remote
from unreviewed work. A cloud session container is ephemeral and is reclaimed after
inactivity. Together they meant **a local commit is not a save** — it is a save that lasts
until the container does, which no commit message says.

**RESOLVED: the work branch is pushed after each commit.** Authorised the same day, by the
repository's own stop-hook check and by this session's branch instructions ("PUSH to the
specified branch when your changes are complete"). Nothing about review changes — the branch
is `claude/...` and nothing merges without a pull request — only the storage does.

**So the rule for every session from here: commit by concern, then push. A commit you have
not pushed is not work you have done, and the person who finds out is the next session.**

Two things this cost that are worth keeping:
- **Verify where you are before trusting a path.** The first command of the recovering
  session failed on a case-sensitivity slip (`2027-28-TN-` for `2027-28-Tn-`), which reads
  exactly like a deleted repository. Check `git log --oneline -1` and
  `git rev-parse HEAD origin/<branch>` before concluding anything about loss.
- **A re-cloned container has no Python dependencies.** `bank/requirements.txt` exists
  because two suite stages died inside `pdfminer` and `weasyprint` with a
  `ModuleNotFoundError` that reads like a code defect. Install it first (§3).

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
| servable | 3,931 |
| aligned (counts toward coverage) | 1,992 |
| quarantined, with stated reasons | 1,059 |
| authored by Claude | 27 |
| reviewed and approved by you | 19 |
| **awaiting your review** | **5** |

Alignment: 1,696 `evidenced` · 343 `rehomed` · 1,952 `unverified`. (`not-applicable` is now
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
python3 -m pip install -r bank/requirements.txt   # FIRST, in a fresh container
bash tools/run_all.sh                       # everything, ledger first
python3 tools/run_gates.py                  # gates against the bank
python3 tools/run_gates.py --form FORM-A    # one form, scoped
python3 tools/form_readiness.py --csv reports/form-readiness.csv
```

**21 stages** (`grep -c '^stage ' tools/run_all.sh` — pinned by
`check_handoff_numbers.py`, because this line read "Twelve" until 2026-10-04 and was then
mis-corrected twice). The ledger runs **first**: if a guard has gone missing, nothing
below it can be trusted.

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
5. **Every mistake gets a guard.** `lessons.json` — **84 lessons, 313 guards**.
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

**d. 48 of the 66 misconception tags are APPLIED. 18 remain, and 4 of those are mine.**
Sean authorised the write on 2026-10-04 and settled the open question with it. `misconception-
taxonomy` is down from **66 findings to 14**, and every one of the 18 is *untagged* rather
than mis-tagged — the write introduced no new defect. 48 distractors across 22 items now
carry a `distractorFunction`; 45 of those carry a family; 8 of the 14 live families are cited.

| | |
|---|---|
| tagged | **48** (`authoring/misconception-tags-batch-1.json`) |
| held — fit approximate or needs two families | **14** |
| **rewritten** (`authoring/rewrite-fabrications-batch-1.json`) | **4** |

**What the integrity check after a bulk write should ask is not "did it happen" but "did it
take more than it was given".** Measured across 552 items: **zero** historical claims
changed, **zero** historian approvals changed, **zero** review flags changed. No lifecycle
status moved either — all 22 items were already `authored`, so no ledger transition is owed.

**⚠ A tag does not un-approve an item, and getting that wrong nearly cost 16 of your
approvals.** `apply_authoring.py` used to flag everything it touched while leaving
`historianReview` in place, so 19 items read as *both* approved and awaiting review. My
first fix superseded every approval the tool touched — the gate went green and 16 of your
2026-09-03 judgements were gone. A `distractorFunction` classifies how an option goes
wrong; you approved the **history**. The rule is now measured: `_claims()` fingerprints the
fields an approval is about and excludes the two taxonomy axes, so a tag-only write leaves
the review state alone and says so, while a real change to a stem, explanation or
misconception supersedes the approval into `historianReviewSuperseded` — moved, never
deleted. **All 19 approvals stand.** (L79)

**3 items still read as both approved and flagged, and they are yours to settle:**
`q-us2-dok4-cr2`, `q-us3-dok4-cr3`, `q-us6-dok4-cr3`. They were already contradictory
before any of this, from the original form-a apply. The honest repair is to **clear the
flag** — `form-a-authoring-2026-09-03` names all three and the approval is contemporaneous
with the content — but that is a *promotion*, and a build does not promote items to make a
report read cleaner.

**⛔ `plausible-fabrication` IS NOW AN ITEM FLAW (Sean, 2026-10-04), applying this product's
CCR rule to the bank: a distractor must not assert history that never happened.** Wrong means
wrong BY THE HISTORY. The reason is that **the distractor outlives the item** — a student may
carry away the false claim rather than the correction, and a rationale on a teacher key never
reaches the student who simply remembers reading the option. The function keeps its name
because the gate needs one to report the defect; what changes is that a tagged option is
**rewritten**, anchored in something that really happened and is wrong for *this* stem, never
swapped for a different invented claim.

**⚠ And one of those four exposed bad history in its own misconception label.** `PSTIM-0041/B`
is recorded as *"invents a negotiated settlement for the blockade"* — but the Berlin Blockade
**was** ended by negotiation: the Jessup–Malik talks at the UN produced the New York Agreement
of May 1949. The false parts of that option are *"peace treaty"* and *"permanent zones"*, not
the existence of a settlement. **The label written to describe a fabrication was itself a
fabrication**, and no gate could have caught it — nothing reads a misconception for historical
truth. That is what `requiresHistorianReview` is for, and why it cannot be automated away.

**Still open on the taxonomy, none of it blocking:** the means-for-ends shape (3 cases, no
family fits — F4); MC-F-07 written in one direction only (F5); one distractor needing two
families (F6). And **the function list is provisional**: three of the seven functions rest on
a single case each, drawn from 22 items across 5 standards. The axis is sound; its membership
should be re-measured after the first real authoring batch rather than treated as closed.

**One retirement came with the axis.** `MC-F-11 Surface term match` was never a family — its
own statement describes the *option* and its own reteach note said *"this is a test-taking
error, not a content gap."* It is now the `surface-cue` **function**, flagged `itemFlaw`.
Retired rather than deleted, and it cost no data only because nothing cited any family yet.
**That window is now closed.**

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
  what `requiresHistorianReview` is for — and until 2026-10-07 nothing listed WHAT to check.
  `tools/historian_qc.py` now turns "review this item" into "confirm these assertions":
  it extracts every confirmable claim, orders them **worst-first** (negative-existence,
  then precise dates, quantities, superlatives, causal claims, named entities), and
  cross-checks the two things this repo CAN check — years against the standard's own
  declared era, and a content hash so a review of text since edited cannot read as
  current. **It verifies no history and affirms nothing.** The `historian-qc` gate checks
  the QUEUE, never the history: every queued item has a record, no record is stale. A
  non-empty queue is not a finding; an EMPTY one is, because the flag has stopped being
  set. Current: **16 items, 188 claims, 1 flag** — a negative claim in my own writing,
  confirmed true on inspection. An `outside-declared-era` check sat beside it until its
  first run flagged five items and **all five were correct history**: a standard's `era`
  is where TDOE PLACES it in the course, not a boundary on its content (US.01 reads
  1877-1900 and its cluster is 'Reconstruction'; the Klan it names was founded 1866).
  Year spans are now orientation, not accusation — a flag wrong five times out of five
  teaches you to skip the heading where the one real finding lives. L84.
  *Why it was missing: the plumbing for a review was so visible that the absence of the
  review's SUBJECT was invisible. `ai_review.py` triages rubric shape, key contradiction,
  translation and citation form — not one reads a date, an actor or an attribution. L83.*

## 8. Standard-first generation — the answer to "repair or rebuild"

**US.01 is the proof, measured 2026-10-05: it arrived BUILDABLE AT ZERO AUTHORING DEBT.**
Every line of the invoice — distractor rationales, the two taxonomy axes, DOK rationales,
both translations, explanation quality, choice balance — reads 0, because standard-first
authoring satisfies them on the way in rather than being repaired into them afterwards.
The bank total did not move (4,126): the work was never owed. Compare the cheapest
*repair* standard at 22 units.


The old bank was written **item-first** and filed against standards afterward. That is why
42% of it names nothing that identifies its standard. Authoring **from** the standard makes
alignment true by construction, and removes that entire class of defect.

```bash
python3 tools/generation_brief.py US.05          # the brief: standard, signals, slots, rules
# author generation/US.05.draft.json
python3 tools/submit_items.py generation/US.05.draft.json --apply
```

**Generation is gated BEFORE admission, not reviewed after.** `submit_items.py` runs
**18 admission gates** plus an id/stem collision check against the whole bank, and a draft
that fails any of them **does not enter**. It names what to fix and you regenerate.

*It ran 12 until 2026-10-04. Six item-level gates — serveability,
reporting-category-provenance, key-contradiction, tcap-format, rubric,
stimulus-integrity — judged a draft's own content and ran only on the BANK, so an item
could be admitted and immediately fail them. That is the shape the mandate names
outright: a post-admission batch gate is not an acceptable substitute. The six that
remain bank-only are each excluded by name with a reason in `submit_items.py`, and
`misconception-taxonomy` among them is **HELD, not excluded** — see §6d.*

This matters because the migrated bank *was* built to a real specification — IRT parameters
on 100% of 5,045 items, DOK levels on 100%, blueprint structure, item-writing conventions —
and still shipped the key as the longest choice 53% of the time, 920 explanations restating
the key, and DOK rationales on 8.7%. **The spec was satisfied in form and not in substance,
and nothing measured the difference.** A parameter present in a field looks identical to a
parameter that means something.

What reaches you afterward is only what no gate can judge: **is the history right, and is
this a question you would give your students?** Everything else is enforced.

## 9. To continue the loop

**74 of 94 standards can build a form. 4,126 authoring units to green them all.**
Cheapest next: US.33 (22) · US.31 (32) · US.60 (33) · US.02 (35) · US.59 (38).

*That total was **2,281** until 2026-10-04, and **4,102** for part of that day. Neither
move was a re-estimate. The invoice had been carrying private copies of three rules the
gates already owned (**L72**) — it is the number that picks the next standard, so it made
the cheap work look cheaper than it is; every line a gate owns is now charged by calling
that gate. The third figure, 4,126, is the first DECREASE: 37 units discharged by the 48 misconception tags and the 4 rewrites of 2026-10-04/05 (§6d). The second move, +61, added the two gates it priced at nothing at all while
forms went on selecting the items that fail them: `stimulusDebt` and `truncationDebt`
(**L75**). That second measurement first came back saying buildability collapsed from 73
to 1, which was `distractor-coverage` and `explanation-quality` — debt this invoice
already prices — counted twice and read as a discovery. A defect rate near 100% is a sign
the population is wrong, not a finding.*

*`stimulusDebt` is the one line authoring cannot discharge: a stem saying "use the
photograph" with no photograph needs a rights-cleared image or a rewritten stem, and both
are decisions rather than units of writing (§6b, §6). It is counted anyway — an invoice
that omits the work it cannot do reads as a smaller invoice rather than a blocked one.*

Per form, the recipe that produced both forms:

> **⚠️ Neither FORM-A nor FORM-B is green today, and this section used to call them
> "both green ones".** Measured 2026-10-04, `run_gates.py --form FORM-A` is **HELD on six
> gates** — record-complete, distractor-coverage, serveability, choice-length-cue,
> misconception-taxonomy, stimulus-integrity. This is not a regression in the forms: both
> were authored before `misconception-taxonomy` (Phase 1+2) and `stimulus-integrity`
> (Phase 3) existed, and a form cannot have been built to a gate that had not been
> written. It IS the current release state, and the release gate is Grade A only, so
> neither form may be described as shipped or shippable. Re-measure before quoting this.

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

## 14. The AI first pass — it triages, it never approves (2026-09-03)

You are the only reviewer this project has, and two sessions put 10 items, 83 rubrics, 30 held
records and 7 citations on your desk. You asked for an AI review with guardrails to shrink that.

**The obvious version of this would have destroyed the bank.** An AI pass that writes approvals
empties the queue *and* removes the reason a district could trust any of it — invisibly, because
an approval record looks identical whoever wrote it. Every gate would still read green and
nothing on the page would say a machine had signed off on machine work. That is the same class
of failure as a form that renders perfectly while testing the wrong standards.

So: `tools/ai_review.py` reads the queue, checks what is checkable against sources of truth
already in the repo, drafts the bounded corrections, and sorts the rest by **the question you
actually have to answer**. It writes only into an `aiReview` namespace that **counts toward no
gate, satisfies no provenance, and lets nothing ship**.

**Your queue, triaged** — `reports/REVIEW-WORKSHEET.md`:

| | | what it is |
|---|---|---|
| **28** | delete one sentence | key contradictions where the drafted deletion leaves a finished argument. Before/after shown; **not applied** |
| **2** | rewrite | key contradictions where deletion leaves too little behind |
| **10** | needs you | authored content and the four rubrics I wrote — historical and pedagogical claims |

**The queue was 119 and 79 of those rows were my fault.** Extracting the scoring guides out of
`explanation` stamped all 79 `needs-review` — but none of that content was new. All 79 were
migrated bank text moving fields unchanged, zero carried authored provenance, and the extraction
gate already proved the move was faithful. They were never yours to review. `gate_review_debt`
now fails any component flagged `needs-review` that was not actually authored. See §L64.

**Every recommendation carries its evidence and its cannot-verify list.** A verdict with no
evidence is an opinion; a reviewer that never says "I don't know" is not reviewing.

**`clear-recommended` is permitted on four declared classes only** (`policy/ai-review.json`),
all deterministic with in-repo evidence. Anything touching history, a citation, Spanish, bias or
a rubric *descriptor* escalates — including when it looks easy.

**`ai-review-boundary` enforces it on the RECORDS**, not on the reviewer's source, because a
tool can be rewritten and a policy file is prose until something reads it. Proved on all eight
ways across the line: AI naming itself as historian or bias reviewer, an `aiReview` block
writing into `historianReview`, a block that fails to disclaim itself, a verdict with no
evidence, an escalation admitting no uncertainty, and clearing a citation or a historical claim.

**Nothing has been cleared.** 119 items carry a recommendation; zero carry an approval.
