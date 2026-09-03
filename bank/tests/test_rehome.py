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

import inspect

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
_, flagged, _ = content.relevance_scan([brown], REAL)
check("a correctly-filed Brown v. Board item is NOT flagged", not flagged,
      f"flagged {[f[0]['id'] for f in flagged]}")

# ── one definition, shared ──────────────────────────────────────────────
print("\n  the gate and the triage tool share one definition")
import itemio
items = itemio.load_dir(REAL.output_dir)
judged, flagged, _ = content.relevance_scan(items, REAL)
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
      content.relevance_scan([], REAL) == (0, [], []))

# ── identifying signals: strong enough to say what an item is ABOUT ─────
print("\n  identifying_signals — the relevance gate needs the same strictness as re-home")
us17 = STDS["US.17"]["text"]
check("'Support' (from 'Support for conservation') is NOT an identifying signal",
      "Support" not in alignment.identifying_signals(us17),
      f"got {alignment.identifying_signals(us17)}")
check("the standard's real names ARE identifying signals",
      all(any(n in s for s in alignment.identifying_signals(us17))
          for n in ("Square Deal", "Meat Inspection Act")),
      f"got {alignment.identifying_signals(us17)}")
check("a 19th-Amendment text is NOT relevant to Theodore Roosevelt's standard",
      alignment.relevant_to("The Nineteenth Amendment guaranteed women the vote in 1920.",
                            us17) == [],
      f"got {alignment.relevant_to('The Nineteenth Amendment...', us17)}")
check("a Square Deal text IS relevant to it",
      bool(alignment.relevant_to("Roosevelt's Square Deal promised fairness.", us17)))
# Standards write "19th Amendment"; items commonly spell "Nineteenth Amendment".
# Literal matching read those items as naming nothing.
us20 = STDS["US.20"]["text"]
check("a WORD-spelled ordinal matches a numeral-written standard",
      bool(alignment.relevant_to("What did the Nineteenth Amendment guarantee?", us20)))
check("and the numeral form still matches",
      bool(alignment.relevant_to("What did the 19th Amendment guarantee?", us20)))
check("normalisation does not invent a match",
      alignment.relevant_to("What did the Fourth Amendment protect?", us20) == [],
      f"got {alignment.relevant_to('What did the Fourth Amendment protect?', us20)}")

# ── an item aligned to ONE of its codes is not aligned to all of them ───
print("\n  per-standard placement — a form heading is a claim")
from gates import coverage as cov2
multi = dict(fixtures.item(id="M-1"),
             standardCodes=["US.17", "US.20"],
             stem="What did the Nineteenth Amendment guarantee?",
             choices=[{"id": "A", "text": "The vote regardless of sex", "textEs": None,
                       "explanation": None, "misconception": None}])
r = cov2.gate_form_standard_relevance([multi], REAL, standards=["US.17"])
check("an item printed under a standard it does not name FAILS", not r.passed)
check("the finding says the heading claims more than the item supports",
      any("claims more than the item supports" in str(f) for f in r.findings))
r = cov2.gate_form_standard_relevance([multi], REAL, standards=["US.20"])
check("the same item under the standard it IS about passes", r.passed,
      "; ".join(str(f) for f in r.findings[:1]))
check("EMPTY scan FAILS", not cov2.gate_form_standard_relevance([], REAL).passed)

# ── authored teacher text must not prove alignment ──────────────────────
print("\n  relevance reads STUDENT-VISIBLE text only")
hoover = fixtures.item(id="H-9", standardCodes=["US.46"],
                       stem="What did the Reconstruction Finance Corporation do under Hoover?",
                       explanation="This is the standard contrast with the New Deal's relief.")
hoover["choices"] = [{"id": "A", "text": "It lent federal money to banks and railroads",
                      "textEs": None, "explanation": None, "misconception": None}]
hoover["correctAnswer"] = "A"
hay = content._haystack(hoover)
check("the key explanation is excluded from the relevance haystack",
      "New Deal" not in hay, f"haystack was {hay[:120]!r}")
check("so a Hoover item does not claim the New Deal standard on authored prose",
      alignment.relevant_to(hay, STDS["US.46"]["text"]) == [],
      f"got {alignment.relevant_to(hay, STDS['US.46']['text'])}")

# ── one placement rule, shared ──────────────────────────────────────────
print("\n  readiness and the builder share one placement rule")
import form_readiness, forms as fb, inspect
for mod in (form_readiness, fb):
    src = inspect.getsource(mod)
    check(f"{mod.__name__} places via alignment.relevant_to",
          "alignment.relevant_to" in src)
    check(f"{mod.__name__} excludes the explanation from its haystack",
          'it.get("explanation")' not in src.split("relevant_to")[0][-400:])

# ── one definition of what an item is ABOUT ─────────────────────────────
print("\n  subject_text — stem plus the KEY, never the distractors")
it = fixtures.item(id="SJ-1", stem="What did the Truman Doctrine commit the United States to?")
it["choices"] = [
    {"id": "A", "text": "Supporting free peoples resisting subjugation", "textEs": None,
     "explanation": None, "misconception": None},
    {"id": "B", "text": "An alliance with the Soviet Union", "textEs": None,
     "explanation": "wrong", "misconception": "x"}]
it["correctAnswer"] = "A"
it["explanation"] = "This is the Marshall Plan's political companion."
txt = alignment.subject_text(it)
check("the stem is included", "Truman Doctrine" in txt)
check("the KEY is included", "free peoples" in txt)
check("a DISTRACTOR is excluded — it filed a Carter item under the Cold War",
      "Soviet Union" not in txt, f"got {txt!r}")
check("the authored explanation is excluded (L38)", "Marshall Plan" not in txt)

check("the relevance gate uses the ONE matcher, not a copy",
      "alignment.relevant_to" in inspect.getsource(content.relevance_scan),
      "relevance_scan re-implemented the match and its copy forgot to lowercase")

items_all = itemio.load_dir(REAL.output_dir)
judged, flagged, _ = content.relevance_scan(items_all, REAL)
manual = sum(1 for i in items_all if itemio.servable(i)
             and any(alignment.judgeable_signals(STDS[c]["text"]) for c in i["standardCodes"]
                     if c in STDS)
             and any(alignment.relevant_to(alignment.subject_text(i), STDS[c]["text"])
                     for c in i["standardCodes"] if c in STDS))
check("the gate agrees with a manual computation of the same rule",
      judged - len(flagged) == manual, f"gate={judged-len(flagged)} manual={manual}")

# ── relevance is a property of the ITEM, not the printed page ───────────
print("\n  form relevance measures SOURCE items, not the stripped student surface")
src = inspect.getsource(__import__("run_gates"))
check("the form runner passes source items to form-standard-relevance",
      "gate_form_standard_relevance(sel" in src,
      "the student surface strips the key, so an item naming its standard only in "
      "the key reads as naming nothing")

# ── weakly identifiable standards are disclosed ────────────────────────
print("\n  identifiability — a standard identifiable by one coarse signal")
# US.25 used to be the example here: its ONLY proper-noun signal is "World War
# I", so an essay on 1890-1914 imperialism matched it. Topic signals gave it
# real content terms, which is the improvement working — so the example moved
# to a standard that is STILL weak. The principle under test is unchanged:
# identifiability counts what the matcher can actually use, and a standard
# below two signals is disclosed rather than papered over.
check("US.65 is weakly identifiable (one signal: 'baby boomer generation')",
      alignment.identifiability(STDS["US.65"]["text"]) < 2,
      f"got {alignment.judgeable_signals(STDS['US.65']['text'])}")
check("identifiability counts TOPIC signals too — it measured only proper nouns, "
      "so nine standards scored zero and nothing said so",
      alignment.identifiability(STDS["US.13"]["text"]) > 0,
      f"got {alignment.judgeable_signals(STDS['US.13']['text'])}")
check("a richly named standard is not",
      alignment.identifiability(STDS["US.60"]["text"]) >= 2)
import form_readiness as _fr2
check("readiness reports identifiability per standard",
      "weaklyIdentifiable" in inspect.getsource(_fr2))

print("\n" + "=" * 74)
print(f"{'ALL PASS' if not FAILED else str(len(FAILED)) + ' FAILED'}")
for f in FAILED:
    print("  FAILED:", f)
print("=" * 74)
sys.exit(1 if FAILED else 0)
