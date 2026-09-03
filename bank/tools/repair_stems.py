#!/usr/bin/env python3
"""Repair stems that swallowed their own choice list.

The stem is cut at the point where its first choice text begins. The repair is
only accepted when what remains still reads as a question — ending on '?', ':'
or a dash. Anything else is HELD rather than guessed, because a stem trimmed to
the wrong place changes what the item asks.

Usage: python3 tools/repair_stems.py [--apply]
"""
from __future__ import annotations

import argparse, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import binding as binding_mod
import itemio
from gates import content

TAIL_OK = ("?", ":", "—", "–", "-")


def repair(item):
    stem = item.get("stem") or ""
    cuts = []
    for c in itemio.choices(item):
        t = (c.get("text") or "").strip()
        if len(t) > 25:
            idx = stem.find(t[:40])
            if idx > 0:
                cuts.append(idx)
    if not cuts:
        return None, "no choice text found inside the stem"
    cut = min(cuts)
    head = stem[:cut].strip()
    # Drop a stranded option label or key marker left behind by the paste.
    head = re.sub(r"(?:CORRECT ANSWER|ANSWER KEY)?\s*[A-H]\.?\s*$", "", head,
                  flags=re.I).strip()
    if not head.endswith(TAIL_OK):
        return None, f"trimmed stem would not read as a question: …{head[-40:]!r}"
    if len(head) < 25:
        return None, "trimmed stem is too short to be the real question"
    return head, None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    b = binding_mod.load(); print(b.declaration())
    items = itemio.load_dir(b.output_dir)
    if not items:
        print("EMPTY SCAN — nothing to repair."); return 1
    r = content.gate_embedded_key(items, b)
    ids = {str(f).split(" ")[0].rstrip(":") for f in r.findings}
    by_id = {i["id"]: i for i in items}
    fixed, held = {}, []
    for iid in sorted(ids):
        head, why = repair(by_id.get(iid, {}))
        (fixed.__setitem__(iid, head) if head else held.append((iid, why)))
    print(f"\n{len(ids)} defective stem(s): {len(fixed)} repairable, {len(held)} held")
    for iid, head in list(fixed.items())[:4]:
        print(f"   {iid} -> …{head[-70:]!r}")
    for iid, why in held:
        print(f"   HELD {iid}: {why}")
    if not a.apply:
        print("\nDRY RUN — nothing changed. Re-run with --apply."); return 0
    n = 0
    for path in sorted({i["_file"] for i in items if i["id"] in ids}):
        full = os.path.join(itemio.BANK_ROOT, path)
        doc = json.load(open(full, encoding="utf-8"))
        for rec in doc.get("items", []):
            rid = rec.get("id")
            if rid in fixed:
                rec.setdefault("provenance", {})["stemRepair"] = {
                    "was": rec["stem"], "reason": "stem had swallowed its own choice list"}
                rec["stem"] = fixed[rid]; n += 1
            elif rid in dict(held):
                rec["status"] = "quarantined"
                rec.setdefault("provenance", {})["stemHold"] = {
                    "reason": dict(held)[rid], "note": "content retained; not servable"}
        json.dump(doc, open(full, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"\nrepaired {n} stem(s); held {len(held)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
