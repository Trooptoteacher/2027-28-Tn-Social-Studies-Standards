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
    return " ".join([item.get("stem") or "", item.get("explanation") or ""]
                    + [c.get("text") or "" for c in itemio.choices(item)]).lower()


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
        sigsets = {c: alignment.standard_signals(stds[c]["text"]) for c in codes}
        if not any(sigsets.values()):
            continue
        judged += 1
        if it.get("id") in allow:
            continue
        hay = _haystack(it)
        if not any(sig.lower() in hay for sigs in sigsets.values() for sig in sigs):
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
        if share > chance + TOLERANCE:
            findings.append(Finding(f"{k}-choice cohort",
                f"the key is the longest option in {hits}/{total} items ({share:.1%}) "
                f"against {chance:.0%} by chance — a student can beat this bank without "
                f"reading the stems"))
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
