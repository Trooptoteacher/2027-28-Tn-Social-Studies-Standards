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
check("the dry run wrote nothing",
      [c.get("misconceptionFamily") for c in mid["choices"]] == [None] * len(mid["choices"]))

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

# ------------------------------------------- the proposal is a draft, not a write
print("\n  THE FAMILY PROPOSAL CANNOT READ AS AN APPROVAL")

PROP = os.path.join(BANK, "reviewed", "misconception-family-proposal.json")
prop = json.load(open(PROP, encoding="utf-8"))
# The purpose of this block is unchanged — a draft a model wrote must never
# read as a signature. What changed is that the TAXONOMY is approved while the
# ASSIGNMENTS are not, so the status moved from DRAFT to READY TO APPLY and the
# proof follows it rather than being dropped.
check("it declares itself not-yet-applied", prop["status"].startswith("READY TO APPLY"))
check("…and says the write is a SEPARATE act from approving the taxonomy",
      "separate act" in prop["status"])
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

# The whole point: nothing was applied.
live = content.gate_misconception_taxonomy(items)
check("NOTHING from the proposal is in the bank — the gate still fails all 66, "
      "which is the honest state while the taxonomy is DRAFT",
      len(live.findings) == 66, f"{len(live.findings)} finding(s)")
check("no bank item cites a family yet",
      not any(c.get("misconceptionFamily") for i in items for c in itemio.choices(i)
              if isinstance(c, dict)))
# A draft must not be mistakable for the signed thing.
check("the draft is NOT keyed `tnMaterialsReview`-style as a settled review — the "
      "key names it a proposal",
      "misconception-family-proposal" in os.path.basename(PROP)
      and "approved" not in prop and "signedBy" not in prop)

print(f"\n  {'FAILED: ' + ', '.join(FAILED) if FAILED else 'all repair-path proofs pass'}")
sys.exit(1 if FAILED else 0)
