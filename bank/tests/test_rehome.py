#!/usr/bin/env python3
"""Pins for the re-home triage.

Every rule here was learned by sampling proposals and finding them wrong.
Precision went 50% -> 60% -> ~90% across three passes, and each pass removed
one class of bad evidence. Loosen any of these and the tool starts producing
confident mislabels, which are worse than the flags they replace.
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
import rehome
from gates import content

B = binding_mod.load(os.path.join(HERE, "fixtures", "testbinding", "binding.json"))
REAL = binding_mod.load()
STDS = REAL.standards()
FAILED = []


def check(label, cond, detail=""):
    print(f"    [{'ok  ' if cond else 'FAIL'}] {label}" + (f"\n           {detail}" if detail and not cond else ""))
    if not cond:
        FAILED.append(label)


print("=" * 74)
print("RE-HOME TRIAGE PINS")
print("=" * 74)

# ── what may count as evidence ──────────────────────────────────────────
print("\n  evidence rules — an assignment matcher must be stricter than a detector")
check("a bare generic word is never evidence ('industry')",
      rehome.strong_signals("its effects on American industry") == [],
      f"got {rehome.strong_signals('its effects on American industry')}")
check("a single-word country name is not evidence ('Germany' sent every WWI/WWII item to Yalta)",
      rehome.strong_signals("separation of Germany") == [],
      f"got {rehome.strong_signals('separation of Germany')}")
check("bullet-initial capitalisation is not a name ('Economic recession')",
      rehome.strong_signals("Economic recession") == [],
      f"got {rehome.strong_signals('Economic recession')}")
check("a multi-word name IS evidence ('Dawes Act')",
      rehome.strong_signals("Dawes Act") == ["Dawes Act"],
      f"got {rehome.strong_signals('Dawes Act')}")
check("a person's full name IS evidence",
      rehome.strong_signals("Ida B. Wells-Barnett") == ["Ida B. Wells-Barnett"],
      f"got {rehome.strong_signals('Ida B. Wells-Barnett')}")

# ── the stem decides ────────────────────────────────────────────────────
print("\n  the STEM decides, the explanation only corroborates")
lists = rehome.checklists(STDS)
eisenhower = fixtures.item(
    id="E-1", standardCodes=["US.66"],
    stem="Eisenhower's concept of 'Modern Republicanism' was characterized by —",
    explanation="He accepted the New Deal programs rather than dismantling them.")
prop, why = rehome.propose(eisenhower, lists, ["US.66"])
check("a name appearing only in the EXPLANATION cannot move an item",
      prop is None, f"proposed {prop}")

tonkin = fixtures.item(
    id="T-1", standardCodes=["US.74"],
    stem="Read the excerpt from the Gulf of Tonkin Resolution passed in August 1964.",
    explanation="Congress authorised escalation in Vietnam.")
prop, why = rehome.propose(tonkin, lists, ["US.74"])
check("a name in the STEM does move it", prop is not None and prop["to"] == "US.80",
      f"proposed {prop} ({why})")

# ── the standard's stem names count for relevance ───────────────────────
print("\n  a standard is identified by its whole sentence, not only its checklist")
ne = alignment.named_entities(STDS["US.74"]["text"])
check("US.74's subject is extracted ('Brown v. Board of Education')",
      any("Brown v. Board" in n for n in ne), f"got {ne}")
check("the standard's opening VERB is not treated as a name",
      not any(n.lower().startswith(("examine", "describe", "analyze")) for n in ne),
      f"got {ne}")
check("bullets do not merge into a phantom entity",
      all("Controversy" not in n or n.startswith("Controversy")
          for n in alignment.named_entities(STDS["US.84"]["text"])),
      f"got {alignment.named_entities(STDS['US.84']['text'])}")
brown = fixtures.item(id="B-1", standardCodes=["US.74"],
                      stem="What was the long-term significance of Brown v. Board of Education?")
_, flagged = content.relevance_scan([brown], REAL)
check("a correctly-filed Brown v. Board item is NOT flagged", not flagged,
      f"flagged {[f[0]['id'] for f in flagged]}")

# ── one definition, shared ──────────────────────────────────────────────
print("\n  the gate and the triage tool share one definition")
import itemio
items = itemio.load_dir(REAL.output_dir)
judged, flagged = content.relevance_scan(items, REAL)
r = content.gate_standard_relevance(items, REAL)
flagged_ids = {i["id"] for i, _, _ in flagged}
# The gate no longer fails on every flagged item — an item honestly marked
# `unverified` is kept and passes. What must hold is that both read ONE
# definition of relevance: every gate finding is an item the scan flagged.
gate_ids = {str(f).split(" ")[0].rstrip(":") for f in r.findings}
check("every gate finding is an item relevance_scan flagged (one shared definition)",
      gate_ids <= flagged_ids, f"gate-only ids: {sorted(gate_ids - flagged_ids)[:5]}")
check("a flagged item that CLAIMS evidence does produce a gate finding",
      bool(content.gate_standard_relevance(
          [dict(next(i for i, _, _ in flagged), alignmentStatus="evidenced")],
          REAL).findings))
check("the same item marked unverified produces none — kept, not a defect",
      not content.gate_standard_relevance(
          [dict(next(i for i, _, _ in flagged), alignmentStatus="unverified")],
          REAL).findings)
check("relevance_scan on an empty bank flags nothing and judges nothing",
      content.relevance_scan([], REAL) == (0, []))

print("\n" + "=" * 74)
print(f"{'ALL PASS' if not FAILED else str(len(FAILED)) + ' FAILED'}")
for f in FAILED:
    print("  FAILED:", f)
print("=" * 74)
sys.exit(1 if FAILED else 0)
