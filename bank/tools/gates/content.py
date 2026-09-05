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
    judged, flagged, unjudgeable = 0, [], []
    for it in items:
        if not itemio.servable(it):
            continue
        codes = [c for c in (it.get("standardCodes") or []) if c in stds]
        # IDENTIFYING signals only. standard_signals() falls back to bare content
        # words, and "Support for conservation" yielded "Support" — enough for a
        # constructed response on the 19th Amendment to claim Theodore
        # Roosevelt's standard. L10, reappearing in a second matcher.
        #
        # judgeable_signals() adds TOPIC signals, because nine standards carry no
        # proper noun at all and this loop used to `continue` past every item
        # claiming one — 331 servable items judged by nobody, counted by nothing,
        # and reported as "0 aligned" rather than "cannot be judged" (L51). They
        # are counted now, and unjudgeable ones are RETURNED so the gate can fail
        # on them instead of skipping them.
        sigsets = {c: alignment.judgeable_signals(stds[c]["text"]) for c in codes}
        if codes and not any(sigsets.values()):
            unjudgeable.append(it)
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
    return judged, flagged, unjudgeable


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
    judged, flagged, unjudgeable = relevance_scan(items, binding)
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
    # An item this system CANNOT judge must not vanish from the count. Skipping
    # it read as a clean pass over a population nobody looked at (L51).
    if unjudgeable:
        codes = sorted({c for it in unjudgeable for c in (it.get("standardCodes") or [])})
        findings.append(Finding("(unjudgeable)",
            f"{len(unjudgeable)} servable item(s) claim standard(s) this system has no "
            f"signal for, so their alignment cannot be judged either way: "
            f"{', '.join(codes)} — see the signal-coverage gate", ""))
    return Result(name, not findings, len(items), findings, judged=judged,
                  note=(f"{unverified} item(s) honestly marked unverified — kept and usable, "
                        f"not counted as coverage; {len(allow)} allowlisted; "
                        f"{len(unjudgeable)} unjudgeable"))


def gate_signal_coverage(items, binding=None) -> Result:
    """Every standard must be JUDGEABLE — the matcher must have something to
    match on.

    This gate measures the standards file, not the items, because the defect it
    catches exists before a single item is written: a standard whose sentence
    carries no proper noun ("Describe working conditions in industries...",
    "Analyze the increasing impact of television and mass media...") gave the
    relevance matcher an EMPTY signal set. relevance_scan then skipped every
    item claiming it — 331 servable items across 9 standards — without counting
    them as judged or flagging anything. The readiness report showed those
    standards at "0 aligned", which reads as "no items exist" and is a
    different, much less alarming statement than "no item here can ever be
    checked".

    A gate green against nothing, per standard. It is the whole-gate defect of
    L11/L15 one level down, and the `judged` counter could not see it because
    the gate as a whole was judging 3,600 other items.
    """
    name = "signal-coverage"
    stds = binding.standards() if binding else {}
    if not stds:
        return Result(name, False, 0, [Finding("(empty)",
            "no standards to measure — a signal-coverage gate that scans zero "
            "standards proves nothing", "")], judged=0)
    claims = collections.Counter()
    for it in items or []:
        if itemio.servable(it):
            for c in (it.get("standardCodes") or []):
                claims[c] += 1
    findings, weak = [], []
    for code in sorted(stds):
        sigs = set(alignment.judgeable_signals(stds[code]["text"]))
        if not sigs:
            findings.append(Finding(code,
                f"no judgeable signal — nothing in this standard's sentence can identify "
                f"an item as testing it, so every relevance verdict on it is vacuous "
                f"({claims.get(code, 0)} servable item(s) claim it)", binding.standards_file))
        elif len(sigs) == 1:
            weak.append(code)
    return Result(name, not findings, len(stds), findings, judged=len(stds),
                  note=(f"{len(weak)} standard(s) identifiable by a single signal — every "
                        f"verdict on them is soft, human judgement recommended: "
                        f"{', '.join(weak)}" if weak else "every standard carries 2+ signals"))


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
    # Below four items the tolerance band is UNREACHABLE: with n=2 the only
    # possible shares are 0%, 50% and 100%, so a two-item draft could never
    # pass no matter how it was written. A gate that cannot be satisfied is
    # worse than no gate — it is the "alarm that fires on the harmless" again,
    # in the one shape that blocks work entirely.
    MIN_COHORT = 4
    if all(total < MIN_COHORT for _, total in cohorts.values()):
        n = sum(t for _, t in cohorts.values())
        return Result(name, True, len(items), [], judged=judged,
                      inapplicable=f"only {n} selected-response item(s) — below {MIN_COHORT} "
                                   f"the proportion cannot land inside the tolerance band, so "
                                   f"there is no distribution to judge")
    findings, notes = [], []
    for k, (hits, total) in sorted(cohorts.items()):
        if total < MIN_COHORT:
            notes.append(f"{k}-choice n={total} (below {MIN_COHORT}, not judged)")
            continue
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
    if judged == 0:
        return Result(name, True, len(items), [], judged=0,
                      inapplicable="no item in this set carries any Spanish field, so there "
                                   "is no bilingual claim to check")
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


# ---------------------------------------------------------------------------
# What a form CLAIMS TO BE, and what an extended response needs to be scored.
#
# Sean Reynolds, first teacher read of FORM-A: "this is a mixed classroom
# assessment, not a TCAP-field-testable form. Six extended responses/DBQs can
# be valuable instructionally, but they must be tagged tcap_format: false and
# supported by rubrics; the 12 MC items also lack the required standards,
# DOK/Hess, distractor, bias, citation, and IRT metadata in the supplied form."
#
# He was right about every part of it, and the measurement was worse than
# "thin": tcapFormat existed on 0 of 3,958 servable items, a rubric on 0 of 100
# constructed-response and document-based items, a bias review on none at all —
# while twenty-two gates read green. A form that mixes twelve selected-response
# items with six extended responses READS as a test form, and nothing in the
# artifact said otherwise.
# ---------------------------------------------------------------------------

TCAP_POLICY = os.path.join(itemio.BANK_ROOT, "policy", "tcap-format.json")


def _tcap_policy():
    with open(TCAP_POLICY, encoding="utf-8") as fh:
        return json.load(fh)


def gate_tcap_format(items, binding=None) -> Result:
    """Every item declares whether it is field-testable, and cannot claim it lightly.

    The default is FALSE and there is no automatic path to True: a machine
    affirming its own field-testability is precisely the unverified compliance
    claim this repo refuses to make. True requires a named human AND every
    field the policy lists, because an item missing its DOK rationale, its
    distractor analysis, its bias review or its IRT block cannot be judged
    field-testable by anybody.
    """
    name = "tcap-format"
    if (r := empty_scan_guard(name, items)):
        return r
    pol = _tcap_policy()
    never = set(pol["neverTcapFormat"]["itemTypes"])
    req = pol["requiredBeforeTrue"]
    findings, judged, claimed = [], 0, 0
    for it in items:
        if not itemio.servable(it):
            continue
        judged += 1
        if "tcapFormat" not in it:
            findings.append(Finding(it.get("id", "?"),
                "no tcapFormat — the item does not say whether it is field-testable, so a "
                "form built from it cannot say what it is", it.get("_file", "")))
            continue
        if it["tcapFormat"] is not True:
            if not (it.get("tcapFormatReason") or "").strip():
                findings.append(Finding(it.get("id", "?"),
                    "tcapFormat is false with no stated reason — 'no' without a reason is "
                    "indistinguishable from 'nobody looked'", it.get("_file", "")))
            continue
        claimed += 1
        if it.get("itemType") in never:
            findings.append(Finding(it.get("id", "?"),
                f"claims tcapFormat true, but item type {it.get('itemType')!r} is never "
                f"TCAP-format under policy v{pol['policyVersion']}", it.get("_file", "")))
        missing = [f for f in req["fields"] if not it.get(f)]
        if missing:
            findings.append(Finding(it.get("id", "?"),
                f"claims tcapFormat true but carries no {', '.join(missing)} — the policy "
                f"requires every one of these before the claim can be made",
                it.get("_file", "")))
        if not (it.get(req["humanAffirmation"]) or "").strip():
            findings.append(Finding(it.get("id", "?"),
                f"claims tcapFormat true with no {req['humanAffirmation']} — no person is "
                f"named as having judged it field-testable", it.get("_file", "")))
        for ch in itemio.choices(it):
            if isinstance(ch, dict) and ch.get("id") != it.get("correctAnswer"):
                gap = [f for f in req["perDistractor"] if not (ch.get(f) or "").strip()]
                if gap:
                    findings.append(Finding(it.get("id", "?"),
                        f"claims tcapFormat true but distractor {ch.get('id')} has no "
                        f"{', '.join(gap)}", it.get("_file", "")))
    return Result(name, not findings, len(items), findings, judged=judged,
                  note=(f"{claimed} item(s) claim field-testability; {judged - claimed} are "
                        f"declared classroom-formative. Policy source of record: "
                        f"{pol['sourceOfRecord']} — NOT a TDOE publication."))


def gate_rubric(items, binding=None) -> Result:
    """An extended response with no rubric is not scoreable.

    100 of 100 constructed-response and document-based items had no rubric, and
    `record-complete` never asked — it was written around the four-option
    record shape, so the fields an extended response needs were not in its
    list. A gate that checks the wrong shape passes the wrong thing.

    A carrier written by the backfill (`status: not-written`) must NOT read as
    a rubric: an empty scaffold that satisfies a presence check is the same
    defect as an IRT parameter present in a field and meaning nothing (L50).
    """
    name = "rubric"
    if (r := empty_scan_guard(name, items)):
        return r
    pol = _tcap_policy()
    needs = set(pol["neverTcapFormat"]["itemTypes"])
    pool = [i for i in items if itemio.servable(i) and i.get("itemType") in needs]
    if not pool:
        return Result(name, True, len(items), [], judged=0,
                      inapplicable="no constructed-response or document-based item in this "
                                   "set, so there is no rubric to check")
    findings, written = [], 0
    for it in pool:
        rub = it.get("rubric")
        if not isinstance(rub, dict):
            findings.append(Finding(it.get("id", "?"),
                f"{it.get('itemType')} with no rubric — a teacher cannot score it and two "
                f"teachers cannot agree on it", it.get("_file", "")))
            continue
        pts, crit = rub.get("scorePoints"), rub.get("criteria") or []
        if not pts or not crit:
            findings.append(Finding(it.get("id", "?"),
                f"rubric is a CARRIER, not a rubric (scorePoints={pts!r}, {len(crit)} "
                f"criteria) — it must not count as one", it.get("_file", "")))
            continue
        # A 4-point rubric has FIVE bands: 0 through 4. Requiring one band per
        # point failed every correctly-extracted rubric in the bank — the gate
        # was counting the top score instead of the scale.
        if len(crit) != pts + 1:
            findings.append(Finding(it.get("id", "?"),
                f"rubric tops out at {pts} point(s) but describes {len(crit)} band(s), not "
                f"{pts + 1} (0 through {pts}) — a student cannot be told what earns the "
                f"missing one", it.get("_file", "")))
            continue
        if {c.get("points") for c in crit} != set(range(pts + 1)):
            findings.append(Finding(it.get("id", "?"),
                f"rubric bands are {sorted(c.get('points') for c in crit)}, not "
                f"0-{pts} — a scale with a gap or a duplicate is not scoreable",
                it.get("_file", "")))
            continue
        blank = [c for c in crit if not (c.get("descriptor") or "").strip()]
        if blank:
            findings.append(Finding(it.get("id", "?"),
                f"{len(blank)} score point(s) have no descriptor — an unlabelled band is "
                f"scored by feel", it.get("_file", "")))
            continue
        written += 1
    return Result(name, not findings, len(items), findings, judged=len(pool),
                  note=f"{written}/{len(pool)} extended-response item(s) carry a real rubric")


def gate_bias_review(items, binding=None) -> Result:
    """Every item states where its bias and sensitivity review stands.

    Not a judgement of the content — this system cannot make one. It is the
    same discipline as historian review: `not-started` is honest and passes at
    bank level; what fails is an item that says NOTHING, because silence reads
    as "reviewed" to anyone skimming.
    """
    name = "bias-review"
    if (r := empty_scan_guard(name, items)):
        return r
    ok = {"not-started", "needs-review", "approved", "revised"}
    findings, tally = [], collections.Counter()
    judged = 0
    for it in items:
        if not itemio.servable(it):
            continue
        judged += 1
        br = it.get("biasReview")
        if not isinstance(br, dict) or not br.get("status"):
            findings.append(Finding(it.get("id", "?"),
                "no biasReview status — an item that says nothing about bias review reads as "
                "reviewed", it.get("_file", "")))
            continue
        st = br["status"]
        tally[st] += 1
        if st not in ok:
            findings.append(Finding(it.get("id", "?"),
                f"biasReview status {st!r} is not one of {sorted(ok)}", it.get("_file", "")))
        elif st == "approved" and not (br.get("reviewer") or "").strip():
            findings.append(Finding(it.get("id", "?"),
                "biasReview approved with no reviewer named — an approval nobody signed",
                it.get("_file", "")))
    if not judged:
        return Result(name, True, len(items), [], judged=0,
                      inapplicable="no item in this set carries a rubric — an assessment form "
                                   "is selected response, so there is no relocation to check")
    return Result(name, not findings, len(items), findings, judged=judged,
                  note="; ".join(f"{v} {k}" for k, v in tally.most_common()))


def gate_key_contradiction(items, binding=None) -> Result:
    """The key's own explanation must not call the key wrong.

    Found by reading one rendered teacher key: item 1 of FORM-A keys B and its
    rationale says "B is incorrect because it describes a different program".
    30 servable items do this — a migrated distractor explanation welded into
    the key rationale, pointing at whatever letter the key used to be.

    `explanation-quality` could not see it: that gate asks whether the
    explanation merely restates the DOK rationale, which is a question about
    FORM. This is a question about whether the sentence agrees with the record
    it is attached to, and it is the teacher who gets handed the contradiction.
    """
    name = "key-contradiction"
    if (r := empty_scan_guard(name, items)):
        return r
    rx = re.compile(r"\b([A-Z])\b\s+(?:is|was)\s+(?:incorrect|wrong|not correct|not right)", re.I)
    findings, judged = [], 0
    for it in items:
        if not itemio.servable(it):
            continue
        key = (it.get("correctAnswer") or "").strip()
        exp = it.get("explanation") or ""
        if not key or not exp:
            continue
        judged += 1
        for m in rx.finditer(exp):
            if m.group(1).upper() == key.upper():
                findings.append(Finding(it.get("id", "?"),
                    f"the key is {key} and its own explanation says {m.group(0)!r} — the "
                    f"teacher key contradicts the answer key", it.get("_file", "")))
                break
    return Result(name, not findings, len(items), findings, judged=judged)


AI_REVIEW_POLICY = os.path.join(itemio.BANK_ROOT, "policy", "ai-review.json")
_AI_MARKERS = re.compile(r"\b(ai|claude|gpt|llm|machine|automated|auto|bot|model)\b", re.I)


def gate_ai_review_boundary(items, binding=None) -> Result:
    """An AI review pass may recommend. It may never approve.

    Sean asked for an AI first pass so the review queue stops being one person's
    bottleneck. This is the gate that keeps that from quietly becoming an AI
    signing off on AI work — and it is enforced on the RECORDS rather than on
    the reviewer's source, because a tool can be rewritten and a policy file is
    prose until something reads it.

    Four things fail here:
      1. An aiReview that wrote into a human-review field.
      2. A human review stamp whose reviewer name reads as a machine.
      3. A recommendation with no evidence — that is an opinion, not a review.
      4. A `clear-recommended` verdict on a class the policy never declared
         clearable. The clearable list is short on purpose: the classes where
         the evidence is deterministic and already in the repo. Anything about
         history, a citation, Spanish, bias, or a rubric descriptor escalates,
         including when it looks easy.

    The reason this matters more than the queue: an approval record looks
    identical whoever wrote it. If AI clearance ever reached historianReview,
    the bank would still pass every gate and the reason a district could trust
    it would be gone, with nothing on the page to say so.
    """
    name = "ai-review-boundary"
    if (r := empty_scan_guard(name, items)):
        return r
    with open(AI_REVIEW_POLICY, encoding="utf-8") as fh:
        pol = json.load(fh)
    clearable = set(pol["clearableClasses"]) - {"$comment"}
    findings, judged, verdicts = [], 0, collections.Counter()
    for it in items:
        if not itemio.servable(it) and it.get("status") != "held":
            continue
        # The population is items carrying a review claim of EITHER kind. A set
        # with none — a form whose items nobody has reviewed yet — is N/A with a
        # reason, not NOT MEASURED: this gate scoped to a form judged zero and
        # failed all-gates-measured, which is an alarm firing on the harmless
        # for the fourth time (L49, L59, L62). "Nothing here claims review" is a
        # true and safe statement; "this was not measured" is not the same thing.
        if it.get("aiReview") or it.get("historianReview") or (
                it.get("biasReview") or {}).get("reviewer"):
            judged += 1
        # 2 — a human stamp that names a machine.
        hr = it.get("historianReview") or {}
        who = str(hr.get("reviewer") or "")
        if who and _AI_MARKERS.search(who):
            findings.append(Finding(it.get("id", "?"),
                f"historianReview names {who!r} as the reviewer — a human review record may "
                f"not name a machine", it.get("_file", "")))
        br = (it.get("biasReview") or {}).get("reviewer")
        if br and _AI_MARKERS.search(str(br)):
            findings.append(Finding(it.get("id", "?"),
                f"biasReview names {br!r} as the reviewer", it.get("_file", "")))

        ai = it.get("aiReview")
        if not ai:
            continue
        # 1 — the AI pass must have written nowhere but its own namespace.
        if ai.get("pass") and it.get("requiresHistorianReview") is False and hr:
            pass  # a human may have settled it later; that is fine and expected.
        for forbidden in ("historianReview", "tcapFormatAffirmedBy"):
            if forbidden in ai:
                findings.append(Finding(it.get("id", "?"),
                    f"aiReview carries {forbidden!r} — the AI pass wrote into a human-review "
                    f"field", it.get("_file", "")))
        if not str(ai.get("isNotAnApproval") or "").strip():
            findings.append(Finding(it.get("id", "?"),
                "aiReview does not state that it is not an approval — a review block that "
                "does not disclaim itself reads as one", it.get("_file", "")))
        for f in ai.get("findings") or []:
            v = f.get("verdict")
            verdicts[v] += 1
            # 3 — no evidence, no verdict.
            if not (f.get("evidence") or []):
                findings.append(Finding(it.get("id", "?"),
                    f"aiReview verdict {v!r} carries no evidence — a verdict with no evidence "
                    f"is an opinion", it.get("_file", "")))
            if v == "escalate" and not (f.get("cannotVerify") or []):
                findings.append(Finding(it.get("id", "?"),
                    "an escalation states nothing it could not verify — a reviewer that never "
                    "says 'I don't know' is not reviewing", it.get("_file", "")))
            # 4 — clearing only what the policy declared clearable.
            if v == "clear-recommended" and f.get("class") not in clearable:
                findings.append(Finding(it.get("id", "?"),
                    f"aiReview recommends clearing class {f.get('class')!r}, which the policy "
                    f"never declared clearable ({', '.join(sorted(clearable))})",
                    it.get("_file", "")))
    if not judged:
        return Result(name, True, len(items), [], judged=0,
                      inapplicable="no item in this set carries a review claim of either "
                                   "kind, so there is no review boundary to cross here")
    return Result(name, not findings, len(items), findings, judged=judged,
                  note=("; ".join(f"{v} {k}" for k, v in verdicts.most_common())
                        + " — recommendations only; none of this counts toward Grade A"
                        if verdicts else f"{judged} human review claim(s), no AI pass stamped"))


def gate_review_debt(items, binding=None) -> Result:
    """A structural operation may not manufacture a review obligation.

    Extracting 79 scoring guides out of the `explanation` field and into a
    structured `rubric` field stamped every one of them `needs-review`. None of
    that content was new — it was migrated bank text moving fields unchanged,
    and the extraction gate already proves the move was faithful. The effect was
    to put 79 rows on the only reviewer this project has that were never his to
    read, and to inflate his queue from 40 to 119.

    Review debt is the scarcest resource here. A queue padded with work nobody
    needed to do is not a neutral error: it buries the ten items that genuinely
    need a person, and it teaches whoever is reading to skim.

    So: `needs-review` on a component is a claim that something was AUTHORED.
    Relocated content inherits the item's status and says so.
    """
    name = "review-debt"
    if (r := empty_scan_guard(name, items)):
        return r
    findings, judged = [], 0
    tally = collections.Counter()
    for it in items:
        rub = it.get("rubric")
        if not isinstance(rub, dict) or not rub.get("status"):
            continue
        judged += 1
        st, rs = rub.get("status"), rub.get("reviewStatus")
        tally[f"{st}/{rs}"] += 1
        if rs == "needs-review" and st != "authored":
            findings.append(Finding(it.get("id", "?"),
                f"rubric is {st!r} but flagged needs-review — a relocation is not authoring, "
                f"and marking it for review spends a reviewer's attention on work nobody did",
                it.get("_file", "")))
        if st == "extracted" and not rub.get("extractionVerified"):
            findings.append(Finding(it.get("id", "?"),
                "rubric claims to be extracted but does not record that the extraction was "
                "verified — 'moved from somewhere' is not evidence that it moved intact",
                it.get("_file", "")))
        if st == "authored" and rs != "needs-review" and not it.get("requiresHistorianReview"):
            findings.append(Finding(it.get("id", "?"),
                "rubric was AUTHORED but claims no review is needed — authored pedagogical "
                "claims are never silently settled", it.get("_file", "")))
    if not judged:
        return Result(name, True, len(items), [], judged=0,
                      inapplicable="no item in this set carries a rubric — an assessment form "
                                   "is selected response, so there is no relocation to check")
    return Result(name, not findings, len(items), findings, judged=judged,
                  note="; ".join(f"{v} {k}" for k, v in tally.most_common()))


TAXONOMY = os.path.join(itemio.BANK_ROOT, "taxonomy", "misconception-families.json")


def _families():
    if not os.path.exists(TAXONOMY):
        return {}
    with open(TAXONOMY, encoding="utf-8") as fh:
        return {f["id"]: f for f in json.load(fh).get("families", [])}


def gate_misconception_taxonomy(items, binding=None) -> Result:
    """A distractor's misconception must resolve to a taxonomy ID.

    This is the gate the whole analytics layer rests on. 66 misconceptions
    existed in this bank and all 66 were DISTINCT FREE-TEXT SENTENCES — "assumes
    excavation was manual", "assigns the canal to the preceding administration".
    Two items teaching the same confusion carried two different sentences, so
    nothing could count them together, and a remediation report that cannot
    aggregate is a list of anecdotes.

    A family ID recurs across items, standards AND courses. That is what lets a
    report say "this student reverses cause and effect" — a transferable finding
    — instead of "this student missed US.34". Free text stays as the human-
    readable statement; the ID is what the analytics read.

    Legacy items are NOT failed for lacking a misconception: 3,771 of them were
    migrated before this existed and that is a stated gap, not a defect in the
    gate. What fails is a misconception that CLAIMS a family the taxonomy does
    not define, or an item authored after the taxonomy that names none.
    """
    name = "misconception-taxonomy"
    if (r := empty_scan_guard(name, items)):
        return r
    fams = _families()
    if not fams:
        return Result(name, False, len(items), [Finding("(taxonomy)",
            "no misconception families defined — the analytics layer has nothing to aggregate "
            "on and every misconception is an anecdote", TAXONOMY)], judged=0)
    findings, judged, cited = [], 0, collections.Counter()
    for it in items:
        if not itemio.servable(it) or it.get("itemType") not in ("mcq", "multiple-select"):
            continue
        authored = (it.get("provenance") or {}).get("authoring") or it.get("aiGenerated")
        for ch in itemio.choices(it):
            if not isinstance(ch, dict) or ch.get("id") == it.get("correctAnswer"):
                continue
            fam, txt = ch.get("misconceptionFamily"), (ch.get("misconception") or "").strip()
            if not fam and not txt:
                if authored:
                    judged += 1
                    findings.append(Finding(it.get("id", "?"),
                        f"distractor {ch.get('id')} was authored with no misconception — a "
                        f"distractor written to be merely wrong is noise, not diagnosis",
                        it.get("_file", "")))
                continue
            judged += 1
            if not fam:
                findings.append(Finding(it.get("id", "?"),
                    f"distractor {ch.get('id')} names a misconception in free text but cites no "
                    f"family — free text cannot aggregate, so this diagnoses one student on one "
                    f"item and nothing else", it.get("_file", "")))
                continue
            if fam not in fams:
                findings.append(Finding(it.get("id", "?"),
                    f"distractor {ch.get('id')} cites family {fam!r}, which the taxonomy does "
                    f"not define ({len(fams)} defined)", it.get("_file", "")))
                continue
            cited[fam] += 1
    return Result(name, not findings, len(items), findings, judged=judged,
                  note=(f"{len(cited)}/{len(fams)} family(ies) cited; "
                        f"{sum(cited.values())} distractor(s) resolve to one"
                        if cited else f"{len(fams)} family(ies) defined, none cited yet"))
