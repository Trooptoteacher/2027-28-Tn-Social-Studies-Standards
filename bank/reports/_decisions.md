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

**5. Forms are built and gated (`tools/forms.py`).**
Student form and teacher key render from ONE assembly with ONE deterministic
choice ordering, so a key letter cannot drift between the two surfaces. The
student surface is built by OMISSION at assembly time, not by hiding anything at
render time. Page numbering lives in the `@page` margin box: rendering the same
form with a fixed footer div was measured and it freezes at **"Page 1 of 5" on
every page**, exactly as the guardrail predicted. Four print gates read the
rendered PDF — pagination, the 9 pt floor measured glyph by glyph, key leakage,
and the calibration disclosure — each proven in `tests/test_form_gates.py`.

**6. A gate that judged nothing no longer reports PASS.**
`teacher-side-isolation` was reporting **PASS over 3,986 items while judging
zero**, because its inner filter removed everything and the empty-scan guard only
watched the outer scan. Results now carry a `judged` count and report
`NOT MEASURED`, which is not a pass; an `all-gates-measured` gate holds the
release while any gate formed no opinion. The gate itself moved to form scope,
where it has something real to judge.

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
