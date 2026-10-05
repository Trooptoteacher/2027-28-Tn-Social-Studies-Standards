#!/usr/bin/env python3
"""Prove the governed repair path — `tools/apply_authoring.py`.

The tool wrote `[explanation, misconception]` and had no slot for a family,
while `misconception-taxonomy` fails a distractor that names a misconception in
free text and cites none. Applying a record is also what STAMPS
`provenance.authoring`, which is what makes that gate begin judging the item —
so the repair path was manufacturing the findings it is meant to clear, and 20
of the 22 items failing it today were written by it.

These proofs run the real tool against a COPY of the repository, because a tool
whose `--apply` path is only ever exercised by a dry run is a tool whose apply
path is untested. That is not hypothetical here: the dry run and the write take
different branches through `normalise`.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.dirname(HERE)
REPO = os.path.dirname(BANK)
sys.path.insert(0, os.path.join(BANK, "tools"))

FAILED = []


def check(label, cond, detail=""):
    print(f"    [{'ok  ' if cond else 'FAIL'}] {label}"
          + (f"\n           {detail}" if detail and not cond else ""))
    if not cond:
        FAILED.append(label)


# ------------------------------------------------------------ normalise(), unit
print("\n  BOTH AUTHORED SHAPES NORMALISE TO ONE")

import apply_authoring as aa

# Four values since taxonomyVersion 2 (explanation, misconception, family,
# function). The legacy 2-list carries NEITHER axis, which is the point: it is
# still legal and still tells you what it leaves undone.
check("the legacy 2-list still parses, with neither axis",
      aa.normalise(["why it is wrong", "what the student believes"])
      == ("why it is wrong", "what the student believes", None, None))
check("the object form carries a family",
      aa.normalise({"explanation": "x" * 12, "misconception": "y" * 12,
                    "misconceptionFamily": "MC-F-04"})[2] == "MC-F-04")
check("…and a distractorFunction",
      aa.normalise({"explanation": "x" * 12, "misconception": "y" * 12,
                    "distractorFunction": "partial-truth"})[3] == "partial-truth")
check("the object form without either axis is legal and reports None for both",
      aa.normalise({"explanation": "x" * 12, "misconception": "y" * 12})[2:] == (None, None))

for bad, why in [(["only one"], "a 1-list"), (["a", ""], "an empty half"),
                 ("a string", "a bare string"), ({"explanation": "x"}, "no misconception")]:
    try:
        aa.normalise(bad)
        check(f"{why} is refused", False, "it was accepted")
    except aa.AuthoringError:
        check(f"{why} is refused", True)

check("14 LIVE families are what a family is checked against (MC-F-11 retired, "
      "MC-F-15 added)",
      len(aa._families()) == 14 and "MC-F-11" not in aa._families(),
      f"found {sorted(aa._families())}")

# --------------------------------------------------- end to end, in a sandbox
print("\n  THE APPLY PATH, RUN FOR REAL IN A COPY OF THE REPO")

tmp = tempfile.mkdtemp(prefix="aa-proof-")
sandbox = os.path.join(tmp, "repo")
shutil.copytree(REPO, sandbox, symlinks=True,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
SB = os.path.join(sandbox, "bank")


def run(*args):
    return subprocess.run([sys.executable, "tools/apply_authoring.py", *args],
                          cwd=SB, capture_output=True, text=True)


def find_item(iid):
    for root, _, files in os.walk(os.path.join(SB, "items")):
        for f in files:
            if not f.endswith(".json"):
                continue
            p = os.path.join(root, f)
            doc = json.load(open(p, encoding="utf-8"))
            for it in doc.get("items", []):
                if it.get("id") == iid:
                    return p, it
    return None, None


TARGET = "q-us44-dok1-2"          # three familyless distractors, from form-a.json
path, before = find_item(TARGET)
check("the sandbox holds the target item", before is not None)
_before_bytes = open(path, "rb").read()
cids = [c["id"] for c in before["choices"] if c["id"] != before["correctAnswer"]]

rec = {"$comment": "proof fixture", "items": {TARGET: {"distractors": {
    cid: {"explanation": f"This option names a real New Deal-era body, but not the "
                         f"one the stem asks about ({cid}).",
          "misconception": f"merges the RFC with another Hoover-era measure ({cid})",
          "distractorFunction": "common-misconception",
          "misconceptionFamily": "MC-F-06"} for cid in cids}}}}
recp = os.path.join(SB, "authoring", "proof-family.json")
json.dump(rec, open(recp, "w", encoding="utf-8"), indent=2)

r = run("authoring/proof-family.json")
check("a record carrying both axes validates", r.returncode == 0, r.stdout + r.stderr)
check("…and the untagged warning is NOT printed for it",
      "carry no distractorFunction" not in r.stdout, r.stdout)
_, mid = find_item(TARGET)
# Measured as "unchanged", not as "empty". The first version asserted the
# target carried no family at all, which was true only while nothing in the
# bank was tagged; the 48-tag write of 2026-10-04 broke the premise and the
# proof read as a dry-run leak. What it always meant to say is that the file on
# disk did not move.
check("the dry run wrote nothing — the file is byte-identical",
      open(path, "rb").read() == _before_bytes, "the dry run modified the file")

r = run("authoring/proof-family.json", "--apply")
check("--apply exits 0", r.returncode == 0, r.stdout + r.stderr)
_, after = find_item(TARGET)
got = {c["id"]: c.get("misconceptionFamily") for c in after["choices"]}
fn = {c["id"]: c.get("distractorFunction") for c in after["choices"]}
check("every distractor named now carries its family",
      all(got[c] == "MC-F-06" for c in cids), f"{got}")
check("…and its distractorFunction",
      all(fn[c] == "common-misconception" for c in cids), f"{fn}")
check("the KEY carries neither — a distractor's diagnosis is never written onto "
      "the correct answer",
      got[after["correctAnswer"]] is None and fn[after["correctAnswer"]] is None,
      f"{got} {fn}")
check("the item is marked authored + requiresHistorianReview — a family is a claim "
      "about what a student believes",
      after.get("status") == "authored" and after.get("requiresHistorianReview") is True)

# The gate the whole change exists for.
sys.path.insert(0, os.path.join(SB, "tools"))
r2 = subprocess.run([sys.executable, "-c", """
import sys; sys.path.insert(0,'tools')
import binding as bm, itemio
from gates import content
b=bm.load(); items=itemio.load_dir(b.output_dir)
f=[x for x in content.gate_misconception_taxonomy(items).findings if x.item_id=='q-us44-dok1-2']
print(len(f))
"""], cwd=SB, capture_output=True, text=True)
check("misconception-taxonomy now reports ZERO findings on that item "
      "(it reported 3 before)", r2.stdout.strip() == "0", r2.stdout + r2.stderr)

# An unknown family must be refused BEFORE anything is written.
bad = json.loads(json.dumps(rec))
bad["items"][TARGET]["distractors"][cids[0]]["misconceptionFamily"] = "MC-F-99"
badp = os.path.join(SB, "authoring", "proof-bad-family.json")
json.dump(bad, open(badp, "w", encoding="utf-8"), indent=2)
r = run("authoring/proof-bad-family.json", "--apply")
check("a family the taxonomy does not define is REFUSED", r.returncode != 0)
check("…and the refusal names it and says how many are LIVE",
      "MC-F-99" in (r.stdout + r.stderr) and "14 live" in (r.stdout + r.stderr),
      r.stdout + r.stderr)

# The legacy shape still works, and still says what it costs.
legacy = {"items": {"q-us44-dok2-1": {"distractors": {
    "A": ["A real Hoover-era measure, but not the Bonus Army.",
          "merges the Bonus Army with the RFC, proof fixture"]}}}}
lp = os.path.join(SB, "authoring", "proof-legacy.json")
json.dump(legacy, open(lp, "w", encoding="utf-8"), indent=2)
r = run("authoring/proof-legacy.json")
check("the legacy 2-list record still validates — eight committed records use it",
      r.returncode == 0, r.stdout + r.stderr)
check("…and the run SAYS it will fail misconception-taxonomy, naming the distractor",
      "carry no distractorFunction" in r.stdout and "q-us44-dok2-1/A" in r.stdout,
      r.stdout)

shutil.rmtree(tmp, ignore_errors=True)

# ------------------------------- the review state moves only on a real change
print("\n  A TAXONOMY TAG DOES NOT UN-APPROVE A REVIEWED ITEM")

# The tool set requiresHistorianReview unconditionally and left
# `historianReview` alone, so an approved item came out BOTH approved and
# flagged — 19 of them. The first fix superseded every approval the tool
# touched: it passed the gate and DISCARDED 16 of Sean's recorded judgements on
# a technicality. A distractorFunction classifies how an option goes wrong; the
# historian approved the HISTORY. So the question is measured, not assumed.

check("_claims() covers the fields an approval is about",
      set(aa.CLAIM_FIELDS) == {"stem", "stemEs", "explanation", "explanationEs",
                               "dokRationale"}, aa.CLAIM_FIELDS)
check("…and the two taxonomy axes are NOT among them — including them would "
      "un-approve every item a tagging pass touched",
      "distractorFunction" not in aa.CLAIM_CHOICE_FIELDS
      and "misconceptionFamily" not in aa.CLAIM_CHOICE_FIELDS, aa.CLAIM_CHOICE_FIELDS)

probe = {"id": "X", "stem": "s", "explanation": "e", "dokRationale": "d",
         "choices": [{"id": "A", "text": "t", "misconception": "m"}]}
tagged_only = json.loads(json.dumps(probe))
tagged_only["choices"][0]["distractorFunction"] = "partial-truth"
tagged_only["choices"][0]["misconceptionFamily"] = "MC-F-01"
check("adding both tags leaves the claim fingerprint UNCHANGED",
      aa._claims(probe) == aa._claims(tagged_only))
reworded = json.loads(json.dumps(probe))
reworded["choices"][0]["text"] = "a different option"
check("…but rewording a choice CHANGES it", aa._claims(probe) != aa._claims(reworded))
for f in ("stem", "explanation", "dokRationale"):
    moved = json.loads(json.dumps(probe)); moved[f] = "moved"
    check(f"…and so does changing {f}", aa._claims(probe) != aa._claims(moved))
mis = json.loads(json.dumps(probe))
mis["choices"][0]["misconception"] = "a different confusion"
check("…and so does rewriting a free-text misconception, which IS a claim",
      aa._claims(probe) != aa._claims(mis))

# Measured on the real bank, after the 48-tag write.
import binding as _bm, itemio as _io
bank = _io.load_dir(_bm.load().output_dir)
approved_now = [i for i in bank if i.get("historianReview")]
check("all 19 standing approvals SURVIVED the tagging pass",
      len(approved_now) == 19, len(approved_now))
check("…and none was moved to the superseded list",
      not any(i.get("historianReviewSuperseded") for i in bank))
check("no approved item is ALSO flagged, except the 3 that were already "
      "contradictory before any of this — those are a promotion to make, "
      "which is Sean's call and not a build's",
      sorted(i["id"] for i in bank
             if i.get("historianReview") and i.get("requiresHistorianReview"))
      == ["q-us2-dok4-cr2", "q-us3-dok4-cr3", "q-us6-dok4-cr3"],
      sorted(i["id"] for i in bank
             if i.get("historianReview") and i.get("requiresHistorianReview")))

# ------------------------------------------- the proposal is a draft, not a write
print("\n  THE FAMILY PROPOSAL CANNOT READ AS AN APPROVAL")

PROP = os.path.join(BANK, "reviewed", "misconception-family-proposal.json")
prop = json.load(open(PROP, encoding="utf-8"))
# The purpose of this block is unchanged — a draft a model wrote must never
# read as a signature. What changed is that the TAXONOMY is approved while the
# ASSIGNMENTS are not, so the status moved from DRAFT to READY TO APPLY and the
# proof follows it rather than being dropped.
check("it declares what was and was not written",
      prop["status"].startswith("PARTLY APPLIED"), prop["status"][:60])
check("…and every row carries a disposition, so nothing is ambiguous about "
      "whether it reached the bank",
      all(a.get("disposition") for a in prop["assignments"]))
check("…48 applied, 14 held, 4 for rewrite",
      prop["dispositions"] == {"APPLIED 2026-10-04": 48, "HELD": 14, "REWRITE": 4},
      prop["dispositions"])
check("the applied record is NAMED, so a reviewer can read what was written",
      prop["applied"]["record"] == "authoring/misconception-tags-batch-1.json")
check("…and who authorised it", "Sean Reynolds" in prop["applied"]["authorisedBy"])
check("it covers exactly the 66 distractors that fail the gate",
      len(prop["assignments"]) == 66, f"{len(prop['assignments'])}")
check("every assignment carries a FIT, so a guess cannot be read as a diagnosis",
      all(a.get("fit") for a in prop["assignments"]))
check("52 of 66 resolve cleanly against taxonomyVersion 2, and the file says so "
      "(it was 33 against v1)",
      prop["fitDistribution"]["clear"] == 52, prop["fitDistribution"])
check("the misconception text is quoted VERBATIM from the item, never paraphrased",
      all(a["misconceptionVerbatim"] for a in prop["assignments"]))

import binding as binding_mod, itemio
from gates import content
b = binding_mod.load()
items = itemio.load_dir(b.output_dir)
byid = {i["id"]: i for i in items}
drift = [a for a in prop["assignments"]
         if (next((c.get("misconception") for c in byid[a["itemId"]]["choices"]
                   if c["id"] == a["choiceId"]), None) != a["misconceptionVerbatim"])]
check("…and still matches the bank — a proposal quoting text that has since moved "
      "sends a reviewer to the wrong distractor",
      not drift, f"{len(drift)} row(s) stale: {[(a['itemId'], a['choiceId']) for a in drift[:4]]}")

# The whole point, restated for a partly-applied record: what is in the bank is
# exactly what was authorised, and the held rows are still held. The
# applied-state measurements live in tests/test_taxonomy.py; this asserts the
# RECORD agrees with the bank, which is the half this suite owns.
live = content.gate_misconception_taxonomy(items)
check("the gate's remaining findings equal the rows still held",
      len(live.findings) == 14 + 4, f"{len(live.findings)} finding(s)")
held = {(a["itemId"], a["choiceId"]) for a in prop["assignments"]
        if not a["disposition"].startswith("APPLIED")}
tagged = {(i["id"], c["id"]) for i in items for c in itemio.choices(i)
          if isinstance(c, dict) and c.get("distractorFunction")}
check("…and NO held row was written anyway", not (held & tagged),
      f"{sorted(held & tagged)[:4]}")
applied = {(a["itemId"], a["choiceId"]) for a in prop["assignments"]
           if a["disposition"].startswith("APPLIED")}
check("…and every applied row IS in the bank — the record is not ahead of the data",
      applied <= tagged, f"{sorted(applied - tagged)[:4]}")
check("…and the bank carries nothing the record does not name",
      tagged <= applied, f"{sorted(tagged - applied)[:4]}")
# A draft must not be mistakable for the signed thing.
check("the draft is NOT keyed `tnMaterialsReview`-style as a settled review — the "
      "key names it a proposal",
      "misconception-family-proposal" in os.path.basename(PROP)
      and "approved" not in prop and "signedBy" not in prop)

print(f"\n  {'FAILED: ' + ', '.join(FAILED) if FAILED else 'all repair-path proofs pass'}")
sys.exit(1 if FAILED else 0)
