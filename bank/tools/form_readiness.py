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


def slots(want):
    dok = []
    for lvl, n in sorted(want["dok"].items()):
        dok += [int(lvl)] * n
    dok.sort()
    out = []
    for typ, n in sorted(want["itemType"].items(), key=lambda kv: -kv[1]):
        out += [[typ, None]] * n
    out = [[t, None] for t, _ in out]
    for s, lvl in zip(out, dok):
        s[1] = lvl
    return out


def cost(items, want):
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
        want = (json.load(fh)).get("form")
    plan = slots(want)

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
        used, got = set(), []
        for typ, lvl in plan:
            cand = [i for i in pool if i["id"] not in used
                    and i.get("itemType") == typ and i.get("dokLevel") == lvl] or \
                   [i for i in pool if i["id"] not in used and i.get("itemType") == typ]
            if cand:
                used.add(cand[0]["id"]); got.append(cand[0])
        buildable = len(got) == want["itemCount"]
        c = cost(got, want) if buildable else collections.Counter()
        rows.append({"standard": code, "aligned": len(pool), "buildable": buildable,
                     "shortBy": want["itemCount"] - len(got),
                     "distractorRationale": c["distractorRationale"],
                     "dokRationale": c["dokRationale"], "translation": c["translation"],
                     "explanationRewrite": c["explanationRewrite"],
                     "choiceRebalance": c["choiceRebalance"],
                     "totalAuthoringUnits": sum(c.values())})

    ok = [r for r in rows if r["buildable"]]
    print(f"\n{len(ok)}/{len(rows)} standards can fill a form from aligned items.\n")
    ok.sort(key=lambda r: r["totalAuthoringUnits"])
    print(f"{'standard':<9}{'aligned':>8}{'distract':>9}{'dok':>5}{'transl':>8}"
          f"{'rebal':>7}{'TOTAL':>7}")
    for r in ok[:a.top]:
        print(f"{r['standard']:<9}{r['aligned']:>8}{r['distractorRationale']:>9}"
              f"{r['dokRationale']:>5}{r['translation']:>8}{r['choiceRebalance']:>7}"
              f"{r['totalAuthoringUnits']:>7}")
    tot = sum(r["totalAuthoringUnits"] for r in ok)
    print(f"\nauthoring units to green ONE form for each of the {len(ok)} buildable "
          f"standards: {tot:,}")
    notb = [r for r in rows if not r["buildable"]]
    print(f"{len(notb)} standard(s) cannot fill a form yet: "
          + ", ".join(f"{r['standard']}(-{r['shortBy']})" for r in notb[:12])
          + (" …" if len(notb) > 12 else ""))

    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader()
            w.writerows(rows)
        print(f"\nwrote {a.csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
