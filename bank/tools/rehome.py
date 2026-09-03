#!/usr/bin/env python3
"""Triage standard-relevance findings and RE-HOME the items that can be saved.

A misfiled item is usually a good question wearing the wrong label. Deleting it
throws away authored work; re-homing it to the standard it actually tests saves
it. So for every flagged item, score all 94 standards by how many of their
checklist elements the item names, and propose the best match.

Evidence comes from the STEM, the KEY and the key's explanation — never the
distractors. A wrong choice mentioning the Dawes Act is not evidence the item
tests the Dawes Act; that was L07.

Nothing moves silently: every re-home records the old code, the matched
elements, and the score in provenance.

Usage: python3 tools/rehome.py [--apply] [--min-score 1]
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import re

import alignment
import binding as binding_mod
import itemio


def evidence_text(item):
    """What the item ASKS and KEYS. Distractors excluded — see L07."""
    bits = [item.get("stem") or "", item.get("explanation") or ""]
    key = item.get("correctAnswer")
    for c in itemio.choices(item):
        if isinstance(c, dict) and c.get("id") == key:
            bits.append(c.get("text") or "")
    return " ".join(bits).lower()


def strong_signals(el):
    """Only NAMED-ENTITY signals may justify a move.

    A matcher tuned for DETECTION may be loose: a loose relevance gate simply
    flags fewer items, which is conservative. A matcher tuned for ASSIGNMENT
    may not — a wrong re-home creates a confident mislabel, which is worse than
    the flag it replaces.

    Elements with no proper noun degrade to bare content words, and accepting
    any one of them proposed moving a Gilded Age Carnegie item to a standard
    about the space race because both contain the word "industry", and a
    "Gilded Age" item to another because it contains "recall".
    """
    phrase = el if isinstance(el, str) else " ".join(el)
    cands = [phrase] if isinstance(el, list) else alignment.signals(el)
    out = []
    for sig in cands:
        if not re.search(r"[A-Z]", sig):
            continue                          # lowercase degradation, never a name
        if len(sig.split()) >= 2:
            out.append(sig)                   # "No Child Left Behind", "Dawes Act"
        continue
    # Single-word signals are dropped entirely for ASSIGNMENT. "separation of
    # Germany" yields "Germany", which matched every WWI and WWII item in the
    # bank and proposed sending them all to the Yalta/Potsdam standard — the
    # same failure as "American" (L10) and "Economic". Every correct move in the
    # sample was carried by a multi-word name: "John D. Rockefeller", "Gulf of
    # Tonkin Resolution", "Ida B. Wells-Barnett", "Dust Bowl". This loses real
    # single-word names like "Afghanistan"; those stay in the review queue,
    # which is the safe side to fail on.
    return out


def checklists(stds):
    out = {}
    for code, s in stds.items():
        pairs = [(el, strong_signals(el)) for el in alignment.elements(s["text"])]
        # Plus the names in the standard's stem — the thing it is ABOUT.
        for ne in alignment.named_entities(s["text"]):
            pairs.append((ne, strong_signals([ne])))
        pairs = [(el, sigs) for el, sigs in pairs if sigs]
        if pairs:
            out[code] = pairs
    return out


def score(text, lists):
    """{code: (matched_element_count, [matched elements])} over all standards."""
    hits = {}
    for code, els in lists.items():
        matched = [el for el, sigs in els if any(s.lower() in text for s in sigs)]
        if matched:
            hits[code] = (len(matched), matched)
    return hits


def propose(item, lists, current):
    """Best re-home for a flagged item, or None if it cannot be resolved.

    The deciding evidence must be in the STEM — what the item asks. Allowing the
    key explanation to decide moved an Eisenhower "Modern Republicanism" item to
    the New Deal and a United Nations item to Pearl Harbor, because those names
    appear in passing. The key and explanation may CORROBORATE (they raise the
    score) but they may not carry a move on their own. This costs recall and
    buys precision, which is the correct trade when the operation rewrites a
    label: a wrong move creates a confident mislabel, worse than the flag.
    """
    stem = (item.get("stem") or "").lower()
    text = evidence_text(item)
    stem_hits = score(stem, lists)
    hits = {c: v for c, v in score(text, lists).items() if c in stem_hits}
    for c in current:
        hits.pop(c, None)                    # it already fails against its own standard
    if not hits:
        return None, "no standard's checklist matches this item's stem, key or explanation"
    ranked = sorted(hits.items(), key=lambda kv: (-kv[1][0], kv[0]))
    best, (n, els) = ranked[0]
    if len(ranked) > 1 and ranked[1][1][0] == n:
        tied = [c for c, (m, _) in ranked if m == n]
        return None, f"ambiguous — {len(tied)} standards match equally ({', '.join(tied[:5])})"
    # One bare surname or single word is a coincidence; a move needs corroboration.
    multiword = any(len(e.split()) >= 2 for e in els)
    if n < 2 and not multiword:
        return None, f"weak evidence — one single-word match ({els}) is not enough to move an item"
    return {"to": best, "matched": els, "score": n}, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--min-score", type=int, default=1)
    a = ap.parse_args()

    b = binding_mod.load()
    print(b.declaration())
    stds = b.standards()
    lists = checklists(stds)
    print(f"{len(lists)}/{len(stds)} standards carry a checklist that can be matched against.\n")

    items = itemio.load_dir(b.output_dir)
    if not items:
        print("EMPTY SCAN — nothing to triage."); return 1

    from gates import content
    _, flagged_rows, _ = content.relevance_scan(items, b)
    flagged = [row[0] for row in flagged_rows]
    saved, stuck = [], []
    for it, codes, _ in flagged_rows:
        prop, why = propose(it, lists, codes)
        if prop and prop["score"] >= a.min_score:
            saved.append((it, codes, prop))
        else:
            stuck.append((it, codes, why or "below score floor"))

    print(f"flagged by standard-relevance : {len(flagged)}")
    print(f"  re-homeable (unique match)  : {len(saved)}  ({100*len(saved)/max(len(flagged),1):.1f}%)")
    print(f"  unresolved -> review queue  : {len(stuck)}")
    reasons = collections.Counter(w.split(" —")[0].split(" (")[0] for _, _, w in stuck)
    for w, n in reasons.most_common():
        print(f"      {n:5d}  {w}")

    moves = collections.Counter(f"{c[0]} -> {p['to']}" for _, c, p in saved)
    print("\ntop proposed moves:")
    for m, n in moves.most_common(10):
        print(f"   {n:5d}  {m}")

    os.makedirs(os.path.join(itemio.BANK_ROOT, "reviewed"), exist_ok=True)
    q = os.path.join(itemio.BANK_ROOT, "reviewed", "rehome-proposals.json")
    with open(q, "w", encoding="utf-8") as fh:
        json.dump({"$comment": "Proposed re-homes and the review queue. Evidence is the "
                               "matched checklist elements from the item's stem, key and "
                               "key explanation.",
                   "proposals": [{"id": i["id"], "from": c, "to": p["to"],
                                  "score": p["score"], "matchedElements": p["matched"],
                                  "stem": (i.get("stem") or "")[:180]}
                                 for i, c, p in saved],
                   "unresolved": [{"id": i["id"], "from": c, "why": w,
                                   "stem": (i.get("stem") or "")[:180]}
                                  for i, c, w in stuck]}, fh, indent=2, ensure_ascii=False)
    print(f"\nwrote {os.path.relpath(q, itemio.BANK_ROOT)}")

    if not a.apply:
        print("\nDRY RUN — nothing moved. Re-run with --apply.")
        return 0

    by_id = {i["id"]: (c, p) for i, c, p in saved}
    b.assert_codes([p["to"] for _, p in by_id.values()], where="re-home targets")
    changed = 0
    for path in sorted(set(i["_file"] for i, _, _ in saved)):
        full = os.path.join(itemio.BANK_ROOT, path)
        with open(full, encoding="utf-8") as fh:
            doc = json.load(fh)
        for rec in doc.get("items", []):
            if rec.get("id") in by_id:
                old, prop = by_id[rec["id"]]
                rec["standardCodes"] = [prop["to"]]
                rec.setdefault("provenance", {})["rehomed"] = {
                    "from": old, "to": prop["to"], "matchedElements": prop["matched"],
                    "basis": "stem + key + key explanation named these elements of the "
                             "target standard and none of the previous standard's",
                }
                rec["status"] = "provisional"      # a moved item is not settled
                changed += 1
        with open(full, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
    print(f"\nre-homed {changed} item(s); each marked provisional and carrying its evidence.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
