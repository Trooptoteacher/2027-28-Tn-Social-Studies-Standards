#!/usr/bin/env python3
"""Hold items whose key explanation calls the key wrong.

Found by reading ONE rendered teacher key. FORM-A item 1 keys B, and its
rationale reads "B is incorrect because it describes a different program,
event, or idea than this New Deal policy." A teacher grading from that page is
handed a contradiction, and the item was on a form both this system and its
twenty-two gates called GREEN.

The shape is a migrated distractor explanation welded into the key rationale,
still pointing at whatever letter the key used to be. It is not a wrong
ANSWER — the keys check out; it is a wrong RATIONALE, and it is teacher-facing.

Nothing is rewritten. Rewriting a rationale to agree with its key is authoring,
and the corrected sentence has to say why the key is right, which nobody here
can verify against the history. The item is held out of service and the defect
is written to a review sheet with the exact sentence, so the fix is a read and
not an investigation.

Usage: python3 tools/hold_key_contradictions.py [--apply]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import binding as binding_mod
import itemio

SHEET = os.path.join(itemio.BANK_ROOT, "reviewed", "key-contradictions.json")
RX = re.compile(r"\b([A-Z])\b\s+(?:is|was)\s+(?:incorrect|wrong|not correct|not right)", re.I)


def offending_sentence(exp, key):
    """The one sentence to read — not the whole rationale."""
    for sent in re.split(r"(?<=[.!?])\s+", exp):
        for m in RX.finditer(sent):
            if m.group(1).upper() == key.upper():
                return sent.strip()
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    b = binding_mod.load()
    print(b.declaration())

    items = itemio.load_dir(b.output_dir)
    if not items:
        print("EMPTY SCAN — nothing to hold, and that is a failure, not a clean run")
        return 1

    hits = {}
    for it in items:
        if not itemio.servable(it):
            continue
        key, exp = (it.get("correctAnswer") or "").strip(), it.get("explanation") or ""
        if key and exp and (sent := offending_sentence(exp, key)):
            hits[it["id"]] = {
                "id": it["id"], "file": it.get("_file"), "key": key,
                "standardCodes": it.get("standardCodes"),
                "stem": (it.get("stem") or "")[:200],
                "keyText": next((c.get("text") for c in itemio.choices(it)
                                 if isinstance(c, dict) and c.get("id") == key), None),
                "offendingSentence": sent,
                "defect": f"the explanation for key {key} declares {key} incorrect",
                "whatToDo": ("Confirm the key is right, then rewrite ONLY this sentence so it "
                             "says why the key is right. Do not delete the sentence — a "
                             "rationale that stops mid-argument is the next defect."),
                "resolution": None, "reviewer": None,
            }

    print(f"\n{len(hits)} item(s) whose key explanation calls the key wrong")
    for h in list(hits.values())[:5]:
        print(f"  [{h['id']}] key={h['key']} — {h['offendingSentence'][:110]}")
    if len(hits) > 5:
        print(f"  … and {len(hits) - 5} more")

    if not a.apply:
        print("\nDRY RUN — pass --apply to hold them and write the review sheet")
        return 0

    held = 0
    for path in sorted({i["_file"] for i in items if i["id"] in hits}):
        full = os.path.join(itemio.BANK_ROOT, path)
        with open(full, encoding="utf-8") as fh:
            doc = json.load(fh)
        recs = doc if isinstance(doc, list) else (doc.get("items") or doc.get("questions") or [])
        for rec in recs:
            if rec.get("id") in hits:
                rec["status"] = "held"
                rec["heldReason"] = hits[rec["id"]]["defect"]
                held += 1
        with open(full, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)

    os.makedirs(os.path.dirname(SHEET), exist_ok=True)
    with open(SHEET, "w", encoding="utf-8") as fh:
        json.dump({
            "$comment": ("Items held because the key's own explanation declares the key "
                         "incorrect. Found by reading a rendered teacher key, not by a gate — "
                         "the gate exists now (key-contradiction) and this is its backlog. "
                         "Rewrite the one sentence, set resolution and reviewer, then run "
                         "tools/hold_key_contradictions.py --apply again to re-measure."),
            "items": list(hits.values()),
        }, fh, indent=2, ensure_ascii=False)
    print(f"\nheld {held} item(s); review sheet: {os.path.relpath(SHEET, itemio.BANK_ROOT)}")
    print("Content retained in place. Nothing rewritten — the corrected sentence must say "
          "why the key IS right, and that is a claim about history.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
