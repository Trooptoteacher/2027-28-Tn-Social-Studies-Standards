#!/usr/bin/env python3
"""Prove each gate before trusting it.

For every gate, three runs:
  CLEAN   fixture -> must PASS
  DEFECT  fixture carrying exactly that gate's defect -> must FAIL
  EMPTY   set -> must FAIL

A test that has never failed is worth nothing, so each DEFECT case asserts the
gate goes red AND that its finding names the item we broke. The defect fixture
differs from the clean one by exactly its defect — same 17 fields, same
bilingual twins, same distractor apparatus.
"""
from __future__ import annotations

import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(BANK, "tools"))
sys.path.insert(0, HERE)

import binding as binding_mod
import fixtures
from gates import record, coverage

B = binding_mod.load(os.path.join(HERE, "fixtures", "testbinding", "binding.json"))
CODES = ["US.04", "US.05"]

PASSED, FAILED = [], []


def check(label, cond, detail=""):
    (PASSED if cond else FAILED).append(label)
    mark = "ok  " if cond else "FAIL"
    print(f"    [{mark}] {label}" + (f" — {detail}" if detail and not cond else ""))


def prove(gate, defect_bank, broken_id, clean_bank=None):
    """clean passes · defect fails and names the broken item · empty fails."""
    name = gate.__name__.replace("gate_", "")
    print(f"\n  {name}")
    clean = clean_bank if clean_bank is not None else fixtures.clean_bank(CODES)

    r = gate(clean, B)
    check(f"{name}: clean fixture PASSES", r.passed,
          "; ".join(str(f) for f in r.findings[:3]))

    r = gate(defect_bank, B)
    check(f"{name}: defect fixture FAILS", not r.passed)
    if broken_id:
        named = any(broken_id in str(f) for f in r.findings)
        check(f"{name}: finding names the broken record ({broken_id})", named,
              f"findings: {[str(f)[:60] for f in r.findings[:3]]}")

    r = gate([], B)
    check(f"{name}: EMPTY scan FAILS", not r.passed,
          "a gate green against nothing reads exactly like a clean pass")


def mutate(index=0, **over):
    """Clean bank with exactly one record altered."""
    bank = fixtures.clean_bank(CODES)
    bank[index].update(over)
    return bank, bank[index]["id"]


print("=" * 74)
print("GATE PROOFS")
print(B.declaration())
print("=" * 74)

# 1 ── record completeness
bank, bid = mutate(0)
del bank[0]["dokRationale"]
prove(record.gate_record_complete, bank, bid)

# 2 ── binding: foreign prefix, undefined code, superseded year
for label, over in (("foreign prefix", {"standardCodes": ["GC.01"]}),
                    ("undefined code", {"standardCodes": ["US.99"]}),
                    ("superseded year", {"standardsYear": "2026-27"})):
    bank, bid = mutate(0, **over)
    print(f"\n  -- binding defect: {label}")
    r = record.gate_binding(bank, B)
    check(f"binding: {label} FAILS", not r.passed)
    check(f"binding: finding names {bid}", any(bid in str(f) for f in r.findings))
bank, bid = mutate(0, standardCodes=["GC.01"])
prove(record.gate_binding, bank, bid)

# 3 ── key integrity: key names a choice id that does not exist
bank, bid = mutate(0, correctAnswer="E")
prove(record.gate_key_integrity, bank, bid)
#      duplicate choice ids
bank2 = fixtures.clean_bank(CODES)
bank2[0]["choices"][2]["id"] = "A"
r = record.gate_key_integrity(bank2, B)
check("key-integrity: duplicate choice id FAILS", not r.passed)

# 4 ── distractor coverage: two distractors naming the same misconception
bank = fixtures.clean_bank(CODES)
bank[0]["choices"][2]["misconception"] = bank[0]["choices"][0]["misconception"]
prove(record.gate_distractor_coverage, bank, bank[0]["id"])
#      and a distractor with no explanation at all
bank3 = fixtures.clean_bank(CODES)
victim = next(c for c in bank3[0]["choices"] if c["id"] != bank3[0]["correctAnswer"])
victim["explanation"] = ""
r = record.gate_distractor_coverage(bank3, B)
check(f"distractor-coverage: distractor {victim['id']!r} with no explanation FAILS", not r.passed)

# 5 ── truncation: a stem cut mid-sentence by a bulk edit
bank, bid = mutate(0, stem="How did the Homestead Act change settlement patterns in the")
prove(record.gate_truncation, bank, bid)
#      an em-dash completion stem is NOT truncation
bank4 = fixtures.clean_bank(CODES)
bank4[0]["stem"] = "The Homestead Act offered settlers —"
r = record.gate_truncation(bank4, B)
check("truncation: em-dash completion stem is NOT flagged", r.passed,
      "; ".join(str(f) for f in r.findings[:2]))

# 6 ── blueprint: the BANK is measured on depth + proportion, the FORM exactly
bank = fixtures.clean_bank(CODES)[:-1]                      # one standard short of minimum
r = coverage.gate_blueprint(bank, B)
check("bank: a standard BELOW minimum depth FAILS", not r.passed)

deep = fixtures.clean_bank(CODES) + fixtures.clean_bank(CODES)   # twice the depth
r = coverage.gate_blueprint(deep, B)
check("bank: EXTRA depth is not drift — it PASSES", r.passed,
      "; ".join(str(f) for f in r.findings[:2]))

skew = fixtures.clean_bank(CODES * 3)
for it in skew:
    it["dokLevel"] = 1                                       # a bank drifted to recall
r = coverage.gate_blueprint(skew, B)
check("bank: a bank drifted to all-recall FAILS on DOK proportion", not r.passed)
check("the finding quotes the share and the target",
      any("target" in str(f) for f in r.findings), f"got {[str(f)[:80] for f in r.findings[:2]]}")

prove(coverage.gate_blueprint, fixtures.clean_bank(CODES)[:-1], "US.05")

#      the FORM must match its DECLARED tier exactly, in either direction.
#      Tier-shape proofs live in tests/test_regressions.py; this pins that the
#      bank-level suite still exercises the form gate's contract.
import json as _json
# By POSITION, not by name. A named tier pinned this to "selected-response"
# and the suite died on StopIteration when the ladder became TCAP-style,
# instead of saying what had changed.
_tier = _json.load(open(B.blueprint_file))["form"]["tiers"][-1]
form = [fixtures.item(id=f"F-{n}", standardCodes=["US.04"],
                      itemType=sl["types"][0], dokLevel=sl["dok"])
        for n, sl in enumerate(_tier["slots"])]
TIERS = {"US.04": _tier["id"]}
check("form: a form matching its declared tier PASSES",
      coverage.gate_form_blueprint(form, B, standards=["US.04"], tiers=TIERS).passed,
      "; ".join(str(f) for f in
                coverage.gate_form_blueprint(form, B, standards=["US.04"],
                                             tiers=TIERS).findings[:2]))
over = form + [fixtures.item(id="EXTRA", standardCodes=["US.04"])]
check("form: one item OVER the tier FAILS",
      not coverage.gate_form_blueprint(over, B, standards=["US.04"], tiers=TIERS).passed)
check("form: one item UNDER the tier FAILS",
      not coverage.gate_form_blueprint(form[:-1], B, standards=["US.04"], tiers=TIERS).passed)
check("form: EMPTY scan FAILS", not coverage.gate_form_blueprint([], B).passed)

#      quarantined items do not count as coverage
bank6 = fixtures.clean_bank(CODES)
bank6[0]["status"] = "quarantined"
check("bank: a quarantined item is NOT counted as coverage",
      not coverage.gate_blueprint(bank6, B).passed)

#      the blueprint must be ACHIEVABLE — every standard reaches SOME tier.
#      The gate iterates the whole standards file, so the proof narrows the
#      binding's standards to the two the fixture bank covers.
class _Narrow:
    def __init__(self, b, codes):
        self._b, self._codes = b, set(codes)
    def __getattr__(self, k):
        return getattr(self._b, k)
    def standards(self):
        return {k: v for k, v in self._b.standards().items() if k in self._codes}

NB = _Narrow(B, CODES)
mixed = fixtures.clean_bank(CODES)
r = coverage.gate_blueprint_achievability(mixed, NB)
check("achievability: a bank where every standard reaches a tier PASSES", r.passed,
      "; ".join(str(f) for f in r.findings[:2]))
# Read the tier names from the BLUEPRINT. Listing them literally pinned this
# to a ladder that no longer exists, and a hard-coded name is the same rot the
# handoff-number check exists to catch.
_TIER_IDS = [t["id"] for t in _json.load(open(B.blueprint_file))["form"]["tiers"]]
check("the note reports which tier each standard reached",
      any(t in r.note for t in _TIER_IDS), f"{r.note!r} names none of {_TIER_IDS}")

thin = fixtures.clean_bank(CODES)[:3]      # US.04 can no longer fill any tier
r = coverage.gate_blueprint_achievability(thin, NB)
check("achievability: a standard that fills NO tier FAILS", not r.passed)
check("the finding names the lowest tier it could not reach",
      any("lowest tier" in str(f) for f in r.findings),
      f"got {[str(f)[:100] for f in r.findings[:1]]}")
check("achievability: EMPTY scan FAILS",
      not coverage.gate_blueprint_achievability([], NB).passed)

# 7 ── answer-position de-bias: a bank a student can beat without reading
bank = fixtures.clean_bank(CODES * 6)
for it in bank:
    if it["itemType"] == "mcq":
        it["correctAnswer"] = "C"
prove(coverage.gate_key_position, bank, "4-choice", clean_bank=fixtures.clean_bank(CODES * 6))

# 8 ── serveability: bilingual field absent, and a standard that does not exist
bank, bid = mutate(0, stemEs="")
prove(coverage.gate_serveability, bank, bid)
bank7 = fixtures.clean_bank(CODES)
bank7[0]["image"] = {"src": "images/nope.png", "alt": "x", "altEs": "x"}
r = coverage.gate_serveability(bank7, B)
check("serveability: unresolvable image FAILS", not r.passed)

# 9 ── reporting-category provenance
bank, bid = mutate(0, reportingCategory="Government and Civics",
                   reportingCategorySource="tdoe-blueprint")
prove(coverage.gate_reporting_category, bank, bid)

# 10 ── teacher-side isolation: key material on a student surface
bank = fixtures.clean_bank(CODES)
bank[0].update(bankTier="student", _surface="student-form")
prove(coverage.gate_teacher_side_isolation, bank, bank[0]["id"],
      clean_bank=[dict(i, bankTier="student", _surface="student-form",
                       correctAnswer=None, explanation="", explanationEs="",
                       dokRationale="",
                       choices=[dict(c, explanation=None) for c in i["choices"]])
                  for i in fixtures.clean_bank(CODES)])

print("\n" + "=" * 74)
print(f"{len(PASSED)} proof(s) passed, {len(FAILED)} failed")
if FAILED:
    for f in FAILED:
        print("  FAILED:", f)
print("=" * 74)
sys.exit(1 if FAILED else 0)
