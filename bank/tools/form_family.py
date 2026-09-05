#!/usr/bin/env python3
"""Build a FAMILY of parallel forms — N versions of the same test.

"Five parallel tests, equal in rigor, testing the same content" (Sean) is a
claim about a SET of forms, and nothing in this repo measured a set. Each form
was gated on its own and could pass every gate while being a different test
from its siblings.

Parallel means, exactly: same standards, same count, same DOK profile, same
stimulus mix, ZERO shared items. The allocation here is what makes that true by
construction — per standard, take the two DOK levels the blueprint declares,
pull N items from each, and deal one of each into every form. A standard that
cannot supply N at BOTH levels does not go on the family at all, because a
standard present on three forms and absent from two is the divergence the whole
exercise exists to prevent.

Usage:
  python3 tools/form_family.py US-CORE --forms 5 --standards US.46 US.60 US.74
  python3 tools/form_family.py US-CORE --forms 5 --standards ... --apply
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import alignment
import binding as binding_mod
import forms as formbuild
import itemio

FAMILY_DIR = os.path.join(itemio.BANK_ROOT, "forms", "families")


def per_standard_pool(items, standards, b):
    """Aligned, per-standard-relevant MCQs, grouped by DOK.

    Same placement rule the single-form builder uses — an item counts toward a
    standard only if it is relevant to THAT standard.
    """
    stds = b.standards()
    pool = collections.defaultdict(lambda: collections.defaultdict(list))
    for it in items:
        if not itemio.aligned(it) or it.get("itemType") not in ("mcq", "multiple-select"):
            continue
        hay = alignment.subject_text(it)
        for c in (it.get("standardCodes") or []):
            if c not in standards:
                continue
            t = (stds.get(c) or {}).get("text")
            if t and alignment.relevant_to(hay, t):
                pool[c][it.get("dokLevel")].append(it)
    return pool


def allocate(pool, standards, blueprint, n_forms):
    """{form_index: [items]} plus the standards that could not be carried.

    Deterministic: items are sorted by id and dealt round-robin, so the same
    bank and the same request always produce the same family.
    """
    per = blueprint.get("perStandard") or {}
    forms = {i: [] for i in range(n_forms)}
    dropped, profile = {}, {}
    for code in standards:
        want = per.get(code, {}).get("dok") or {}
        levels = sorted(int(k) for k in want)
        if len(levels) != 2:
            dropped[code] = f"blueprint declares {len(levels)} DOK level(s), parallelism needs 2"
            continue
        have = {lv: sorted(pool[code].get(lv, []), key=lambda i: i["id"]) for lv in levels}
        short = [f"DOK{lv} has {len(have[lv])}, needs {n_forms}"
                 for lv in levels if len(have[lv]) < n_forms]
        if short:
            dropped[code] = "; ".join(short)
            continue
        for k in range(n_forms):
            for lv in levels:
                forms[k].append(have[lv][k])
        profile[code] = {str(lv): 1 for lv in levels}
    return forms, dropped, profile


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("family_id")
    ap.add_argument("--forms", type=int, default=5)
    ap.add_argument("--standards", nargs="+", required=True,
                    help="Name the standards actually authored. Never a wildcard.")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    b = binding_mod.load()
    print(b.declaration())
    b.assert_codes(a.standards, where=f"family {a.family_id} standard list")
    with open(b.blueprint_file, encoding="utf-8") as fh:
        blueprint = json.load(fh)

    items = itemio.load_dir(b.output_dir)
    if not items:
        print("EMPTY SCAN — no items; refusing to report a family built from nothing")
        return 1
    pool = per_standard_pool(items, set(a.standards), b)
    forms, dropped, profile = allocate(pool, a.standards, blueprint, a.forms)

    carried = sorted(profile)
    print(f"\nFamily {a.family_id}: {a.forms} parallel form(s), "
          f"{len(carried)}/{len(a.standards)} standard(s) carried")
    for code in carried:
        print(f"   {code}: DOK {'+'.join(sorted(profile[code]))} x{a.forms} forms")
    for code, why in sorted(dropped.items()):
        print(f"   DROPPED {code}: {why}")
    if not carried:
        print("\nNo standard can supply the depth for a parallel family. Refusing to build.")
        return 1

    ids = [f"{a.family_id}-{chr(65 + k)}" for k in range(a.forms)]
    counts = {len(v) for v in forms.values()}
    print(f"\n{ids[0]}..{ids[-1]}, {counts.pop()} items each, zero shared items")

    if not a.apply:
        print("\nDRY RUN — pass --apply to render the family")
        return 0

    os.makedirs(FAMILY_DIR, exist_ok=True)
    members = []
    for k, fid in enumerate(ids):
        picked = forms[k]
        b.assert_codes([c for i in picked for c in i["standardCodes"]],
                       where=f"form {fid} contents")
        members.append(formbuild.render_selection(fid, picked, carried, b, blueprint,
                                                  family=a.family_id))
        print(f"   -> forms/{fid}/")

    fam = {
        "$comment": ("A FAMILY is N versions of the same test. Parallel means same standards, "
                     "same count, same DOK profile, same stimulus mix and ZERO shared items — "
                     "a property of the SET, which no single-form gate can see."),
        "familyId": a.family_id, "course": b.course, "standardsYear": b.standards_year,
        "forms": ids, "standards": carried, "dokProfilePerStandard": profile,
        "droppedStandards": dropped,
        "declaredParallel": True,
        "claimsFullCourseCoverage": False,
        "$coverageNote": ("Set claimsFullCourseCoverage true only when this family carries every "
                          "standard in the course. A partial family is legitimate; claiming full "
                          "coverage without it is not."),
    }
    with open(os.path.join(FAMILY_DIR, f"{a.family_id}.json"), "w", encoding="utf-8") as fh:
        json.dump(fam, fh, indent=2, ensure_ascii=False)
    print(f"   -> forms/families/{a.family_id}.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
