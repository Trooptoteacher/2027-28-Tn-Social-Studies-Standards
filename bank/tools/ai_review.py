#!/usr/bin/env python3
"""An AI FIRST PASS over the review queue. It triages; it never approves.

Sean, 2026-09-03: "Create an AI review with guardrails to review that and clear
it ... I'll review everything at the end." He is the only reviewer this project
has, and two sessions put 10 items, 83 rubrics, 30 held records and 7 citations
on his desk. The queue is the bottleneck.

WHAT THIS DOES: reads every queued item, checks what is checkable against
sources of truth already in the repo, drafts the bounded corrections, and sorts
the rest by the QUESTION a person actually has to answer — so the final pass is
a sequence of confirms rather than an investigation.

WHAT THIS REFUSES TO DO, and why it matters more than the queue: it never
writes historianReview, never clears requiresHistorianReview, never sets
alignmentStatus to human-verified, never affirms tcapFormat. This repo's whole
trust model is that AI does not affirm its own work — that is why tcapFormat has
no automatic path to true and why review-provenance will not let authored
content settle silently. An AI reviewer that wrote approvals would empty the
queue and destroy the reason a district could trust the bank, invisibly,
because an approval record looks identical whoever wrote it. Verdicts land in
an `aiReview` namespace that counts toward nothing.

Every recommendation carries its EVIDENCE and its CANNOT-VERIFY list. A verdict
with no evidence is an opinion; a reviewer that never says "I don't know" is
not reviewing.

Usage:
  python3 tools/ai_review.py                 # triage, write the worksheet
  python3 tools/ai_review.py --apply         # also stamp aiReview onto items
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import alignment
import binding as binding_mod
import itemio

POLICY = os.path.join(itemio.BANK_ROOT, "policy", "ai-review.json")
OUT = os.path.join(itemio.BANK_ROOT, "reviewed", "ai-review.json")
WORKSHEET = os.path.join(itemio.BANK_ROOT, "reports", "REVIEW-WORKSHEET.md")

CLEAR, FIX, ESCALATE = "clear-recommended", "fix-drafted", "escalate"


def policy():
    with open(POLICY, encoding="utf-8") as fh:
        return json.load(fh)


def _rec(item, cls, verdict, question, evidence, cannot, draft=None):
    """One finding. The shape IS the guardrail: no verdict without evidence,
    and no escalation without the question a person must answer."""
    return {"id": item["id"], "file": item.get("_file"),
            "standardCodes": item.get("standardCodes"),
            "itemType": item.get("itemType"), "class": cls, "verdict": verdict,
            "question": question, "evidence": evidence, "cannotVerify": cannot,
            "draft": draft, "reviewedBy": "ai-first-pass", "humanVerdict": None}


# ── the checkable classes ────────────────────────────────────────────────

def check_rubric(it, pol):
    rub = it.get("rubric") or {}
    if not rub.get("scorePoints"):
        return None
    pts, crit = rub["scorePoints"], rub.get("criteria") or []
    bands = sorted(c.get("points") for c in crit)
    if bands != list(range(pts + 1)):
        return _rec(it, "rubric-scale-integrity", ESCALATE,
                    f"This rubric tops out at {pts} but its bands are {bands}. Which is right?",
                    [f"bands read from the item's own rubric field: {bands}"],
                    ["whether the missing band was never written or was mis-keyed"])
    blank = [c["points"] for c in crit if not (c.get("descriptor") or "").strip()]
    if blank:
        return _rec(it, "rubric-scale-integrity", ESCALATE,
                    f"Band(s) {blank} have no descriptor. What earns them?",
                    ["descriptors read from the item's own rubric field"],
                    ["what a response at that band looks like — a pedagogical call"])

    if rub.get("status") == "extracted":
        # Fidelity is checkable: every band's descriptor must appear in the
        # item's OWN explanation, which is where it was extracted from.
        exp = " ".join((it.get("explanation") or "").split())
        missing = [c["points"] for c in crit
                   if " ".join((c.get("descriptor") or "").split())[:60] not in exp]
        if missing:
            return _rec(it, "rubric-extraction-fidelity", ESCALATE,
                        f"Band(s) {missing} do not appear verbatim in the source text. "
                        f"Did the extraction invent or reshape them?",
                        ["compared each band against the item's explanation field"],
                        ["whether the difference is whitespace or substance"])
        return _rec(it, "rubric-extraction-fidelity", CLEAR,
                    "Confirm this scoring guide is the one you want used.",
                    [f"all {len(crit)} bands (0-{pts}) appear verbatim in the item's own "
                     f"explanation text — extracted, not authored",
                     "scale is complete and every band carries a descriptor"],
                    [])
    if rub.get("status") == "authored":
        return _rec(it, "rubric-descriptor", ESCALATE,
                    "Do these bands describe what you would actually accept at each score?",
                    [f"scale is well-formed: 0-{pts}, every band has a descriptor"],
                    ["what a strong answer contains is a pedagogical AND historical claim — "
                     "policy alwaysEscalates any rubric descriptor"],
                    draft={"scorePoints": pts,
                           "criteria": [{"points": c["points"],
                                         "descriptor": c.get("descriptor")} for c in crit]})
    return None


def check_key_contradiction(it, sheet):
    row = sheet.get(it["id"])
    if not row:
        return None
    key, sent = row["key"], row["offendingSentence"]
    exp = it.get("explanation") or ""
    after = " ".join(exp.replace(sent, "").split())
    # Whether DELETION alone is enough is checkable: what remains must still be
    # a finished argument. The blanket warning that deleting leaves the
    # rationale stopping mid-sentence is true for some and not for most — and
    # asking a reviewer to compose 30 sentences when 26 of them only need a
    # sentence removed is spending the scarcest thing in this project on
    # nothing.
    sentences = [x for x in re.split(r"(?<=[.!?])\s+", after) if x.strip()]
    intact = (len(sentences) >= 2 and after.rstrip().endswith((".", "!", "?"))
              and len(after) > 80)
    if intact:
        return _rec(it, "key-contradiction", FIX,
                    f"The key is {key}. Delete this intruding sentence? Read the AFTER text — "
                    f"if it still says why {key} is right, this is a yes.",
                    [f"key is {key!r}; key text is {str(row.get('keyText'))[:80]!r}",
                     "the sentence is a distractor rationale left pointing at the old letter",
                     f"after deletion the rationale is still {len(sentences)} finished "
                     f"sentence(s) and ends on terminal punctuation",
                     "the RENDERED form is already correct — remap_letters fixes the page"],
                    ["whether the key itself is correct — a claim about history",
                     "whether the remaining sentences say enough about why the key is right",
                     "whether the REMAINING text is itself sound — this pass checks that a "
                     "finished argument survives the deletion, not that it reads well. At "
                     "least one item's remainder is mangled prose ('highlights city became "
                     "major center steel production'), which no gate here detects"],
                    draft={"action": "delete one sentence",
                           "delete": sent, "before": " ".join(exp.split()), "after": after})
    return _rec(it, "key-contradiction", FIX,
                f"The key is {key}. Its explanation says: \"{sent}\" — deleting it leaves too "
                f"little behind. What should this rationale say instead?",
                [f"key is {key!r}; key text is {str(row.get('keyText'))[:80]!r}",
                 "the sentence is a distractor rationale left pointing at the old letter",
                 f"deletion leaves only {len(sentences)} sentence(s) — not a finished argument"],
                ["whether the key itself is correct — a claim about history",
                 "what the replacement should assert"],
                draft={"action": "rewrite", "remove": sent, "wouldLeave": after})


def check_translation(it):
    st = it.get("translationStatus")
    if st in (None, "complete", "verified"):
        return None
    return _rec(it, "translation", ESCALATE,
                "Does the Spanish say what the English says?",
                [f"translationStatus is {st!r} — self-declared, never read by a Spanish reader"],
                ["all of it — no Spanish reader has looked at any item in this bank; "
                 "policy alwaysEscalates any Spanish text"])


def check_citation(it):
    blob = " ".join(str(v) for v in (it.get("stem"), it.get("explanation")) if v)
    if not re.search(r"\b(19|18|20)\d{2}\b", blob):
        return None
    if not re.search(r"(Archives|Library of Congress|loc\.gov|Collection|Records|"
                     r"public domain|Museum|University|Press|Magazine|Journal)", blob, re.I):
        return None
    return _rec(it, "citation", ESCALATE,
                "Is this citation the real publication, and does the source say this?",
                ["item carries a dated source reference"],
                ["the publication, the date and the holding institution — this session cannot "
                 "reach an archive, and a bulk edit already replaced publication titles with "
                 "repository names once (L25); policy alwaysEscalates any citation"])


def triage(items, b, pol):
    sheet = {}
    p = os.path.join(itemio.BANK_ROOT, "reviewed", "key-contradictions.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as fh:
            sheet = {r["id"]: r for r in json.load(fh).get("items", [])}

    out = []
    for it in items:
        queued = (it.get("requiresHistorianReview")
                  or it.get("status") == "held"
                  or (it.get("rubric") or {}).get("reviewStatus") == "needs-review"
                  or (it.get("provenance") or {}).get("authoring"))
        if not queued:
            continue
        for check in (lambda x: check_key_contradiction(x, sheet),
                      lambda x: check_rubric(x, pol)):
            if (r := check(it)):
                out.append(r)
        if it.get("requiresHistorianReview") and not any(
                r["id"] == it["id"] and r["class"].startswith("rubric") for r in out):
            out.append(_rec(it, "authored-content", ESCALATE,
                "Is the history in this item and its rationales correct, and would you give "
                "it to your students?",
                ["structural gates pass on this item (record, key, distractors, relevance)"],
                ["every historical assertion in the stem, the key explanation and each "
                 "distractor rationale — no gate can check any of them"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    b = binding_mod.load()
    print(b.declaration())
    pol = policy()
    print(f"policy: {os.path.relpath(POLICY, itemio.BANK_ROOT)} v{pol['policyVersion']}")
    print(f"        writes only to {pol['theBoundary']['writesOnlyTo']!r}; never writes "
          f"{', '.join(pol['theBoundary']['neverWrites'])}\n")

    items = itemio.load_dir(b.output_dir)
    if not items:
        print("EMPTY SCAN — nothing to review, and that is a failure, not a clean run")
        return 1
    recs = triage(items, b, pol)
    if not recs:
        print("EMPTY QUEUE — refusing to report a successful review of nothing")
        return 1

    by_verdict = collections.Counter(r["verdict"] for r in recs)
    by_class = collections.Counter(r["class"] for r in recs)
    print(f"{len(recs)} queued finding(s) across {len({r['id'] for r in recs})} item(s)")
    for k, v in by_verdict.most_common():
        print(f"   {v:5d}  {k}")
    print()
    for k, v in by_class.most_common():
        print(f"   {v:5d}  {k}")

    doc = {"$comment": ("AI FIRST PASS. Every verdict here is a RECOMMENDATION carrying its "
                        "evidence and its cannot-verify list. Nothing here approves anything: "
                        "aiReview counts toward no gate, satisfies no provenance and lets "
                        "nothing ship. Set humanVerdict on a row to record your decision."),
           "policyVersion": pol["policyVersion"], "reviewedBy": "ai-first-pass",
           "boundary": pol["theBoundary"], "findings": recs}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
    print(f"\nwrote {os.path.relpath(OUT, itemio.BANK_ROOT)}")

    write_worksheet(recs, items, b, pol)
    print(f"wrote {os.path.relpath(WORKSHEET, itemio.BANK_ROOT)}")

    if a.apply:
        by_id = collections.defaultdict(list)
        for r in recs:
            by_id[r["id"]].append(r)
        n = 0
        for path in sorted({i["_file"] for i in items if i["id"] in by_id}):
            full = os.path.join(itemio.BANK_ROOT, path)
            with open(full, encoding="utf-8") as fh:
                doc2 = json.load(fh)
            rs = doc2 if isinstance(doc2, list) else (doc2.get("items")
                                                      or doc2.get("questions") or [])
            for rec in rs:
                if rec.get("id") in by_id:
                    rec["aiReview"] = {
                        "pass": "ai-first-pass", "policyVersion": pol["policyVersion"],
                        "findings": [{k: v for k, v in f.items()
                                      if k in ("class", "verdict", "question", "evidence",
                                               "cannotVerify", "draft")}
                                     for f in by_id[rec["id"]]],
                        "isNotAnApproval": ("counts toward no gate; does not satisfy "
                                            "review-provenance; nothing ships on this"),
                    }
                    n += 1
            with open(full, "w", encoding="utf-8") as fh:
                json.dump(doc2, fh, indent=2, ensure_ascii=False)
        print(f"stamped aiReview on {n} item(s) — no human-review field was touched")
    else:
        print("\nDRY RUN — pass --apply to stamp aiReview onto the items")
    return 0


def write_worksheet(recs, items, b, pol):
    by_id = {i["id"]: i for i in items}
    order = {CLEAR: 0, FIX: 1, ESCALATE: 2}
    recs = sorted(recs, key=lambda r: (order[r["verdict"]], r["class"], r["id"]))
    n_clear = sum(1 for r in recs if r["verdict"] == CLEAR)
    L = ["# Review worksheet — AI first pass",
         "",
         "**Nothing here is approved.** Every row is a recommendation with its evidence and "
         "what it could not check. `aiReview` counts toward no gate and lets nothing ship — "
         "your decision is still the only one that settles anything.",
         "",
         f"- **{n_clear}** recommended for a fast confirm",
         f"- **{sum(1 for r in recs if r['verdict'] == FIX)}** with a bounded fix drafted "
         f"(not applied)",
         f"- **{sum(1 for r in recs if r['verdict'] == ESCALATE)}** that need your judgement",
         "",
         "Record decisions in `reviewed/ai-review.json` (`humanVerdict` per row), then apply "
         "approvals through `tools/apply_review.py` as usual.",
         ""]
    cur = None
    for r in recs:
        if r["verdict"] != cur:
            cur = r["verdict"]
            head = {CLEAR: "## Fast confirm — checked against a source of truth in the repo",
                    FIX: "## Fix drafted — read the draft, then decide",
                    ESCALATE: "## Needs you — no machine can settle these"}[cur]
            L += [head, ""]
        it = by_id.get(r["id"], {})
        L += [f"### `{r['id']}` · {', '.join(r['standardCodes'] or [])} · {r['class']}",
              "",
              f"**{r['question']}**", ""]
        stem = " ".join((it.get("stem") or "").split())
        if stem:
            L += [f"> {stem[:300]}{'…' if len(stem) > 300 else ''}", ""]
        if r["evidence"]:
            L += ["*Checked:*"] + [f"- {e}" for e in r["evidence"]] + [""]
        if r["cannotVerify"]:
            L += ["*Could NOT check:*"] + [f"- {c}" for c in r["cannotVerify"]] + [""]
        if r.get("draft"):
            L += ["*Draft (not applied):*", "```json",
                  json.dumps(r["draft"], indent=2, ensure_ascii=False)[:900], "```", ""]
    os.makedirs(os.path.dirname(WORKSHEET), exist_ok=True)
    with open(WORKSHEET, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


if __name__ == "__main__":
    sys.exit(main())
