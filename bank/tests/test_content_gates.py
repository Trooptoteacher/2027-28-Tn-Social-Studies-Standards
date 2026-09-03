#!/usr/bin/env python3
"""Prove the content gates — the ones that measure what the bank is ABOUT.

Fixtures are built on US.05, whose standard carries a real checklist
("...including the movement to reservations, assimilation, boarding schools,
and the Dawes Act"). A standard with no checklist cannot be judged, and the
proofs assert that exemption is reported rather than silently passed.
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
from gates import content

B = binding_mod.load(os.path.join(HERE, "fixtures", "testbinding", "binding.json"))
REAL_B = binding_mod.load()          # US.22/65/67 exist only in the full standards file
FAILED = []


def check(label, cond, detail=""):
    print(f"    [{'ok  ' if cond else 'FAIL'}] {label}" + (f"\n           {detail}" if detail and not cond else ""))
    if not cond:
        FAILED.append(label)


def on_std(stem, code="US.05", **over):
    it = fixtures.item(id=over.pop("id", "T-1"), standardCodes=[code], stem=stem, **over)
    return it


ON = "Why did the Dawes Act divide reservation land into individual allotments?"
OFF = "How did Andrew Carnegie's vertical integration reshape the steel industry?"

print("=" * 74)
print("CONTENT GATE PROOFS")
print("=" * 74)

# ── alignment claim ──────────────────────────────────────────────────────
print("\n  alignment-claim — content quality and alignment confidence are separate axes")
def A(it, st):
    it["alignmentStatus"] = st
    return it

clean = [A(on_std(ON, id=f"T-{n}"), "evidenced") for n in range(6)]
r = content.gate_standard_relevance(clean, B)
check("items whose evidence backs their claim PASS", r.passed,
      "; ".join(str(f) for f in r.findings[:2]))

off = copy.deepcopy(clean)
off[2]["stem"] = OFF
off[2]["choices"] = [dict(c, text="Steel industry consolidation.") for c in off[2]["choices"]]
off[2]["explanation"] = "Carnegie bought suppliers at every stage of production."
r = content.gate_standard_relevance(off, B)
check("an item CLAIMING 'evidenced' with no evidence FAILS", not r.passed)
check("the finding offers the three honest ways out",
      any("mark it" in str(f) and "unverified" in str(f) for f in r.findings),
      f"got {[str(f)[:110] for f in r.findings[:1]]}")

# The point of the whole redesign: an unverified item is KEPT, and honest.
honest = copy.deepcopy(off)
honest[2]["alignmentStatus"] = "unverified"
r = content.gate_standard_relevance(honest, B)
check("the same item marked 'unverified' PASSES — kept, usable, honestly labelled",
      r.passed, "; ".join(str(f) for f in r.findings[:2]))
check("the note says unverified items are kept and not counted as coverage",
      "kept and usable" in r.note, r.note)
check("its CONTENT is untouched by the label",
      honest[2]["stem"] == OFF and bool(honest[2]["choices"])
      and bool(honest[2]["explanation"]))

silent = copy.deepcopy(clean)
del silent[1]["alignmentStatus"]
r = content.gate_standard_relevance(silent, B)
check("an item with NO alignmentStatus FAILS (a silent claim)", not r.passed)

fake = copy.deepcopy(clean)
fake[0]["alignmentStatus"] = "rehomed"
r = content.gate_standard_relevance(fake, B)
check("'rehomed' without move evidence in provenance FAILS", not r.passed)
fake[0]["provenance"] = {"rehomed": {"from": ["US.04"], "to": "US.05"}}
check("'rehomed' WITH move evidence passes", content.gate_standard_relevance(fake, B).passed)

check("EMPTY scan FAILS", not content.gate_standard_relevance([], B).passed)

# US.04 names its subject in the stem, so it is judgeable (L21).
r = content.gate_standard_relevance(
    [A(on_std("How did the Homestead Act change western settlement?", code="US.04", id="H-1"),
       "evidenced")], B)
check("a standard naming its subject in the STEM is judged, and a matching item passes",
      r.passed and r.judged == 1, f"status={r.status!r} judged={r.judged}")

# A standard that names nothing cannot be judged at all.
no_sig = [A(on_std("Anything at all.", code="US.22", id=f"N-{n}"), "not-applicable")
          for n in range(4)]
r = content.gate_standard_relevance(no_sig, REAL_B)
check("a standard that names NOTHING is NOT MEASURED, not passed", not r.measured,
      f"status={r.status!r} judged={r.judged}")

# Coverage must not count what alignment has not established.
import itemio as _io
check("an unverified item is servable but NOT counted toward coverage",
      _io.servable(honest[2]) and not _io.aligned(honest[2]))
check("an evidenced item counts toward coverage", _io.aligned(clean[0]))

# ── choice-length cue ────────────────────────────────────────────────────
print("\n  choice-length-cue")
even = []
for n in range(40):
    it = on_std(ON, id=f"L-{n}")
    for i, c in enumerate(it["choices"]):
        c["text"] = "word " * (4 + i)          # D always longest
    fixtures._sync_key(it, "ABCD"[n % 4])       # key rotates -> longest 25% of the time
    even.append(it)
r = content.gate_choice_length_cue(even, B)
check("a bank where the key is longest at chance PASSES", r.passed, r.note)

cued = copy.deepcopy(even)
for it in cued:
    for i, c in enumerate(it["choices"]):
        c["text"] = "word " * (12 if c["id"] == it["correctAnswer"] else 4)
r = content.gate_choice_length_cue(cued, B)
check("a bank where the key is ALWAYS longest FAILS", not r.passed)
check("the finding says a student can beat it without reading",
      any("without reading" in str(f) for f in r.findings))
check("EMPTY scan FAILS", not content.gate_choice_length_cue([], B).passed)
check("a bank with no selected-response is NOT MEASURED",
      not content.gate_choice_length_cue(
          [dict(i, itemType="constructed-response", choices=[]) for i in even], B).measured)

# ── duplicate stems ──────────────────────────────────────────────────────
print("\n  duplicate-stems")
uniq = [on_std(f"{ON} Variation {n}.", id=f"D-{n}") for n in range(5)]
check("all-distinct stems PASS", content.gate_duplicate_stems(uniq, B).passed)
dup = copy.deepcopy(uniq)
dup[3]["stem"] = dup[0]["stem"]
r = content.gate_duplicate_stems(dup, B)
check("two ids sharing one stem FAILS", not r.passed)
check("the finding names both ids",
      any("D-0" in str(f) and "D-3" in str(f) for f in r.findings),
      f"got {[str(f)[:90] for f in r.findings[:1]]}")
check("punctuation/case differences still count as duplicates",
      not content.gate_duplicate_stems(
          [on_std(ON, id="X1"), on_std(ON.upper().replace("?", " ?"), id="X2")], B).passed)
check("EMPTY scan FAILS", not content.gate_duplicate_stems([], B).passed)

print("\n" + "=" * 74)
print(f"{'ALL PASS' if not FAILED else str(len(FAILED)) + ' FAILED'}")
for f in FAILED:
    print("  FAILED:", f)
print("=" * 74)
sys.exit(1 if FAILED else 0)
