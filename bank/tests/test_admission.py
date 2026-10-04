#!/usr/bin/env python3
"""Prove admission REFUSES, gate by gate.

The mandate is explicit: "Failed items remain outside the bank in a
course/version-specific quarantine with machine-readable reasons. A
post-admission batch gate is not an acceptable substitute." Twelve gates ran on
the bank and not at admission, so an item could be ADMITTED and immediately fail
them, and the only thing that noticed was a whole-bank run nobody could
attribute to the draft that caused it. Six of those twelve judge a draft's own
content and are now at admission.

Each proof plants ONE defect in an otherwise clean draft and requires that
`submit_items.py` refuse it, BY NAME. A gate added to a list is not a gate that
runs: this file is the difference between the two claims.

`tcapFormat` is the one requirement these proofs added rather than found, and it
is the clearest instance of the pattern — it was absent from the generation
skeleton and backfilled into the bank afterwards by
`backfill_assessment_metadata.py`.
"""
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(BANK, "tools"))
sys.path.insert(0, HERE)

import binding as binding_mod
import itemio
import submit_items
from gates import content, coverage

FAILED = []


def check(label, cond, detail=""):
    print(f"    [{'ok  ' if cond else 'FAIL'}] {label}"
          + (f"\n           {detail}" if detail and not cond else ""))
    if not cond:
        FAILED.append(label)


B = binding_mod.load()

# ------------------------------------------------------------- the list itself
print("\n  THE SIX GATES ARE AT ADMISSION, AND THE OTHER SIX HAVE REASONS")

import run_gates
adm = {g.__name__ for g in submit_items.ADMISSION_GATES}
for g in ("gate_serveability", "gate_reporting_category", "gate_key_contradiction",
          "gate_tcap_format", "gate_rubric", "gate_stimulus_integrity"):
    check(f"{g} runs at admission", g in adm)

left = sorted({g.__name__ for g in run_gates.ITEM_GATES} - adm)
check("exactly six item-level gates remain bank-only", len(left) == 6, f"{left}")
src = open(os.path.join(BANK, "tools", "submit_items.py"), encoding="utf-8").read()
for g in left:
    short = g.replace("gate_", "").replace("_", "-")
    named = short in src or g in src
    check(f"…and {short} is excluded BY NAME with a reason, not by a blanket", named)
check("misconception-taxonomy is recorded as HELD, not as not-applicable",
      "HELD, not excluded" in src)
check("the vacuous-pass reason is stated for the review-state gates",
      "passes vacuously on every submission" in src)

# ------------------------------------------------------- a clean draft is admitted
print("\n  A CLEAN DRAFT PASSES ALL 18, AND EACH DEFECT IS REFUSED BY NAME")

bank = itemio.load_dir(B.output_dir)
seed = next(i for i in bank if i["id"] == "US.05-GEN-01")


def clean_draft():
    """A fresh draft: the admitted US.05 item, re-identified so it does not
    collide, with a stem the bank does not already carry."""
    it = copy.deepcopy(seed)
    it.pop("_file", None)
    it.pop("provenance", None)
    it["id"] = "US.05-PROOF-01"
    it["stem"] = ("Under the Dawes Act, what happened to land left over after "
                  "individual allotments were assigned?")
    it["stemEs"] = ("Según la Ley Dawes, ¿qué ocurrió con las tierras que quedaron "
                    "después de asignar las parcelas individuales?")
    return {"items": [it]}


def submit(draft, tmpname):
    p = os.path.join(BANK, "generation", tmpname)
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(draft, fh, indent=2, ensure_ascii=False)
    try:
        r = subprocess.run([sys.executable, "tools/submit_items.py",
                            f"generation/{tmpname}"],
                           cwd=BANK, capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr
    finally:
        os.remove(p)


rc, out = submit(clean_draft(), "_proof_clean.draft.json")
check("the clean draft clears every admission gate", rc == 0 and "REFUSED" not in out,
      out[-1500:])
check("…and all 18 are reported, not 12",
      "All 18 admission gates pass." in out, [l for l in out.splitlines() if "admission gates" in l])
check("it was a DRY RUN — nothing entered the bank",
      "DRY RUN" in out and len(itemio.load_dir(B.output_dir)) == len(bank))

# --- a code the standards file does not define. This proof EXPECTED
# serveability to catch it and was wrong: `binding.assert_codes()` raises
# BindingViolation before any gate runs, which is a harder refusal than a
# finding. Recorded as what actually happens, because a proof that asserts the
# wrong mechanism passes for the wrong reason the day the mechanism moves.
d = clean_draft(); d["items"][0]["standardCodes"] = ["US.05", "US.99"]
rc, out = submit(d, "_proof_serve.draft.json")
check("an undefined standard code is refused BEFORE the gates, by the binding "
      "assertion, and the refusal names the code",
      rc != 0 and "BINDING VIOLATION" in out and "US.99" in out, out[-700:])

# --- serveability's own half: the bilingual twins a servable item must carry
d = clean_draft(); d["items"][0]["explanationEs"] = ""
rc, out = submit(d, "_proof_es.draft.json")
check("serveability REFUSES a draft whose Spanish explanation is blank",
      rc != 0 and "serveability" in out, out[-700:])

# --- reporting category: a category with no declared source
d = clean_draft()
d["items"][0]["reportingCategory"] = "Economics"
d["items"][0]["reportingCategorySource"] = None
rc, out = submit(d, "_proof_rc.draft.json")
check("reporting-category-provenance REFUSES a category with no source — TDOE has "
      "published no 2027-28 blueprint, so a category here is invention",
      rc != 0 and "reporting-category" in out, out[-700:])

# --- key contradiction: the explanation says the key is wrong
d = clean_draft()
key = next(c for c in d["items"][0]["choices"]
           if c["id"] == d["items"][0]["correctAnswer"])
d["items"][0]["explanation"] = (
    f"{key['text'].rstrip('.')} is incorrect, because the Act did the opposite of this "
    f"and the student should not choose it.")
rc, out = submit(d, "_proof_keyc.draft.json")
check("key-contradiction REFUSES a draft whose explanation calls its own key wrong",
      rc != 0 and "key-contradiction" in out, out[-700:])

# --- tcap format: the item does not say whether it is field-testable
d = clean_draft(); d["items"][0].pop("tcapFormat", None)
rc, out = submit(d, "_proof_tcap.draft.json")
check("tcap-format REFUSES a draft that does not say whether it is field-testable — "
      "this field was backfilled into the bank AFTER admission",
      rc != 0 and "tcap-format" in out, out[-700:])

d = clean_draft(); d["items"][0]["tcapFormat"] = True
rc, out = submit(d, "_proof_tcap2.draft.json")
check("…and one CLAIMING field-testability it has not earned", rc != 0, out[-700:])

# --- rubric: a constructed-response draft with no rubric
d = clean_draft()
it = d["items"][0]
it["itemType"] = "constructed-response"
it["correctAnswer"] = None
it["choices"] = []
it.pop("rubric", None)
rc, out = submit(d, "_proof_rubric.draft.json")
check("rubric REFUSES a constructed-response draft carrying no rubric",
      rc != 0 and "rubric" in out, out[-700:])

# --- stimulus integrity: the stem orders a source the item does not carry
d = clean_draft()
d["items"][0]["stem"] = ("Use the photograph to answer the question. What happened to "
                         "tribal land under the Dawes Act of 1887?")
d["items"][0]["image"] = None
rc, out = submit(d, "_proof_stim.draft.json")
check("stimulus-integrity REFUSES a draft telling a student to use a source it lacks — "
      "111 items in the migrated bank do exactly this",
      rc != 0 and "stimulus-integrity" in out, out[-700:])

d = clean_draft()
d["items"][0]["stem"] = ("Use the photograph to answer the question. What happened to "
                         "tribal land under the Dawes Act of 1887?")
d["items"][0]["image"] = {"src": "/images/x.jpg", "alt": "a", "altEs": "a",
                          "citationChicago": "c", "rightsLabel": "r",
                          "rightsStatementVerbatim": "v", "hostingInstitution": "h",
                          "commercialUse": "unknown"}
rc, out = submit(d, "_proof_stim2.draft.json")
check("…and one whose stimulus is not cleared for commercial use — this bank is sold",
      rc != 0 and "commercialUse" in out, out[-700:])

# ------------------------------------------- the N/A that moving the gate exposed
print("\n  A TEXT-ONLY DRAFT IS N/A FOR THE STIMULUS GATE, NOT 'NOT MEASURED'")

r = content.gate_stimulus_integrity(clean_draft()["items"], B)
check("a text-only draft is N/A with a stated reason",
      r.passed and r.judged == 0 and r.inapplicable, f"{r.passed} {r.judged} {r.inapplicable!r}")
check("…and the reason names the empty population",
      "carries a stimulus" in r.inapplicable, r.inapplicable)
# The loophole this could open: N/A must be unreachable while the population exists.
r = content.gate_stimulus_integrity(itemio.load_dir(B.output_dir), B)
check("N/A is UNREACHABLE on the bank, where 111 items reference a stimulus they lack",
      not r.inapplicable and not r.passed and r.judged == 111,
      f"inapplicable={r.inapplicable!r} judged={r.judged}")

print(f"\n  {'FAILED: ' + ', '.join(FAILED) if FAILED else 'all admission proofs pass'}")
sys.exit(1 if FAILED else 0)
