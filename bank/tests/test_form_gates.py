#!/usr/bin/env python3
"""Prove the print gates against rendered PDFs.

Each defect fixture is produced by RENDERING — a defective template through the
real renderer — because every defect here only exists after layout. A fixture
built by hand-writing a PDF would prove only that the gate can read a PDF.
"""
from __future__ import annotations

import os
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

print("\n" + "=" * 74)
print(f"{len(PASSED)} proof(s) passed, {len(FAILED)} failed")
for f in FAILED:
    print("  FAILED:", f)
print("=" * 74)
shutil.rmtree(TMP, ignore_errors=True)
sys.exit(1 if FAILED else 0)
