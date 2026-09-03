# Status — US History and Geography item bank

**HELD.** Not Grade A. This file is the measurement, not a summary of intent.

```
BINDING — course: United States History and Geography (us-history-geography) · prefix: US · standards year: 2027-28 · standards file: ../standards/us-history-geography.json · output: /home/user/2027-28-Tn-Social-Studies-Standards/bank/items/us-history-geography
```

## Gates

| Gate | Result | Scanned | Findings |
|---|---|---|---|
| `record-complete` | **FAIL** | 3986 | 3868 |
| `binding` | **PASS** | 3986 | 0 |
| `key-integrity` | **PASS** | 3986 | 0 |
| `distractor-coverage` | **FAIL** | 3986 | 23064 |
| `truncation` | **FAIL** | 3986 | 100 |
| `blueprint-conformance` | **FAIL** | 3986 | 681 |
| `key-position-debias` | **PASS** | 3844 | 0 |
| `serveability` | **FAIL** | 3986 | 1014 |
| `reporting-category-provenance` | **PASS** | 3986 | 0 |
| `teacher-side-isolation` | **PASS** | 3986 | 0 |
| `release-readiness` | **FAIL** | 3986 | 6 |

**5/11 pass.** Grade A requires all of them.

## Bank

- Source: **5,045** items from the 2026-27 `history-hack-web-app` bank
- Servable: **3986** (3779 migrated, 207 provisional)
- Quarantined (not servable, not coverage): **1059**
  - 929 — standard retired / no 2027-28 home
  - 130 — tests an element the 2027-28 standard dropped
- Standards with a servable item: **76/94**
- Standards receiving nothing: **18** — US.01, US.02, US.03, US.07, US.09, US.40, US.50, US.53, US.55, US.57, US.71, US.75, US.77, US.87, US.89, US.91, US.93, US.94

## Authoring debt

| Gap | Count |
|---|---|
| distractor rationales absent | 11532 |
| items with no dokRationale | 3728 |
| items with no stemEs | 522 |
| items with no explanationEs | 492 |
| standards with no reporting-category source | 94 |

## Decisions taken

Sean delegated these. Each is recorded with what it was decided against, and each
is reversible by editing one committed file.

**1. Migration routing — the similarity floor was REMOVED, not tuned.**
Measurement showed `difflib` character similarity is anti-correlated with alignment:
`US.16→US.17` scores 0.79 and is a pure bullet reorder, while `US.12` scores 0.89
having deleted the Clayton Antitrust Act, and `US.60` scores 0.94 having changed its
verb from *Explain* to *Analyze*. Routing is now by **element-level delta** — the
standard's content checklist — in `tools/alignment.py`, pinned by
`tests/test_alignment.py`. An item is quarantined only when it tests an element the
2027-28 standard actually dropped, and the finding names that element.
Effect: 3,986 servable across 76/94 standards, versus 1,511 across 30/94 under a
0.90 floor.

**2. `reportingCategory` — left UNMAPPED. No interim mapping authored.**
Authoring one would be fabrication dressed as data, against the source-of-truth
guardrail. TDOE's US History EOC blueprint is keyed to the 2026-27 standards and none
exists for 2027-28. The provenance gate reads green over all-`UNMAPPED` because
consistency is all it can check — so a **`release-readiness`** gate was added that
HOLDS on it. A green column over 94 unsourced categories is the same trap as a gate
green over an empty set.

**3. Blueprint — adopted as an OPERATING TARGET, not signed off.**
6 items/standard, DOK 2/2/1/1, 4 mcq + 1 CR + 1 DBQ. Kept deliberately modest:
`blueprint-conformance` fails in both directions, so a target set too high can never
go green. `release-readiness` holds while the status reads `operating`.

**4. Repo — kept at `bank/` inside the standards repo.**
Not just convenience: the bank is derived from `standards/` and `crosswalk/`, and
co-locating them means the three can never drift out of version sync. Split out with
`git subtree split` if it moves — and it would then have to pin this repo by commit
SHA, which is the coupling co-location gives free.

## What is NOT decided

- The 18 standards receiving nothing are genuinely new. No routing choice reaches
  them; they are original authoring.
- Every servable item still needs distractor rationales written. That is the
  largest single piece of work in the project and no tool can shortcut it.

## Separate finding — the live app

`history-hack-web-app/lib/trivia-questions.ts:158` fetches the bank from `public/`, so
every stem, `correctAnswer` and `explanation` — including 213 teacher-tier items — is
served as a static file with no auth. **Critical** against the teacher-side-only
guardrail, in the shipping app, independent of this repo.
