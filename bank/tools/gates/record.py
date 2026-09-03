"""Per-record gates: schema completeness, binding, key integrity, distractors, truncation."""
from __future__ import annotations

import re
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import itemio
from gates import Finding, Result, empty_scan_guard


# --------------------------------------------------------------- schema
def gate_record_complete(items, binding=None) -> Result:
    """Every required field present. A gate fails a missing one."""
    name = "record-complete"
    if (r := empty_scan_guard(name, items)):
        return r
    req = itemio.required_fields()
    findings = []
    for it in items:
        missing = [f for f in req if it.get(f) in (None, "", [], {})]
        # reportingCategory is allowed to be null ONLY while its source says UNMAPPED;
        # that is a tracked gap, not a silently absent field.
        if "reportingCategory" in missing and it.get("reportingCategorySource") == "UNMAPPED":
            missing.remove("reportingCategory")
        # constructed-response items legitimately carry no choices
        if itemio.is_single_select(it) and not itemio.choices(it):
            missing.append("choices")
        if "correctAnswer" in missing and not itemio.is_single_select(it):
            missing.remove("correctAnswer")
        if missing:
            findings.append(Finding(it.get("id", "?"), f"missing {sorted(set(missing))}", it.get("_file", "")))
    return Result(name, not findings, len(items), findings)


# -------------------------------------------------------------- binding
def gate_binding(items, binding=None) -> Result:
    """No standard code outside the declared course, and no superseded year.

    This is the artifact-side twin of the build-time assertion. The generator
    asserts before it writes; this asserts after, on what actually landed.
    """
    name = "binding"
    if (r := empty_scan_guard(name, items)):
        return r
    findings = []
    valid = binding.valid_codes()
    for it in items:
        for code in (it.get("standardCodes") or []):
            if not binding.code_re.match(str(code)):
                findings.append(Finding(it.get("id", "?"),
                    f"standard code {code!r} is outside declared prefix {binding.prefix!r}",
                    it.get("_file", "")))
            elif code not in valid:
                findings.append(Finding(it.get("id", "?"),
                    f"standard code {code!r} matches the prefix but is not defined in the "
                    f"declared standards file", it.get("_file", "")))
        yr = it.get("standardsYear")
        if yr != binding.standards_year:
            findings.append(Finding(it.get("id", "?"),
                f"standardsYear {yr!r} != declared {binding.standards_year!r}"
                + (" (SUPERSEDED — 84 of 94 US codes changed meaning)"
                   if yr in binding.forbidden_years else ""),
                it.get("_file", "")))
    return Result(name, not findings, len(items), findings)


# --------------------------------------------------------- key integrity
def gate_key_integrity(items, binding=None) -> Result:
    """correctAnswer names a choice id that exists; exactly one key per
    single-select item; no orphan or duplicate choice ids."""
    name = "key-integrity"
    if (r := empty_scan_guard(name, items)):
        return r
    findings = []
    for it in items:
        ch = itemio.choices(it)
        ids = [c.get("id") for c in ch if isinstance(c, dict)]
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            findings.append(Finding(it.get("id", "?"), f"duplicate choice id(s) {sorted(dupes)}", it.get("_file", "")))
        if any(i in (None, "") for i in ids):
            findings.append(Finding(it.get("id", "?"), "choice with empty/missing id", it.get("_file", "")))
        if not itemio.is_single_select(it):
            continue
        key = it.get("correctAnswer")
        if isinstance(key, list):
            findings.append(Finding(it.get("id", "?"),
                f"single-select item has {len(key)} keys; exactly one required", it.get("_file", "")))
            continue
        if key not in ids:
            findings.append(Finding(it.get("id", "?"),
                f"correctAnswer {key!r} names no existing choice id (have {ids})", it.get("_file", "")))
    return Result(name, not findings, len(items), findings)


# ---------------------------------------------------- distractor coverage
def gate_distractor_coverage(items, binding=None) -> Result:
    """Every wrong choice has its own explanation, and no two distractors on an
    item name the same misconception.

    Distractors written to be merely wrong are noise; distractors written to
    diagnose are the reason a bank is worth building. Nothing else in the
    record does this job.
    """
    name = "distractor-coverage"
    if (r := empty_scan_guard(name, items)):
        return r
    findings, judged = [], 0
    for it in items:
        if not itemio.is_single_select(it):
            continue
        judged += 1
        key = it.get("correctAnswer")
        seen = {}
        for c in itemio.choices(it):
            if not isinstance(c, dict) or c.get("id") == key:
                continue
            cid = c.get("id")
            if not (c.get("explanation") or "").strip():
                findings.append(Finding(it.get("id", "?"),
                    f"distractor {cid!r} has no explanation", it.get("_file", "")))
            mis = (c.get("misconception") or "").strip().lower()
            if not mis:
                findings.append(Finding(it.get("id", "?"),
                    f"distractor {cid!r} names no misconception", it.get("_file", "")))
            elif mis in seen:
                findings.append(Finding(it.get("id", "?"),
                    f"distractors {seen[mis]!r} and {cid!r} name the same misconception "
                    f"({mis!r}) — one of them diagnoses nothing", it.get("_file", "")))
            else:
                seen[mis] = cid
    return Result(name, not findings, len(items), findings, judged=judged)


# ------------------------------------------------------------ truncation
# A TCAP-style completion stem legitimately ends in an em dash:
#   "Reagan's challenge to Gorbachev was directed at the wall dividing —"
# That is not truncation. Real truncation ends on a comma, a conjunction, or
# simply stops. Bulk edits and translation passes both truncate silently.
_TERMINAL = tuple(".!?…;\"'")
# A stem may legitimately END on a colon or a dash and let the choices finish the
# sentence: "…connected Omaha, Nebraska to:" / "…the wall dividing —". That is a
# completion stem, not truncation. An EXPLANATION ending the same way is truncated.
_COMPLETION_TAIL = ("—", "–", "-", ":")
_CLOSERS = tuple(")]}»”’")
_DANGLING = {"and", "or", "but", "the", "a", "an", "of", "to", "in", "for", "with",
             "that", "which", "because", "including", "such", "as", "by", "from"}


def _truncated(text: str, allow_dash: bool) -> str:
    t = (text or "").strip()
    if not t:
        return "empty"
    if allow_dash and t.endswith(_COMPLETION_TAIL):
        return ""
    if t.endswith(","):
        return "ends on a comma"
    # Strip trailing PUNCTUATION only. Stripping digits too turned
    # "…the Homestead Act of 1862?" into "…Act of" and flagged a complete stem.
    last = re.sub(r"[^A-Za-z0-9']+$", "", t).split()
    if last and last[-1].lower() in _DANGLING:
        return f"ends on dangling {last[-1]!r}"
    if not t.endswith(_TERMINAL + _CLOSERS):
        # a choice may be a bare noun phrase; a stem or explanation may not
        return "no terminal punctuation"
    return ""


def gate_truncation(items, binding=None) -> Result:
    """No stem, choice or explanation ends mid-sentence."""
    name = "truncation"
    if (r := empty_scan_guard(name, items)):
        return r
    findings = []
    for it in items:
        for field, allow_dash, strict in (("stem", True, True), ("stemEs", True, True),
                                          ("explanation", False, True), ("explanationEs", False, True),
                                          ("dokRationale", False, True)):
            val = it.get(field)
            if val in (None, ""):
                continue
            why = _truncated(val, allow_dash)
            if why:
                findings.append(Finding(it.get("id", "?"), f"{field} {why}: …{str(val)[-45:]!r}", it.get("_file", "")))
        for c in itemio.choices(it):
            if not isinstance(c, dict):
                continue
            for field in ("text", "textEs", "explanation"):
                val = c.get(field)
                if val in (None, ""):
                    continue
                t = str(val).strip()
                why = ""
                if t.endswith(","):
                    why = "ends on a comma"
                else:
                    last = re.sub(r"[^A-Za-z0-9']+$", "", t).split()
                    if last and last[-1].lower() in _DANGLING:
                        why = f"ends on dangling {last[-1]!r}"
                    elif field == "explanation" and not t.endswith(_TERMINAL + _CLOSERS):
                        why = "no terminal punctuation"
                if why:
                    findings.append(Finding(it.get("id", "?"),
                        f"choice {c.get('id')!r} {field} {why}: …{t[-40:]!r}", it.get("_file", "")))
    return Result(name, not findings, len(items), findings)
