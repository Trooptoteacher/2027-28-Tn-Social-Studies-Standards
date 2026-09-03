#!/usr/bin/env python3
"""Regression pins for defects found in THIS build.

Every entry is a bug that shipped, or nearly shipped, and was fixed. A fix
without a pin is a fix that returns the next time someone edits nearby. Each
test names the defect in the words it was found in, so a future failure reads
as "you reintroduced X", not "assertion false".
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(BANK, "tools"))
sys.path.insert(0, HERE)

import alignment
import binding as binding_mod
import fixtures
from gates import Result, record, coverage, content

B = binding_mod.load(os.path.join(HERE, "fixtures", "testbinding", "binding.json"))
CODES = ["US.04", "US.05"]
FAILED = []


def check(label, cond, detail=""):
    print(f"  [{'ok  ' if cond else 'FAIL'}] {label}" + (f"\n         {detail}" if detail and not cond else ""))
    if not cond:
        FAILED.append(label)


print("=" * 74)
print("REGRESSION PINS")
print("=" * 74)

# ── truncation: trailing digits were being stripped ──────────────────────
print("\n  truncation — 384 false positives came from these two")
b = fixtures.clean_bank(CODES)
b[0]["stem"] = "Which was a direct consequence of the Homestead Act of 1862?"
r = record.gate_truncation(b, B)
check("a complete stem ending in a year + '?' is NOT truncation",
      r.passed, f"stripping trailing DIGITS turned this into '...Act of' and flagged "
                f"a dangling preposition. findings={[str(f)[:80] for f in r.findings[:2]]}")

b = fixtures.clean_bank(CODES)
b[0]["stem"] = "The Transcontinental Railroad connected Omaha, Nebraska to:"
r = record.gate_truncation(b, B)
check("a TCAP completion stem ending in a colon is NOT truncation",
      r.passed, f"findings={[str(f)[:80] for f in r.findings[:2]]}")

b = fixtures.clean_bank(CODES)
b[0]["explanation"] = "The Act mattered because it changed who could own land and:"
r = record.gate_truncation(b, B)
check("an EXPLANATION ending in a colon IS truncation (only stems complete)",
      not r.passed)

b = fixtures.clean_bank(CODES)
b[0]["stem"] = "How did the Homestead Act change settlement patterns in the"
check("a stem that simply stops IS truncation",
      not record.gate_truncation(b, B).passed)

# ── de-bias: statistically significant but practically trivial ───────────
print("\n  key-position-debias — effect size, not p-value alone")
big = fixtures.clean_bank(CODES * 60)          # large n makes chi-square touchy
mcq = [i for i in big if i["itemType"] == "mcq"]
for n, it in enumerate(mcq):                    # ~27/25/24/24, unbeatable
    if n % 50 == 0:
        fixtures._sync_key(it, "A")
r = coverage.gate_key_position(big, B)
check("a 27/25/24/24 split at large n PASSES (no student can exploit it)",
      r.passed, f"note={r.note} findings={[str(f)[:90] for f in r.findings[:1]]}")

allc = fixtures.clean_bank(CODES * 60)
for it in allc:
    if it["itemType"] == "mcq":
        fixtures._sync_key(it, "C")
r = coverage.gate_key_position(allc, B)
check("a bank where every key is C FAILS", not r.passed)
check("the finding quotes the share, not just a chi-square",
      any("%" in str(f) for f in r.findings), f"got {[str(f)[:90] for f in r.findings[:1]]}")

# ── a gate that judged nothing is not a pass ────────────────────────────
print("\n  vacuous gates — teacher-side-isolation reported PASS over 3,986 while judging 0")
clean = fixtures.clean_bank(CODES)              # nothing carries a surface tag
r = coverage.gate_teacher_side_isolation(clean, B)
check("no student surfaces present -> NOT MEASURED, not PASS",
      r.status == "NOT MEASURED" and not r.measured, f"status={r.status!r} judged={r.judged}")
check("the runner does not count NOT MEASURED as a pass",
      not (r.passed and r.measured))
check("all-gates-measured FAILS while any gate formed no opinion",
      not coverage.unmeasured_gates([r, Result("other", True, 5, [], judged=5)]).passed)
check("all-gates-measured PASSES when every gate judged something",
      coverage.unmeasured_gates([Result("a", True, 5, [], judged=5),
                                 Result("b", False, 5, [], judged=5)]).passed)

no_mcq = [i for i in fixtures.clean_bank(CODES) if i["itemType"] != "mcq"]
r = record.gate_distractor_coverage(no_mcq, B)
check("distractor-coverage over a bank with no selected-response is NOT MEASURED",
      not r.measured, f"status={r.status!r} judged={r.judged}")

# ── alignment signal strength, stated legibly ───────────────────────────
print("\n  alignment signals — a signal must actually identify something")
check("'American' is not a usable signal (it matches almost every US item)",
      "American" not in alignment.signals("desire to spread American democratic"),
      f"got {alignment.signals('desire to spread American democratic')}")
check("'Amendment' alone is not a usable signal",
      alignment.signals("18th Amendment") == ["18th Amendment"],
      f"got {alignment.signals('18th Amendment')}")
check("a bare category noun ('Act', 'Treaty', 'War') identifies nothing",
      all(alignment._key(w) in alignment._GENERIC for w in ("Act", "Treaty", "War")))

# ── an extractor must prove itself before its silence counts ────────────
print("\n  extraction — a broken extractor's zero looks exactly like a real zero")
import extraction

BROKEN = "EN-US EN-US EN-US EN-US"          # what the PDF scan actually produced
GOOD = "Summarize the major events of Reconstruction, and explain the impact of the "\
       "Compromise of 1877."
CONTROLS = ["Compromise of 1877", "Reconstruction"]

try:
    extraction.absent(BROKEN, "reporting category", CONTROLS, source="standards PDF")
    check("a broken extraction REFUSES to report an absence", False,
          "it returned an answer instead of raising")
except extraction.UnprovenExtractor as e:
    check("a broken extraction REFUSES to report an absence", True)
    check("the error says the finding is meaningless, not that the term is missing",
          "meaningless" in str(e).lower())

check("a proven extraction may report a real absence",
      extraction.absent(GOOD, "reporting category", CONTROLS, source="standards PDF"))
check("a proven extraction confirms a real presence",
      not extraction.absent(GOOD, "Compromise of 1877", CONTROLS, source="standards PDF"))
try:
    extraction.prove(GOOD, [], source="standards PDF")
    check("supplying NO controls is itself refused", False)
except extraction.UnprovenExtractor:
    check("supplying NO controls is itself refused", True)


# ── the lessons ledger enforces itself ──────────────────────────────────
print("\n  check-lessons — the rule 'every mistake gets a guard', made enforceable")
import copy, json, subprocess, tempfile, shutil

LEDGER = os.path.join(BANK, "lessons.json")
BASE = json.load(open(LEDGER, encoding="utf-8"))


def run_ledger(doc):
    """Run the checker against a mutated ledger, restoring the real one after."""
    orig = open(LEDGER, encoding="utf-8").read()
    try:
        json.dump(doc, open(LEDGER, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        r = subprocess.run([sys.executable, os.path.join(BANK, "tools", "check_lessons.py")],
                           capture_output=True, text=True)
        return r.returncode, r.stdout
    finally:
        open(LEDGER, "w", encoding="utf-8").write(orig)


rc, _ = run_ledger(BASE)
check("the real ledger PASSES", rc == 0)

d = copy.deepcopy(BASE); d["lessons"] = []
rc, out = run_ledger(d)
check("an EMPTY ledger FAILS", rc != 0)
check("the empty-ledger message names the self-referential defect",
      "same defect it exists to prevent" in out, out[:200])

d = copy.deepcopy(BASE); d["lessons"][0]["guards"] = []
rc, out = run_ledger(d)
check("a lesson with NO guard FAILS", rc != 0)
check("the message calls an unguarded lesson a promise", "promise" in out, out[:200])

d = copy.deepcopy(BASE); d["lessons"][0]["guards"][0]["contains"] = "a string nobody wrote"
rc, out = run_ledger(d)
check("a guard whose code was removed or renamed FAILS", rc != 0)
check("the message says the lesson is unenforced", "unenforced" in out, out[:200])

d = copy.deepcopy(BASE); d["lessons"][0]["guards"][0]["file"] = "tests/test_nonexistent.py"
rc, _ = run_ledger(d)
check("a guard pointing at a missing file FAILS", rc != 0)

d = copy.deepcopy(BASE); d["registeredSuites"] = [s for s in d["registeredSuites"]
                                                  if not s.endswith("test_alignment.py")]
rc, out = run_ledger(d)
check("an ORPHAN suite (exists but never runs) FAILS", rc != 0)
check("the message says it would never run", "never run" in out, out[:300])


# ── the builder must be able to satisfy the gate ────────────────────────
print("\n  form builder — a gate the builder cannot satisfy stays red forever")
import forms as formbuild
from gates import coverage as cov

pilot = fixtures.clean_bank(CODES * 2)
targets = formbuild.key_targets(pilot, "FORM-T")
letters = collections.Counter(targets.values()) if (collections := __import__("collections")) else None
check("key_targets spreads key positions evenly across the form",
      max(letters.values()) - min(letters.values()) <= 1, f"got {dict(letters)}")
rot = [formbuild.ordered_choices(it, "FORM-T", targets.get(it["id"]))[1]
       for it in pilot if it["itemType"] == "mcq"]
got = collections.Counter(rot)
check("the rendered key letter actually lands on its target",
      max(got.values()) - min(got.values()) <= 1, f"got {dict(got)}")
check("both surfaces get the SAME letter for an item",
      formbuild.ordered_choices(pilot[0], "FORM-T", targets.get(pilot[0]["id"]))[1]
      == formbuild.ordered_choices(pilot[0], "FORM-T", targets.get(pilot[0]["id"]))[1])

# ── de-bias is TWO-SIDED ────────────────────────────────────────────────
print("\n  choice-length-cue — balancing to zero is also a cue")
def cue(bank, ratio):
    """Make the key the longest option in `ratio` of the items."""
    n = int(len(bank) * ratio)
    for i, it in enumerate(bank):
        for c in it["choices"]:
            long = (c["id"] == it["correctAnswer"]) if i < n else (c["id"] != it["correctAnswer"])
            c["text"] = "word " * (12 if long else 4)
    return bank

allkeys = cue(fixtures.clean_bank(CODES * 10), 1.0)
check("key longest in 100% of items FAILS",
      not content.gate_choice_length_cue(allkeys, B).passed)
nokeys = cue(fixtures.clean_bank(CODES * 10), 0.0)
r = content.gate_choice_length_cue(nokeys, B)
check("key longest in 0% of items ALSO FAILS (the reverse cue)", not r.passed)
check("the finding says the reverse is equally learnable",
      any("never right" in str(f) for f in r.findings),
      f"got {[str(f)[:90] for f in r.findings[:1]]}")

# ── a gate must measure the artifact at the level it exists ─────────────
print("\n  form-key-position — the bank gate measured a distribution no student sees")
rendered = [{"id": f"R-{n}", "_formKeyLetter": "ABCD"[n % 4]} for n in range(12)]
check("an evenly rendered form PASSES", cov.gate_form_key_position(rendered, B).passed)
skewed = [{"id": f"S-{n}", "_formKeyLetter": ("D" if n % 3 else "A")} for n in range(12)]
check("a skewed rendered form FAILS", not cov.gate_form_key_position(skewed, B).passed)
check("EMPTY scan FAILS", not cov.gate_form_key_position([], B).passed)
check("a form with no rendered key letters is N/A, not a pass",
      bool(cov.gate_form_key_position([{"id": "X"}], B).inapplicable))

# ── N/A must not become a loophole ──────────────────────────────────────
print("\n  N/A semantics — the narrow exception to 'judged nothing is not a pass'")
na = Result("g", True, 5, [], judged=0, inapplicable="nothing of this kind is present")
vac = Result("h", True, 5, [], judged=0)
check("N/A reports as N/A, never PASS", na.status == "N/A")
check("N/A does not count as a pass", not na.counts_as_pass)
check("a judged-0 gate with NO reason still reports NOT MEASURED", vac.status == "NOT MEASURED")
check("all-gates-measured ignores N/A", cov.unmeasured_gates([na]).passed)
check("all-gates-measured still fails unexplained vacuity",
      not cov.unmeasured_gates([vac]).passed)
check("the N/A reason is shown in the report", "nothing of this kind" in na.report())
# The loophole: a gate must not claim inapplicable while its population exists.
withcite = [dict(fixtures.item(id="C-1"),
                 explanation="Hughes, first published in The Crisis, June 1921.")]
check("citation-integrity does NOT claim N/A when a citation is present",
      not content.gate_citation_integrity(withcite, B).inapplicable)
check("it DOES claim N/A when no item carries a citation",
      bool(content.gate_citation_integrity(
          [fixtures.item(id="N-1", explanation="Because the Act transferred land cheaply.")],
          B).inapplicable))

# ── every gate that exists is running ───────────────────────────────────
print("\n  check-gates-wired — a rewrite deleted two gates and only luck surfaced it")
import subprocess as _sp
r = _sp.run([sys.executable, os.path.join(BANK, "tools", "check_gates_wired.py")],
            capture_output=True, text=True)
check("the real gate wiring PASSES", r.returncode == 0, r.stdout[-300:])
check("it counts every gate in the package",
      "gates defined: " in r.stdout and "in a runner list" in r.stdout)

import importlib, run_gates as _rg
_orig = list(_rg.GATES)
try:
    _rg.GATES = [g for g in _orig if g.__name__ != "gate_truncation"]
    import inspect as _i
    # A gate dropped from the list is caught as "wired nowhere".
    from gates import record as _rec
    defined = {n for n, f in vars(_rec).items() if n.startswith("gate_") and _i.isfunction(f)}
    check("dropping a gate from the runner list leaves it undeclared and unwired",
          "gate_truncation" in defined
          and "gate_truncation" not in {g.__name__ for g in _rg.GATES})
finally:
    _rg.GATES = _orig

# The tiered blueprint must stay EXACT within its tier.
print("\n  form-blueprint tiers — tiering is not a loosening")
from gates import coverage as cov3
import json as _json
_bp = _json.load(open(os.path.join(BANK, "blueprints",
                                   "us-history-geography.blueprint.json")))["form"]
sel_tier = next(t for t in _bp["tiers"] if t["id"] == "selected-response")
good = []
for n, slot in enumerate(sel_tier["slots"]):
    it = fixtures.item(id=f"T-{n}", standardCodes=["US.05"],
                       itemType=slot["types"][0], dokLevel=slot["dok"])
    good.append(it)
r = cov3.gate_form_blueprint(good, B, standards=["US.05"],
                             tiers={"US.05": "selected-response"})
check("a form matching its declared tier PASSES", r.passed,
      "; ".join(str(f) for f in r.findings[:2]))
check("one item OVER the tier FAILS",
      not cov3.gate_form_blueprint(good + [fixtures.item(id="X", standardCodes=["US.05"])],
                                   B, standards=["US.05"],
                                   tiers={"US.05": "selected-response"}).passed)
check("one item UNDER the tier FAILS",
      not cov3.gate_form_blueprint(good[:-1], B, standards=["US.05"],
                                   tiers={"US.05": "selected-response"}).passed)
wrong = [dict(i) for i in good]; wrong[0]["dokLevel"] = 3
check("right count but a wrong DOK FAILS",
      not cov3.gate_form_blueprint(wrong, B, standards=["US.05"],
                                   tiers={"US.05": "selected-response"}).passed)
check("a form declaring NO tier FAILS — it cannot be checked",
      not cov3.gate_form_blueprint(good, B, standards=["US.05"], tiers={}).passed)
check("a form claiming a tier it does not fill FAILS",
      not cov3.gate_form_blueprint(good, B, standards=["US.05"],
                                   tiers={"US.05": "full"}).passed)

# ── committed reports must still be producible ──────────────────────────
print("\n  check-reports-fresh — a stale CSV shipped because output was suppressed")
import subprocess as _sp2
r = _sp2.run([sys.executable, os.path.join(BANK, "tools", "check_reports_fresh.py")],
             capture_output=True, text=True)
check("every committed report can be regenerated", r.returncode == 0, r.stdout[-300:])

import check_reports_fresh as _crf
check("the readiness CSV is one of the checked reports",
      "reports/form-readiness.csv" in _crf.REPORTS)
check("it distinguishes a crashed generator from a failing gate",
      "not about the generator" in open(
          os.path.join(BANK, "tools", "check_reports_fresh.py"), encoding="utf-8").read())

# The readiness tool must speak the tiered blueprint.
import form_readiness as _fr, json as _j
_form = _j.load(open(os.path.join(BANK, "blueprints",
                                  "us-history-geography.blueprint.json")))["form"]
_sel = next(t for t in _form["tiers"] if t["id"] == "selected-response")
_pool = [fixtures.item(id=f"RD-{n}", standardCodes=["US.05"],
                       itemType=sl["types"][0], dokLevel=sl["dok"])
         for n, sl in enumerate(_sel["slots"])]
_tier, _got = _fr.reachable_tier(_pool, _form)
check("readiness reports the tier a pool can actually reach",
      _tier is not None and _tier["id"] == "selected-response",
      f"got {_tier['id'] if _tier else None}")
check("readiness returns no tier for a pool that fills none",
      _fr.reachable_tier(_pool[:2], _form)[0] is None)
check("readiness and the builder agree on the ladder",
      [t["id"] for t in _form["tiers"]]
      == ["full", "extended", "extended-dok3", "selected-response"])

# ── a gate must be SATISFIABLE ──────────────────────────────────────────
print("\n  choice-length-cue — a gate that cannot be satisfied is worse than no gate")
def mcq_set(n, key_longest):
    out = []
    for i in range(n):
        it = fixtures.item(id=f"CL-{i}", standardCodes=["US.05"],
                           stem="Why did the Dawes Act divide reservation land?")
        fixtures._sync_key(it, "ABCD"[i % 4])
        long_is_key = i < key_longest
        for c in it["choices"]:
            hit = (c["id"] == it["correctAnswer"]) if long_is_key else (c["id"] != it["correctAnswer"])
            c["text"] = "word " * (12 if hit else 4)
        out.append(it)
    return out

r = content.gate_choice_length_cue(mcq_set(2, 0), B)
check("a 2-item set is N/A — the tolerance band is unreachable at that size",
      bool(r.inapplicable), f"status={r.status!r}")
check("the reason says the proportion cannot land in the band",
      "cannot land inside the tolerance band" in r.inapplicable, r.inapplicable)
check("N/A here is not counted as a pass", not r.counts_as_pass)
r = content.gate_choice_length_cue(mcq_set(8, 2), B)
check("an 8-item set at 25% PASSES", r.passed, r.note)
check("an 8-item set at 100% FAILS",
      not content.gate_choice_length_cue(mcq_set(8, 8), B).passed)
check("an 8-item set at 0% FAILS (the reverse cue still holds)",
      not content.gate_choice_length_cue(mcq_set(8, 0), B).passed)

# ── the admission loop refuses before it admits ─────────────────────────
print("\n  submit_items — generation is gated BEFORE admission, not reviewed after")
import submit_items as _si
names = [g.__name__ for g in _si.ADMISSION_GATES]
check("the admission gates include alignment, distractors and the cue",
      {"gate_standard_relevance", "gate_distractor_coverage",
       "gate_choice_length_cue"} <= set(names), f"got {names}")
check("review-provenance is NOT an admission gate (a draft has none yet)",
      "gate_review_provenance" not in names)
check("it refuses an empty draft",
      "refusing to report a successful submission of nothing" in
      open(os.path.join(BANK, "tools", "submit_items.py"), encoding="utf-8").read())
check("it checks a draft stem against the whole bank for duplicates",
      hasattr(_si, "dedupe_against_bank"))

print("\n" + "=" * 74)
print(f"{'ALL PASS' if not FAILED else str(len(FAILED)) + ' FAILED'}")
for f in FAILED:
    print("  FAILED:", f)
print("=" * 74)
sys.exit(1 if FAILED else 0)
