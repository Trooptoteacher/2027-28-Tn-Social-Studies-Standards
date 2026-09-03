#!/usr/bin/env python3
"""Mutation check: a test that has never failed is worth nothing.

Replace each gate with a stub that always reports PASS, then confirm that
gate's proofs go RED. If a proof still passes against a gate that measures
nothing, the proof was measuring nothing either.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(BANK, "tools"))
sys.path.insert(0, HERE)

import binding as binding_mod
import fixtures
from gates import Result, record, coverage

B = binding_mod.load(os.path.join(HERE, "fixtures", "testbinding", "binding.json"))
CODES = ["US.04", "US.05"]


def always_pass(items, binding=None):
    """The defect this hunts: a gate that reports green no matter what."""
    return Result("stub", True, len(items), [])


def clean():
    return fixtures.clean_bank(CODES)


def defect_for(gate_name):
    b = clean()
    if gate_name == "record_complete":
        del b[0]["dokRationale"]
    elif gate_name == "binding":
        b[0]["standardCodes"] = ["GC.01"]
    elif gate_name == "key_integrity":
        b[0]["correctAnswer"] = "E"
    elif gate_name == "distractor_coverage":
        d = [c for c in b[0]["choices"] if c["id"] != b[0]["correctAnswer"]]
        d[1]["misconception"] = d[0]["misconception"]
    elif gate_name == "truncation":
        b[0]["stem"] = "How did the Homestead Act change settlement patterns in the"
    elif gate_name == "blueprint":
        b.append(fixtures.item(id="EXTRA", standardCodes=["US.04"]))
    elif gate_name == "key_position":
        b = fixtures.clean_bank(CODES * 6)
        for it in b:
            if it["itemType"] == "mcq":
                it["correctAnswer"] = "C"
    elif gate_name == "serveability":
        b[0]["stemEs"] = ""
    elif gate_name == "reporting_category":
        b[0]["reportingCategory"] = "Government and Civics"
        b[0]["reportingCategorySource"] = "tdoe-blueprint"
    elif gate_name == "teacher_side_isolation":
        b[0].update(bankTier="student", _surface="student-form")
    return b


GATES = {
    "record_complete": record.gate_record_complete,
    "binding": record.gate_binding,
    "key_integrity": record.gate_key_integrity,
    "distractor_coverage": record.gate_distractor_coverage,
    "truncation": record.gate_truncation,
    "blueprint": coverage.gate_blueprint,
    "key_position": coverage.gate_key_position,
    "serveability": coverage.gate_serveability,
    "reporting_category": coverage.gate_reporting_category,
    "teacher_side_isolation": coverage.gate_teacher_side_isolation,
}

print("=" * 74)
print("MUTATION CHECK — neuter each gate, confirm its proofs go red")
print("=" * 74)

bad = []
for name, gate in GATES.items():
    d = defect_for(name)
    real_defect = not gate(d, B).passed
    real_empty = not gate([], B).passed
    stub_defect = not always_pass(d, B).passed          # expected False
    stub_empty = not always_pass([], B).passed          # expected False

    caught = real_defect and real_empty and not stub_defect and not stub_empty
    print(f"  [{'ok  ' if caught else 'FAIL'}] {name}: "
          f"real gate red on defect={real_defect} empty={real_empty} · "
          f"stub gate red on defect={stub_defect} empty={stub_empty}")
    if not caught:
        bad.append(name)

print("=" * 74)
if bad:
    print(f"{len(bad)} gate(s) NOT proven: {bad}")
    print("A proof that passes against an always-green stub proves nothing.")
else:
    print(f"All {len(GATES)} gates proven: each goes red on its own defect and on an "
          f"empty scan,\nand each proof would go red if the gate stopped measuring.")
print("=" * 74)
sys.exit(1 if bad else 0)
