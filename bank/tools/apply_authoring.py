#!/usr/bin/env python3
"""Apply an authoring record to the bank.

The record is committed data (authoring/*.json) so a reviewer reads WHAT was
written, not the script that wrote it. Every applied item is marked
`status: authored` and `requiresHistorianReview`, because a rationale explaining
a misconception is still a historical claim.

Refuses to write a distractor rationale onto the KEY, refuses to write to an id
the record does not name, and refuses to invent a choice id the item does not
have — the three ways a bulk content write silently corrupts a bank.

Usage: python3 tools/apply_authoring.py authoring/form-a.json [--apply]
"""
from __future__ import annotations

import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import binding as binding_mod
import itemio


class AuthoringError(Exception):
    pass


TAXONOMY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "taxonomy", "misconception-families.json")


def _families():
    """The family ids the taxonomy defines. Empty if the file is gone, and an
    empty set makes `validate` refuse every family rather than accept any —
    a missing taxonomy must re-raise the hold, not wave records through."""
    if not os.path.exists(TAXONOMY):
        return set()
    with open(TAXONOMY, encoding="utf-8") as fh:
        return {f["id"] for f in json.load(fh).get("families", [])}


def normalise(payload):
    """One internal shape for a distractor payload, from either authored form.

    The record format was a bare 2-list `[explanation, misconception]` with no
    slot for a family — and `misconception-taxonomy` fails a distractor that
    names a misconception in free text and cites no family. Applying a record
    therefore CREATED a finding: stamping `provenance.authoring` is exactly
    what makes that gate start judging an item, so 20 of the 22 items failing
    it today were written by this tool. The 2-list is still accepted, because
    eight committed records use it and a committed record is data a reviewer
    reads, not something to rewrite under them — but a record that uses it is
    told what it is leaving behind.

    Returns (explanation, misconception, family_or_None).
    """
    if isinstance(payload, list):
        if len(payload) != 2 or not all(payload):
            raise AuthoringError("needs [explanation, misconception], both non-empty")
        return payload[0], payload[1], None
    if isinstance(payload, dict):
        expl = payload.get("explanation")
        mis = payload.get("misconception")
        fam = payload.get("misconceptionFamily")
        if not expl or not mis:
            raise AuthoringError("needs explanation and misconception, both non-empty")
        return expl, mis, fam
    raise AuthoringError("must be [explanation, misconception] or an object with "
                         "explanation / misconception / misconceptionFamily")


def validate(record, items_by_id):
    """Fail before writing anything. A partial content write is worse than none.

    Returns the distractors that will land with NO misconception family. They
    are not an error — the 2-list form is still legal — but they are a cost,
    and the caller prints it, because the gate they will fail is invisible
    until the next full run.
    """
    problems, unfamilied, fams = [], [], _families()
    for iid, spec in record["items"].items():
        it = items_by_id.get(iid)
        if not it:
            problems.append(f"{iid}: not in the bank"); continue
        ids = {c.get("id") for c in itemio.choices(it) if isinstance(c, dict)}
        key = it.get("correctAnswer")
        for cid, txt in (spec.get("choiceText") or {}).items():
            if cid not in ids:
                problems.append(f"{iid}: choiceText for {cid!r} which does not exist")
            elif not isinstance(txt, str) or len(txt.strip()) < 10:
                problems.append(f"{iid}/{cid}: replacement choice text is too short to be real")
        for cid, payload in (spec.get("distractors") or {}).items():
            if cid not in ids:
                problems.append(f"{iid}: choice {cid!r} does not exist (have {sorted(ids)})")
            if cid == key:
                problems.append(f"{iid}: {cid!r} is the KEY — a distractor rationale must never "
                                f"be written onto the correct answer")
            try:
                _, _, fam = normalise(payload)
            except AuthoringError as e:
                problems.append(f"{iid}/{cid}: {e}")
                continue
            if fam is None:
                unfamilied.append(f"{iid}/{cid}")
            elif fam not in fams:
                problems.append(f"{iid}/{cid}: cites misconception family {fam!r}, which "
                                f"taxonomy/misconception-families.json does not define "
                                f"({len(fams)} defined)")
        mis = []
        for payload in (spec.get("distractors") or {}).values():
            try:
                mis.append(normalise(payload)[1].strip().lower())
            except AuthoringError:
                pass
        if len(mis) != len(set(mis)):
            problems.append(f"{iid}: two distractors name the same misconception")
    if problems:
        raise AuthoringError("authoring record rejected:\n  - " + "\n  - ".join(problems))
    return unfamilied


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("record"); ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    b = binding_mod.load(); print(b.declaration())
    with open(a.record, encoding="utf-8") as fh:
        rec = json.load(fh)
    items = itemio.load_dir(b.output_dir)
    by_id = {i["id"]: i for i in items}
    unfamilied = validate(rec, by_id)
    print(f"\nrecord validated: {len(rec['items'])} item(s), no key overwrites, "
          f"no invented choices, no duplicate misconceptions")
    if unfamilied:
        print(f"\n  ⚠ {len(unfamilied)} distractor(s) carry no misconceptionFamily and will "
              f"FAIL `misconception-taxonomy`\n    once this record is applied — a free-text "
              f"misconception cannot aggregate. Applying a\n    record is what makes that gate "
              f"start judging the item, so this is a cost the\n    record incurs, not a "
              f"pre-existing one: {', '.join(unfamilied[:6])}"
              + (" …" if len(unfamilied) > 6 else ""))

    if not a.apply:
        print("DRY RUN — nothing written. Re-run with --apply."); return 0

    touched = 0
    for path in sorted({by_id[i]["_file"] for i in rec["items"] if i in by_id}):
        full = os.path.join(itemio.BANK_ROOT, path)
        with open(full, encoding="utf-8") as fh:
            doc = json.load(fh)
        for r in doc.get("items", []):
            spec = rec["items"].get(r.get("id"))
            if not spec:
                continue
            for f in ("dokRationale", "explanation", "stemEs", "explanationEs"):
                if spec.get(f):
                    r[f] = spec[f]
            for cid, txt in (spec.get("choiceText") or {}).items():
                for c in r.get("choices") or []:
                    if c.get("id") == cid:
                        c.setdefault("_wasText", c.get("text"))
                        c["text"] = txt
            for cid, payload in (spec.get("distractors") or {}).items():
                expl, mis, fam = normalise(payload)
                for c in r.get("choices") or []:
                    if c.get("id") == cid:
                        c["explanation"], c["misconception"] = expl, mis
                        if fam:
                            c["misconceptionFamily"] = fam
            if spec.get("stemEs"):
                # Authored here, not by a certified translator.
                r["translationStatus"] = "needs-review"
            r["status"] = "authored"
            r["requiresHistorianReview"] = True
            r.setdefault("provenance", {})["authoring"] = {
                "record": os.path.basename(a.record),
                "note": "rationales explain misconceptions and remain historical claims",
            }
            touched += 1
        with open(full, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
    print(f"applied to {touched} item(s); each marked authored + requiresHistorianReview")
    return 0


if __name__ == "__main__":
    sys.exit(main())
