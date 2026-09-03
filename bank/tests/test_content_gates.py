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

# ── standard-relevance ───────────────────────────────────────────────────
print("\n  standard-relevance")
clean = [on_std(ON, id=f"T-{n}") for n in range(6)]
r = content.gate_standard_relevance(clean, B)
check("an item naming its standard's element PASSES", r.passed,
      "; ".join(str(f) for f in r.findings[:2]))
check("it actually judged the items (not exempted)", r.judged == 6, f"judged={r.judged}")

bad = copy.deepcopy(clean)
bad[2]["stem"] = OFF
bad[2]["choices"] = [dict(c, text="Steel industry consolidation strategy.") for c in bad[2]["choices"]]
bad[2]["explanation"] = "Carnegie bought suppliers at every stage of production."
r = content.gate_standard_relevance(bad, B)
check("an off-standard item FAILS", not r.passed)
check("the finding names the item and what the standard asks about",
      any("T-2" in str(f) and "Dawes Act" in str(f) for f in r.findings),
      f"got {[str(f)[:100] for f in r.findings[:2]]}")

# US.04 carries NO "including" checklist, but it names the Homestead Act in its
# stem — so it IS judgeable. Matching the checklist alone was L21: it flagged
# correctly-filed items whose standard names its subject before the "including".
r = content.gate_standard_relevance(
    [on_std("How did the Homestead Act change western settlement?", code="US.04", id="H-1")], B)
check("a standard naming its subject in the STEM is judged, and a matching item passes",
      r.passed and r.judged == 1, f"status={r.status!r} judged={r.judged}")

# A standard that names nothing at all genuinely cannot be judged, and that must
# be reported rather than silently passed. US.22, US.65 and US.67 are the three.
no_sig = [on_std("Anything at all about nothing in particular.", code="US.22", id=f"N-{n}")
          for n in range(4)]
r = content.gate_standard_relevance(no_sig, REAL_B)
check("a standard that names NOTHING is NOT MEASURED, not passed",
      not r.measured, f"status={r.status!r} judged={r.judged}")
check("EMPTY scan FAILS", not content.gate_standard_relevance([], B).passed)

# The allowlist is a reviewed decision, and it must actually work.
import json
AL = os.path.join(BANK, "reviewed", "relevance-allowlist.json")
orig = open(AL, encoding="utf-8").read()
try:
    d = json.loads(orig)
    d["items"] = {"T-2": "reviewed 2026-09-03: excerpt is on-standard; names no listed term"}
    json.dump(d, open(AL, "w", encoding="utf-8"), indent=2)
    r = content.gate_standard_relevance(bad, B)
    check("an allowlisted item stops failing", r.passed,
          "; ".join(str(f) for f in r.findings[:2]))
    check("the allowlist count is reported", "1 item(s) allowlisted" in r.note, r.note)
finally:
    open(AL, "w", encoding="utf-8").write(orig)
check("the allowlist file was restored", json.loads(open(AL, encoding="utf-8").read())["items"] == {})

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
