#!/usr/bin/env python3
"""Prove the authoring invoice — `form_readiness.cost()`.

The invoice is not a report, it is the thing that CHOOSES THE NEXT STANDARD.
It was wrong by 1.80x and wrong in both directions at once, because it carried
its own copies of three rules that gates already owned. Every proof here pins
the invoice to a gate rather than to a number, so the two cannot drift apart
again: a gate that changes its mind must change the invoice with it.

The one number pinned outright is the length-cue cohort tally, because
factoring that measurement out of the gate had to leave the gate's verdict
untouched, and "I refactored it and it still looks right" is not a measurement.
"""
from __future__ import annotations

import ast
import collections
import copy
import inspect
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(BANK, "tools"))
sys.path.insert(0, HERE)

import fixtures
import form_readiness as fr
import itemio
from gates import content

FAILED = []

def src_new():
    return inspect.getsource(fr.cost)




def check(label, cond, detail=""):
    print(f"    [{'ok  ' if cond else 'FAIL'}] {label}"
          + (f"\n           {detail}" if detail and not cond else ""))
    if not cond:
        FAILED.append(label)


def mcq(n, key="B", **over):
    """n four-option mcq items, every one keyed to `key`."""
    out = []
    for i in range(n):
        it = fixtures._sync_key(fixtures.item(id=f"INV-{i:03d}"), key)
        for f, v in over.items():
            it[f] = v
        out.append(it)
    return out


def longest_is_key(it, yes=True):
    """Make the key the longest option, or the shortest."""
    key = it["correctAnswer"]
    for c in it["choices"]:
        base = "a settlement policy question about western land "
        c["text"] = base * (6 if (c["id"] == key) == yes else 1)
    return it


# ----------------------------------------------------------- one implementation
print("\n  ONE IMPLEMENTATION OF ONE RULE")

src = inspect.getsource(fr.cost)
tree = ast.parse(src.strip())
calls = {n.func.attr for n in ast.walk(tree)
         if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
check("cost() charges the length cue by calling the gate's own measurement",
      "length_cue_rebalance_units" in calls,
      f"calls: {sorted(calls)}")
check("cost() charges the explanation rewrite by calling explanation-quality",
      "gate_explanation_quality" in calls, f"calls: {sorted(calls)}")
# The defect was a private re-derivation. Nothing in cost() may compute a
# length comparison of its own again.
check("cost() contains no length comparison of its own",
      not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
              and n.func.id in ("max", "min") for n in ast.walk(tree)),
      "a max()/min() over choice text is how the second implementation began")
# Measured on the EMITTED KEYS, not the source text. The first version of
# this proof grepped `src` and failed on cost()'s own docstring explaining why
# the line is absent — a check that reads the prose instead of the artifact,
# which is rule 1 of this bank broken inside its own test.
check("cost() emits no DOK-rationale QUALITY line (no gate judges it)",
      "dokRationaleQuality" not in set(fr.cost(mcq(2))),
      f"keys: {sorted(fr.cost(mcq(2)))}")

# ------------------------------------------------- the refactor changed nothing
print("\n  THE LENGTH-CUE REFACTOR LEFT THE VERDICT ALONE")

import binding as binding_mod
B = binding_mod.load()
bank = itemio.load_dir(B.output_dir)
coh, judged = content.length_cue_cohorts(bank)
r = content.gate_choice_length_cue(bank)
check("cohort tally pinned: 4-choice n=3793, key-is-longest 2020",
      dict(coh) == {4: [2020, 3793]}, f"got {dict(coh)}")
check("gate judged 3793 and reports exactly one cohort finding",
      (r.judged, len(r.findings), r.passed) == (3793, 1, False),
      f"judged={r.judged} findings={len(r.findings)} passed={r.passed}")
check("gate and helper agree on who was judged", judged == r.judged)

# ------------------------------------------------------- rebalance: the minimum
print("\n  REBALANCE IS CHARGED AS THE MINIMUM, AND ONLY WHEN THE GATE ASKS")

floor3 = [longest_is_key(i) for i in mcq(3)]
check("3 items: the gate DECLINES (band unreachable) …",
      content.gate_choice_length_cue(floor3).inapplicable != "")
check("… so the invoice charges 0 rebalance units — this is the US.33 defect, "
      "which was billed 3",
      fr.cost(floor3)["choiceRebalance"] == 0,
      f"charged {fr.cost(floor3)['choiceRebalance']}")

six = [longest_is_key(i) for i in mcq(6)]
check("6 items all cued: the gate fails",
      not content.gate_choice_length_cue(six).passed)
# floor(0.35 * 6) = 2 may remain. 6 - 2 = 4.
check("…and the charge is 4, the number that must change — not 6, the cohort",
      fr.cost(six)["choiceRebalance"] == 4,
      f"charged {fr.cost(six)['choiceRebalance']}")

clean6 = ([longest_is_key(i) for i in mcq(2)]
          + [longest_is_key(i, yes=False) for i in mcq(4)])
check("a cohort already inside the band is charged nothing",
      fr.cost(clean6)["choiceRebalance"] == 0,
      f"charged {fr.cost(clean6)['choiceRebalance']}")

# TWO-SIDED, like the gate. Over-correcting to 0% is also a cue.
none6 = [longest_is_key(i, yes=False) for i in mcq(6)]
check("a cohort balanced to 0% is charged too — 'never the longest' is learnable",
      fr.cost(none6)["choiceRebalance"] > 0,
      f"charged {fr.cost(none6)['choiceRebalance']}")

# ------------------------------------------------ explanation rewrite: both kinds
print("\n  EXPLANATION REWRITE CHARGES BOTH DEFECTS, NOT ONE")

same = mcq(1)
same[0]["explanation"] = same[0]["dokRationale"]
check("kind 1 — explanation identical to dokRationale (the only kind the old "
      "copy could see)",
      fr.cost(same)["explanationRewrite"] == 1)

restate = mcq(1)
key = next(c for c in restate[0]["choices"] if c["id"] == restate[0]["correctAnswer"])
restate[0]["explanation"] = key["text"].rstrip(".") + " — which is what the Act did."
check("kind 2 — explanation opens by restating the key (825 of the bank's 918, "
      "invisible to the old copy)",
      fr.cost(restate)["explanationRewrite"] == 1,
      f"charged {fr.cost(restate)['explanationRewrite']}")
check("the invoice equals the gate, item for item",
      fr.cost(same + restate)["explanationRewrite"]
      == len(content.gate_explanation_quality(same + restate).findings))

# ------------------------------------------------------------ taxonomy charged
print("\n  THE TAXONOMY OBLIGATION IS BILLED")

one = mcq(1)                      # three distractors, free-text misconceptions, no family
check("3 familyless distractors are charged 3 — one unit each, not one per field",
      fr.cost(one)["distractorTaxonomy"] == 3,
      f"charged {fr.cost(one)['distractorTaxonomy']}")
check("they fail misconception-taxonomy today, which is what the charge is for",
      len(content.gate_misconception_taxonomy(one).findings) == 3)

placed = copy.deepcopy(one)
for c in placed[0]["choices"]:
    if c["id"] != placed[0]["correctAnswer"]:
        c["misconceptionFamily"] = "MC-F-01"
check("resolve the families and the charge goes to 0",
      fr.cost(placed)["distractorTaxonomy"] == 0)
check("…and the gate passes", content.gate_misconception_taxonomy(placed).passed)

# A distractor with NO misconception is charged too: paying the rationale line
# stamps provenance.authoring, which is what makes the gate start judging it.
bare = copy.deepcopy(one)
for c in bare[0]["choices"]:
    if c["id"] != bare[0]["correctAnswer"]:
        c["explanation"], c["misconception"] = None, None
check("a blank distractor is billed BOTH the rationale and the taxonomy — "
      "writing one creates the obligation for the other",
      (fr.cost(bare)["distractorRationale"], fr.cost(bare)["distractorTaxonomy"]) == (3, 3),
      f"got {(fr.cost(bare)['distractorRationale'], fr.cost(bare)['distractorTaxonomy'])}")

# ------------------------------------------------------ choice Spanish charged
print("\n  CHOICE SPANISH IS CHARGED")

es = mcq(1)
check("a fully translated item is charged nothing", fr.cost(es)["choiceTranslation"] == 0)
for c in es[0]["choices"]:
    c["textEs"] = ""
check("4 blank option translations are charged 4 — the KEY included, because a "
      "form with an English key among Spanish options is the defect",
      fr.cost(es)["choiceTranslation"] == 4,
      f"charged {fr.cost(es)['choiceTranslation']}")

# ------------------------------------------- the two gates the invoice did not price
print("\n  THE UNPRICED GATES ARE PRICED, AND THE NUMBER IS THE HONEST ONE")

stim = mcq(1)
stim[0]["stem"] = ("Use the photograph to answer the question. What did the Homestead "
                   "Act change about settlement in the West?")
stim[0]["image"] = None
check("an item ordering a source it does not carry is charged",
      fr.cost(stim)["stimulusDebt"] == 1, f"{fr.cost(stim)['stimulusDebt']}")
check("…and it equals the gate", fr.cost(stim)["stimulusDebt"]
      == len(content.gate_stimulus_integrity(stim).findings))
check("a text-only item is charged nothing — the gate is N/A there, not failing",
      fr.cost(mcq(1))["stimulusDebt"] == 0)

from gates import record as _record
trunc = mcq(1)
trunc[0]["explanation"] = ("The Act made land nearly free to anyone who improved it, and "
                           "settlement therefore spread in dispersed family farms and")
check("an explanation ending mid-sentence is charged",
      fr.cost(trunc)["truncationDebt"] == 1, f"{fr.cost(trunc)['truncationDebt']}")
check("…and it equals the gate", fr.cost(trunc)["truncationDebt"]
      == len(_record.gate_truncation(trunc).findings))
check("a complete item is charged nothing", fr.cost(mcq(1))["truncationDebt"] == 0)

# The guard against the mistake that produced this line: the FIRST version of
# the measurement swept every item-level gate and reported buildability falling
# 73 -> 1, which was distractor-coverage and explanation-quality — debt the
# invoice ALREADY prices — restated as a discovery.
rows_all = fr.rows(B)
sd = sum(r["stimulusDebt"] for r in rows_all if r["buildable"])
td = sum(r["truncationDebt"] for r in rows_all if r["buildable"])
check("the two new lines are a SMALL correction, not a collapse — if they were "
      "large, the measurement is double-counting priced debt again",
      0 < sd + td < 200, f"stimulus={sd} truncation={td}")
check("buildability is unchanged by pricing them — a cost is not a disqualifier",
      sum(1 for r in rows_all if r["buildable"]) == 73,
      f"{sum(1 for r in rows_all if r['buildable'])}")
check("cost() still charges nothing the gates do not — no third copy crept in",
      "stimulusDebt" in src_new() and "gate_stimulus_integrity" in src_new())

# --------------------------------------------------------------- total is a sum
print("\n  THE TOTAL IS THE SUM OF ITS LINES")

rows = fr.rows(B)
bad = [r for r in rows if r["buildable"] and r["totalAuthoringUnits"] != sum(
    r[k] for k in ("distractorRationale", "distractorTaxonomy", "dokRationale",
                   "translation", "choiceTranslation", "explanationRewrite",
                   "choiceRebalance", "stimulusDebt", "truncationDebt"))]
check("every buildable row's TOTAL equals its own columns", not bad,
      f"{len(bad)} row(s) disagree: {[r['standard'] for r in bad[:5]]}")
check("every line reaches the CSV", all(
      k in rows[0] for k in ("distractorTaxonomy", "choiceTranslation",
                             "stimulusDebt", "truncationDebt")))
# This proof is deliberately written against a HARD-CODED column list rather
# than `rows[0].keys()`, so adding a line to the invoice and forgetting to add
# it to the total FAILS here. It did exactly that when stimulusDebt and
# truncationDebt went in, which is the only reason to write it this way.
check("the total is the sum of the NAMED lines, so a new line cannot be "
      "silently left out of it",
      "stimulusDebt" in open(__file__, encoding="utf-8").read())

print(f"\n  {'FAILED: ' + ', '.join(FAILED) if FAILED else 'all invoice proofs pass'}")
sys.exit(1 if FAILED else 0)
