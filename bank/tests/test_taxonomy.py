#!/usr/bin/env python3
"""Prove the two-axis misconception taxonomy (taxonomyVersion 2).

A distractor says WHAT IT DOES (`distractorFunction`) and, when what it does is
encode a real reasoning error, WHICH error (`misconceptionFamily`). One field
held both until 2026-10-04, which is why 6 of the bank's 66 real misconceptions
could not be classified at all — "contradicts the source", "invents a time
limit the treaty does not contain" and "answers a question that was not asked"
describe the OPTION, not the student.

Two proofs here are about the SHAPE of the change rather than its behaviour,
and they are the ones that matter in a year: that MC-F-11 cannot come back as a
family, and that `contradicts-stimulus` is accepted on the items it exists for.
The second nearly shipped broken — see the comment on it.
"""
from __future__ import annotations

import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(BANK, "tools"))
sys.path.insert(0, HERE)

import apply_authoring as aa
import binding as binding_mod
import fixtures
import itemio
from gates import content

FAILED = []


def check(label, cond, detail=""):
    print(f"    [{'ok  ' if cond else 'FAIL'}] {label}"
          + (f"\n           {detail}" if detail and not cond else ""))
    if not cond:
        FAILED.append(label)


B = binding_mod.load()
TAX = json.load(open(os.path.join(BANK, "taxonomy", "misconception-families.json"),
                     encoding="utf-8"))


def authored(**over):
    """An authored mcq whose three distractors are tagged as `over` says."""
    it = fixtures._sync_key(fixtures.item(id="TAX-1"), "B")
    it.setdefault("provenance", {})["authoring"] = {"record": "proof"}
    for c in it["choices"]:
        if c["id"] == it["correctAnswer"]:
            continue
        for k, v in over.items():
            c[k] = v
    return [it]


def findings(items):
    return content.gate_misconception_taxonomy(items).findings


# ------------------------------------------------------------------- the file
print("\n  THE TAXONOMY DECLARES BOTH AXES")

check("taxonomyVersion is 2", TAX["taxonomyVersion"] == 2, TAX["taxonomyVersion"])
check("it is no longer DRAFT — Sean approved it for citation",
      TAX["status"].startswith("APPROVED"), TAX["status"][:70])
check("…and the approval names who and when",
      "Sean Reynolds" in TAX["status"] and "2026-10-04" in TAX["status"])
check("it says a family remains a per-assignment claim needing historian review",
      "requiresHistorianReview" in TAX["status"])

fams = {f["id"]: f for f in TAX["families"]}
funcs = {x["id"]: x for x in TAX["distractorFunctions"]}
live = {k for k, v in fams.items() if not v.get("retired")}
check("MC-F-15 Polarity reversal exists and is live",
      fams.get("MC-F-15", {}).get("name") == "Polarity reversal" and "MC-F-15" in live)
check("…and it says what distinguishes it from MC-F-04, which is the whole risk",
      "MC-F-04" in (fams["MC-F-15"].get("notToBeConfusedWith") or {}))
check("exactly one function requires a family, and it is common-misconception",
      [k for k, v in funcs.items() if v.get("requiresFamily")] == ["common-misconception"],
      [k for k, v in funcs.items() if v.get("requiresFamily")])
check("two functions are declared ITEM FLAWS",
      sorted(k for k, v in funcs.items() if v.get("itemFlaw")) == ["implausible", "surface-cue"])
check("plausible-fabrication carries the cross-product flag, unsettled",
      "reviewNote" in funcs["plausible-fabrication"]
      and "OPPOSITE conclusion" in funcs["plausible-fabrication"]["reviewNote"])

# ---------------------------------------------------------------- MC-F-11
print("\n  MC-F-11 WAS NEVER A FAMILY, AND CANNOT COME BACK AS ONE")

check("MC-F-11 is retired, not deleted — deleting erases the reasoning",
      fams["MC-F-11"].get("retired") is True and "MC-F-11" in fams)
check("…and it points at the function that replaced it",
      "surface-cue" in (fams["MC-F-11"].get("supersededBy") or ""))
check("the retirement reason quotes MC-F-11's own words against it",
      "test-taking error" in (fams["MC-F-11"].get("retiredReason") or ""))
check("_families() returns LIVE families only, so new content cannot cite it",
      "MC-F-11" not in content._families() and len(content._families()) == 14,
      sorted(content._families()))
f = findings(authored(distractorFunction="common-misconception",
                      misconceptionFamily="MC-F-11"))
check("citing the retired family FAILS, and the finding says what superseded it",
      len(f) == 3 and "RETIRED" in f[0].detail and "surface-cue" in f[0].detail,
      f and f[0].detail)

# --------------------------------------------------------------- the gate
print("\n  A FAMILY IS REQUIRED ONLY WHERE IT MEANS SOMETHING")

check("common-misconception + a live family passes",
      not findings(authored(distractorFunction="common-misconception",
                            misconceptionFamily="MC-F-15")))
f = findings(authored(distractorFunction="common-misconception"))
check("common-misconception with NO family fails", len(f) == 3 and "cites no family" in f[0].detail)
check("partial-truth with no family PASSES — the error is in reading the question, "
      "not in a belief about the past",
      not findings(authored(distractorFunction="partial-truth")))
check("right-answer-wrong-question with no family passes",
      not findings(authored(distractorFunction="right-answer-wrong-question")))
f = findings(authored(distractorFunction="partial-truth", misconceptionFamily="MC-F-15"))
check("a family on a NON-misconception function fails — it is a diagnosis the option "
      "does not support",
      len(f) == 3 and "Only" in f[0].detail, f and f[0].detail)
f = findings(authored(distractorFunction="made-up"))
check("an undefined function fails, and the finding lists the real ones",
      len(f) == 3 and "does not define" in f[0].detail and "partial-truth" in f[0].detail)
f = findings(authored(misconceptionFamily="MC-F-15"))
check("a family with NO function fails — v1's single field is not accepted any more",
      len(f) == 3 and "names no distractorFunction" in f[0].detail, f and f[0].detail)

print("\n  THE TWO ITEM FLAWS ARE REPORTED, NOT ACCEPTED")
for flaw in ("surface-cue", "implausible"):
    f = findings(authored(distractorFunction=flaw))
    check(f"{flaw} is reported as an ITEM FLAW and tells the writer to rewrite",
          len(f) == 3 and "ITEM FLAW" in f[0].detail and "Rewrite" in f[0].detail,
          f and f[0].detail)

# ------------------------------------------- contradicts-stimulus, the near-miss
print("\n  contradicts-stimulus IS ACCEPTED ON THE ITEMS IT EXISTS FOR")
# This check first read `it.get("image")`. ZERO items in this bank carry an
# image record — all 178 source-bearing items supply the source INLINE in the
# stem — so it would have failed the function on EVERY item in the bank,
# including all 178 it was written for. Caught by measuring the field rather
# than trusting its name.
bank = itemio.load_dir(B.output_dir)
check("no item in the bank carries an `image` record, which is why the first "
      "version of this check was wrong",
      not any(i.get("image") for i in bank))
check("178 items DO supply a source, inline",
      sum(1 for i in bank if content.supplies_a_source(i)) == 178,
      sum(1 for i in bank if content.supplies_a_source(i)))

byid = {i["id"]: i for i in bank}


def tagged(iid, fn):
    it = copy.deepcopy(byid[iid])
    it.setdefault("provenance", {})["authoring"] = {"record": "proof"}
    for c in it["choices"]:
        if c["id"] != it["correctAnswer"]:
            c["distractorFunction"], c["misconceptionFamily"] = fn, None
    return [it]


check("accepted on PS-0067, which puts an excerpt in front of the student",
      not [x for x in findings(tagged("PS-0067", "contradicts-stimulus"))
           if "contradict" in x.detail])
check("REFUSED on PSTIM-0079, which orders a photograph it does not carry — there "
      "is nothing there to contradict",
      [x for x in findings(tagged("PSTIM-0079", "contradicts-stimulus"))
       if "no source" in x.detail])
check("a plain content item with no source refuses it too",
      [x for x in findings(authored(distractorFunction="contradicts-stimulus"))
       if "no source" in x.detail])

# ----------------------------------------------------------- the repair path
print("\n  THE REPAIR PATH WRITES BOTH AXES, AND REFUSES THE REST")

e, m = "x" * 14, "y" * 14
check("normalise returns four values now",
      len(aa.normalise({"explanation": e, "misconception": m,
                        "distractorFunction": "partial-truth"})) == 4)
check("the legacy 2-list still parses, with neither axis",
      aa.normalise([e, m]) == (e, m, None, None))
check("the object form carries both",
      aa.normalise({"explanation": e, "misconception": m,
                    "distractorFunction": "common-misconception",
                    "misconceptionFamily": "MC-F-15"})[2:] == ("MC-F-15", "common-misconception"))

live_f, funcs_f = aa._taxonomy()
check("apply_authoring reads LIVE families only", "MC-F-11" not in live_f and len(live_f) == 14)
check("…and all seven functions", len(funcs_f) == 7)


def rejected(payload):
    rec = {"items": {"q-us44-dok1-2": {"distractors": {"A": payload}}}}
    items = itemio.load_dir(B.output_dir)
    try:
        aa.validate(rec, {i["id"]: i for i in items})
        return None
    except aa.AuthoringError as err:
        return str(err)

for payload, why, needle in [
    ({"explanation": e, "misconception": m, "distractorFunction": "common-misconception"},
     "common-misconception with no family", "cites no misconceptionFamily"),
    ({"explanation": e, "misconception": m, "distractorFunction": "common-misconception",
      "misconceptionFamily": "MC-F-11"}, "a retired family", "does not define as live"),
    ({"explanation": e, "misconception": m, "distractorFunction": "common-misconception",
      "misconceptionFamily": "MC-F-99"}, "an undefined family", "does not define as live"),
    ({"explanation": e, "misconception": m, "distractorFunction": "surface-cue"},
     "an ITEM FLAW as a function", "ITEM FLAW"),
    ({"explanation": e, "misconception": m, "distractorFunction": "invented"},
     "an undefined function", "does not define"),
    ({"explanation": e, "misconception": m, "misconceptionFamily": "MC-F-15"},
     "a family with no function", "names no distractorFunction"),
    ({"explanation": e, "misconception": m, "distractorFunction": "partial-truth",
      "misconceptionFamily": "MC-F-15"}, "a family under a non-misconception function",
     "Only 'common-misconception'"),
]:
    got = rejected(payload)
    check(f"the record is refused for {why}", got is not None and needle in got, got)

check("a well-formed record is accepted",
      rejected({"explanation": e, "misconception": m,
                "distractorFunction": "common-misconception",
                "misconceptionFamily": "MC-F-06"}) is None)

# -------------------------------------------------------------- the proposal
print("\n  THE RE-MEASURED PROPOSAL, AND WHAT THE DECISION BOUGHT")

prop = json.load(open(os.path.join(BANK, "reviewed",
                                   "misconception-family-proposal.json"), encoding="utf-8"))
check("it is measured against taxonomyVersion 2", prop["taxonomyVersion"] == 2)
check("all 66 are covered", len(prop["assignments"]) == 66)
check("52 now resolve cleanly, up from 33", prop["fitDistribution"]["clear"] == 52,
      prop["fitDistribution"])
check("ZERO unresolved and ZERO unclassifiable remain — both categories are gone",
      "unresolved" not in prop["fitDistribution"]
      and "function-not-family" not in prop["fitDistribution"], prop["fitDistribution"])
check("MC-F-15 absorbed 12 cases and is the second-most-cited family",
      prop["familiesUsed"]["MC-F-15"] == 12, prop["familiesUsed"])
check("the 13 approximate fits were NOT forced clean by the new options",
      prop["fitDistribution"]["approximate"] == 13, prop["fitDistribution"])
check("every assignment names a function", all(a["proposedDistractorFunction"]
                                               for a in prop["assignments"]))
check("a family appears only under common-misconception",
      all((a["proposedFamily"] is None)
          == (a["proposedDistractorFunction"] != "common-misconception")
          for a in prop["assignments"]))
check("the plausible-fabrication tension is carried as an open finding",
      any(f["id"] == "F7" for f in prop["whatIsStillOpen"]))
check("it is STILL not applied, and says so", "READY TO APPLY" in prop["status"])
check("…and the bank bears that out — nothing cites a function or a family yet",
      not any(c.get("misconceptionFamily") or c.get("distractorFunction")
              for i in bank for c in itemio.choices(i) if isinstance(c, dict)))
check("the misconceptions are quoted verbatim and still match the bank",
      all(a["misconceptionVerbatim"] == next(
          (c.get("misconception") for c in byid[a["itemId"]]["choices"]
           if c["id"] == a["choiceId"]), None) for a in prop["assignments"]))

print(f"\n  {'FAILED: ' + ', '.join(FAILED) if FAILED else 'all taxonomy proofs pass'}")
sys.exit(1 if FAILED else 0)
