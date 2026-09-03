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
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import alignment
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


def ordered_choices(item, form_id, target_letter=None):
    """Deterministic per-item choice order, shared by BOTH surfaces.

    Seeded from the item id and the form id so the same item on the same form
    always renders identically, and the teacher key can never disagree with the
    student form about which letter is the key.

    When `target_letter` is given the order is rotated so the key lands there.
    Leaving key placement to the hash alone put 42% of one form's keys on D —
    the de-bias gate exists to catch that, and the BUILDER is what has to
    satisfy it. A gate the builder cannot satisfy is a gate that stays red.
    """
    ch = [c for c in itemio.choices(item) if isinstance(c, dict)]
    if not ch:
        return [], None
    seed = int(hashlib.sha256(f"{form_id}:{item['id']}".encode()).hexdigest()[:8], 16)
    order = list(ch)
    random.Random(seed).shuffle(order)
    letters = "ABCDEFGH"
    if target_letter and target_letter in letters[:len(order)]:
        want = letters.index(target_letter)
        at = next((n for n, c in enumerate(order)
                   if c.get("id") == item.get("correctAnswer")), None)
        if at is not None:
            order[want], order[at] = order[at], order[want]
    out, key_letter = [], None
    for i, c in enumerate(order):
        letter = letters[i]
        if c.get("id") == item.get("correctAnswer"):
            key_letter = letter
        out.append({**c, "_letter": letter})
    return out, key_letter


def key_targets(items, form_id):
    """Balanced key positions across the form: {item_id: letter}.

    Round-robin over the available positions, offset by the form id so two
    forms do not share the same pattern.
    """
    letters = "ABCDEFGH"
    offset = int(hashlib.sha256(form_id.encode()).hexdigest()[:4], 16)
    out, n = {}, 0
    for it in items:
        ch = [c for c in itemio.choices(it) if isinstance(c, dict)]
        if not ch or not it.get("correctAnswer"):
            continue
        out[it["id"]] = letters[(offset + n) % len(ch)]
        n += 1
    return out


def fill_tier(pool, tier):
    """Fill a tier's slots from a pool, or return None if any slot is empty.

    A form blueprint is a set of SLOTS and selection has to fill them. The first
    builder took the first N items per standard by id and never looked at DOK or
    item type, so the form gate existed before the builder could satisfy it.
    """
    used, got = set(), []
    for slot in tier["slots"]:
        cand = [i for i in pool if i["id"] not in used
                and i.get("itemType") in slot["types"] and i.get("dokLevel") == slot["dok"]]
        if not cand:
            return None
        used.add(cand[0]["id"]); got.append(cand[0])
    return got


def select(items, standards, blueprint):
    """Servable, ALIGNED, per-standard-RELEVANT items filling the best tier available.

    A standard is built at the highest tier it can fill and the form DECLARES
    which. Requiring a document-based item everywhere blocked 71 of 94
    standards, and a four-option question cannot assess DOK-4 anyway — so the
    lower tiers are honest instruments with a stated ceiling, not diluted ones.

    Never a wildcard: the caller names the standards actually authored.
    """
    form = blueprint["form"]
    stds = binding_mod.load().standards()
    by_std = collections.defaultdict(list)
    for it in items:
        if not itemio.aligned(it):
            continue
        hay = alignment.subject_text(it)
        for c in (it.get("standardCodes") or []):
            t = stds.get(c, {}).get("text")
            if t and alignment.relevant_to(hay, t):
                by_std[c].append(it)

    picked, short, tiers = [], {}, {}
    for code in standards:
        pool = sorted(by_std.get(code, []), key=lambda i: i["id"])
        for tier in form["tiers"]:
            got = fill_tier(pool, tier)
            if got:
                picked += got
                tiers[code] = tier["id"]
                break
        else:
            short[code] = (len(pool), form["itemCount"])
    return picked, short, tiers



def esc(v):
    """Escape a metadata value for the key page.

    The analysis block prints RECORD text — citations, rationales, reviewer
    names — that no author wrote as HTML. An unescaped ampersand or angle
    bracket in a citation silently swallows the rest of the line, and the
    reader sees a short field rather than a broken one.
    """
    if v is None:
        return ""
    return (str(v).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


_LETTER_REF = re.compile(
    r"\b(Choice|Option|Answer)\s+([A-H])\b|\b([A-H])(?=\s+(?:is|was)\s+"
    r"(?:correct|incorrect|wrong|right|the|a\b))")


def remap_letters(text, item, ordered):
    """Rewrite hard-coded choice letters to the letters THIS FORM prints.

    The builder re-letters choices to de-bias key position — that is the whole
    point of key_targets(). But 2,440 of 3,928 servable items name a letter
    inside their explanation, and the moment a choice moves, the sentence
    points at the wrong option. FORM-A item 1 keys C in the bank, rendered as
    KEY: B, and printed "B is incorrect because it describes a different
    program" directly beneath it. The form was GREEN.

    The mapping is the builder's own permutation, so this is a remap and not
    authoring: source letter -> the letter that choice now carries. Nothing in
    the record changes; the record keeps its own letters and the RENDER speaks
    the form's.

    Found by Sean reading the rendered key. Every gate had measured the record,
    where the letters were self-consistent. Measure the artifact.

    NOT IDEMPOTENT, deliberately: applying it twice maps B->D->A. render()
    calls it exactly once per field, and gate_form_key_contradiction measures
    the rendered PDF rather than trusting that.
    """
    if not text:
        return text
    src = [c for c in itemio.choices(item) if isinstance(c, dict)]
    letters = "ABCDEFGH"
    # The record's own positional letter for each choice id, and where it went.
    from_id = {c.get("id"): letters[i] for i, c in enumerate(src) if i < len(letters)}
    to_id = {c.get("id"): c["_letter"] for c in ordered}
    mapping = {}
    for cid, old in from_id.items():
        # An item whose choice ids ARE letters ("A".."D") names them directly.
        for key in {old, cid}:
            if isinstance(key, str) and len(key) == 1 and key.upper() in letters:
                mapping[key.upper()] = to_id.get(cid, old)

    def sub(m):
        word, lettered, bare = m.group(1), m.group(2), m.group(3)
        old = (lettered or bare or "").upper()
        new = mapping.get(old, old)
        return f"{word} {new}" if word else new

    return _LETTER_REF.sub(sub, text)


def analysis_block(it, key_letter, ordered, b):
    """The per-item metadata a teacher key must carry.

    Sean, first read: the selected-response items "lack the required standards,
    DOK/Hess, distractor, bias, citation, and IRT metadata in the supplied
    form." Every one of those was in the RECORD and none of it reached the
    PAGE — the key printed "KEY: B · DOK 1 · US.46" and stopped. A teacher
    cannot judge an item's rigour, fairness or fit from three tokens, and
    neither can an adoption reviewer.
    """
    stds = b.standards()
    rows = []
    for code in it.get("standardCodes") or []:
        text = (stds.get(code) or {}).get("text")
        rows.append((code, esc(text) if text else
                     "<i>not in the declared standards file</i>"))
    out = ['<div class="analysis"><p class="ahead">Item analysis</p><dl>']
    for code, text in rows:
        out.append(f"<dt>Standard</dt><dd><b>{esc(code)}</b> — {text}</dd>")
    dok = it.get("dokLevel")
    rat = esc(it.get("dokRationale") or "") or \
        '<i>no DOK rationale — the level is a number nobody justified</i>'
    out.append(f"<dt>DOK / Hess</dt><dd>Level {dok} — {rat}</dd>")
    rc, rcs = it.get("reportingCategory"), it.get("reportingCategorySource")
    out.append(f"<dt>Reporting category</dt><dd>{esc(rc or '—')} "
               f"<span class='prov'>(source of record: {esc(rcs or 'UNMAPPED')})</span></dd>")
    irt = it.get("irtParameters") or {}
    out.append("<dt>IRT</dt><dd>" + (
        " · ".join(f"{k} {v}" for k, v in irt.items()) if irt else "—")
        + f" <span class='prov'>({esc(it.get('calibrationStatus') or 'unknown')} — "
          f"estimates, not calibrated against student responses)</span></dd>")
    fmt = it.get("tcapFormat")
    out.append(f"<dt>Format</dt><dd>{'field-testable' if fmt else 'classroom-formative'} "
               f"<span class='prov'>(tcapFormat: {str(bool(fmt)).lower()}"
               + (f" — {esc(it.get('tcapFormatReason'))}" if not fmt and
                  it.get("tcapFormatReason") else "") + ")</span></dd>")
    br = it.get("biasReview") or {}
    out.append(f"<dt>Bias / sensitivity</dt><dd>{esc(br.get('status') or 'not stated')}"
               + (f" — {esc(br.get('reviewer'))}" if br.get("reviewer") else "") + "</dd>")
    cite = it.get("citation") or (it.get("source") or {}).get("citation") \
        if isinstance(it.get("source"), dict) else it.get("citation")
    out.append(f"<dt>Citation</dt><dd>{esc(cite) if cite else '—'}</dd>")
    hr = it.get("historianReview") or {}
    out.append("<dt>Historian review</dt><dd>"
               + (f"{esc(hr.get('reviewer'))}, {esc(hr.get('reviewedAt'))}"
                  if hr.get("reviewer") else
                  ("<b>required, not yet done</b>" if it.get("requiresHistorianReview")
                   else "not required")) + "</dd>")
    misc = [f"<b>{c['_letter']}</b> — {esc(c.get('misconception'))}"
            for c in ordered
            if c.get("_letter") != key_letter and (c.get("misconception") or "").strip()]
    out.append("<dt>Distractor diagnosis</dt><dd>"
               + ("; ".join(misc) if misc else
                  "<i>no misconception named — a distractor written to be merely wrong is "
                  "noise, not diagnosis</i>") + "</dd>")
    rub = it.get("rubric") or {}
    if it.get("itemType") in ("constructed-response", "document-based"):
        if rub.get("scorePoints") and rub.get("criteria"):
            band = "".join(
                f"<li><b>{esc(str(c.get('points')))}</b> — {esc(c.get('descriptor'))}</li>"
                for c in rub["criteria"])
            out.append(f"<dt>Rubric</dt><dd>{rub['scorePoints']}-point"
                       f"<ol class='rubric'>{band}</ol></dd>")
        else:
            out.append("<dt>Rubric</dt><dd><b>NOT WRITTEN</b> — this item cannot be scored "
                       "consistently by two teachers</dd>")
    out.append("</dl></div>")
    return "".join(out)


def render(items, form_id, b, teacher: bool, targets=None, tier_note=""):
    targets = targets if targets is not None else key_targets(items, form_id)
    blocks = []
    for n, it in enumerate(items, 1):
        ch, key_letter = ordered_choices(it, form_id, targets.get(it["id"]))
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
                parts.append('<p class="rat"><b>Why the key is right:</b> '
                             + remap_letters(it["explanation"], it, ch) + '</p>')
            for c in ch:
                if c.get("_letter") != key_letter and (c.get("explanation") or "").strip():
                    parts.append(f'<p class="rat"><b>{c["_letter"]} —</b> '
                                 + remap_letters(c["explanation"], it, ch) + '</p>')
            parts.append(analysis_block(it, key_letter, ch, b))
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
                       f"not met a student; this form is not a calibrated instrument."
                       + (f" {tier_note}" if tier_note else "")),
        "items": "\n".join(blocks),
    }


def build(form_id, standards, b=None):
    b = b or binding_mod.load()
    b.assert_codes(standards, where=f"form {form_id} standard list")
    with open(b.blueprint_file, encoding="utf-8") as fh:
        blueprint = json.load(fh)
    items = itemio.load_dir(b.output_dir)
    picked, short, tiers = select(items, standards, blueprint)
    if not picked:
        raise SystemExit(f"EMPTY SELECTION — no servable items for {standards}. "
                         f"Refusing to render an empty form.")
    b.assert_codes([c for i in picked for c in i["standardCodes"]],
                   where=f"form {form_id} contents")

    out = os.path.join(FORMS_DIR, form_id)
    os.makedirs(out, exist_ok=True)
    from weasyprint import HTML as WHTML
    form = blueprint["form"]
    by_id = {t["id"]: t for t in form["tiers"]}
    ceilings = {by_id[t]["dokCeiling"] for t in tiers.values()} or {3}
    tier_note = form["disclosureByCeiling"][str(min(ceilings))]
    manifest = {"formId": form_id, "course": b.course, "standardsYear": b.standards_year,
                "standards": standards, "itemCount": len(picked),
                "tierByStandard": tiers, "dokCeiling": min(ceilings),
                "tierDisclosure": tier_note,
                "shortOfBlueprint": short, "surfaces": {}}
    targets = key_targets(picked, form_id)
    for teacher in (False, True):
        name = "teacher-key" if teacher else "student"
        html = render(picked, form_id, b, teacher, targets, tier_note)
        hp = os.path.join(out, f"{name}.html")
        with open(hp, "w", encoding="utf-8") as fh:
            fh.write(html)
        WHTML(string=html, base_url=out).write_pdf(os.path.join(out, f"{name}.pdf"))
        manifest["surfaces"][name] = {"html": f"{name}.html", "pdf": f"{name}.pdf"}
    # Items as they appear on the student surface, so teacher-side-isolation
    # has something real to judge.
    student_records = []
    for it in picked:
        ch, key_letter = ordered_choices(it, form_id, targets.get(it["id"]))
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
