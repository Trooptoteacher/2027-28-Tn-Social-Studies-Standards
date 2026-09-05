#!/usr/bin/env python3
"""Stand up a walled course: its binding and its blueprint, before any item exists.

One shared toolchain, many walled courses — never crossed. The binding is the
wall and it is written FIRST, because a generator that will happily emit another
course's prefix will eventually do it. Adding a course is a deliberate,
reproducible edit, which is why this is a committed tool rather than six files
someone hand-wrote once.

THE BLUEPRINT IS BACKWARD DESIGN. It exists before a single item is written and
the bank is measured against it. Depth is 2 items per standard per form x 5
parallel forms = 10 DOK-MATCHED items per standard (Sean, 2026-09-05): a
misconception seen once is noise, seen twice on two independently authored items
it is a diagnosis, and diagnosis is the product.

The DOK pair is DERIVED FROM THE STANDARD'S OWN VERB, not set flat. A standard
that says "Identify" cannot honestly carry DOK-3 items; one that says "Analyze"
should not be assessed at recall. alignment.VERB_TIER is the one definition of
that ladder and it is shared with the migration router, so the blueprint and the
alignment layer cannot disagree about what a standard demands.

Usage:
  python3 tools/scaffold_course.py --list
  python3 tools/scaffold_course.py grade-08 [--apply]
  python3 tools/scaffold_course.py --all --apply
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import alignment
import itemio

REPO = os.path.dirname(itemio.BANK_ROOT)
STD_DIR = os.path.join(REPO, "standards")

# The six courses in scope. Named, never globbed — "never build a unit with a
# wildcard" applies to courses too.
IN_SCOPE = ["grade-06", "grade-07", "grade-08", "us-history-geography",
            "world-history-geography", "tennessee-history"]

SR = ["mcq", "multiple-select"]

# The form ladder is COURSE-INDEPENDENT and is carried into every blueprint,
# because the form builder and four form gates read it. Scaffolding a course
# without it silently removes the tiers those gates resolve against — which is
# exactly what happened the first time this tool ran: it rewrote the working US
# blueprint and FORM-A stopped building on a KeyError.
FORM_LADDER = {
    "surface": "assessment",
    "allowedItemTypes": SR,
    "$formNote": ("Form PACKAGING — length, unit vs whole-course, which standards sit on "
                  "which form — is an assembly decision that touches no item and is deferred "
                  "to next year. Whole-course forms would run 62-188 items; era grouping "
                  "gives roughly 18. Decide when forms are built."),
    "dokCeilingRationale": ("DOK-4 is structurally impossible in a selected-response item, so "
                            "a selected-response form CANNOT assess it and must say so on the "
                            "page rather than pretend."),
    "itemCount": 6,
    "tiers": [
        {"id": "tcap-standard", "label": "TCAP-style form — selected response, DOK 1-3",
         "dokCeiling": 3,
         "slots": [{"types": SR, "dok": 1}, {"types": SR, "dok": 1},
                   {"types": SR, "dok": 2}, {"types": SR, "dok": 2},
                   {"types": SR, "dok": 3}, {"types": SR, "dok": 3}]},
        {"id": "tcap-short", "label": "TCAP-style short form — selected response, DOK 1-3",
         "dokCeiling": 3,
         "slots": [{"types": SR, "dok": 1}, {"types": SR, "dok": 2},
                   {"types": SR, "dok": 2}, {"types": SR, "dok": 3}]},
        {"id": "tcap-floor", "label": "TCAP-style floor form — selected response, DOK 1-2 only",
         "dokCeiling": 2,
         "slots": [{"types": SR, "dok": 1}, {"types": SR, "dok": 2},
                   {"types": SR, "dok": 2}]},
    ],
    "disclosureByCeiling": {
        "3": ("This is a selected-response form. It assesses Depth of Knowledge levels 1 "
              "through 3. It carries no extended-response item, so it does not assess DOK-4 — "
              "a four-option question cannot ask a student to construct and defend an "
              "argument. Extended responses and document-based questions are delivered as "
              "separate activities."),
        "2": ("This is a selected-response form. It assesses Depth of Knowledge levels 1 and 2 "
              "only — the bank does not yet hold enough DOK-3 selected-response items aligned "
              "to this standard to build a fuller form. It does not assess DOK-3 or DOK-4."),
    },
}

FORMS = 5
PER_FORM = 2
DEPTH = FORMS * PER_FORM          # 10 DOK-matched items per standard
MCQ_DOK_CEILING = 3               # a four-option item cannot reach DOK-4


def all_prefixes():
    """Every prefix TDOE publishes, so a wall can name the others explicitly."""
    out = {}
    for fn in sorted(os.listdir(STD_DIR)):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(STD_DIR, fn), encoding="utf-8") as fh:
            out[fn[:-5]] = json.load(fh).get("standardsPrefix")
    return out


def dok_pair(text):
    """The two DOK levels this standard is assessed at. MEASURED, not tuned.

    Parallelism forces exactly two levels per standard: each of the 5 forms
    takes 2 items on the standard, so the profile must be identical across
    forms — 5 at one level, 5 at the other.

    The rule: a standard is assessed at DOK 1-2 when its verb is low AND it
    NAMES A CHECKLIST ("...including the Sherman Antitrust Act of 1890"),
    because a named element is content a student can legitimately be asked to
    recall. A standard with no checklist has nothing to name — "Analyze the
    increasing impact of television" cannot be honestly assessed at recall — so
    it starts at DOK 2.

    Two simpler rules were computed first and both failed at the bank level.
    Treating the verb as a CEILING gave 45/44/11, which is the drift-to-recall
    the blueprint exists to prevent. Treating it as a FLOOR gave 6/39/55, which
    leaves a formative bank with almost no accessible entry point. This rule
    gives 26/50/24 across all 4,380 items and was not tuned to do so — the
    distribution is what fell out of asking whether the standard names anything.

    Capped at 3 throughout: DOK-4 is structurally impossible in a
    selected-response item, and a blueprint that asked for it would be
    unmeetable by construction — the defect that made the previous blueprint
    unbuildable for 71 of 94 standards.
    """
    tier = alignment.VERB_TIER.get(alignment.verb(text), 2)
    names_content = bool(alignment.elements(text))
    if tier <= 2 and names_content:
        return 1, 2
    return 2, min(MCQ_DOK_CEILING, 3)


def build(slug, prefixes):
    path = os.path.join(STD_DIR, f"{slug}.json")
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    pre = doc["standardsPrefix"]
    stds = doc.get("standards") or []
    if not stds:
        raise SystemExit(f"{slug}: standards file defines nothing — refusing to scaffold")

    forbidden = sorted({p for p in prefixes.values() if p and p != pre})
    binding = {
        "$comment": ("THE BINDING. Every generator and every gate loads this file and asserts "
                     "against it. One shared toolchain, many walled courses. A generator that "
                     "will happily emit another course's prefix will eventually do it."),
        "bindingVersion": 1,
        "course": slug,
        "courseTitle": doc.get("title", slug),
        "standardsPrefix": pre,
        "standardsYear": doc.get("standardsYear", "2027-28"),
        "standardsFile": f"../standards/{slug}.json",
        "standardsSourceDocument": "TN-Social-Studies-Standards-2027-28.pdf",
        "crosswalkFile": f"../crosswalk/{slug}.csv",
        "outputDir": f"items/{slug}",
        "quarantineDir": f"quarantine/{slug}",
        "blueprintFile": f"blueprints/{slug}.blueprint.json",
        "reportingCategoryFile": f"reporting-categories/{slug}.json",
        "forbiddenPrefixes": {
            "$comment": ("Every OTHER TN course prefix. Listed explicitly rather than inferred, "
                         "so adding a course is a deliberate edit and a typo cannot silently "
                         "widen the wall."),
            "prefixes": forbidden,
        },
        "forbiddenStandardsYears": {
            "$comment": ("A standard code is not a stable identifier across years — 84 of the "
                         "94 US codes changed meaning between 2026-27 and 2027-28. Any item "
                         "still claiming the prior year is a hard failure, not a warning."),
            "years": ["2026-27"],
        },
        "disclosureLine": "classroom-formative · pre-field-test",
    }

    per, tally, levels = {}, collections.Counter(), collections.Counter()
    for s in stds:
        txt = s.get("text", "")
        lo, hi = dok_pair(txt)
        half = DEPTH // 2
        dok = {str(lo): half, str(hi): DEPTH - half}
        tally[f"DOK {lo}-{hi}"] += 1
        levels[lo] += half
        levels[hi] += DEPTH - half
        per[s["code"]] = {"itemCount": DEPTH, "dok": dok,
                          "itemType": {"mcq": DEPTH},
                          "verb": alignment.verb(txt),
                          "namesContent": bool(alignment.elements(txt)),
                          "dokReason": (
                              "verb tier and whether the standard names a checklist; capped at "
                              "3 because a four-option item cannot ask a student to construct "
                              "and defend an argument")}

    blueprint = {
        "$comment": ("BACKWARD DESIGN. Committed before a single item is written; the bank is "
                     "measured against it per standard, per DOK, per item type, and drift "
                     "fails in EITHER direction. Depth is 2 items per standard per form x 5 "
                     "parallel forms = 10 DOK-MATCHED items. Five items at DOK 1,2,2,3,3 do "
                     "not build five equal forms — they build one form and four different "
                     "ones — so the target is depth AT A LEVEL, never raw count."),
        "blueprintVersion": 1,
        "course": slug,
        "standardsPrefix": pre,
        "standardsYear": binding["standardsYear"],
        "status": "SCAFFOLDED 2026-09-05 — 2x depth locked by Sean Reynolds; per-standard DOK "
                  "derived from each standard's verb, not set flat",
        "parallelForms": FORMS,
        "itemsPerStandardPerForm": PER_FORM,
        "depthPerStandard": DEPTH,
        "rationale": {
            "depth": ("A misconception detected once is noise; detected twice, on two "
                      "independently authored items, is a diagnosis. Misconception-level "
                      "remediation is the product, so 1x is not a cheaper version of it."),
            "dokFromVerb": ("A standard that says 'Identify' cannot honestly carry DOK-3 "
                            "items; one that says 'Analyze' should not be assessed at recall. "
                            "Shared with the alignment router via alignment.VERB_TIER."),
            "mcqOnly": ("Assessment forms are selected response (Sean, 2026-09-03). DBQs are "
                        "delivered as separate activities; LEQs are out of scope."),
        },
        "form": FORM_LADDER,
        "bank": {
            "$comment": ("How the BANK is measured, as opposed to a form. A form must match its "
                         "tier exactly and fails in either direction; a bank of thousands "
                         "measured against an exact target could only ever fail, and 'too many "
                         "items' is depth, not drift. So: a minimum depth per standard plus the "
                         "DOK proportion. The proportion is this blueprint's OWN computed "
                         "distribution, so the target and the design cannot drift apart — the "
                         "previous default was a hard-coded 33/33/17/17 that reserved 17% for "
                         "DOK-4, which a selected-response bank can never contain."),
            "minPerStandard": DEPTH,
            "dokProportion": {str(k): round(levels[k] / sum(levels.values()), 4)
                              for k in sorted(levels)},
            "proportionTolerance": 0.10,
        },
        "dokDistribution": {
            "$comment": ("The aggregate this course's per-standard pairs produce. Stated so it "
                         "is a measured fact rather than an emergent surprise — a bank that "
                         "drifts to recall is the failure mode this blueprint exists to catch, "
                         "and it is invisible one standard at a time."),
            "items": sum(levels.values()),
            "byLevel": {str(k): levels[k] for k in sorted(levels)},
            "share": {str(k): round(levels[k] / sum(levels.values()) * 100, 1)
                      for k in sorted(levels)},
        },
        "perStandard": per,
    }
    return binding, blueprint, tally, len(stds), levels


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("course", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="overwrite an existing binding or blueprint (says what is lost first)")
    a = ap.parse_args()

    prefixes = all_prefixes()
    if a.list:
        for slug in IN_SCOPE:
            print(f"  {slug:<26} prefix {prefixes.get(slug)}")
        return 0

    targets = IN_SCOPE if a.all else ([a.course] if a.course else [])
    if not targets:
        print("name a course, or --all. Never a wildcard.")
        return 1
    for slug in targets:
        if slug not in IN_SCOPE:
            print(f"{slug} is not in the declared scope {IN_SCOPE}")
            return 1

    for slug in targets:
        binding, blueprint, tally, n, levels = build(slug, prefixes)
        bp_path = os.path.join(itemio.BANK_ROOT, binding["blueprintFile"])
        bn_path = os.path.join(itemio.BANK_ROOT, "bindings", f"{slug}.json")
        print(f"\n{slug} — prefix {binding['standardsPrefix']}, {n} standards, "
              f"{n * DEPTH:,} items at depth {DEPTH}")
        print(f"   walls off {len(binding['forbiddenPrefixes']['prefixes'])} other prefix(es)")
        for k, v in sorted(tally.items()):
            print(f"   {v:>4} standard(s) -> {k}")
        tot = sum(levels.values())
        print("   aggregate DOK: " + " · ".join(
            f"DOK{k} {levels[k] / tot * 100:.0f}%" for k in sorted(levels)))
        if not a.apply:
            continue
        # A scaffolder that silently overwrites a live file is how the working
        # US form definition was destroyed on this tool's first run: the new
        # blueprint had no `tiers`, and FORM-A stopped building on a KeyError.
        # Scaffolding is for standing a course UP, not for rewriting one that
        # is already carrying work.
        existing = [p for p in (bn_path, bp_path) if os.path.exists(p)]
        if existing and not a.force:
            print("   REFUSED — already exists: "
                  + ", ".join(os.path.relpath(p, itemio.BANK_ROOT) for p in existing))
            print("   Scaffolding is for standing a course up. Pass --force only if you have "
                  "read what is in there and mean to replace it.")
            continue
        for p, doc in ((bn_path, binding), (bp_path, blueprint)):
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as fh:
                json.dump(doc, fh, indent=2, ensure_ascii=False)
        for d in (binding["outputDir"], binding["quarantineDir"]):
            os.makedirs(os.path.join(itemio.BANK_ROOT, d), exist_ok=True)
        print(f"   -> bindings/{slug}.json  +  {binding['blueprintFile']}")
    if not a.apply:
        print("\nDRY RUN — pass --apply to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
