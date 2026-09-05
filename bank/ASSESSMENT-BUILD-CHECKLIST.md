# Assessment build checklist — six courses, five parallel forms

**Written 2026-09-05. Every number here was measured, not estimated.** Re-derive them with
`python3 tools/course_scope.py [--per-form 1|2]` — a number in prose is a claim that rots, and
this repo has already been bitten by that twice.

**The ask:** enough MCQ items to build a minimum of **5 parallel forms** per course, equal in
rigor, testing the same content, with **every single standard assessed**. DBQs and LEQs stay
separate. Primary sources permitted as appropriately-short excerpts. Images, political cartoons,
charts and graphs included.

---

## 0. The one decision that sizes everything

**How many MCQ items per standard, per form?**

| | depth needed per standard | standards ready today | **MCQ items still to author** |
|---|---|---|---|
| **1 item / standard / form** | 5 DOK-matched | 65 / 438 | **1,819** |
| **2 items / standard / form** (recommended) | 10 DOK-matched | 38 / 438 | **3,764** |

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

## 6. DBQ / LEQ — separate, already built for U.S.

The architecture is done and holds for the new courses:

- [x] Assessment forms are selected-response only (`surface: assessment`, `allowedItemTypes`)
- [x] 34 U.S. DBQs build as standalone branded activities with source cards, citations, HIPP
      scaffolds and teacher scoring guides
- [ ] Extend `dbq_activity.py` to the other five courses
- [ ] **LEQs do not exist yet** in any course — no item type, no rubric shape, no builder

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
