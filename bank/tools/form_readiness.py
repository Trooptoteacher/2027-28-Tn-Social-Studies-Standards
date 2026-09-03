#!/usr/bin/env python3
"""What would it take to make a green form for each standard?

The pilot discovered its authoring cost item by item. That cost is measurable
in advance: for every standard, whether it has the depth and mix a form needs,
and exactly how many rationales, DOK notes and translations authoring it would
require. Scope the work before starting it.

Usage: python3 tools/form_readiness.py [--top N] [--csv path]
"""
from __future__ import annotations

import argparse, collections, csv, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import alignment
import binding as binding_mod
import itemio
from gates import content


def reachable_tier(pool, form):
    """The highest tier this pool can fill, and the items that fill it.

    Shares the builder's ladder. This tool measured a FLAT blueprint and broke
    silently when the blueprint became tiered — its CSV was regenerated with
    output suppressed and the failure shipped.
    """
    for tier in form["tiers"]:
        used, got = set(), []
        for slot in tier["slots"]:
            cand = [i for i in pool if i["id"] not in used
                    and i.get("itemType") in slot["types"]
                    and i.get("dokLevel") == slot["dok"]]
            if not cand:
                got = None
                break
            used.add(cand[0]["id"]); got.append(cand[0])
        if got:
            return tier, got
    return None, []


def cost(items, want=None):
    """Authoring needed to bring this selection to Grade A."""
    c = collections.Counter()
    for it in items:
        if not (it.get("dokRationale") or "").strip():
            c["dokRationale"] += 1
        for f in ("stemEs", "explanationEs"):
            if not (it.get(f) or "").strip():
                c["translation"] += 1
        if content.worst_translation_defect(it):
            c["translation"] += 1
        for ch in itemio.choices(it):
            if isinstance(ch, dict) and ch.get("id") != it.get("correctAnswer"):
                if not (ch.get("explanation") or "").strip():
                    c["distractorRationale"] += 1
        exp = (it.get("explanation") or "").strip()
        if exp and exp == (it.get("dokRationale") or "").strip():
            c["explanationRewrite"] += 1
    mcq = [i for i in items if i.get("itemType") == "mcq" and itemio.choices(i)]
    longest = sum(1 for i in mcq
                  if max(itemio.choices(i), key=lambda c: len(c.get("text") or ""))
                  .get("id") == i.get("correctAnswer"))
    if mcq and abs(longest / len(mcq) - 0.25) > 0.10:
        c["choiceRebalance"] = len(mcq)
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--csv")
    a = ap.parse_args()
    b = binding_mod.load(); print(b.declaration())
    with open(b.blueprint_file, encoding="utf-8") as fh:
        form = json.load(fh)["form"]

    # Same placement rule the FORM BUILDER uses — an item counts toward a
    # standard only if it is relevant to THAT standard. Two implementations of
    # one rule is L22.
    stds = b.standards()
    items = itemio.load_dir(b.output_dir)
    by_std = collections.defaultdict(list)
    for it in items:
        if not itemio.aligned(it):
            continue
        hay = " ".join([it.get("stem") or ""]
                       + [c.get("text") or "" for c in itemio.choices(it)])
        for c in (it.get("standardCodes") or []):
            t = stds.get(c, {}).get("text")
            if t and alignment.relevant_to(hay, t):
                by_std[c].append(it)

    rows = []
    for code in sorted(b.valid_codes()):
        pool = sorted(by_std.get(code, []), key=lambda i: i["id"])
        tier, got = reachable_tier(pool, form)
        buildable = tier is not None
        c = cost(got) if buildable else collections.Counter()
        rows.append({"standard": code, "aligned": len(pool), "buildable": buildable,
                     "tier": tier["id"] if tier else "none",
                     "dokCeiling": tier["dokCeiling"] if tier else None,
                     "distractorRationale": c["distractorRationale"],
                     "dokRationale": c["dokRationale"], "translation": c["translation"],
                     "explanationRewrite": c["explanationRewrite"],
                     "choiceRebalance": c["choiceRebalance"],
                     "totalAuthoringUnits": sum(c.values())})

    ok = [r for r in rows if r["buildable"]]
    print(f"\n{len(ok)}/{len(rows)} standards can fill a form from aligned items.\n")
    ok.sort(key=lambda r: r["totalAuthoringUnits"])
    print(f"{'standard':<9}{'tier':<18}{'aligned':>8}{'distract':>9}{'dok':>5}"
          f"{'transl':>8}{'rebal':>7}{'TOTAL':>7}")
    for r in ok[:a.top]:
        print(f"{r['standard']:<9}{r['tier']:<18}{r['aligned']:>8}"
              f"{r['distractorRationale']:>9}{r['dokRationale']:>5}{r['translation']:>8}"
              f"{r['choiceRebalance']:>7}{r['totalAuthoringUnits']:>7}")
    tiers = collections.Counter(r["tier"] for r in rows)
    print("\ntier reached: " + ", ".join(f"{k}={v}" for k, v in tiers.most_common()))
    tot = sum(r["totalAuthoringUnits"] for r in ok)
    print(f"\nauthoring units to green ONE form for each of the {len(ok)} buildable "
          f"standards: {tot:,}")
    notb = [r for r in rows if not r["buildable"]]
    print(f"{len(notb)} standard(s) cannot fill a form yet: "
          + ", ".join(f"{r['standard']}({r['aligned']})" for r in notb[:12])
          + (" …" if len(notb) > 12 else ""))

    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader()
            w.writerows(rows)
        print(f"\nwrote {a.csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
