# Assessment build checklist — six courses, five parallel forms

**Written 2026-09-05. Every number here was measured, not estimated.** Re-derive them with
`python3 tools/course_scope.py [--per-form 1|2]` — a number in prose is a claim that rots, and
this repo has already been bitten by that twice.

**The ask:** enough MCQ items to build a minimum of **5 parallel forms** per course, equal in
rigor, testing the same content, with **every single standard assessed**. DBQs stay separate; **LEQs are out of scope**. Primary sources permitted as appropriately-short excerpts. Images, political cartoons,
charts and graphs included.

---

## 0. The one decision that sizes everything

**How many MCQ items per standard, per form?**

| | depth needed per standard | standards ready today | **MCQ items still to author** |
|---|---|---|---|
| 1 item / standard / form | 5 DOK-matched | 65 / 438 | 1,819 |
| **2 items / standard / form — TAKEN** | 10 DOK-matched | 38 / 438 | **3,764** |

**Decided 2026-09-05: 2×.** A misconception detected once is noise; detected twice, on two
independently authored items, is a diagnosis. The whole product is misconception-level
remediation, so 1× is not a cheaper version of it — it is a version that does not work. Two
supporting reasons: a single 4-option MCQ against 25% guessing makes a borderline student's
standard score close to a coin flip, and you would be routing reteach off noise; and after field
testing you WILL retire items, which at 1× leaves a hole with no substitute.

**Depth is hard to add later; form count is easy.** If the volume has to come down, the fallback
is 2× deep and three forms wide (6 per standard, 2,628 items), never 1× deep and five wide.
Going 1× → 2× means revisiting all 438 standards and re-checking DOK-match on every one.

One item per standard makes the whole score for that standard a coin-flip on a single question —
a student who misreads one stem reads as not having mastered the standard. Two gives you a
defensible per-standard signal and lets a bad item be dropped without leaving a hole.

**Everything below assumes 2. Say the word and I halve it.**

---

## 1. Scope — measured

| course | prefix | standards | bank today |
|---|---|---|---|
| Sixth Grade Social Studies | `6` | 62 | none |
| Seventh Grade Social Studies | `7` | 65 | none |
| Eighth Grade Social Studies | `8` | 74 | none |
| United States History & Geography | `US` | 94 | 3,928 servable |
| World History & Geography | `W` | 76 | none |
| Tennessee History | `TN` | 67 | none |
| **total** | | **438** | |

- [ ] **Confirm "6-8" means all three grade courses.** TN splits them into three separate
      standards documents with three prefixes. That is 201 of the 438 standards — nearly half
      the job.
- [ ] **Confirm Tennessee History is in scope as its own course.** `TN.01–TN.67` exists as a
      standalone standards file.

---

## 2. What already exists, honestly

Only U.S. History has a bank. Against the 5-parallel-form requirement:

| | US.01–US.94 |
|---|---|
| standards with ≥5 aligned MCQs | 72 / 94 |
| standards with ≥5 aligned MCQs **at the same DOK** | **65 / 94** |
| standards with ≥10 aligned MCQs at the same DOK | **38 / 94** |
| standards with **zero** aligned MCQs | 11 |

**DOK-match is what makes forms parallel.** Five items on the same standard at DOK 1, 2, 2, 3, 3
do not build five equal forms; they build one form and four different ones. This is the number
that matters and it is 65, not 72.

- [ ] Author **99** items to reach 5 DOK-matched per US standard *(or **324** to reach 10)*
- [ ] The other five courses start from zero: **1,720 items at 1×, 3,440 at 2×**

---

## 3. ⚠️ The stimulus gap — read this before planning anything

**Zero of 3,928 servable items carry an image, cartoon, chart or graph.** Not one.

Worse: **111 items instruct the student to use a stimulus that does not exist.**

> *"Use the photograph to answer the question. This photograph shows the completion of the
> transcontinental railroad at Promontory Summit, Utah, May 10, 1869."*
>
> `image: None`

The "photograph" is a *prose description of a photograph*. As printed, the student is told to
read an image that was never there — so the item does not test source analysis at all, it tests
reading a caption. On a form claiming to assess visual-source skills, that is a false claim about
what was measured.

- [ ] Hold all 111 and decide per item: attach the real asset, or rewrite the stem so it stops
      referencing an image
- [ ] Build `gate_stimulus_integrity` — an item referencing a stimulus must carry one, and a
      stimulus must carry rights + citation. **This gate does not exist yet.**
- [ ] Source real assets. `history-hack-web-app` already holds a cited, rights-cleared image
      bank (`public/data/us-history/primary-sources/images/unit-N.json`, with
      `hostingInstitution`, `rightsStatementVerbatim`, `citationChicago`, `commercialUse`) —
      **U.S. only.** Grades 6–8, World and Tennessee have no equivalent and need one built.
- [ ] Decide the stimulus share per form (suggest ~20%: ≈9 of 45 items) and **match it across
      all five parallel forms** — a cartoon on Form A and not on Form B breaks parallelism
- [ ] Charts and graphs must survive grayscale and never encode the answer in colour alone
      (existing accessibility rule; no gate reads a chart yet)

---

## 4. Per course, in order — repeat six times

For each of `6`, `7`, `8`, `US`, `W`, `TN`:

- [ ] **Declare the binding.** New `binding.json`: course, prefix, standards year `2027-28`,
      standards file, output dir, quarantine dir, forbidden prefixes. **One toolchain, many
      walled courses — never crossed.** A generator that will happily emit another course's
      prefix will eventually do it.
- [ ] **Commit the blueprint before a single item is written.** Per standard: item count, DOK
      spread, MCQ/multiple-select mix, stimulus share. The bank is measured against this file.
- [ ] **Reporting category:** leave `UNMAPPED` with `sourceOfRecord` stated. TDOE has published
      no 2027-28 blueprint; inventing an interim mapping is fabrication dressed as data.
- [ ] **Generate → gate → regenerate**, per standard, through `submit_items.py`. Nothing enters
      the bank that has not passed the 12 admission gates.
- [ ] **Author to DOK-match**, not to raw count.
- [ ] **Build the 5 forms** and gate each one scoped.
- [ ] **Bilingual**: every item needs ES twins. *No Spanish reader has ever looked at this bank.*

---

## 5. New gates required — none of these exist yet

Parallelism is a claim nothing currently measures.

- [ ] **`gate_form_parallelism`** — across a declared form family: identical item count, identical
      DOK distribution, identical standard coverage, identical stimulus-type counts, and **zero
      item overlap**. Fails on any divergence.
- [ ] **`gate_standard_coverage_complete`** — every standard in the course appears on every form
      in the family. "Every single standard must be assessed" is otherwise unverified prose.
- [ ] **`gate_stimulus_integrity`** — a stimulus reference implies a stimulus; a stimulus implies
      rights, citation, alt text (EN/ES), and grayscale legibility.
- [ ] **`gate_excerpt_length`** — a primary-source excerpt must fit a stated word ceiling per
      grade band. Grade 6 and Grade 11 cannot share one limit.
- [ ] **`gate_reading_load`** — total words on a form, per grade band. Five forms equal in rigor
      must also be equal in reading burden.
- [ ] Each proved three ways before trusting it: defect fails, clean passes, empty fails —
      **and run against known-clean output before wiring** (five gates have now failed correct
      work because I skipped that step).

---

## 6. DBQ — separate, already built for U.S.

The architecture is done and holds for the new courses:

- [x] Assessment forms are selected-response only (`surface: assessment`, `allowedItemTypes`)
- [x] 34 U.S. DBQs build as standalone branded activities with source cards, citations, HIPP
      scaffolds and teacher scoring guides
- [ ] Extend `dbq_activity.py` to the other five courses
- [x] ~~LEQs~~ — **out of scope** (Sean, 2026-09-05)

---

## 7. Sequence

| phase | work | gate |
|---|---|---|
| **1** | Confirm scope + the 1× / 2× decision | — |
| **2** | Fix the 111 phantom-stimulus items; build `gate_stimulus_integrity` | stimulus |
| **3** | Build the three parallelism gates **against the existing US bank** | parallelism |
| **4** | Close US to DOK-match (99 or 324 items); ship 5 US forms | full US family green |
| **5** | Stand up Grade 8 (closest content to US, reuses the most) | 5 forms |
| **6** | Grades 6, 7, World, Tennessee | 5 forms each |

**Phase 3 before phase 4 deliberately.** Build the parallelism gates against the bank that
already exists, so the first five forms are measured by something that has already been proven —
rather than discovering after 300 authored items that "parallel" was never checked.

---

## 8. What this costs you, not me

At 2×, ~4,380 items reach Grade A only through a human. You are the only reviewer this project
has. **Nothing here is field-tested; every form ships disclosed as `classroom-formative ·
pre-field-test`, and no item in this bank has ever met a student.**

- [ ] Decide review capacity per week, and let that set the generation rate
- [ ] Decide whether Spanish review is hired out — it is a hard blocker on serving any of this
      bilingually, at any scale
- [ ] Historian review on authored content — no gate can check whether the history is right

**Nothing ships until all three release gates read A.** "Close" is not "A."

---

## 9. The data bank — what the whole thing is actually for

**Sean, 2026-09-05:** *the best test data bank for all of these courses, better than Performance
Matters, with the ability to analyse the data, drive remediation, and create parallel tests.*

That is a different product from an item bank. An item bank is a substrate; this is
**administration → response data → diagnosis → reteach**. Two of those four do not exist in any
form.

### The differentiator, and the measurement that hurts

A district platform reports *"62% mastery on US.04."* A teacher cannot teach from that. What
they can teach from is *"17 of your 24 students chose B, which conflates the Homestead Act with
railroad land grants — here is the reteach."*

The item record already has the field for that: every distractor carries a `misconception`.
**That field is the entire differentiator, and it is empty.**

| | |
|---|---|
| MCQ items | 3,793 |
| items where **every** distractor names a misconception | **22** |
| items where **none** do | **3,771** |
| distractors carrying a named misconception | **66 of 11,379 — 0.6%** |

This is the L50 pattern in its most expensive form yet: *a parameter present in a field is
indistinguishable from a parameter that means something.* The architecture is right and 99.4% of
it is unbuilt.

### Free text cannot aggregate — the taxonomy is the real deliverable

All 66 existing misconceptions are distinct free-text sentences: *"assumes excavation was
manual"*, *"assigns the canal to the preceding administration"*. Two items teaching the **same**
confusion carry two different sentences, and nothing can count them together.

So the load-bearing artifact is not the item bank. It is a **controlled misconception taxonomy**
— stable IDs, reusable across items, standards and courses — because only an ID recurs, and only
a recurring thing can be counted, trended, or routed to a resource.

- [x] **14 structural families built** — `taxonomy/misconception-families.json`. A family is a
      REASONING ERROR (chronological displacement, agent substitution, causation reversal, source
      purpose confusion…), course-independent, so a student showing the same family across US and
      World is a transferable finding rather than two content gaps. **DRAFT — needs your read
      before mass authoring cites them.**
- [x] **`gate_misconception_taxonomy` built and wired.** Free text without a family ID now fails.
      It currently names its own backlog: the 66 legacy free-text misconceptions need family IDs
- [ ] Author content-level misconceptions per item, each citing a family, as items are written
- [ ] Backfill 11,313 distractor misconceptions against the taxonomy *(this is larger than the
      item authoring itself — see §0)*
- [ ] Every taxonomy entry links to a reteach resource. The lecture packs, Frayer models and
      DBQ activities already exist in `history-hack-web-app` and are the obvious targets

### The response layer — none of this exists

- [ ] **Administration model**: form family, form ID, roster, date, setting
- [ ] **Response model**: student × item × chosen option × time. **The chosen option, not just
      right/wrong** — a bank that records only scores throws away every diagnosis it was built
      to make
- [ ] **Item analytics**: p-value, point-biserial, distractor pull per option, flag any item
      where a distractor outperforms the key
- [ ] **Real IRT calibration.** 3,926 items carry IRT parameters and **all 3,928 are
      `pre-field-test`** — estimated, never met a student. They are placeholders and must be
      disclosed as such until responses replace them
- [ ] **Mastery reporting**: student / class / standard, and **misconception-level**, which is
      the part a competitor's standard-level rollup does not give a teacher
- [ ] **Privacy before any of it**: student response data is FERPA-regulated. Data model,
      retention, and who can see what — decided *before* the first row is written, not after.
      **Flag for legal review.**

### On "better than Performance Matters"

I can say what would differentiate this: **misconception-level diagnosis with reteach routing**,
built on a taxonomy, from items that were written to diagnose rather than merely to be wrong.
That is a real architectural advantage and it is achievable.

I cannot say it is better than a shipping product, and neither should any deck. That is a
competitive claim requiring evidence this project does not have — no item here has met a student,
no parameter is calibrated, and there is no response data at all. **Build the capability, prove
it in your own classroom, then make the claim with data behind it.**

### Revised sequence

| phase | work |
|---|---|
| ~~**1**~~ | ~~Six course bindings + committed blueprints~~ — **DONE 2026-09-05**, `tools/scaffold_course.py` |
| ~~**2**~~ | ~~Misconception taxonomy v1~~ — **families DONE**, `taxonomy/misconception-families.json` (DRAFT, needs your read) |
| **3** | Stimulus programme: repair the 111, source assets, `gate_stimulus_integrity` (§3) |
| **4** | Parallelism gates, built against the existing US bank (§5) |
| **5** | Generate → gate → regenerate, course by course, taxonomy IDs from the first item |
| **6** | Response + analytics layer, ready before first administration |
| **7** | First administration, next school year → real calibration |

**Phase 2 moved ahead of authoring deliberately.** Every item authored without a taxonomy ID is
an item that has to be revisited to be useful — and at 3,764 items that is the difference
between a data bank and a pile of questions.

---

## 10. Building now, students next year (Sean, 2026-09-05)

*"I don't want a pilot era. What I'm doing right now is creating all of the data banks. This
will not see students until next year."*

That reorders what is urgent, and the line is clean:

**Must be right NOW — it lives inside the item record and costs a full pass to change later:**
misconception taxonomy ID per distractor · DOK level and its written rationale · standard codes
and alignment evidence · stimulus asset with rights and citation · bilingual twins · reporting
category provenance.

**Can wait — it is an assembly decision that touches no item:** form length, unit vs whole-course
packaging, how many parallel forms, which standards sit on which form, print layout. The bank
does not change when you change your mind about any of these.

So the §9 form-architecture note (whole-course forms run 94–188 items; era grouping gives ~18)
is **recorded and deferred**. It is a next-year decision.

**No pilot.** The earlier recommendation to prove one era in class first was right for a
validation phase and wrong for this one. The consequence to hold onto: nothing in these banks
will be calibrated until administration next year, so **every IRT parameter stays
`pre-field-test` and every surface keeps saying so.** 3,928 items already carry estimates that
have never met a student.

### The foundation question, re-measured

Earlier the call was to save the migrated bank — the content was sound and only alignment was
uncertain. **That was right then and the requirements have changed.** The bank now has to carry
a named misconception on every distractor, and it does not.

| | authoring units | on what foundation |
|---|---|---|
| **A — retrofit the existing bank** | 5,625 distractor fields + 3,440 fresh items + 324 = **9,389** | items that also carry the 53% key-longest cue and unverified alignment |
| **B — generate fresh through the gated loop** | **4,358 items** | clean by construction; misconceptions and taxonomy IDs written with the item |

**Path B is less than half the work and produces the better bank.** Retrofit is per-DISTRACTOR
authoring; fresh is per-ITEM, and the item arrives with its misconceptions already in it.

- [ ] Adopt Path B for all six courses
- [ ] **Nothing is deleted.** The existing 3,928 items stay as content reference, as a fallback
      where generation struggles, and as the source of the DBQ activities already built
