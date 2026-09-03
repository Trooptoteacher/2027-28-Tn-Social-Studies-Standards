#!/usr/bin/env python3
"""Turn a document-based item into a standalone DBQ ACTIVITY.

Sean, 2026-09-03: "let's turn those larger DBQ questions into actual separate
DBQ questions. We'll put the primary source of the context in my brand. Make
sure we have the citations and sourcing. Make sure it's easily read, and then
just turn that into an activity." And, in the same pass: "all the questions on
the assessment builder need to be TCAP-style multiple choice, maybe multiple
select."

Those two are one decision. A DBQ crammed into a six-item test form was the
reason FORM-A read as "a mixed classroom assessment, not a TCAP-field-testable
form": three primary sources, a three-part prompt and a six-band scoring guide,
rendered as question 6 of 6 with a KEY line and a paragraph headed "Why the key
is right." The DBQ was never a test item. It is a lesson, and it now renders as
one.

Nothing about the item is rewritten. The documents, their citations and the
prompt are the item's own text; the scoring guide is the rubric extracted from
it (L58). What is ADDED is apparatus a student writes on — sourcing scaffolds,
a planning frame, ruled space — which is the difference between a question and
an activity.

Usage:
  python3 tools/dbq_activity.py --list
  python3 tools/dbq_activity.py <item-id> [--out deliverables/dbq]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import binding as binding_mod
import itemio

# America 250 — the locked History Hack palette. B&W-safe by construction:
# every distinction here is a border, a tint or a glyph, never colour alone.
BRAND = {
    "heritage": "#1F3A5F", "gold": "#C9A227", "goldText": "#846009",
    "red": "#B22234", "cream": "#F8F5EF", "warm": "#F3ECD6", "cool": "#EAF0F7",
    "ink": "#23282E", "soft": "#41506A", "mute": "#5F6B7D", "hair": "#C9CFD8",
}

# TWO stem formats live in this bank and a parser that knows one silently
# reports zero documents for the other — which reads as "this item has no
# sources" rather than "this parser cannot see them". Measured before writing:
# 26 of 34 DBQs use the second shape.
#   A)  DOCUMENT A: <citation>            B)  DOCUMENT 1
#       "<excerpt>"                           Source: <citation>
#                                             "<excerpt>"
DOC_RX = re.compile(r"^\s*DOCUMENT\s+([A-Z]|\d{1,2})\s*[:.\-—]?\s*(.*)$", re.I)
SOURCE_RX = re.compile(r"^\s*Source\s*[:\-—]\s*(.+)$", re.I)
# A separator may be hyphens, em-dashes, equals or box-drawing rules.
SEP_RX = re.compile(r"^\s*[-=\u2500-\u257F\u2014\u2015_]{3,}\s*$")


def esc(v):
    if v is None:
        return ""
    return str(v).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def split_citation(head, body):
    """(citation, excerpt) for one document block.

    The item writes the citation as the DOCUMENT line and the excerpt as the
    quoted text beneath it. Where the excerpt runs on the same line after a
    colon, the first quoted span is the excerpt and everything before it is the
    citation. A block with no distinguishable citation is REPORTED, never
    published: an unsourced primary source is the one thing this repo will not
    ship (guardrail 1).
    """
    lines = [l for l in (head + "\n" + body).splitlines() if l.strip()]
    cite = None
    rest = []
    for l in lines:
        if cite is None:
            if (m := SOURCE_RX.match(l)):
                cite = m.group(1).strip()
                continue
            if not l.lstrip().startswith(("\u201c", '"')):
                cite = l.strip(" :")
                continue
        rest.append(l)
    text = "\n".join(rest).strip()
    m = re.search(r'["\u201c](.+)["\u201d]\s*$', text, re.S)
    if m:
        return cite, m.group(1).strip()
    return cite, text.strip('"\u201c\u201d \n')


def parse(item):
    """Break a DBQ stem into title, directions, documents and prompt."""
    stem = item.get("stem") or ""
    lines = stem.splitlines()
    title = (lines[0] if lines else "").strip()
    title = re.sub(r"^DOCUMENT[- ]BASED QUESTION\s*[:\-—]?\s*", "", title, flags=re.I).strip()

    directions = ""
    if (m := re.search(r"^\s*Directions?\s*:\s*(.+?)(?=\n\s*-{3,}|\n\s*DOCUMENT\s+[A-Z])",
                       stem, re.S | re.I | re.M)):
        directions = " ".join(m.group(1).split())

    docs, cur, prompt_lines, seen_doc = [], None, [], False
    for line in lines[1:]:
        d = DOC_RX.match(line)
        if d:
            seen_doc = True
            if cur:
                docs.append(cur)
            cur = {"label": d.group(1).upper(), "head": d.group(2).strip(), "body": []}
            continue
        if cur is not None:
            if SEP_RX.match(line):
                docs.append(cur)
                cur = None
                continue
            cur["body"].append(line)
        elif seen_doc:
            prompt_lines.append(line)
    if cur:
        docs.append(cur)

    # Everything after the LAST document block that is not part of it.
    tail = stem
    if docs:
        last = docs[-1]
        # The prompt begins after the final separator, or after the last quoted excerpt.
        parts = [p for p in re.split(r"\n\s*[-=\u2500-\u257F\u2014\u2015_]{3,}\s*\n", stem)]
        tail = parts[-1] if len(parts) > 1 else ""
    prompt = " ".join((tail or "\n".join(prompt_lines)).split())

    out = []
    for n, d in enumerate(docs):
        cite, exc = split_citation(d["head"], "\n".join(d["body"]))
        # A stem with no CLOSING separator leaves the prompt inside the last
        # document's body, and the item reads as having no prompt at all — four
        # DBQs were held for exactly that. The prompt is whatever follows the
        # final closing quotation mark of the last excerpt.
        if n == len(docs) - 1 and exc:
            blob = "\n".join(d["body"])
            if (m := re.search(r'["\u201d](?!.*["\u201d])', blob, re.S)):
                trailing = blob[m.end():].strip()
                if len(trailing) > 60:
                    exc = exc[:exc.rfind(trailing[:40])].strip() if trailing[:40] in exc else exc
                    if not prompt or len(trailing) > len(prompt):
                        prompt = " ".join(trailing.split())
        out.append({"label": d["label"], "citation": cite, "excerpt": exc})
    return {"title": title or "Document-Based Question", "directions": directions,
            "documents": out, "prompt": prompt}


def prompt_parts(prompt):
    """The prompt's own numbered demands, so a student can tick them off.

    A three-part prompt printed as one 90-word paragraph is where students lose
    a band without ever being confused about the history.
    """
    body = prompt
    lead = body
    parts = []
    if (m := re.search(r"(?:should address|must|address)\s*:?\s*(.*)$", body, re.S | re.I)):
        found = re.findall(r"\(\d+\)\s*([^()]+?)(?=\s*\(\d+\)|$)", m.group(1), re.S)
        if len(found) >= 2:
            parts = [" ".join(p.split()).strip(" ;.,") for p in found]
            lead = body[:m.start()].strip()
    if not parts:
        found = re.findall(r"—\s*([^—]+)", body)
        if len(found) >= 2:
            parts = [" ".join(p.split()).strip(" ;.,") for p in found]
            lead = body[:body.index("—")].strip()
    return lead, parts


HIPP = [("H", "Historical context", "What was happening when this was made?"),
        ("I", "Intended audience", "Who was meant to read or hear it?"),
        ("P", "Purpose", "What was it trying to make the audience do or think?"),
        ("P", "Point of view", "Who is speaking, and how does that shape it?")]


def css(teacher):
    B = BRAND
    return f"""
@page {{
  size: Letter; margin: 0.7in 0.7in 0.85in 0.7in;
  @bottom-left {{ content: "%(footer)s"; font-size: 9pt; color: {B['mute']}; }}
  @bottom-right {{ content: "Page " counter(page) " of " counter(pages);
                   font-size: 9pt; color: {B['mute']}; }}
}}
body {{ font-family: Calibri, Carlito, "Segoe UI", sans-serif; font-size: 11pt;
        line-height: 1.5; color: {B['ink']}; background: #fff; margin: 0; }}
h1, h2, h3 {{ font-family: Cambria, "Times New Roman", Georgia, serif;
              color: {B['heritage']}; margin: 0; }}
h1 {{ font-size: 20pt; line-height: 1.2; }}
h2 {{ font-size: 13pt; margin: 18pt 0 6pt; }}
.eyebrow {{ font-family: Cambria, serif; font-size: 10pt; font-weight: bold;
            letter-spacing: .06em; text-transform: uppercase; color: {B['red']};
            margin: 0 0 2pt; }}
.masthead {{ border: 1.2pt solid {B['heritage']}; background: {B['cream']};
             padding: 10pt 12pt; margin: 0 0 12pt; }}
.standard {{ font-size: 10pt; color: {B['soft']}; margin: 6pt 0 0; }}
.standard b {{ color: {B['heritage']}; }}
.directions {{ background: {B['cool']}; border: 0.8pt solid {B['hair']};
               padding: 8pt 10pt; font-size: 10.5pt; margin: 0 0 14pt; }}
/* Source card: warm tint + full border. No single-edge stripe. */
.doc {{ border: 1pt solid {B['heritage']}; background: {B['warm']};
        padding: 10pt 12pt; margin: 0 0 6pt; page-break-inside: avoid; }}
.doclabel {{ font-family: Cambria, serif; font-weight: bold; font-size: 11pt;
             color: {B['heritage']}; margin: 0 0 4pt; }}
.cite {{ font-size: 9.5pt; color: {B['soft']}; margin: 0 0 8pt;
         border-bottom: 0.6pt solid {B['gold']}; padding-bottom: 5pt; }}
/* The excerpt is the thing being read. Serif, 12pt, wide leading. */
.excerpt {{ font-family: Georgia, "Times New Roman", serif; font-size: 12pt;
            line-height: 1.65; margin: 0; }}
.excerpt::before {{ content: "\\201C"; }}
.excerpt::after {{ content: "\\201D"; }}
.sourcing {{ border: 0.8pt solid {B['hair']}; border-top: none;
             padding: 8pt 12pt 10pt; margin: 0 0 16pt; page-break-inside: avoid; }}
.sourcing p.h {{ font-size: 9.5pt; font-weight: bold; color: {B['goldText']};
                 margin: 0 0 6pt; text-transform: uppercase; letter-spacing: .05em; }}
table.hipp {{ width: 100%; border-collapse: collapse; }}
table.hipp td {{ vertical-align: top; padding: 3pt 4pt 10pt 0; font-size: 9.5pt; }}
table.hipp td.k {{ width: 30%; color: {B['soft']}; }}
table.hipp td.k b {{ color: {B['heritage']}; font-size: 10pt; }}
.rule {{ border-bottom: 0.7pt solid {B['hair']}; height: 15pt; }}
.rules .rule {{ margin-top: 6pt; }}
.prompt {{ border: 1.2pt solid {B['heritage']}; padding: 10pt 12pt;
           margin: 0 0 12pt; page-break-inside: avoid; }}
.prompt .lead {{ font-size: 11.5pt; margin: 0; }}
ol.parts {{ margin: 8pt 0 0; padding-left: 18pt; }}
ol.parts li {{ font-size: 10.5pt; margin: 0 0 4pt; }}
table.plan {{ width: 100%; border-collapse: collapse; margin: 0 0 14pt; }}
table.plan th, table.plan td {{ border: 0.7pt solid {B['hair']}; padding: 6pt;
                                font-size: 10pt; text-align: left; vertical-align: top; }}
table.plan th {{ background: {B['cool']}; color: {B['heritage']};
                 font-family: Cambria, serif; }}
table.plan td.blank {{ height: 42pt; }}
.write .line {{ border-bottom: 0.7pt solid {B['hair']}; height: 22pt; }}
.teacherband {{ border: 1.2pt solid {B['red']}; background: {B['cream']};
                padding: 6pt 10pt; font-weight: bold; font-size: 10.5pt;
                color: {B['red']}; margin: 0 0 12pt; }}
table.rubric {{ width: 100%; border-collapse: collapse; margin: 0 0 12pt; }}
table.rubric th, table.rubric td {{ border: 0.7pt solid {B['hair']}; padding: 6pt;
                                    font-size: 9.5pt; vertical-align: top; text-align: left; }}
table.rubric th {{ background: {B['heritage']}; color: {B['cream']};
                   font-family: Cambria, serif; }}
table.rubric td.pts {{ width: 8%; font-weight: bold; text-align: center;
                       font-size: 12pt; color: {B['heritage']}; }}
.note {{ font-size: 9.5pt; color: {B['soft']}; background: {B['cream']};
         border: 0.7pt solid {B['hair']}; padding: 8pt 10pt; margin: 0 0 10pt; }}
.disclosure {{ font-size: 9pt; color: {B['soft']}; border-top: 0.7pt solid {B['hair']};
               padding-top: 6pt; margin-top: 14pt; }}
.newpage {{ page-break-before: always; }}
"""


def render(item, parsed, b, teacher):
    stds = b.standards()
    codes = item.get("standardCodes") or []
    P = []
    P.append('<div class="masthead"><p class="eyebrow">History Hack &middot; '
             'Document-Based Question</p>'
             f'<h1>{esc(parsed["title"])}</h1>')
    for c in codes:
        t = (stds.get(c) or {}).get("text")
        P.append(f'<p class="standard"><b>{esc(c)}</b> — {esc(t) if t else "—"}</p>')
    P.append('</div>')
    if teacher:
        P.append('<div class="teacherband">TEACHER EDITION — scoring guide and expected '
                 'evidence. Not for student distribution.</div>')
    P.append('<p class="standard">Name _______________________________ '
             'Class ____________ Date ____________</p>')
    if parsed["directions"]:
        P.append(f'<div class="directions"><b>Directions.</b> {esc(parsed["directions"])}</div>')

    P.append("<h2>The sources</h2>")
    for d in parsed["documents"]:
        P.append('<div class="doc">'
                 f'<p class="doclabel">Document {esc(d["label"])}</p>'
                 f'<p class="cite">{esc(d["citation"])}</p>'
                 f'<p class="excerpt">{esc(d["excerpt"])}</p></div>')
        rows = "".join(
            f'<tr><td class="k"><b>{k}</b> — {esc(label)}<br>{esc(q)}</td>'
            f'<td><div class="rule"></div><div class="rule"></div></td></tr>'
            for k, label, q in HIPP)
        P.append('<div class="sourcing"><p class="h">Source it &mdash; '
                 f'Document {esc(d["label"])}</p>'
                 f'<table class="hipp">{rows}</table></div>')

    lead, parts = prompt_parts(parsed["prompt"])
    P.append('<div class="newpage"></div><h2>The question</h2>'
             f'<div class="prompt"><p class="lead">{esc(lead)}</p>')
    if parts:
        P.append('<ol class="parts">'
                 + "".join(f"<li>{esc(p)}</li>" for p in parts) + "</ol>")
    P.append("</div>")

    P.append("<h2>Plan your answer</h2>")
    P.append('<table class="plan"><tr><th style="width:22%">Your claim</th>'
             '<td class="blank"></td></tr></table>')
    body = "".join(
        f'<tr><td>Document {esc(d["label"])}</td><td class="blank"></td>'
        f'<td class="blank"></td></tr>' for d in parsed["documents"])
    P.append('<table class="plan"><tr><th style="width:16%">Source</th>'
             '<th style="width:42%">Evidence you will use</th>'
             '<th>Why it supports your claim</th></tr>' + body
             + '<tr><td>Outside knowledge</td><td class="blank"></td>'
               '<td class="blank"></td></tr></table>')

    P.append('<div class="newpage"></div><h2>Write your response</h2>'
             '<div class="write">' + '<div class="line"></div>' * 26 + "</div>")

    if teacher:
        rub = item.get("rubric") or {}
        P.append('<div class="newpage"></div><h2>Scoring guide</h2>')
        if rub.get("scorePoints") and rub.get("criteria"):
            rows = "".join(
                f'<tr><td class="pts">{esc(c.get("points"))}</td>'
                f'<td>{("<b>" + esc(c.get("label")) + ".</b> ") if c.get("label") else ""}'
                f'{esc(c.get("descriptor"))}</td></tr>'
                for c in sorted(rub["criteria"], key=lambda x: -(x.get("points") or 0)))
            P.append(f'<table class="rubric"><tr><th>Pts</th>'
                     f'<th>{esc(rub["scorePoints"])}-point scale</th></tr>{rows}</table>')
            if rub.get("notes"):
                P.append(f'<div class="note"><b>Expected evidence and document analysis.</b> '
                         f'{esc(rub["notes"])}</div>')
        else:
            P.append('<div class="note"><b>NO RUBRIC.</b> This activity cannot be scored '
                     'consistently by two teachers until one is written.</div>')
        P.append('<div class="note"><b>Sourcing.</b> Every document above carries its own '
                 'citation as written in the item record. Verify each against the holding '
                 'institution before classroom use — an unsourced primary source is worse '
                 'than a missing one.</div>')

    P.append('<div class="disclosure">History Hack &middot; TroopToTeacher Technologies. '
             f'Tennessee Academic Standards {esc(b.standards_year)}. '
             'classroom-formative &middot; pre-field-test — this activity has not been '
             'field-tested and its scoring guide is not calibrated.</div>')
    return "".join(P)


def build(item, b, out_dir):
    from weasyprint import HTML as WHTML
    parsed = parse(item)
    problems = []
    if not parsed["documents"]:
        problems.append("no DOCUMENT blocks parsed from the stem")
    for d in parsed["documents"]:
        if not d["citation"]:
            problems.append(f"Document {d['label']} has no citation line")
        if not d["excerpt"] or len(d["excerpt"]) < 40:
            problems.append(f"Document {d['label']} has no usable excerpt")
    if not parsed["prompt"]:
        problems.append("no prompt parsed")
    if problems:
        return None, problems

    os.makedirs(out_dir, exist_ok=True)
    footer = f"{item['id']} · {', '.join(item.get('standardCodes') or [])}"
    written = []
    for teacher in (False, True):
        name = "teacher-edition" if teacher else "student-activity"
        html = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                f'<title>{esc(parsed["title"])}</title>'
                f'<style>{css(teacher).replace("%(footer)s", footer)}</style></head><body>'
                + render(item, parsed, b, teacher) + "</body></html>")
        with open(os.path.join(out_dir, f"{name}.html"), "w", encoding="utf-8") as fh:
            fh.write(html)
        WHTML(string=html, base_url=out_dir).write_pdf(os.path.join(out_dir, f"{name}.pdf"))
        written.append(f"{name}.pdf")
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump({"itemId": item["id"], "standardCodes": item.get("standardCodes"),
                   "title": parsed["title"], "documents": parsed["documents"],
                   "surface": "activity", "tcapFormat": item.get("tcapFormat"),
                   "rubric": bool((item.get("rubric") or {}).get("scorePoints")),
                   "surfaces": written}, fh, indent=2, ensure_ascii=False)
    return parsed, []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("item_id", nargs="?")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", default="deliverables/dbq")
    a = ap.parse_args()
    b = binding_mod.load()
    print(b.declaration())

    items = [i for i in itemio.load_dir(b.output_dir)
             if itemio.servable(i) and i.get("itemType") == "document-based"]
    if not items:
        print("EMPTY SCAN — no document-based items; refusing to report success over nothing")
        return 1

    if a.list:
        print(f"\n{len(items)} document-based item(s):")
        for it in items:
            p = parse(it)
            rub = (it.get("rubric") or {}).get("scorePoints")
            print(f"  {it['id']:<24} {','.join(it.get('standardCodes') or []):<16} "
                  f"{len(p['documents'])} doc(s)  rubric={rub or '—'}  {p['title'][:44]}")
        return 0

    targets = items if a.all else [i for i in items if i["id"] == a.item_id]
    if not targets:
        print(f"no document-based item with id {a.item_id!r} — try --list")
        return 1

    ok, held = 0, []
    for it in targets:
        out = os.path.join(itemio.BANK_ROOT, a.out, it["id"])
        parsed, problems = build(it, b, out)
        if problems:
            held.append((it["id"], problems))
            print(f"HELD {it['id']}: " + "; ".join(problems))
            continue
        ok += 1
        print(f"\n{it['id']} — {parsed['title']}")
        for d in parsed["documents"]:
            print(f"    Document {d['label']}: {d['citation'][:88]}")
        print(f"  -> {a.out}/{it['id']}/student-activity.pdf  +  teacher-edition.pdf")
    print(f"\n{ok} built, {len(held)} held")
    return 1 if held and not ok else 0


if __name__ == "__main__":
    sys.exit(main())
