# Governance — two standards years, running side by side

**Read this before building anything for 2027-28.**

History Hack now carries two live standards sets at once. The 2026-27 set is what Tennessee teachers
are teaching **this** school year, and it stays current and untouched. The 2027-28 set is what
**every new course build targets** — there is no capacity to build the new courses twice, so nothing
new gets built against the old standards.

Running two sets side by side is normal. Letting them touch is not. This file is the contract that
keeps them apart.

---

## 1. One owner per fact

| Fact | Owner | Everyone else |
|---|---|---|
| The 2026-27 standard text | `2026-27-Tn.-Social-Studies-Standards` | reads it |
| The 2027-28 standard text | **this repo** | reads it |
| How a 2026-27 code maps to a 2027-28 code | **this repo**, `crosswalk/` | reads it |
| Primary sources keyed to 2026-27 | `-2026-27-Social-Studies-Primary-Sources` | reads it |
| Built lessons, decks, packs, delivery | `history-hack-web-app` | — |

Nothing is copied between these. A standard's text is never re-typed into a build, a skill, a deck,
or a spec — it is read from the owning repo at build time. A second copy is a second version, and
the second version is always the one that goes stale.

## 2. A standard code is not a stable identifier

This is the rule everything else hangs off.

> In 2026-27, `US.01` is the Homestead Act and the Transcontinental Railroad.
> In 2027-28, `US.01` is Reconstruction and the Compromise of 1877.
> The Homestead Act standard still exists — it is now `US.04`.

**416 codes exist in both years and mean different things**, including **84 of the 94** U.S. History
codes and **72 of the 74** Grade 8 codes. They are enumerated in `crosswalk/collisions.csv`.

Consequences, all mandatory:

- **Every reference to a standard carries its year.** `US.12` is ambiguous. `US.12 (2027-28)` is not.
  Data files carry `standardsYear`; filenames, folders and routes carry the year in the path.
- **Never carry an asset forward by code.** Not a primary source, not a question, not an image, not a
  Cornell packet, not a biography card. Matching codes are the *least* reliable signal available.
- **Never write a gate, script, or query that joins the two years on `code`.** It will match, it will
  look right, and it will be wrong 416 times.

## 3. Reuse goes through the crosswalk, by content — and the code is stripped

Sean's requirement is that we reuse what is relevant from the existing library rather than rebuild
it. That reuse is legitimate. It just has to be re-pointed rather than assumed, and **the old code
never comes with it.**

> **Sean, 2026-08-28: anything pulled over from the 2026-27 library is stripped of the standard code
> and added to the current standard of the new approved 2027-28 standards. Carried over by content
> category, never by code.**

A 2026-27 code riding along on a carried asset is a live landmine: it matches, it renders, and it
mislabels. So it does not travel with the asset at all. It is recorded **once**, in a migration
ledger that lives outside the content tree, and nowhere else.

To reuse an existing asset for a 2027-28 standard:

1. Look up the **2026-27** code in `crosswalk/<course>.csv` and read its `disposition`:
   - **`unchanged`** — the same standard, possibly re-coded. The content carries forward.
   - **`revised`** — recognisably the same standard, reworded. Read BOTH sentences. The words after
     "including" in the state's sentence are a content checklist; if the revision added a named
     person, event or act, the asset does not yet cover the standard.
   - **`retired`** — no successor. Nothing carries. Its assets stay where they are, serving 2026-27.
   - **`new`** — no origin. Build it. There is nothing to carry forward, and reaching for the
     nearest-looking old asset is how the wrong lesson ships.
2. **Strip the old code from the asset** — out of every field, out of the filename, and out of the
   prose. Standard codes turn up inside student-facing sentences ("TN U.S. History standard US.04
   asks students to…"), where no field-level strip will find them.
3. **Re-attach it to a 2027-28 standard chosen on content**, and stamp it `standardsYear: "2027-28"`.
   The right home is often **not** the crosswalk's successor: the crosswalk maps *standards*, and
   this is an *asset*. A Carnegie portrait hanging on 2026-27 `US.04` belongs on 2027-28 `US.09`,
   which names Carnegie — not on `US.08`, which is `US.04`'s standard-level successor, and certainly
   not on `US.04`, which is now the Homestead Act.
4. **Categorise it** with an era or cluster heading from that course's own 2027-28 standards. Those
   headings are the state document's, not ours, and they are the category the carry-forward is made
   on.
5. **Record it once** in the migration ledger, outside the content tree: asset id, old code, new
   codes, content category, disposition, and who reviewed it.

**13 of the 20 courses have no 2026-27 counterpart at all** — K–5, African American History, Ancient
History, Contemporary Issues, Economics, Psychology, Sociology, World Geography. For those, step 1
has no row and the answer is always "build it".

In `history-hack-web-app` this is mechanised and enforced: `scripts/carry-forward.mjs` does the
stripping and refuses when a code is embedded in prose, and `npm run check:carry-forward` fails a
stray old code in a file or filename, a match made by code, a missing or unknown content category,
an unrecorded carry, and a `retired`/`new` disposition.

## 4. Namespace isolation in the web app

2027-28 is a **new section** of `history-hack-web-app`, not a change to the existing one. The current
year's content keeps working exactly as it does today, on the paths it already uses.

- 2027-28 data lives under a `2027-28` path segment, in its own tree. Existing paths are not moved,
  renamed, or re-pointed.
- 2027-28 routes live under a `2027-28` segment. Existing routes are untouched.
- 2027-28 deliverables live under a `2027-28` deliverables directory.
- **No file is shared between the two trees.** If both years need the same image, each tree points at
  its own copy under its own year, with its own standard code and its own citation. A shared file is
  a file that one year's edit silently changes for the other.
- Nothing in a 2027-28 path may read a 2026-27 path, and nothing in a 2026-27 path may read a
  2027-28 path.

## 5. What 2027-28 builds are, and are not

- **Cornell notes are built from the standard**, as soon as it is unpacked. That is the deliverable.
- **There are no slide decks for 2027-28.** The 2026-27 lecture-build cycle runs OER section → deck →
  Cornell → every other handout. With no OER for the new standards, that chain has no first link, so
  the Cornell notes are authored from the unpacked standard directly. A 2027-28 pack containing a
  deck is a pack that was cloned from a 2026-27 pack, and it is carrying that pack's lesson.
- **The QC process does not change.** The same gates, the same Grade-A release bar, the same
  accessibility and adoption reviews apply to 2027-28 work. A new standards year is not a reason for
  a new quality bar, and the gates are the reason the builds live beside them.

## 6. Unpacking a standard

"Unpacking" produces, per standard, from the verbatim text in this repo and nothing else:

- the standard's **named elements** — every person, event, act, case and term the sentence names,
  especially everything after "including", which is a content checklist and not decoration
- its **content strands** (`strand`) and whether it is **legally required** (`tca`)
- its **era** and **cluster**, which are the document's own headings, not ours
- the **Social Studies Practices** the standard can carry (`practices`, SSP.01–SSP.06)

Every one of those fields is already in `standards/<course>.json`. Unpacking reads them; it does not
re-derive them from a PDF, a summary, or memory.

## 7. Two traps that have already cost us

Both are recorded in the web app's build memory. They are repeated here because this is the file
someone reads when starting a new course.

- **Scaffolding a pack is not building one.** A cloned pack renders perfectly while teaching the
  wrong standard — right page count, no blank slides, legible type, and someone else's lesson. Mark
  an unauthored pack unauthored and do not render it.
- **A source of truth you did not read is indistinguishable from one you did**, until something
  measures it. Nine decks once shipped at 8%–54% coverage of their source because coverage was
  reported and never enforced. Whatever measures 2027-28 coverage must **fail**, not report.
