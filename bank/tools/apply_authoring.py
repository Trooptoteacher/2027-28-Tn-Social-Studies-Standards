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

import argparse, datetime, json, os, sys

TODAY = datetime.date.today().isoformat()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import binding as binding_mod
import itemio


class AuthoringError(Exception):
    pass


TAXONOMY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "taxonomy", "misconception-families.json")


def _taxonomy():
    """Live families and the distractor functions, from the committed taxonomy.

    Empty if the file is gone, and empty makes `validate` refuse every family
    and every function rather than accept any:
    a missing taxonomy must re-raise the hold, not wave records through.
    """
    if not os.path.exists(TAXONOMY):
        return set(), {}
    with open(TAXONOMY, encoding="utf-8") as fh:
        d = json.load(fh)
    live = {f["id"] for f in d.get("families", []) if not f.get("retired")}
    return live, {x["id"]: x for x in d.get("distractorFunctions", [])}


def _families():
    return _taxonomy()[0]


def normalise(payload):
    """One internal shape for a distractor payload, from either authored form.

    Returns (explanation, misconception, family, function). Since
    taxonomyVersion 2 a distractor says WHAT IT DOES as well as which
    misconception it encodes, and a family is required only when the function
    is `common-misconception`.

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
        return payload[0], payload[1], None, None
    if isinstance(payload, dict):
        expl = payload.get("explanation")
        mis = payload.get("misconception")
        fam = payload.get("misconceptionFamily")
        fn = payload.get("distractorFunction")
        if not expl or not mis:
            raise AuthoringError("needs explanation and misconception, both non-empty")
        return expl, mis, fam, fn
    raise AuthoringError("must be [explanation, misconception] or an object with explanation / "
                         "misconception / distractorFunction / misconceptionFamily")


CLAIM_FIELDS = ("stem", "stemEs", "explanation", "explanationEs", "dokRationale")
CLAIM_CHOICE_FIELDS = ("text", "textEs", "explanation", "misconception")


def _claims(item):
    """Everything on an item that a historian's approval is ABOUT.

    Deliberately EXCLUDES `distractorFunction` and `misconceptionFamily`: those
    classify how an option goes wrong, which is a pedagogical judgement, not a
    statement about the past. Including them would make a tagging pass
    un-approve every item it touched.
    """
    return (tuple(item.get(f) for f in CLAIM_FIELDS),
            tuple((c.get("id"), tuple(c.get(f) for f in CLAIM_CHOICE_FIELDS))
                  for c in (item.get("choices") or []) if isinstance(c, dict)))


def validate(record, items_by_id):
    """Fail before writing anything. A partial content write is worse than none.

    Returns the distractors that will land with NO distractorFunction. They are
    not an error — the 2-list form is still legal — but they are a cost, and
    the caller prints it, because the gate they will fail is invisible until
    the next full run.
    """
    problems, untagged = [], []
    fams, funcs = _taxonomy()
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
                _, _, fam, fn = normalise(payload)
            except AuthoringError as e:
                problems.append(f"{iid}/{cid}: {e}")
                continue
            if fn is None and fam is None:
                untagged.append(f"{iid}/{cid}")
                continue
            if fn is None:
                problems.append(f"{iid}/{cid}: cites a family but names no distractorFunction. "
                                f"Since taxonomyVersion 2 a family is only meaningful under "
                                f"'common-misconception'")
                continue
            if fn not in funcs:
                problems.append(f"{iid}/{cid}: claims distractorFunction {fn!r}, which the "
                                f"taxonomy does not define ({', '.join(sorted(funcs))})")
                continue
            if funcs[fn].get("itemFlaw"):
                problems.append(f"{iid}/{cid}: {fn!r} is an ITEM FLAW, not a function to write "
                                f"down — {funcs[fn]['statement']} Rewrite the option instead of "
                                f"labelling it")
                continue
            if funcs[fn].get("requiresFamily"):
                if not fam:
                    problems.append(f"{iid}/{cid}: is 'common-misconception' and cites no "
                                    f"misconceptionFamily — free text cannot aggregate")
                elif fam not in fams:
                    problems.append(f"{iid}/{cid}: cites misconception family {fam!r}, which "
                                    f"taxonomy/misconception-families.json does not define as "
                                    f"live ({len(fams)} live)")
            elif fam:
                problems.append(f"{iid}/{cid}: is {fn!r} and also cites family {fam!r}. Only "
                                f"'common-misconception' carries a family")
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
    return untagged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("record"); ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    b = binding_mod.load(); print(b.declaration())
    with open(a.record, encoding="utf-8") as fh:
        rec = json.load(fh)
    items = itemio.load_dir(b.output_dir)
    by_id = {i["id"]: i for i in items}
    untagged = validate(rec, by_id)
    print(f"\nrecord validated: {len(rec['items'])} item(s), no key overwrites, "
          f"no invented choices, no duplicate misconceptions")
    if untagged:
        print(f"\n  ⚠ {len(untagged)} distractor(s) carry no distractorFunction and will "
              f"FAIL `misconception-taxonomy`\n    once this record is applied — until an option "
              f"says what it DOES, nothing can tell a\n    diagnosis from a deliberately-wrong "
              f"option. Applying a record is what makes that\n    gate start judging the item, so "
              f"this is a cost the record incurs, not a\n    pre-existing one: "
              f"{', '.join(untagged[:6])}" + (" …" if len(untagged) > 6 else ""))

    if not a.apply:
        print("DRY RUN — nothing written. Re-run with --apply."); return 0

    touched, superseded, untouched_review = 0, [], []
    for path in sorted({by_id[i]["_file"] for i in rec["items"] if i in by_id}):
        full = os.path.join(itemio.BANK_ROOT, path)
        with open(full, encoding="utf-8") as fh:
            doc = json.load(fh)
        for r in doc.get("items", []):
            spec = rec["items"].get(r.get("id"))
            if not spec:
                continue
            # A snapshot of every field a historian's approval is ABOUT, taken
            # before this record writes, so "did a claim move" is measured
            # rather than inferred from which keys the record happens to carry.
            before_claims = _claims(r)
            for f in ("dokRationale", "explanation", "stemEs", "explanationEs"):
                if spec.get(f):
                    r[f] = spec[f]
            for cid, txt in (spec.get("choiceText") or {}).items():
                for c in r.get("choices") or []:
                    if c.get("id") == cid:
                        c.setdefault("_wasText", c.get("text"))
                        c["text"] = txt
            for cid, payload in (spec.get("distractors") or {}).items():
                expl, mis, fam, fn = normalise(payload)
                for c in r.get("choices") or []:
                    if c.get("id") == cid:
                        c["explanation"], c["misconception"] = expl, mis
                        if fn:
                            c["distractorFunction"] = fn
                        if fam:
                            c["misconceptionFamily"] = fam
            changed_claims = _claims(r) != before_claims
            if spec.get("stemEs"):
                # Authored here, not by a certified translator.
                r["translationStatus"] = "needs-review"
            r["status"] = "authored"
            # THE REVIEW STATE MOVES ONLY IF A CLAIM A HISTORIAN APPROVED MOVED.
            #
            # This tool used to set requiresHistorianReview unconditionally and
            # leave `historianReview` alone, so an item a historian had
            # approved came out BOTH approved and flagged — a contradiction
            # `review-provenance` is written to catch, and it caught 19.
            #
            # The first fix superseded every standing approval the tool touched,
            # which passed the gate and was WRONG: it discarded 19 of Sean's
            # recorded judgements on a technicality. A `distractorFunction` or
            # a `misconceptionFamily` is a PEDAGOGICAL CLASSIFICATION of how an
            # option goes wrong; the historian approved the HISTORY. Adding a
            # taxonomy tag does not make a reviewed item unreviewed.
            #
            # So the question is measured, not assumed: did this write change a
            # field the approval was ABOUT? Stems, explanations, choice text
            # and the free-text misconception are historical claims. The two
            # taxonomy axes are not. Only a real change supersedes — and then
            # the approval is MOVED, never deleted, because the record in
            # reviewed/historian-approvals.json is append-only evidence that a
            # person approved a prior version. What changes is the ITEM's
            # claim, which may no longer say it is reviewed. Expressing it that
            # way needs no change to the gate, and a gate relaxed to let a
            # write pass is not a gate.
            if changed_claims:
                prior = r.pop("historianReview", None)
                if prior:
                    hist = r.setdefault("historianReviewSuperseded", [])
                    stamp = {**prior, "supersededBy": os.path.basename(a.record),
                             "supersededOn": TODAY,
                             "reason": "a historical claim on this item changed after this "
                                       "approval, so it no longer covers what the item says; "
                                       "the approval record stands as evidence for the version "
                                       "that was reviewed"}
                    if stamp not in hist:
                        hist.append(stamp)
                    superseded.append(r.get("id"))
                r["requiresHistorianReview"] = True
            elif not r.get("historianReview"):
                # Never reviewed, and only tags were written: it still needs a
                # historian, because the content it carries was authored.
                r["requiresHistorianReview"] = True
            else:
                untouched_review.append(r.get("id"))
            r.setdefault("provenance", {})["authoring"] = {
                "record": os.path.basename(a.record),
                "note": "rationales explain misconceptions and remain historical claims",
            }
            touched += 1
        with open(full, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
    print(f"applied to {touched} item(s); each marked authored + requiresHistorianReview")
    if untouched_review:
        print(f"\n  {len(untouched_review)} standing historian approval(s) LEFT INTACT: this "
              f"record changed\n    only taxonomy tags on them, and a tag classifies how an "
              f"option goes wrong rather\n    than asserting anything about the past. An "
              f"approval of the history still holds.")
    if superseded:
        print(f"\n  {len(superseded)} standing historian approval(s) SUPERSEDED, because "
              f"a historical claim on them\n    changed and an approval cannot cover text it "
              f"never saw. The approval records\n    stand; the items no longer claim review:\n"
              f"    {', '.join(sorted(superseded)[:8])}"
              + (" …" if len(superseded) > 8 else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
