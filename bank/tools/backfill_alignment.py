#!/usr/bin/env python3
"""Stamp every item with its ALIGNMENT CONFIDENCE, from evidence.

Content quality and alignment confidence are different axes. This writes the
second one so an unverified label stops reading as a verdict on the question.
Nothing is deleted, nothing is downgraded in usability — the field only decides
what may be COUNTED as standards coverage.
"""
from __future__ import annotations

import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import binding as binding_mod
import itemio
from gates import content


def main():
    b = binding_mod.load()
    print(b.declaration())
    for root in (b.output_dir, b.quarantine_dir):
        items = itemio.load_dir(root)
        if not items:
            print(f"EMPTY SCAN — nothing under {root}"); continue
        judged, flagged, _ = content.relevance_scan(items, b)
        flagged_ids = {i["id"] for i, _, _ in flagged}
        judged_ids = set()
        stds = b.standards()
        import alignment as al
        for it in items:
            codes = [c for c in (it.get("standardCodes") or []) if c in stds]
            # judgeable_signals is what relevance_scan actually judges on. This
            # asked standard_signals — a THIRD definition, looser than both — so
            # an item could be marked judged here and skipped there. One rule,
            # one implementation (L22).
            if any(al.judgeable_signals(stds[c]["text"]) for c in codes):
                judged_ids.add(it["id"])

        counts = collections.Counter()
        for path in sorted({i["_file"] for i in items}):
            full = os.path.join(itemio.BANK_ROOT, path)
            with open(full, encoding="utf-8") as fh:
                doc = json.load(fh)
            for rec in doc.get("items", []):
                rid = rec.get("id")
                # A human verification is a RECORDED FACT about work someone
                # did. A recompute must never erase it — this loop wrote every
                # status unconditionally, so the next backfill after a review
                # pass would have silently thrown that review away (L53).
                if rec.get("alignmentStatus") == "human-verified":
                    counts["human-verified"] += 1
                    continue
                if (rec.get("provenance") or {}).get("rehomed"):
                    st = "rehomed"
                elif rid not in judged_ids:
                    st = "not-applicable"
                elif rid in flagged_ids:
                    st = "unverified"
                else:
                    st = "evidenced"
                rec["alignmentStatus"] = st
                counts[st] += 1
            with open(full, "w", encoding="utf-8") as fh:
                json.dump(doc, fh, indent=2, ensure_ascii=False)
        label = os.path.basename(root)
        print(f"\n{label}: {sum(counts.values())} item(s)")
        for k, v in counts.most_common():
            print(f"   {v:5d}  {k}")
    print("\nNothing deleted. `unverified` means kept and usable, not counted as coverage.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
