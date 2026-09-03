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

# 6 ── blueprint conformance: drift in both directions
bank = fixtures.clean_bank(CODES)[:-1]                      # one short
r = coverage.gate_blueprint(bank, B)
check("blueprint: UNDER count FAILS", not r.passed)
bank = fixtures.clean_bank(CODES) + [fixtures.item(id="EXTRA", standardCodes=["US.04"])]
prove(coverage.gate_blueprint, bank, "US.04")
#      right count, wrong DOK spread
bank5 = fixtures.clean_bank(CODES)
for it in bank5:
    it["dokLevel"] = 1
r = coverage.gate_blueprint(bank5, B)
check("blueprint: right count / wrong DOK spread FAILS", not r.passed)
#      quarantined items do not count as coverage
bank6 = fixtures.clean_bank(CODES)
bank6[0]["status"] = "quarantined"
r = coverage.gate_blueprint(bank6, B)
check("blueprint: quarantined item is NOT counted as coverage", not r.passed)

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
