"""Content gates — what the bank is ABOUT, not how it was made.

Sixteen gates measured structure and every one of them passed a bank in which
1,680 items (42%) contain no named element of the standard they are filed
under: a Vietnam anti-war question under "the founding of the United Nations",
a Korea question under "prosperity and consumerism in the 1950s". That is the
failure the owner named at the outset — a bank that renders perfectly while
testing the wrong standards — and structure gates are constitutionally unable
to see it.

These are not accuracy checks. They cannot tell you whether a stem's history is
right; that needs a historian. They tell you an item is filed somewhere its own
words do not support, that a form can be beaten without reading it, and that
the same question appears twice.
"""
from __future__ import annotations

import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import alignment
import itemio
from gates import Finding, Result, empty_scan_guard

ALLOWLIST = os.path.join(itemio.BANK_ROOT, "reviewed", "relevance-allowlist.json")


def _allowed():
    """Items a human has confirmed are correctly filed despite not naming an element.

    The escape hatch is a reviewed, committed decision — not a loosened gate.
    """
    if not os.path.exists(ALLOWLIST):
        return {}
    with open(ALLOWLIST, encoding="utf-8") as fh:
        return json.load(fh).get("items", {})


def _haystack(item):
    """Delegates to alignment.subject_text — one definition of what an item is
    about, shared by the gate, the form builder and the readiness report."""
    return alignment.subject_text(item)


def relevance_scan(items, binding):
    """(judged, flagged) — THE definition of on-standard, shared by the gate and
    tools/rehome.py. Re-deriving it in the triage tool made the two disagree by
    437 items, which is the same defect as a status report that recomputes its
    own gate results."""
    stds = binding.standards()
    allow = _allowed()
    judged, flagged = 0, []
    for it in items:
        if not itemio.servable(it):
            continue
        codes = [c for c in (it.get("standardCodes") or []) if c in stds]
        # IDENTIFYING signals only. standard_signals() falls back to bare content
        # words, and "Support for conservation" yielded "Support" — enough for a
        # constructed response on the 19th Amendment to claim Theodore
        # Roosevelt's standard. L10, reappearing in a second matcher.
        sigsets = {c: alignment.identifying_signals(stds[c]["text"]) for c in codes}
        if not any(sigsets.values()):
            continue
        judged += 1
        if it.get("id") in allow:
            continue
        # Call the ONE matcher. This re-implemented it and its copy forgot to
        # lowercase the haystack, so a proper-noun signal could never match —
        # L22 a fourth time. A rule with two implementations has two behaviours.
        hay = alignment.subject_text(it)
        if not any(alignment.relevant_to(hay, stds[c]["text"]) for c in codes):
            flagged.append((it, codes, sigsets))
    return judged, flagged


def gate_standard_relevance(items, binding=None) -> Result:
    """An item's ALIGNMENT CLAIM must be backed by evidence.

    This gate used to fail on every item that named nothing from its standard,
    which treated an unverified label as a verdict on the question. It is not:
    the content is intact and the item is kept and usable. What must never
    happen is an item CLAIMING an alignment nobody established — that is the
    "renders perfectly while testing the wrong standards" failure.

    So: `evidenced` and `human-verified` must be backed. `rehomed` must carry
    its move evidence. `unverified` is an honest label and passes — it simply
    does not count toward standards coverage (see itemio.aligned).
    """
    name = "alignment-claim"
    if (r := empty_scan_guard(name, items)):
        return r
    judged, flagged = relevance_scan(items, binding)
    flagged_ids = {it["id"] for it, _, _ in flagged}
    allow = _allowed()
    findings, unverified = [], 0
    for it in items:
        if not itemio.servable(it):
            continue
        st = it.get("alignmentStatus")
        if st is None:
            findings.append(Finding(it.get("id", "?"),
                "no alignmentStatus — an item with no stated alignment confidence is a "
                "silent claim", it.get("_file", "")))
        elif st == "unverified":
            unverified += 1
        elif st in ("evidenced", "human-verified"):
            if it["id"] in flagged_ids and it["id"] not in allow:
                findings.append(Finding(it.get("id", "?"),
                    f"claims alignmentStatus {st!r} to {', '.join(it.get('standardCodes') or [])} "
                    f"but names nothing that identifies it — either re-home it, mark it "
                    f"unverified, or record a human verification",
                    it.get("_file", "")))
        elif st == "rehomed":
            if not (it.get("provenance") or {}).get("rehomed"):
                findings.append(Finding(it.get("id", "?"),
                    "marked rehomed but carries no move evidence in provenance",
                    it.get("_file", "")))
    return Result(name, not findings, len(items), findings, judged=judged,
                  note=(f"{unverified} item(s) honestly marked unverified — kept and usable, "
                        f"not counted as coverage; {len(allow)} allowlisted"))


def gate_choice_length_cue(items, binding=None) -> Result:
    """The key must not be the longest choice far more often than chance.

    A student who knows no history can beat a bank where the key is reliably
    the longest option — the same defect as a bank where 60% of keys are C,
    and equally invisible to every structural gate. Measured at 53.3% against
    ~25% chance on the migrated bank.
    """
    name = "choice-length-cue"
    if (r := empty_scan_guard(name, items)):
        return r
    TOLERANCE = 0.10                       # points over chance before it is exploitable
    cohorts = collections.defaultdict(lambda: [0, 0])
    judged = 0
    for it in items:
        if not itemio.servable(it) or not itemio.is_single_select(it):
            continue
        ch = [c for c in itemio.choices(it) if isinstance(c, dict) and c.get("text")]
        if len(ch) < 3 or not it.get("correctAnswer"):
            continue
        judged += 1
        k = len(ch)
        cohorts[k][1] += 1
        longest = max(ch, key=lambda c: len(c["text"]))
        if longest.get("id") == it["correctAnswer"]:
            cohorts[k][0] += 1
    findings, notes = [], []
    for k, (hits, total) in sorted(cohorts.items()):
        chance, share = 1.0 / k, hits / total
        notes.append(f"{k}-choice n={total} key-is-longest {share:.1%} (chance {chance:.0%})")
        # TWO-SIDED. Balancing a cued set down to 0% is also a cue — "the longest
        # option is never right" is just as learnable as "the longest option is
        # always right", and a one-sided gate calls that a pass. Found by
        # over-correcting a real form from 66.7% to 0.0% and being told it passed.
        if share > chance + TOLERANCE:
            findings.append(Finding(f"{k}-choice cohort",
                f"the key is the longest option in {hits}/{total} items ({share:.1%}) "
                f"against {chance:.0%} by chance — a student can beat this bank without "
                f"reading the stems"))
        elif share < chance - TOLERANCE:
            findings.append(Finding(f"{k}-choice cohort",
                f"the key is the longest option in only {hits}/{total} items ({share:.1%}) "
                f"against {chance:.0%} by chance — 'the longest option is never right' is "
                f"equally learnable"))
    return Result(name, not findings, len(items), findings, judged=judged,
                  note="; ".join(notes))


def _norm(s):
    return re.sub(r"[^a-z0-9 ]", "", (s or "").lower()).strip()


def gate_duplicate_stems(items, binding=None) -> Result:
    """The same question must not exist twice under two ids.

    Two ids carrying one stem can land on the same form, and a bank that counts
    both toward coverage is counting one question twice.
    """
    name = "duplicate-stems"
    if (r := empty_scan_guard(name, items)):
        return r
    by = collections.defaultdict(list)
    judged = 0
    for it in items:
        if not itemio.servable(it) or not (it.get("stem") or "").strip():
            continue
        judged += 1
        by[_norm(it["stem"])].append(it)
    findings = []
    for stem, group in sorted(by.items()):
        if len(group) > 1:
            ids = [g.get("id") for g in group]
            codes = sorted({c for g in group for c in (g.get("standardCodes") or [])})
            findings.append(Finding(", ".join(ids[:4]),
                f"{len(group)} items share one stem, filed under {codes}: "
                f"\"{group[0]['stem'][:70]}…\""))
    return Result(name, not findings, len(items), findings, judged=judged)


# ------------------------------------------------------- citation integrity
# A bulk edit replaced PUBLICATION TITLES with REPOSITORY names across the
# primary-source items, leaving the date intact and a dangling noun behind:
#   'first published in Library of Congress, NAACP Records (loc.gov), June 1921'
# where the source is Langston Hughes in The Crisis, June 1921. The repository
# is where a scan lives; it is not where the work was published. These are the
# DBQ and constructed-response items — the ones an adoption reviewer reads
# first — so a wrong attribution here is a compliance problem, not a typo.
_REPOSITORIES = r"(?:Library of Congress|National Archives|loc\.gov|archives\.gov|Project Gutenberg)"
_CITATION_DEFECTS = [
    (re.compile(r"\((?:loc|archives)\.gov\)\s+(magazine|newspaper|journal)", re.I),
     "a repository is glued to '{0}' where the publication title was replaced"),
    (re.compile(r"(?:first\s+)?published in\s+" + _REPOSITORIES, re.I),
     "'published in' names a REPOSITORY, not a publication"),
    (re.compile(r"reported in\s+[^,]{0,40},\s*" + _REPOSITORIES + r"[^)]*\)\s+(newspaper|magazine)", re.I),
     "'reported in' names a repository followed by a dangling '{0}'"),
]


def gate_citation_integrity(items, binding=None) -> Result:
    """A citation must name where a work was PUBLISHED, not where a scan lives.

    Source of truth only: an item whose attribution is wrong does not ship, and
    an unsourced item is worse than a missing one.
    """
    name = "citation-integrity"
    if (r := empty_scan_guard(name, items)):
        return r
    findings, judged, held = [], 0, 0
    for it in items:
        blob = " ".join([it.get("stem") or "", it.get("explanation") or "",
                         str(it.get("correctAnswer") or "")])
        if not re.search(r"published|reported in|loc\.gov|archives\.gov", blob, re.I):
            continue
        if not itemio.servable(it):
            # Held out of service. The defect is real and still tracked in
            # reviewed/citation-corrections.json; it just cannot reach a reader.
            if it.get("citationStatus") == "corrupted-held":
                held += 1
            continue
        judged += 1
        if it.get("citationStatus") == "verified":
            continue
        for rx, msg in _CITATION_DEFECTS:
            m = rx.search(blob)
            if m:
                detail = msg.format(*(m.groups() or ("",)))
                findings.append(Finding(it.get("id", "?"),
                    f"{detail}: …{m.group(0)[:80]}…", it.get("_file", "")))
                break
    if judged == 0:
        return Result(name, True, len(items), [], judged=0,
                      inapplicable="no item in this set carries a source citation, so there "
                                   "is no attribution to check",
                      note=f"{held} held out of service awaiting source verification"
                           if held else "")
    return Result(name, not findings, len(items), findings, judged=judged,
                  note=f"{judged} servable item(s) carry a citation" +
                       (f"; {held} held out of service awaiting source verification" if held else ""))


# ------------------------------------------------------- translation claim
# A bilingual claim is an accessibility claim. Measured on the migrated bank:
# 1,132 items carry a `textEs` that is a verbatim copy of the English, and 469
# carry a word-substitution pseudo-translation — "The programs violated the 5th
# enmienda's protection against government taking of property". The second is
# worse than nothing because it LOOKS translated. Most were honestly marked
# needs-review; 93 claimed `complete`.
_ES_MARK = re.compile(r"[áéíóúñü¿¡]", re.I)
_ES_FUNC = re.compile(r"\b(los|las|del|que|para|por|una|con|el|la|de|en|un)\b", re.I)


def _spanishy(t):
    t = t or ""
    return bool(_ES_MARK.search(t)) or bool(_ES_FUNC.search(t))


def translation_defect(en, es):
    """None, 'untranslated-copy' or 'pseudo-translation'.

    An identical short string is fine — an acronym (SNCC) or a proper noun does
    not change between languages.
    """
    en, es = (en or "").strip(), (es or "").strip()
    if not es:
        return None
    if es == en:
        return None if (len(en) < 25 or en.isupper()) else "untranslated-copy"
    if len(es) > 25 and not _spanishy(es):
        return "pseudo-translation"
    return None


def worst_translation_defect(item):
    for c in itemio.choices(item):
        if isinstance(c, dict):
            d = translation_defect(c.get("text"), c.get("textEs"))
            if d:
                return d
    return (translation_defect(item.get("stem"), item.get("stemEs"))
            or translation_defect(item.get("explanation"), item.get("explanationEs")))


def gate_translation_claim(items, binding=None) -> Result:
    """translationStatus must match what the Spanish fields actually contain.

    Same shape as alignment-claim: an item may honestly say its translation is
    unfinished. It may not claim `complete` while its Spanish is English.
    """
    name = "translation-claim"
    if (r := empty_scan_guard(name, items)):
        return r
    findings, judged = [], 0
    counts = collections.Counter()
    for it in items:
        if not itemio.servable(it):
            continue
        if not any((it.get(f) or "").strip() for f in ("stemEs", "explanationEs")) and \
           not any((c.get("textEs") or "").strip() for c in itemio.choices(it) if isinstance(c, dict)):
            continue
        judged += 1
        d = worst_translation_defect(it)
        counts[d or "ok"] += 1
        if d and it.get("translationStatus") == "complete":
            findings.append(Finding(it.get("id", "?"),
                f"claims translationStatus 'complete' but its Spanish is a {d} — a bilingual "
                f"claim is an accessibility claim", it.get("_file", "")))
    return Result(name, not findings, len(items), findings, judged=judged,
                  note=f"{counts.get('untranslated-copy', 0)} untranslated copy, "
                       f"{counts.get('pseudo-translation', 0)} pseudo-translation, "
                       f"{counts.get('ok', 0)} genuine — all honestly labelled except the findings")


# ------------------------------------------------------ explanation quality
def gate_explanation_quality(items, binding=None) -> Result:
    """The key's explanation says WHY it is right — not a restatement of it.

    Two defects measured on the bank: an explanation identical to the item's own
    dokRationale (a terse editorial note standing in for both), and an
    explanation that opens by repeating the key choice verbatim.
    """
    name = "explanation-quality"
    if (r := empty_scan_guard(name, items)):
        return r
    findings, judged = [], 0
    for it in items:
        if not itemio.servable(it):
            continue
        exp = (it.get("explanation") or "").strip()
        if not exp:
            continue
        judged += 1
        if exp == (it.get("dokRationale") or "").strip():
            findings.append(Finding(it.get("id", "?"),
                "explanation is identical to dokRationale — one editorial note standing in "
                "for two different jobs", it.get("_file", "")))
            continue
        key = next((c for c in itemio.choices(it)
                    if isinstance(c, dict) and c.get("id") == it.get("correctAnswer")), None)
        if key and (key.get("text") or "").strip():
            kt = key["text"].strip().rstrip(".")
            if len(kt) > 30 and exp.lower().startswith(kt.lower()[:min(len(kt), 60)]):
                findings.append(Finding(it.get("id", "?"),
                    "explanation opens by restating the key verbatim rather than saying why "
                    "it is right", it.get("_file", "")))
    return Result(name, not findings, len(items), findings, judged=judged)


# ---------------------------------------------------- embedded answer key
# Nine items carry their ENTIRE body inside the stem — question, then all four
# options inline, with an answer-key marker surviving the paste:
#   "Which best explains why the Truman Doctrine…? H It committed the United
#    States to supporting free peoples… B. It authorized… C. It replaced…"
# Rendered on a form the student reads every option twice and sees the marker.
# Each alternative carries its own boundary. A single leading \b applied to the
# whole group could never match "(correct)", because there is no word boundary
# between a space and a parenthesis — the marker was undetectable and the test
# is what said so.
_KEY_MARKER = re.compile(r"(?:\bCORRECT ANSWER\b|\bANSWER KEY\b|\(correct\)|\bANS:)", re.I)


def gate_embedded_key(items, binding=None) -> Result:
    """No answer-key marker, and no choice text, inside student-visible fields."""
    name = "embedded-answer-key"
    if (r := empty_scan_guard(name, items)):
        return r
    findings, judged = [], 0
    for it in items:
        if not itemio.servable(it):
            continue
        judged += 1
        stem = it.get("stem") or ""
        if _KEY_MARKER.search(stem):
            findings.append(Finding(it.get("id", "?"),
                "stem contains an answer-key marker", it.get("_file", "")))
            continue
        leaked = [c.get("id") for c in itemio.choices(it)
                  if isinstance(c, dict) and (c.get("text") or "").strip()
                  and len(c["text"].strip()) > 25 and c["text"].strip()[:40] in stem]
        if len(leaked) >= 2:
            findings.append(Finding(it.get("id", "?"),
                f"stem contains the text of its own choices {leaked} — the student reads "
                f"every option twice", it.get("_file", "")))
            continue
        for c in itemio.choices(it):
            if isinstance(c, dict) and _KEY_MARKER.search((c.get("text") or "") +
                                                          (c.get("textEs") or "")):
                findings.append(Finding(it.get("id", "?"),
                    f"choice {c.get('id')} carries an answer-key marker", it.get("_file", "")))
                break
    return Result(name, not findings, len(items), findings, judged=judged)


# ------------------------------------------------------- review provenance
def gate_review_provenance(items, binding=None) -> Result:
    """An item may not claim human review without a record that names it.

    Authored content carries historical claims no gate can check — "Spain had
    lost its mainland American colonies eighty years earlier" is either right or
    it is not, and only a person can say. That makes the review CLAIM the thing
    worth gating, exactly as with alignment and translation: an item may say it
    is awaiting review, and it may say a named person approved it on a named
    date, but it may not say the second without the record.
    """
    name = "review-provenance"
    if (r := empty_scan_guard(name, items)):
        return r
    path = os.path.join(itemio.BANK_ROOT, "reviewed", "historian-approvals.json")
    approved = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for rec in json.load(fh).get("approvals", []):
                for iid in rec.get("items", []):
                    approved[iid] = rec
    findings, judged, pending = [], 0, 0
    for it in items:
        if not itemio.servable(it):
            continue
        authored = (it.get("provenance") or {}).get("authoring")
        review = it.get("historianReview")
        if not authored and not review:
            continue
        judged += 1
        if review:
            rec = approved.get(it.get("id"))
            if not rec:
                findings.append(Finding(it.get("id", "?"),
                    "claims historian review but no approval record names this item",
                    it.get("_file", "")))
            elif review.get("record") != rec["record"] or review.get("reviewer") != rec["reviewer"]:
                findings.append(Finding(it.get("id", "?"),
                    f"review stamp disagrees with the record ({review.get('reviewer')!r} vs "
                    f"{rec['reviewer']!r})", it.get("_file", "")))
            elif it.get("requiresHistorianReview"):
                findings.append(Finding(it.get("id", "?"),
                    "both approved and still flagged as requiring review", it.get("_file", "")))
        elif authored and not it.get("requiresHistorianReview"):
            findings.append(Finding(it.get("id", "?"),
                "carries authored content but neither claims review nor flags that it needs "
                "one — authored historical claims are never silently settled",
                it.get("_file", "")))
        elif authored:
            pending += 1
    return Result(name, not findings, len(items), findings, judged=judged,
                  note=f"{judged - pending} approved, {pending} awaiting review")
