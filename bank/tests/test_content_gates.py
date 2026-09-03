#!/usr/bin/env python3
"""Prove the content gates — the ones that measure what the bank is ABOUT.

Fixtures are built on US.05, whose standard carries a real checklist
("...including the movement to reservations, assimilation, boarding schools,
and the Dawes Act"). A standard with no checklist cannot be judged, and the
proofs assert that exemption is reported rather than silently passed.
"""
from __future__ import annotations

import copy
import json
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

# ── citation integrity ───────────────────────────────────────────────────
print("\n  citation-integrity — a citation names where a work was PUBLISHED")
GOOD = ('Langston Hughes, "The Negro Speaks of Rivers," first published in The Crisis, '
        'June 1921 (public domain).')
BAD1 = ('Langston Hughes, "The Negro Speaks of Rivers," first published in Library of '
        'Congress, NAACP Records (loc.gov), June 1921 (public domain).')
BAD2 = ('Marcus Garvey, "Africa for the Africans," 1921, reported in Marcus Garvey Papers, '
        'National Archives (archives.gov) newspaper (public domain).')

ok = [A(on_std(ON, id=f"C-{n}", explanation=GOOD), "evidenced") for n in range(3)]
r = content.gate_citation_integrity(ok, B)
check("a citation naming the real publication PASSES", r.passed,
      "; ".join(str(f) for f in r.findings[:2]))
check("it judged the items carrying citations", r.judged == 3, f"judged={r.judged}")

bad = copy.deepcopy(ok); bad[1]["explanation"] = BAD1
r = content.gate_citation_integrity(bad, B)
check("'published in <repository>' FAILS", not r.passed)
check("the finding says a repository stands where a publication belongs",
      any("REPOSITORY" in str(f) or "publication title was replaced" in str(f)
          for f in r.findings), f"got {[str(f)[:100] for f in r.findings[:1]]}")

bad2 = copy.deepcopy(ok); bad2[0]["explanation"] = BAD2
check("a repository glued to a dangling 'newspaper' FAILS",
      not content.gate_citation_integrity(bad2, B).passed)

# A repository named as WHERE A SCAN LIVES is legitimate and must not be flagged.
fine = copy.deepcopy(ok)
fine[2]["explanation"] = ("W.E.B. Du Bois, The Souls of Black Folk (1903), available in the "
                          "public domain through the Library of Congress and Project Gutenberg.")
check("naming a repository as where a scan is AVAILABLE is not a defect",
      content.gate_citation_integrity(fine, B).passed,
      "; ".join(str(f) for f in content.gate_citation_integrity(fine, B).findings[:1]))

check("an item with no citation at all is not judged",
      content.gate_citation_integrity(
          [A(on_std(ON, id="NC-1"), "evidenced")], B).judged == 0)
check("EMPTY scan FAILS", not content.gate_citation_integrity([], B).passed)
check("a human 'verified' citation is exempt",
      content.gate_citation_integrity(
          [dict(bad[1], citationStatus="verified")], B).passed)
# Holding is a real remediation: a held item cannot reach a reader, so it does
# not fail the gate — but it is counted in the note, never silently dropped.
heldset = [dict(bad[1], status="quarantined", citationStatus="corrupted-held")] + ok[:2]
r = content.gate_citation_integrity(heldset, B)
check("a HELD item does not fail the gate (it cannot reach a reader)", r.passed)
check("but the held count is reported, not hidden", "held out of service" in r.note, r.note)

# ── translation claim ────────────────────────────────────────────────────
print("\n  translation-claim — a bilingual claim is an accessibility claim")
def es(it, stemEs=None, choiceEs=None, status="complete"):
    it["stemEs"] = stemEs if stemEs is not None else it["stemEs"]
    if choiceEs is not None:
        for c in it["choices"]:
            c["textEs"] = choiceEs(c)
    it["translationStatus"] = status
    return it

real = [A(on_std(ON, id=f"TR-{n}"), "evidenced") for n in range(3)]
check("genuine Spanish claiming 'complete' PASSES",
      content.gate_translation_claim(real, B).passed,
      "; ".join(str(f) for f in content.gate_translation_claim(real, B).findings[:2]))

copied = copy.deepcopy(real)
es(copied[1], choiceEs=lambda c: c["text"])
r = content.gate_translation_claim(copied, B)
check("Spanish that is a verbatim copy of English, claiming 'complete', FAILS", not r.passed)
check("the finding names it an accessibility claim",
      any("accessibility claim" in str(f) for f in r.findings))

pseudo = copy.deepcopy(real)
es(pseudo[0], choiceEs=lambda c: c["text"].replace("Amendment", "enmienda")
   .replace("federal", "federal") if len(c["text"]) > 25 else c["text"])
pseudo[0]["choices"][0]["textEs"] = ("The programs violated the 5th enmienda's protection "
                                     "against government taking of property")
check("word-substitution pseudo-translation claiming 'complete' FAILS",
      not content.gate_translation_claim(pseudo, B).passed)

honest = copy.deepcopy(copied)
honest[1]["translationStatus"] = "not-started"
check("the SAME item labelled 'not-started' PASSES — honest, not fixed",
      content.gate_translation_claim(honest, B).passed)

check("an acronym identical in both languages is not a defect",
      content.translation_defect("SNCC", "SNCC") is None)
check("a long identical string IS untranslated",
      content.translation_defect("Defense production for WWII and consumer goods for the home",
                                 "Defense production for WWII and consumer goods for the home")
      == "untranslated-copy")
check("EMPTY scan FAILS", not content.gate_translation_claim([], B).passed)
check("an item with no Spanish at all is not judged",
      content.gate_translation_claim(
          [dict(A(on_std(ON, id="NOES"), "evidenced"), stemEs="", explanationEs="",
                choices=[dict(c, textEs="") for c in real[0]["choices"]])], B).judged == 0)

# ── explanation quality ──────────────────────────────────────────────────
print("\n  explanation-quality — the key's explanation says WHY, not WHAT")
good = [A(on_std(ON, id=f"EX-{n}"), "evidenced") for n in range(3)]
check("a real explanation PASSES", content.gate_explanation_quality(good, B).passed,
      "; ".join(str(f) for f in content.gate_explanation_quality(good, B).findings[:2]))

dup = copy.deepcopy(good)
dup[1]["explanation"] = dup[1]["dokRationale"]
r = content.gate_explanation_quality(dup, B)
check("an explanation identical to the dokRationale FAILS", not r.passed)
check("the finding says one note is doing two jobs",
      any("two different jobs" in str(f) for f in r.findings))

restate = copy.deepcopy(good)
keytext = next(c["text"] for c in restate[0]["choices"]
               if c["id"] == restate[0]["correctAnswer"])
restate[0]["explanation"] = keytext + " and this was very significant for the period."
check("an explanation that opens by restating the key FAILS",
      not content.gate_explanation_quality(restate, B).passed)
check("EMPTY scan FAILS", not content.gate_explanation_quality([], B).passed)

# ── embedded answer key ──────────────────────────────────────────────────
print("\n  embedded-answer-key — student-visible text must not carry the key")
base = [A(on_std(ON, id=f"EK-{n}"), "evidenced") for n in range(3)]
check("a normal item PASSES", content.gate_embedded_key(base, B).passed,
      "; ".join(str(f) for f in content.gate_embedded_key(base, B).findings[:2]))

mark = copy.deepcopy(base)
mark[1]["stem"] = "Why did the Dawes Act divide land? CORRECT ANSWER A. To force allotment."
check("an answer-key marker in the stem FAILS",
      not content.gate_embedded_key(mark, B).passed)

inchoice = copy.deepcopy(base)
inchoice[0]["choices"][0]["text"] = "(correct) It divided reservation land into allotments."
check("an answer-key marker in a choice FAILS",
      not content.gate_embedded_key(inchoice, B).passed)

swallowed = copy.deepcopy(base)
ch = swallowed[2]["choices"]
swallowed[2]["stem"] = (swallowed[2]["stem"] + " " + ch[0]["text"] + " B. " + ch[1]["text"])
r = content.gate_embedded_key(swallowed, B)
check("a stem containing its own choice list FAILS", not r.passed)
check("the finding says the student reads every option twice",
      any("twice" in str(f) for f in r.findings))
check("EMPTY scan FAILS", not content.gate_embedded_key([], B).passed)

# ── review provenance ────────────────────────────────────────────────────
print("\n  review-provenance — an approval is a fact about named items, not a mood")
import os as _os
REAL_REC = _os.path.join(_os.path.dirname(HERE), "reviewed", "historian-approvals.json")
real = json.load(open(REAL_REC, encoding="utf-8"))["approvals"][0]
known = real["items"][0]
stamp = {"status": "approved", "record": real["record"],
         "reviewer": real["reviewer"], "date": real["date"]}

def authored(iid, **over):
    it = A(on_std(ON, id=iid), "evidenced")
    it["provenance"] = {"authoring": {"record": "form-a.json"}}
    it["requiresHistorianReview"] = True
    it.update(over)
    return it

check("an authored item awaiting review PASSES",
      content.gate_review_provenance([authored("P-1")], REAL_B).passed)
check("an authored item approved by a REAL record PASSES",
      content.gate_review_provenance(
          [authored(known, historianReview=stamp, requiresHistorianReview=False)],
          REAL_B).passed)

r = content.gate_review_provenance(
    [authored("FAKE-1", historianReview=stamp, requiresHistorianReview=False)], REAL_B)
check("an item CLAIMING review that no record names FAILS", not r.passed)
check("the finding says no record names it",
      any("no approval record names this item" in str(f) for f in r.findings))

r = content.gate_review_provenance(
    [authored(known, historianReview={**stamp, "reviewer": "Someone Else"},
              requiresHistorianReview=False)], REAL_B)
check("a stamp naming a different reviewer than the record FAILS", not r.passed)

r = content.gate_review_provenance(
    [authored(known, historianReview=stamp, requiresHistorianReview=True)], REAL_B)
check("approved AND still flagged as needing review FAILS", not r.passed)

r = content.gate_review_provenance([authored("S-1", requiresHistorianReview=False)], REAL_B)
check("authored content that is silently settled FAILS", not r.passed)
check("the finding says authored claims are never silently settled",
      any("never silently settled" in str(f) for f in r.findings))
check("an unauthored item is not judged",
      content.gate_review_provenance([A(on_std(ON, id="U-1"), "evidenced")], REAL_B).judged == 0)
check("EMPTY scan FAILS", not content.gate_review_provenance([], REAL_B).passed)

print("\n" + "=" * 74)
print(f"{'ALL PASS' if not FAILED else str(len(FAILED)) + ' FAILED'}")
for f in FAILED:
    print("  FAILED:", f)
print("=" * 74)
sys.exit(1 if FAILED else 0)
