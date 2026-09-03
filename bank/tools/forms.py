#!/usr/bin/env python3
"""Assemble a test form from the bank and render it to PDF.

TWO SURFACES, ONE ASSEMBLY. The student form and the teacher key are rendered
from the same selected item list with the same choice ordering, so a key
position can never drift between them. Answer keys, rationales and reteach
guidance appear on the teacher surface ONLY, and the student surface is built
by omission at assembly time — not by hiding anything at render time.

Page numbering goes in the @page margin box. A fixed footer div silently
prints the counter through the footer text, which is why the gate measures the
RENDERED PDF rather than the template.

Usage: python3 tools/forms.py <form-id> --standards US.05 US.15 [--seed 7]
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import binding as binding_mod
import itemio

FORMS_DIR = os.path.join(itemio.BANK_ROOT, "forms")

# 9 pt print floor. Nothing on a student-facing page is set below this, and the
# rendered PDF is measured to prove it — readability over page-fit, always.
CSS = """
@page {
  size: letter;
  margin: 0.75in 0.75in 0.9in 0.75in;
  /* The page counter resolves ONLY inside a margin box. A fixed footer div
     prints the literal text instead, which is the defect this guards. */
  @bottom-center {
    content: "Page " counter(page) " of " counter(pages);
    font-family: Georgia, "Times New Roman", serif;
    font-size: 9pt;
    color: #000;
  }
  @bottom-right { content: "%(formid)s"; font-size: 9pt; color: #000; }
}
body { font-family: Georgia, "Times New Roman", serif; font-size: 11pt;
       line-height: 1.45; color: #000; background: #fff; }
h1 { font-size: 16pt; margin: 0 0 2pt; }
.sub { font-size: 10pt; margin: 0 0 14pt; }
.disclosure { font-size: 9pt; border: 1pt solid #000; padding: 6pt 8pt;
              margin: 0 0 16pt; }
.item { margin: 0 0 16pt; page-break-inside: avoid; }
.stem { font-size: 11pt; margin: 0 0 6pt; }
.num { font-weight: bold; }
ol.choices { list-style: none; margin: 0; padding: 0 0 0 18pt; }
ol.choices li { font-size: 11pt; margin: 0 0 3pt; }
/* The letter is the answer identity — never colour alone, and it survives
   grayscale because it is a glyph, not a swatch. */
.cid { font-weight: bold; }
.meta { font-size: 9pt; margin: 4pt 0 0; }
.key { font-weight: bold; }
.rat { font-size: 9pt; margin: 2pt 0 0 18pt; }
.teacher-band { font-size: 10pt; border: 1pt solid #000; padding: 4pt 8pt;
                margin: 0 0 14pt; font-weight: bold; }
"""

HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>%(title)s</title><style>%(css)s</style></head><body>
<h1>%(title)s</h1>
<p class="sub">%(course)s &middot; Tennessee Academic Standards %(year)s &middot; Form %(formid)s</p>
%(band)s
<div class="disclosure">%(disclosure)s</div>
%(items)s
</body></html>"""


def ordered_choices(item, form_id):
    """Deterministic per-item choice order, shared by BOTH surfaces.

    Seeded from the item id and the form id so the same item on the same form
    always renders identically, and the teacher key can never disagree with the
    student form about which letter is the key.
    """
    ch = [c for c in itemio.choices(item) if isinstance(c, dict)]
    if not ch:
        return [], None
    seed = int(hashlib.sha256(f"{form_id}:{item['id']}".encode()).hexdigest()[:8], 16)
    order = list(ch)
    random.Random(seed).shuffle(order)
    letters = "ABCDEFGH"
    out, key_letter = [], None
    for i, c in enumerate(order):
        letter = letters[i]
        if c.get("id") == item.get("correctAnswer"):
            key_letter = letter
        out.append({**c, "_letter": letter})
    return out, key_letter


def select(items, standards, blueprint):
    """Servable items for the named standards, per the blueprint's counts.

    Never a wildcard: the caller names the standards actually authored.
    """
    by_std = collections.defaultdict(list)
    for it in items:
        if not itemio.servable(it):
            continue
        for c in (it.get("standardCodes") or []):
            by_std[c].append(it)
    picked, short = [], {}
    for code in standards:
        want = blueprint["perStandard"].get(code, blueprint["defaults"])["itemCount"]
        have = sorted(by_std.get(code, []), key=lambda i: i["id"])
        picked += have[:want]
        if len(have) < want:
            short[code] = (len(have), want)
    return picked, short


def render(items, form_id, b, teacher: bool):
    blocks = []
    for n, it in enumerate(items, 1):
        ch, key_letter = ordered_choices(it, form_id)
        lis = "".join(
            f'<li><span class="cid">{c["_letter"]}.</span> {c.get("text","")}</li>'
            for c in ch)
        parts = [f'<div class="item"><p class="stem"><span class="num">{n}.</span> '
                 f'{it.get("stem","")}</p>']
        if lis:
            parts.append(f'<ol class="choices">{lis}</ol>')
        if teacher:
            parts.append(f'<p class="meta"><span class="key">KEY: {key_letter or "—"}</span> '
                         f'&middot; DOK {it.get("dokLevel")} &middot; '
                         f'{", ".join(it.get("standardCodes") or [])}</p>')
            if it.get("explanation"):
                parts.append(f'<p class="rat"><b>Why the key is right:</b> {it["explanation"]}</p>')
            for c in ch:
                if c.get("_letter") != key_letter and (c.get("explanation") or "").strip():
                    parts.append(f'<p class="rat"><b>{c["_letter"]} —</b> {c["explanation"]}</p>')
        parts.append("</div>")
        blocks.append("".join(parts))

    kind = "Teacher Key" if teacher else "Student Form"
    band = ('<p class="teacher-band">TEACHER COPY — contains answer keys and '
            'rationales. Not for student distribution.</p>') if teacher else ""
    return HTML % {
        "title": f"{b.course_title} — {kind}",
        "css": CSS % {"formid": form_id},
        "course": b.course_title, "year": b.standards_year, "formid": form_id,
        "band": band,
        "disclosure": (f"{b.disclosure_line}. Item parameters are estimates and have "
                       f"not met a student; this form is not a calibrated instrument."),
        "items": "\n".join(blocks),
    }


def build(form_id, standards, b=None):
    b = b or binding_mod.load()
    b.assert_codes(standards, where=f"form {form_id} standard list")
    with open(b.blueprint_file, encoding="utf-8") as fh:
        blueprint = json.load(fh)
    items = itemio.load_dir(b.output_dir)
    picked, short = select(items, standards, blueprint)
    if not picked:
        raise SystemExit(f"EMPTY SELECTION — no servable items for {standards}. "
                         f"Refusing to render an empty form.")
    b.assert_codes([c for i in picked for c in i["standardCodes"]],
                   where=f"form {form_id} contents")

    out = os.path.join(FORMS_DIR, form_id)
    os.makedirs(out, exist_ok=True)
    from weasyprint import HTML as WHTML
    manifest = {"formId": form_id, "course": b.course, "standardsYear": b.standards_year,
                "standards": standards, "itemCount": len(picked),
                "shortOfBlueprint": short, "surfaces": {}}
    for teacher in (False, True):
        name = "teacher-key" if teacher else "student"
        html = render(picked, form_id, b, teacher)
        hp = os.path.join(out, f"{name}.html")
        with open(hp, "w", encoding="utf-8") as fh:
            fh.write(html)
        WHTML(string=html, base_url=out).write_pdf(os.path.join(out, f"{name}.pdf"))
        manifest["surfaces"][name] = {"html": f"{name}.html", "pdf": f"{name}.pdf"}
    # Items as they appear on the student surface, so teacher-side-isolation
    # has something real to judge.
    student_records = []
    for it in picked:
        ch, key_letter = ordered_choices(it, form_id)
        student_records.append({
            **{k: v for k, v in it.items() if k not in
               ("correctAnswer", "explanation", "explanationEs", "dokRationale", "_file")},
            "choices": [{"id": c["_letter"], "text": c.get("text"), "textEs": c.get("textEs"),
                         "explanation": None, "misconception": None} for c in ch],
            "correctAnswer": None, "explanation": "", "explanationEs": "", "dokRationale": "",
            "bankTier": "student", "_surface": "student-form", "_formKeyLetter": key_letter,
        })
    with open(os.path.join(out, "student-surface.json"), "w", encoding="utf-8") as fh:
        json.dump({"formId": form_id, "items": student_records}, fh, indent=2, ensure_ascii=False)
    with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
    return manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("form_id")
    ap.add_argument("--standards", nargs="+", required=True,
                    help="Name the standards actually authored. Never a wildcard.")
    a = ap.parse_args()
    b = binding_mod.load()
    print(b.declaration())
    m = build(a.form_id, a.standards, b)
    print(f"\nForm {m['formId']}: {m['itemCount']} items across {len(m['standards'])} standard(s)")
    if m["shortOfBlueprint"]:
        print("  SHORT of blueprint:", m["shortOfBlueprint"])
    print(f"  -> forms/{a.form_id}/student.pdf  +  teacher-key.pdf")


if __name__ == "__main__":
    main()
