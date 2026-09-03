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
from gates import Result, record, coverage

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


print("\n" + "=" * 74)
print(f"{'ALL PASS' if not FAILED else str(len(FAILED)) + ' FAILED'}")
for f in FAILED:
    print("  FAILED:", f)
print("=" * 74)
sys.exit(1 if FAILED else 0)
