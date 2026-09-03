#!/usr/bin/env python3
"""Prove the content gates — the ones that measure what the bank is ABOUT.

Fixtures are built on US.05, whose standard carries a real checklist
("...including the movement to reservations, assimilation, boarding schools,
and the Dawes Act"). A standard with no checklist cannot be judged, and the
proofs assert that exemption is reported rather than silently passed.
"""
from __future__ import annotations

import copy
import inspect
import json
import re
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

# US.22 — "Compare and contrast the arguments of imperialists and
# non-imperialists" — was the example of a standard that could not be judged at
# all, because it carries no proper noun. That exemption was the defect (L51):
# the gate skipped every item claiming it, silently. It is judgeable now, and
# an unjudgeable standard FAILS rather than being quietly exempted (proved
# against a fixture binding further down).
no_sig = [A(on_std("Anything at all.", code="US.22", id=f"N-{n}"), "unverified")
          for n in range(4)]
r = content.gate_standard_relevance(no_sig, REAL_B)
check("a standard with no proper noun is JUDGED, not exempted", r.measured and r.judged == 4,
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

# ── signal coverage: a standard the matcher cannot judge at all ─────────
print("\n  signal-coverage — a gate green against nothing, one level down")
import alignment as _al

NO_NOUN = "Describe working conditions in industries during this era, including the use of women and children as a labor source."
check("a standard with no proper noun yields NO identifying signal",
      not _al.identifying_signals(NO_NOUN))
check("...but DOES yield topic signals, so it is judgeable",
      "working conditions" in _al.topic_signals(NO_NOUN),
      f"got {_al.topic_signals(NO_NOUN)}")
check("a multi-word topic phrase is evidence on its own",
      _al.topic_evidence("Why were working conditions in 1890s factories so dangerous?", NO_NOUN))
check("ONE single word is NOT evidence — 'radio' in a Fireside Chats item must "
      "not claim the standard on popular culture",
      not _al.topic_evidence("President Roosevelt used the radio to reassure depositors.",
                             "Describe the growth and effects that radio and movies played in "
                             "the emergence of popular culture, such as advertising, "
                             "celebrities, news, and entertainment."))
check("TWO single words are",
      _al.topic_evidence("How did radio and movies reach a national audience in the 1920s?",
                         "Describe the growth and effects that radio and movies played in "
                         "the emergence of popular culture, such as advertising, "
                         "celebrities, news, and entertainment."))
check("a bare abstraction is never a topic signal ('civil' matched civil war, "
      "civil rights and civil defense alike)",
      "civil" not in _al.topic_signals(
          "Analyze the civil rights movement and the Civil Rights Act of 1964."),
      f"got {_al.topic_signals('Analyze the civil rights movement and the Civil Rights Act of 1964.')}")

check("every standard in the real file is judgeable",
      content.gate_signal_coverage(
          [A(on_std(ON, id="S-1"), "evidenced")], REAL_B).passed)
check("the gate DISCLOSES standards identifiable by a single signal",
      "single signal" in content.gate_signal_coverage(
          [A(on_std(ON, id="S-1"), "evidenced")], REAL_B).note)


class _Unjudgeable:
    """A binding whose standards file carries a sentence nothing can match."""
    standards_file = "(fixture)"

    def standards(self):
        return {"US.99": {"code": "US.99", "text": "Explain the impact of the era."}}


UB = _Unjudgeable()
r = content.gate_signal_coverage([A(on_std(ON, id="S-2", code="US.99"), "evidenced")], UB)
check("a standard with NO judgeable signal FAILS the gate", not r.passed)
check("the finding names the standard and how many items claim it",
      any("US.99" in str(f) and "1 servable item" in str(f) for f in r.findings),
      f"got {[str(f) for f in r.findings]}")
check("EMPTY standards scan FAILS — a signal-coverage gate over zero standards "
      "proves nothing", not content.gate_signal_coverage([], None).passed)

print("\n  relevance_scan reports what it cannot judge instead of skipping it")
judged, flagged, unj = content.relevance_scan(
    [A(on_std(ON, id="S-3", code="US.99"), "evidenced")], UB)
check("an item on an unjudgeable standard is NOT counted as judged", judged == 0)
check("...and is RETURNED as unjudgeable rather than dropped", len(unj) == 1)
r = content.gate_standard_relevance([A(on_std(ON, id="S-4", code="US.99"), "evidenced")], UB)
check("the relevance gate FAILS rather than passing over items nobody judged",
      not r.passed)
check("the finding says the alignment cannot be judged either way",
      any("cannot be judged either way" in str(f) for f in r.findings))
check("the note states the unjudgeable count", "unjudgeable" in r.note)

print("\n  a recorded human verification survives a recompute")
import backfill_alignment as _bf
check("backfill preserves human-verified instead of recomputing over it",
      'alignmentStatus") == "human-verified"' in inspect.getsource(_bf),
      "a review pass would be erased by the next backfill")
_bfsrc = inspect.getsource(_bf)
check("backfill judges on the SAME signals relevance_scan judges on",
      "al.judgeable_signals(" in _bfsrc and "al.standard_signals(" not in _bfsrc,
      "a third definition of 'judged' marks items the scan then skips")


# ── what a form claims to be, and what scores an extended response ─────
print("\n  tcap-format / rubric / bias-review / key-contradiction")
CLEAN = A(on_std(ON, id="F-1"), "evidenced")

it = dict(CLEAN, tcapFormat=False, tcapFormatReason="not affirmed")
check("a declared classroom-formative item PASSES",
      content.gate_tcap_format([it], REAL_B).passed)
check("an item with NO tcapFormat FAILS — the form cannot say what it is",
      not content.gate_tcap_format([dict(CLEAN)], REAL_B).passed)
check("false with no reason FAILS — 'no' without a reason is 'nobody looked'",
      not content.gate_tcap_format([dict(CLEAN, tcapFormat=False)], REAL_B).passed)
r = content.gate_tcap_format([dict(CLEAN, tcapFormat=True)], REAL_B)
check("claiming field-testability with no human affirmation FAILS", not r.passed)
check("the finding names the missing affirmation",
      any("tcapFormatAffirmedBy" in str(f) for f in r.findings))
r = content.gate_tcap_format(
    [dict(CLEAN, tcapFormat=True, itemType="document-based",
          tcapFormatAffirmedBy="Sean Reynolds")], REAL_B)
check("a DBQ claiming tcapFormat true FAILS — never TCAP-format under policy",
      not r.passed)
check("EMPTY scan FAILS", not content.gate_tcap_format([], REAL_B).passed)

cr = dict(CLEAN, id="R-1", itemType="constructed-response")
check("an extended response with NO rubric FAILS",
      not content.gate_rubric([cr], REAL_B).passed)
carrier = dict(cr, rubric={"scorePoints": None, "criteria": [], "status": "not-written"})
r = content.gate_rubric([carrier], REAL_B)
check("a CARRIER does not count as a rubric", not r.passed)
check("the finding says so in those words",
      any("CARRIER, not a rubric" in str(f) for f in r.findings))
bands = [{"points": n, "descriptor": "d" * 50} for n in range(5)]
check("a 4-point rubric with FIVE bands (0-4) PASSES — the scale, not the top score",
      content.gate_rubric([dict(cr, rubric={"scorePoints": 4, "criteria": bands})],
                          REAL_B).passed)
check("four bands for a 4-point scale FAILS",
      not content.gate_rubric([dict(cr, rubric={"scorePoints": 4, "criteria": bands[:4]})],
                              REAL_B).passed)
gap = [{"points": n, "descriptor": "d" * 50} for n in (0, 1, 2, 4, 4)]
check("a scale with a gap or duplicate FAILS",
      not content.gate_rubric([dict(cr, rubric={"scorePoints": 4, "criteria": gap})],
                              REAL_B).passed)
blank = [{"points": n, "descriptor": ""} for n in range(5)]
check("bands with no descriptor FAIL — an unlabelled band is scored by feel",
      not content.gate_rubric([dict(cr, rubric={"scorePoints": 4, "criteria": blank})],
                              REAL_B).passed)
r = content.gate_rubric([CLEAN], REAL_B)
check("an mcq-only set is N/A with a stated reason, not a pass over nothing",
      r.inapplicable and r.judged == 0, f"{r.status!r}")

check("not-started bias review PASSES — honest, and not a judgement of content",
      content.gate_bias_review([dict(CLEAN, biasReview={"status": "not-started"})],
                               REAL_B).passed)
check("NO biasReview FAILS — silence reads as reviewed",
      not content.gate_bias_review([dict(CLEAN)], REAL_B).passed)
check("approved with no reviewer FAILS — an approval nobody signed",
      not content.gate_bias_review([dict(CLEAN, biasReview={"status": "approved"})],
                                   REAL_B).passed)
check("EMPTY scan FAILS", not content.gate_bias_review([], REAL_B).passed)

kc = dict(CLEAN, correctAnswer="B",
          explanation="The Dawes Act divided reservation land. B is incorrect because it "
                      "describes a different policy.")
r = content.gate_key_contradiction([kc], REAL_B)
check("an explanation that calls the KEY wrong FAILS", not r.passed)
check("the finding quotes the sentence",
      any("B is incorrect" in str(f) for f in r.findings))
check("the same wording about a DISTRACTOR passes",
      content.gate_key_contradiction(
          [dict(kc, correctAnswer="A")], REAL_B).passed)
check("EMPTY scan FAILS", not content.gate_key_contradiction([], REAL_B).passed)

print("\n  a rubric's zero band is legitimately short")
import apply_rubrics as _ar
_ok = {"X": {"scorePoints": 2, "criteria": [
    {"points": 0, "descriptor": "No response."},
    {"points": 1, "descriptor": "d" * 60}, {"points": 2, "descriptor": "d" * 60}]}}
check("validate accepts a short ZERO band",
      not _ar.validate(_ok, {"X": {"itemType": "constructed-response"}}),
      "it refused four correctly-written rubrics on 'No response, or off-topic.'")
_bad = {"X": {"scorePoints": 2, "criteria": [
    {"points": 0, "descriptor": "No response."},
    {"points": 1, "descriptor": "short"}, {"points": 2, "descriptor": "d" * 60}]}}
check("and still refuses a short SCORING band",
      _ar.validate(_bad, {"X": {"itemType": "constructed-response"}}))


# ── the AI review may recommend; it may never approve ───────────────────
print("\n  ai-review-boundary — the guardrail on the guardrail")
AI_OK = A(on_std(ON, id="AI-1"), "evidenced")
AI_OK["aiReview"] = {
    "pass": "ai-first-pass", "isNotAnApproval": "counts toward no gate",
    "findings": [{"class": "rubric-extraction-fidelity", "verdict": "clear-recommended",
                  "evidence": ["bands appear verbatim in the item's own explanation"],
                  "cannotVerify": []}]}
check("a well-formed AI recommendation PASSES",
      content.gate_ai_review_boundary([AI_OK], REAL_B).passed)


def _ai(mut):
    it = copy.deepcopy(AI_OK)
    mut(it)
    return content.gate_ai_review_boundary([it], REAL_B)


check("AI naming ITSELF as the historian reviewer FAILS",
      not _ai(lambda i: i.update(
          historianReview={"reviewer": "Claude AI first pass", "record": "x"})).passed)
check("AI naming itself as the BIAS reviewer FAILS",
      not _ai(lambda i: i.update(
          biasReview={"status": "approved", "reviewer": "automated review"})).passed)
check("an aiReview block writing into historianReview FAILS",
      not _ai(lambda i: i["aiReview"].update(historianReview={"reviewer": "x"})).passed)
check("an aiReview that does not disclaim itself FAILS — it reads as an approval",
      not _ai(lambda i: i["aiReview"].pop("isNotAnApproval")).passed)
check("a verdict with NO evidence FAILS — that is an opinion, not a review",
      not _ai(lambda i: i["aiReview"]["findings"][0].update(evidence=[])).passed)
check("an escalation naming nothing it could not verify FAILS",
      not _ai(lambda i: i["aiReview"]["findings"][0].update(
          verdict="escalate", cannotVerify=[])).passed)
check("clearing a CITATION FAILS — the policy never declared it clearable",
      not _ai(lambda i: i["aiReview"]["findings"][0].update({"class": "citation"})).passed)
check("clearing a HISTORICAL claim FAILS",
      not _ai(lambda i: i["aiReview"]["findings"][0].update(
          {"class": "authored-content"})).passed)
check("EMPTY scan FAILS", not content.gate_ai_review_boundary([], REAL_B).passed)
_none = content.gate_ai_review_boundary([A(on_std(ON, id="AI-N"), "evidenced")], REAL_B)
check("a set where NOTHING claims review is N/A with a reason, not NOT MEASURED",
      _none.inapplicable and _none.judged == 0, f"{_none.status!r}")
check("a human review claim IS judged even with no AI pass",
      content.gate_ai_review_boundary(
          [dict(A(on_std(ON, id="AI-H"), "evidenced"),
                historianReview={"reviewer": "Sean Reynolds", "record": "r"})],
          REAL_B).judged == 1)

print("\n  the reviewer tool itself never writes a human field")
import ai_review as _air
_src = inspect.getsource(_air)
_pol = _air.policy()
for _f in _pol["theBoundary"]["neverWrites"]:
    _field = _f.split(":")[0]
    check(f"ai_review.py never assigns {_field!r}",
          not re.search(rf'\[\s*["\']{re.escape(_field)}["\']\s*\]\s*=', _src)
          and f'"{_field}":' not in _src.split("POLICY")[-1].split("def main")[0],
          f"the tool writes {_field}, which the policy forbids")
check("the tool writes only into the aiReview namespace",
      '"aiReview"] =' in _src or 'rec["aiReview"]' in _src)
check("every clearable class in the policy is narrow and declared",
      set(_pol["clearableClasses"]) - {"$comment"} and
      all("citation" not in c and "bias" not in c and "descriptor" not in c
          for c in _pol["clearableClasses"] if c != "$comment"),
      "a clearable class touching history, citation or bias is the boundary breaking")


print("\n" + "=" * 74)
print(f"{'ALL PASS' if not FAILED else str(len(FAILED)) + ' FAILED'}")
for f in FAILED:
    print("  FAILED:", f)
print("=" * 74)
sys.exit(1 if FAILED else 0)
