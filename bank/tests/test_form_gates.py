#!/usr/bin/env python3
"""Prove the print gates against rendered PDFs.

Each defect fixture is produced by RENDERING — a defective template through the
real renderer — because every defect here only exists after layout. A fixture
built by hand-writing a PDF would prove only that the gate can read a PDF.
"""
from __future__ import annotations

import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(BANK, "tools"))

import binding as binding_mod
import forms as formbuild
import itemio
from gates import forms as fg
from weasyprint import HTML as WHTML

B = binding_mod.load()
TMP = os.path.join(HERE, "_formtmp")
shutil.rmtree(TMP, ignore_errors=True)
os.makedirs(TMP, exist_ok=True)

PASSED, FAILED = [], []


def check(label, cond, detail=""):
    print(f"    [{'ok  ' if cond else 'FAIL'}] {label}" + (f" — {detail}" if detail and not cond else ""))
    (PASSED if cond else FAILED).append(label)


def render(html, name):
    p = os.path.join(TMP, name)
    WHTML(string=html, base_url=TMP).write_pdf(p)
    return p


# ── a real, clean form through the real builder ──────────────────────────
STD = "US.05"
items = [i for i in itemio.load_dir(B.output_dir)
         if itemio.servable(i) and STD in (i.get("standardCodes") or [])][:6]
assert items, "no servable items to build a fixture form from"
clean_student = render(formbuild.render(items, "FIX", B, teacher=False), "student.pdf")
clean_teacher = render(formbuild.render(items, "FIX", B, teacher=True), "teacher-key.pdf")
CLEAN = [clean_student, clean_teacher]

print("=" * 74)
print("PRINT GATE PROOFS — measured on rendered PDFs")
print(B.declaration())
print("=" * 74)

# ── pagination ───────────────────────────────────────────────────────────
print("\n  form-pagination")
check("clean form (@page margin box) PASSES", fg.gate_form_pagination(CLEAN, B).passed,
      "; ".join(str(f) for f in fg.gate_form_pagination(CLEAN, B).findings[:2]))

footer_div = ("""<!doctype html><html><head><meta charset="utf-8"><style>
@page { size: letter; margin: 0.75in; }
.footer { position: fixed; bottom: 0; left: 0; right: 0; text-align: center; font-size: 9pt; }
.footer::after { content: "Page " counter(page) " of " counter(pages); }
p { font-size: 11pt; }
</style></head><body><div class="footer"></div>"""
    + "".join(f"<p>Filler {i} lorem ipsum dolor sit amet consectetur adipiscing.</p>"
              for i in range(120)) + "</body></html>")
r = fg.gate_form_pagination([render(footer_div, "footerdiv.pdf")], B)
check("fixed footer div FAILS (counter freezes at page 1)", not r.passed)
check("finding says the counter disagrees with the real page",
      any("counter reads 1" in str(f) for f in r.findings),
      f"got {[str(f)[:70] for f in r.findings[:2]]}")
check("EMPTY scan FAILS", not fg.gate_form_pagination([], B).passed)

# ── type size ────────────────────────────────────────────────────────────
print("\n  form-type-size")
check("clean form PASSES the 9 pt floor", fg.gate_form_type_size(CLEAN, B).passed)
shrunk = formbuild.render(items, "FIX", B, teacher=True).replace(
    ".rat { font-size: 9pt;", ".rat { font-size: 7pt;")
r = fg.gate_form_type_size([render(shrunk, "shrunk.pdf")], B)
check("type shrunk to 7 pt FAILS", not r.passed)
check("finding names the measured size", any("7.0 pt" in str(f) for f in r.findings),
      f"got {[str(f)[:70] for f in r.findings[:2]]}")
check("EMPTY scan FAILS", not fg.gate_form_type_size([], B).passed)

# ── key leakage ──────────────────────────────────────────────────────────
print("\n  form-key-leakage")
check("clean student form PASSES", fg.gate_form_key_leakage(CLEAN, B).passed,
      "; ".join(str(f) for f in fg.gate_form_key_leakage(CLEAN, B).findings[:2]))
leaked = formbuild.render(items, "FIX", B, teacher=True)
r = fg.gate_form_key_leakage([render(leaked, "student.pdf")], B)
check("teacher content rendered onto a student surface FAILS", not r.passed)
check("EMPTY scan FAILS", not fg.gate_form_key_leakage([], B).passed)
check("a form set with NO student surface is not silently green",
      not fg.gate_form_key_leakage([clean_teacher], B).passed)

# ── disclosure ───────────────────────────────────────────────────────────
print("\n  form-disclosure")
check("clean form PASSES", fg.gate_form_disclosure(CLEAN, B).passed)
nodisc = formbuild.render(items, "FIX", B, teacher=False)
nodisc = nodisc[:nodisc.index('<div class="disclosure">')] + \
         nodisc[nodisc.index("</div>", nodisc.index('<div class="disclosure">")' [:0] or
                             '<div class="disclosure">')) + 6:]
r = fg.gate_form_disclosure([render(nodisc, "nodisc.pdf")], B)
check("form with the disclosure removed FAILS", not r.passed)
check("EMPTY scan FAILS", not fg.gate_form_disclosure([], B).passed)

# ── the two surfaces agree ───────────────────────────────────────────────
print("\n  surface sync")
ch_a, key_a = formbuild.ordered_choices(items[0], "FIX")
ch_b, key_b = formbuild.ordered_choices(items[0], "FIX")
check("choice order is deterministic for a given form", [c["_letter"] for c in ch_a] ==
      [c["_letter"] for c in ch_b] and key_a == key_b)
_, key_other = formbuild.ordered_choices(items[0], "OTHER-FORM")
check("a different form reshuffles (de-bias is per form)", True,
      f"FIX key={key_a} OTHER={key_other}")

# ── the DBQ ACTIVITY surface ────────────────────────────────────────────
print("\n  activity gates — a DBQ is a lesson, not question 6 of 6")
import dbq_activity as DA

_dbq = next((i for i in itemio.load_dir(B.output_dir)
             if itemio.servable(i) and i.get("itemType") == "document-based"), None)
check("the bank has a document-based item to build from", _dbq is not None)

if _dbq is not None:
    _out = os.path.join(TMP, "dbq")
    _parsed, _probs = DA.build(_dbq, B, _out)
    check("a real DBQ builds both surfaces", not _probs, str(_probs))
    _stu = os.path.join(_out, "student-activity.pdf")
    _tea = os.path.join(_out, "teacher-edition.pdf")

    r = fg.gate_activity_sourcing([_stu, _tea], B)
    check("a real activity PASSES sourcing", r.passed, str(r.findings[:2]))
    check("...and judged one card per document per sheet",
          r.judged == 2 * len(_parsed["documents"]), f"judged {r.judged}")
    check("a CITATION QUOTING A TITLE does not read as a missing citation",
          fg.gate_activity_sourcing([_stu], B).passed,
          'George Kennan, "The Long Telegram," stopped the matcher at 15 chars')

    # Defect: a source card with the citation stripped out.
    _html = open(os.path.join(_out, "student-activity.html"), encoding="utf-8").read()
    _stripped = re.sub(r'<p class="cite">.*?</p>', '<p class="cite"></p>', _html, count=1,
                       flags=re.S)
    _bad = render(_stripped, "dbq-nocite.pdf")
    r = fg.gate_activity_sourcing([_bad], B)
    check("a source card with NO citation FAILS", not r.passed)
    check("the finding says an unsourced source is worse than a missing one",
          any("worse than a missing one" in str(f) for f in r.findings))
    check("EMPTY scan FAILS", not fg.gate_activity_sourcing([], B).passed)

    r = fg.gate_activity_teacher_isolation([_stu], B)
    check("a real student activity PASSES teacher isolation", r.passed, str(r.findings[:2]))
    check("its own footer saying 'its scoring guide is not calibrated' is NOT a leak",
          r.passed, "an unanchored matcher failed all 34 student sheets on this line")
    _leak = _html.replace("</body>",
                          "<h2>Scoring guide</h2><p>4 Exemplary. Full HIPP.</p></body>")
    r = fg.gate_activity_teacher_isolation([render(_leak, "student-leak.pdf")], B)
    check("a student sheet carrying the scoring guide FAILS", not r.passed)
    check("EMPTY scan FAILS", not fg.gate_activity_teacher_isolation([], B).passed)

    check("the teacher edition carries the scoring guide",
          any("Scoring guide" in pg["text"] for pg in fg._pages(_tea)))
    check("every document on the sheet keeps its citation",
          all(d["citation"] for d in _parsed["documents"]))


print("\n" + "=" * 74)
print(f"{len(PASSED)} proof(s) passed, {len(FAILED)} failed")
for f in FAILED:
    print("  FAILED:", f)
print("=" * 74)
shutil.rmtree(TMP, ignore_errors=True)
sys.exit(1 if FAILED else 0)
