"""Print gates. These read the RENDERED PDF.

The template says what was asked for; the PDF says what comes out of the
printer. Every check here is written against a defect that only appears after
rendering — a page counter that never resolved, type that shrank to fit, key
material that survived onto the student copy.
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gates import Finding, Result, empty_scan_guard

PRINT_FLOOR_PT = 9.0
# Citations and the page-margin furniture are allowed at the floor exactly.
_TOL = 0.05


def _pages(pdf_path):
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LTChar, LTTextContainer
    out = []
    for page in extract_pages(pdf_path):
        chars = []
        for el in page:
            if isinstance(el, LTTextContainer):
                for line in el:
                    for ch in getattr(line, "__iter__", lambda: [])():
                        if isinstance(ch, LTChar):
                            chars.append(ch)
        text = "".join(
            el.get_text() for el in page if isinstance(el, LTTextContainer))
        out.append({"text": text, "chars": chars})
    return out


def gate_form_pagination(pdfs, binding=None) -> Result:
    """Every page carries "Page N of M", N runs 1..M, and M equals the real
    page count.

    A fixed footer div prints the counter through the footer text: the literal
    string "counter(page)" appears, or every page reads "Page 1 of 1". Only the
    rendered PDF shows it.
    """
    name = "form-pagination"
    if (r := empty_scan_guard(name, pdfs)):
        return r
    findings, judged = [], 0
    for path in pdfs:
        pages = _pages(path)
        if not pages:
            findings.append(Finding(os.path.basename(path), "rendered 0 pages"))
            continue
        total = len(pages)
        for n, pg in enumerate(pages, 1):
            judged += 1
            m = re.search(r"Page\s+(\d+)\s+of\s+(\d+)", pg["text"])
            if not m:
                if "counter(" in pg["text"]:
                    findings.append(Finding(f"{os.path.basename(path)} p{n}",
                        "footer printed the literal counter() expression — the page "
                        "number never resolved (a fixed div, not an @page margin box)"))
                else:
                    findings.append(Finding(f"{os.path.basename(path)} p{n}",
                        "no 'Page N of M' on this page"))
                continue
            got_n, got_m = int(m.group(1)), int(m.group(2))
            if got_n != n:
                findings.append(Finding(f"{os.path.basename(path)} p{n}",
                    f"page counter reads {got_n}, should be {n}"))
            if got_m != total:
                findings.append(Finding(f"{os.path.basename(path)} p{n}",
                    f"'of {got_m}' disagrees with the real page count {total}"))
    return Result(name, not findings, len(pdfs), findings, judged=judged,
                  note=f"{judged} rendered page(s) checked")


def gate_form_type_size(pdfs, binding=None) -> Result:
    """Nothing on a printed page falls below the 9 pt floor.

    Measured glyph by glyph in the PDF. CSS says what was asked for; a shrink
    applied to save a page shows up only here. Readability over page-fit —
    the fix for a long form is another page.
    """
    name = "form-type-size"
    if (r := empty_scan_guard(name, pdfs)):
        return r
    findings, judged = [], 0
    for path in pdfs:
        under = {}
        for n, pg in enumerate(_pages(path), 1):
            for ch in pg["chars"]:
                judged += 1
                size = round(ch.size, 2)
                if size < PRINT_FLOOR_PT - _TOL and ch.get_text().strip():
                    under.setdefault((n, size), 0)
                    under[(n, size)] += 1
        for (n, size), count in sorted(under.items()):
            findings.append(Finding(f"{os.path.basename(path)} p{n}",
                f"{count} character(s) set at {size} pt, below the {PRINT_FLOOR_PT} pt floor"))
    return Result(name, not findings, len(pdfs), findings, judged=judged,
                  note=f"{judged} glyph(s) measured")


_KEY_MARKERS = [
    (re.compile(r"\bKEY\s*:", re.I), "an answer key marker"),
    (re.compile(r"why the key is right", re.I), "a key rationale"),
    (re.compile(r"\bTEACHER COPY\b", re.I), "the teacher-copy band"),
    (re.compile(r"\bcorrect answer\b", re.I), "an explicit correct-answer label"),
    (re.compile(r"\breteach\b", re.I), "reteach guidance"),
    (re.compile(r"\bDOK\s*[1-4]\b"), "a DOK label"),
]


def gate_form_key_leakage(pdfs, binding=None) -> Result:
    """No key material on a student PDF.

    Enforced on the rendered artifact, because hiding a link leaves the file
    one request away and hiding a div leaves the text in the PDF.
    """
    name = "form-key-leakage"
    student = [p for p in pdfs if os.path.basename(p).startswith("student")]
    if (r := empty_scan_guard(name, student)):
        return r
    findings, judged = [], 0
    for path in student:
        for n, pg in enumerate(_pages(path), 1):
            judged += 1
            for rx, what in _KEY_MARKERS:
                if rx.search(pg["text"]):
                    findings.append(Finding(f"{os.path.basename(path)} p{n}",
                        f"student form carries {what}"))
    return Result(name, not findings, len(student), findings, judged=judged,
                  note=f"{judged} student page(s) checked")


def gate_form_disclosure(pdfs, binding=None) -> Result:
    """Every surface that shows an item discloses its calibration status."""
    name = "form-disclosure"
    if (r := empty_scan_guard(name, pdfs)):
        return r
    want = (binding.disclosure_line or "").replace("·", "").split()
    findings, judged = [], 0
    for path in pdfs:
        pages = _pages(path)
        judged += 1
        head = pages[0]["text"] if pages else ""
        norm = re.sub(r"\s+", " ", head)
        if not all(w in norm for w in want if len(w) > 3):
            findings.append(Finding(os.path.basename(path),
                f"first page does not carry the disclosure {binding.disclosure_line!r} — "
                f"parameters that have never met a student are estimates"))
    return Result(name, not findings, len(pdfs), findings, judged=judged)


_KEY_LINE = re.compile(r"KEY:\s*([A-H])")
_CALLS_WRONG = re.compile(
    r"\b(?:Choice|Option|Answer)\s+([A-H])\b\s*(?:is|was)?\s*"
    r"(?:incorrect|wrong|not correct)|"
    r"\b([A-H])\s+(?:is|was)\s+(?:incorrect|wrong|not correct)", re.I)


def gate_form_key_contradiction(pdfs, binding=None) -> Result:
    """On the printed key, the letter named as the key is never called wrong.

    This is the defect Sean found by reading FORM-A. Item 1 printed
    "KEY: B" and, two lines down, "B is incorrect because it describes a
    different program". The bank record keyed C and was perfectly
    self-consistent: the FORM re-letters choices to de-bias key position, and
    2,440 of 3,928 servable items hard-code a choice letter inside their
    explanation, so the sentence pointed at whatever the letter used to mean.

    Every gate that could have caught it was measuring the RECORD. This one
    reads the rendered teacher PDF, per item block, which is the surface the
    teacher is actually holding — and it is why the remap in forms.py is not
    trusted to be correct just because it was written.
    """
    name = "form-key-contradiction"
    teacher = [p for p in pdfs if "teacher" in os.path.basename(p)]
    if (r := empty_scan_guard(name, teacher)):
        return r
    findings, judged = [], 0
    for path in teacher:
        text = "\n".join(pg["text"] for pg in _pages(path))
        # Split on the KEY line so each block carries exactly one key.
        parts = _KEY_LINE.split(text)
        # parts = [before, letter, block, letter, block, ...]
        for i in range(1, len(parts) - 1, 2):
            key, block = parts[i].upper(), parts[i + 1]
            judged += 1
            for m in _CALLS_WRONG.finditer(block):
                named = (m.group(1) or m.group(2) or "").upper()
                if named == key:
                    findings.append(Finding(
                        f"{os.path.basename(path)} KEY:{key}",
                        f"the printed key is {key} and the same item's rationale says "
                        f"{m.group(0).strip()!r} — the teacher key contradicts the answer key"))
                    break
    return Result(name, not findings, len(teacher), findings, judged=judged,
                  note=f"{judged} keyed item block(s) read on the rendered teacher PDF")


_ANALYSIS_ROWS = ("Item analysis", "DOK / Hess", "Reporting category", "IRT",
                  "Bias / sensitivity", "Citation", "Distractor diagnosis",
                  "Historian review", "Format")


def gate_form_teacher_metadata(pdfs, binding=None) -> Result:
    """The teacher key carries the metadata a teacher needs to judge the item.

    Sean, first read of FORM-A: the selected-response items "lack the required
    standards, DOK/Hess, distractor, bias, citation, and IRT metadata in the
    supplied form." All of it existed in the records; the printed key showed
    "KEY: B · DOK 1 · US.46" and nothing else. A field present in a record and
    absent from the page is, to the person holding the page, not present.

    Measured on the rendered PDF and per keyed item, so an analysis block that
    renders for the first item and silently stops — the exact way a template
    bug hides — fails rather than passing on one sighting.
    """
    name = "form-teacher-metadata"
    teacher = [p for p in pdfs if "teacher" in os.path.basename(p)]
    if (r := empty_scan_guard(name, teacher)):
        return r
    findings, judged = [], 0
    for path in teacher:
        text = "\n".join(pg["text"] for pg in _pages(path))
        blocks = _KEY_LINE.split(text)
        n_keys = (len(blocks) - 1) // 2
        if not n_keys:
            findings.append(Finding(os.path.basename(path),
                "no keyed item block found on the teacher PDF — nothing was measured"))
            continue
        for row in _ANALYSIS_ROWS:
            seen = text.count(row)
            judged += 1
            if seen < n_keys:
                findings.append(Finding(os.path.basename(path),
                    f"'{row}' appears on {seen} of {n_keys} keyed item(s) — the analysis "
                    f"block is missing from {n_keys - seen} of them"))
    return Result(name, not findings, len(teacher), findings, judged=judged,
                  note=f"{len(_ANALYSIS_ROWS)} required row(s) checked per teacher PDF")
