# Status — US History and Geography item bank

**HELD.** Not Grade A. Not shippable. This file is the honest measurement.

BINDING — course: United States History and Geography (us-history-geography) · prefix: US · standards year: 2027-28 · standards file: ../standards/us-history-geography.json · output: /home/user/2027-28-Tn-Social-Studies-Standards/bank/items/us-history-geography

## Gates

| Gate | Result | Scanned | Findings |
|---|---|---|---|
| `record-complete` | **FAIL** | 1511 | 1492 |
| `binding` | **PASS** | 1511 | 0 |
| `key-integrity` | **PASS** | 1511 | 0 |
| `distractor-coverage` | **FAIL** | 1511 | 8922 |
| `truncation` | **FAIL** | 1511 | 29 |
| `blueprint-conformance` | **FAIL** | 1511 | 731 |
| `key-position-debias` | **PASS** | 1487 | 0 |
| `serveability` | **FAIL** | 1511 | 429 |
| `reporting-category-provenance` | **PASS** | 1511 | 0 |
| `teacher-side-isolation` | **PASS** | 1511 | 0 |

**5/10 gates pass.** Grade A requires all of them. "Close" is not "A."

## Bank composition

- Source: 5,045 items from the 2026-27 `history-hack-web-app` bank
- Servable after migration at floor 0.90: **1511** (1151 migrated, 360 provisional)
- Quarantined (not servable, not coverage): **3534**
- Standards with at least one servable item: **30/94**
- Standards receiving nothing: **64**

## Authoring debt

| Gap | Count |
|---|---|
| distractor rationales absent | 4461 |
| items with no dokRationale | 1414 |
| items with no stemEs | 221 |
| items with no explanationEs | 208 |
| standards with no reporting-category source | 94 |

## Blocking decisions (Sean)

1. **Migration floor** — currently 0.90. Sensitivity:

| floor | migrated | provisional | quarantined | standards covered |
|---|---|---|---|---|
| 1.00 | 1151 | 0 | 3894 | 23/94 |
| 0.95 | 1151 | 0 | 3894 | 23/94 |
| 0.90 | 1151 | 360 | 3534 | 30/94 |
| 0.85 | 1151 | 1048 | 2846 | 43/94 |
| 0.80 | 1151 | 1381 | 2513 | 48/94 |
| none | 1151 | 2964 | 930 | 76/94 |

   Even accepting every revised mapping, 18 standards are genuinely new and receive nothing.

2. **Reporting-category source** — 94/94 rows `UNMAPPED`. Needs the TDOE blueprint, or a decision to author an `interim-district` mapping.
3. **Blueprint approval** — the committed blueprint is `DRAFT` (6/std, DOK 2/2/1/1).
4. **Repo location** — built inside the standards repo under `bank/` as a self-contained, extractable tree. Reversible with `git subtree split`.

## Separate finding — existing app

`history-hack-web-app/lib/trivia-questions.ts:158` fetches the item bank from `public/`, so every stem, `correctAnswer` and `explanation` — including 213 teacher-tier items — is served as a static file with no auth. That is a **Critical** against the teacher-side-only guardrail, in the live app, independent of this repo.
