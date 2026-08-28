#!/usr/bin/env python3
"""Parse the official TDOE Tennessee Social Studies Standards PDF into per-course JSON.

VERBATIM parse. Every standard's text, content-strand letters, practice, course
description, and the era/topic headings above it are read straight off the PDF.
Nothing is summarised, reworded, reordered, or invented.

    python3 tools/parse_standards.py source/TN-Social-Studies-Standards-2027-28.pdf standards/

Method
------
The document styles every element distinctly, so classification is by font
metadata rather than by guessing at line order:

    bold, in HDR_TOKENS -> table header cell ("Standard", "Number", ...)
    bold >= 14pt        -> era / topic heading above a standards table
    bold, "Overview:"   -> the era's overview paragraph
    plain 14pt          -> a standard code (US.01) or a practice code (SSP.01)
    plain 12pt          -> standard text, or a description / overview continuation
    plain 11-12pt       -> content-strand letters (only C/E/G/H/P/T/TCA and separators)

Header cells are matched FIRST: most headings are 18pt, but Grade 7 sets three
topic headings at 14pt -- the same size the header cells use.

Lines are consumed in the PDF's own reading order. They are deliberately NOT
re-sorted by y-coordinate: a code cell is vertically centred against a wrapped
text cell, so a y-sort silently detaches the first line of every two-line
standard and hands it to the previous one.

Two independent checks run on every course and the script exits non-zero if
either fails:
  * a table-geometry parse must not find a standard code the line parse missed
  * codes must be gapless from .01 to the course maximum

Courses whose tables carry no Content Strand column (K, 1, 2, Psychology) yield
empty strand lists. That is the document's own shape, not a parse failure.
"""
import json
import re
import sys
from pathlib import Path

import pymupdf

BOILER_PREFIX = ("C—Culture,", "TCA—Tennessee Code Annotated")
BOILER_EXACT = {"Tennessee Social Studies Standards"}
HDR_TOKENS = {"standard", "number", "content standard", "content", "strand",
              "standard number", "content strand", "practice", "practice number",
              "social studies practice"}

SECTION_RE = re.compile(
    r"^\s*(K|[1-8]|AAH|AH|CI|E|P|S|TN|GC|US|WG|W)\s*\|\s*([A-Z][A-Z0-9 ,\-&]+?)\s*$", re.M)
SSP_RE = re.compile(r"^SSP\.\d{1,2}$")

STRAND_TOKEN = r"(?:C|E|G|H|P|T|TCA)"
# The printed strand cell, e.g. "C, E, G, H, P" or a single "E".
STRAND_STRICT = re.compile(r"^" + STRAND_TOKEN + r"(?:\s*,\s*" + STRAND_TOKEN + r")*\s*,?$")
# The same cell where the document typed a period for a comma (TN.03 "C. E, G, H, P, T",
# 5.18 "C. H.P, T,"). Accepted only with 2+ tokens so a stray "H." stays prose.
STRAND_LOOSE = re.compile(r"^" + STRAND_TOKEN + r"(?:\s*[.,]\s*" + STRAND_TOKEN + r")+\s*[.,]?$")

# Strand letters left stranded on the end of a standard's text: either a bare
# "TCA", or a run of two or more strand tokens. Catches a wrapped strand cell
# whose tail was read as prose.
TRAILING_STRAND = re.compile(
    r"(?:^|\s)(?:TCA$|" + STRAND_TOKEN + r"(?:\s*,\s*" + STRAND_TOKEN + r")+\s*$)")

# Headings are bold and at least this size. Most are 18pt; Grade 7 sets its three
# Renaissance/Reformation topic headings at 14pt, the same size as a table header
# cell -- which is why header cells are matched and skipped first.
HEADING_MIN_PT = 14

# An era heading carries a date range in parentheses; a topic heading does not.
ERA_RE = re.compile(r"\(.*\d{3,4}.*[-–—].*\)")

# Courses sharing a prefix that the PDF splits into parts but that number
# continuously and are one course: 5th grade Part 1 (5.01-5.31) + Part 2 (5.32-5.46).
MERGE_PREFIXES = {"5"}

SLUGS = {
    "K": ("kindergarten", "Kindergarten Social Studies", "Elementary"),
    "1": ("grade-01", "First Grade Social Studies", "Elementary"),
    "2": ("grade-02", "Second Grade Social Studies", "Elementary"),
    "3": ("grade-03", "Third Grade Social Studies", "Elementary"),
    "4": ("grade-04", "Fourth Grade Social Studies", "Elementary"),
    "5": ("grade-05", "Fifth Grade Social Studies", "Elementary"),
    "6": ("grade-06", "Sixth Grade Social Studies", "Middle"),
    "7": ("grade-07", "Seventh Grade Social Studies", "Middle"),
    "8": ("grade-08", "Eighth Grade Social Studies", "Middle"),
    "AAH": ("african-american-history", "African American History", "High School"),
    "AH": ("ancient-history", "Ancient History", "High School"),
    "CI": ("contemporary-issues", "Contemporary Issues", "High School"),
    "E": ("economics", "Economics", "High School"),
    "P": ("psychology", "Psychology", "High School"),
    "S": ("sociology", "Sociology", "High School"),
    "TN": ("tennessee-history", "Tennessee History", "High School"),
    "GC": ("us-government-civics", "United States Government and Civics", "High School"),
    "US": ("us-history-geography", "United States History and Geography", "High School"),
    "WG": ("world-geography", "World Geography", "High School"),
    "W": ("world-history-geography", "World History and Geography", "High School"),
}


def norm(s):
    return re.sub(r"[ \t ]+", " ", s.replace(" ", " ")).strip()


def is_boiler(t):
    return (t in BOILER_EXACT or t.startswith(BOILER_PREFIX)
            or re.fullmatch(r"\d{1,3}", t) is not None)


# The Content Strand column sits at the far right of the landscape page. A
# strand cell is often laid out as trailing spans of the SAME line as the
# standard's last text line, so joining a line's spans blindly buries the
# strand inside the prose.
STRAND_COL_FRACTION = 0.75
# A column boundary reads as a horizontal gap several times wider than the
# ~2.7pt that separates words inside a sentence.
COLUMN_GAP_PT = 5.0


def lines_with_style(page):
    """Every non-empty line on the page, in the PDF's own reading order.

    A line whose trailing spans sit in the Content Strand column and read as
    strand letters is emitted as two entries: the prose, then the strand.
    """
    out = []
    x_split = page.rect.width * STRAND_COL_FRACTION
    words = page.get_text("words")

    def split_by_words(ln, line_txt):
        """Split one line at the strand column when prose and strand share a span.

        Only ever splits the line's OWN words: a neighbouring cell can share the
        line's y-band, and borrowing its strand would both mis-attribute the
        strand and leave the real one to be read as prose.
        """
        x0, y0, x1, y1 = ln["bbox"]
        mine = [w for w in words
                if w[1] >= y0 - 1 and w[3] <= y1 + 1 and w[0] >= x0 - 1 and w[2] <= x1 + 1]
        mine.sort(key=lambda w: w[0])
        size = round(ln["spans"][0]["size"])
        # Walk right-to-left and keep the LEFTMOST split that yields a valid
        # strand cell preceded by a column gap. A fixed x threshold cannot do
        # this: the strand column's left edge moves with the cell's width.
        best = None
        for k in range(len(mine) - 1, 0, -1):
            if mine[k][0] - mine[k - 1][2] < COLUMN_GAP_PT:
                continue
            if match_strand(norm(" ".join(w[4] for w in mine[k:])), size):
                best = k
        if best is None:
            return None
        head_txt = norm(" ".join(w[4] for w in mine[:best]))
        tail_txt = norm(" ".join(w[4] for w in mine[best:]))
        # the two halves must reconstruct exactly this line, nothing borrowed
        if norm(head_txt + " " + tail_txt) != norm(line_txt):
            return None
        return head_txt, tail_txt

    for blk in page.get_text("dict")["blocks"]:
        if blk.get("type") != 0:
            continue
        for ln in blk.get("lines", []):
            spans = ln["spans"]
            if not spans:
                continue
            cut = len(spans)
            while cut > 0 and spans[cut - 1]["bbox"][0] >= x_split:
                cut -= 1
            head, tail = spans[:cut], spans[cut:]
            tail_txt = norm("".join(sp["text"] for sp in tail))
            if not (head and tail_txt and match_strand(tail_txt, round(tail[0]["size"]))):
                head, tail, tail_txt = spans, [], ""
            head_txt = norm("".join(sp["text"] for sp in head))
            if not tail_txt and ln["bbox"][2] > x_split and ln["bbox"][0] < x_split:
                split = split_by_words(ln, head_txt)
                if split:
                    head_txt, tail_txt = split
                    tail = head  # same styling; only used for size/bold below
            if head_txt:
                out.append({"text": head_txt, "bold": bool(head[0]["flags"] & 16),
                            "size": round(head[0]["size"])})
            if tail_txt:
                out.append({"text": tail_txt, "bold": bool(tail[0]["flags"] & 16),
                            "size": round(tail[0]["size"])})
    return out


def find_sections(doc):
    """[(prefix, printed_title, first_page_idx, end_page_idx_exclusive)] in doc order."""
    hits = []
    for i, pg in enumerate(doc):
        for m in SECTION_RE.finditer(pg.get_text()):
            hits.append((m.group(1), norm(m.group(2)), i))
    return [(p, t, s, hits[j + 1][2] if j + 1 < len(hits) else doc.page_count)
            for j, (p, t, s) in enumerate(hits)]


def match_strand(text, size):
    if text.startswith("•") or size > 12:
        return None
    if STRAND_STRICT.match(text):
        return text
    if STRAND_LOOSE.match(text):
        return text
    return None


def parse_course(doc, pfx, start, end):
    code_re = re.compile(r"^" + re.escape(pfx) + r"\.(\d{2,3})$")
    practices, standards = [], []
    era = topic = overview = description = ""
    heads = []
    cur = cur_kind = None
    in_overview = in_desc = False
    orphans = []

    def flush():
        nonlocal cur, cur_kind
        if cur is None:
            return
        text = re.sub(r"\s+", " ", " ".join(cur["lines"])).strip()
        if cur_kind == "ssp":
            if not any(p["code"] == cur["code"] for p in practices):
                practices.append({"code": cur["code"], "text": text})
        elif not any(s["code"] == cur["code"] for s in standards):
            raw = cur["strand"].strip().rstrip(".,")
            strands = [s for s in re.split(r"[.,\s]+", raw) if s]
            standards.append({
                "code": cur["code"],
                "text": text,
                "strand": strands,
                "strandRaw": raw,
                "geo": "G" in strands,
                "tca": "TCA" in strands,
                "era": cur["era"],
                "eraOverview": cur["overview"],
                "cluster": cur["topic"] or cur["era"],
                "sourcePage": cur["page"],
            })
        cur, cur_kind = None, None

    def apply_heads():
        nonlocal era, topic, overview
        if not heads:
            return
        if len(heads) == 1:
            if ERA_RE.search(heads[0]):
                era, topic, overview = heads[0], "", ""
            else:
                topic = heads[0]
        else:
            era, topic, overview = heads[0], heads[-1], ""
        heads.clear()

    for pno in range(start, end):
        for ln in lines_with_style(doc[pno]):
            t = ln["text"]
            if is_boiler(t):
                continue
            low = t.lower().rstrip(" :")

            # Table header cells are bold too, so they must be taken out of the
            # way BEFORE the heading test -- one course sets its topic headings
            # at the same 14pt the header cells use.
            if ln["bold"] and low in HDR_TOKENS:
                continue
            if ln["bold"] and ln["size"] >= HEADING_MIN_PT:
                flush()
                in_overview = in_desc = False
                heads.append(t)
                continue
            if t.lower().startswith("course description:"):
                flush()
                description = t.split(":", 1)[1].strip()
                in_desc, in_overview = True, False
                continue
            if ln["bold"] and t.lower().startswith("overview:"):
                flush()
                overview = t.split(":", 1)[1].strip()
                in_overview, in_desc = True, False
                continue

            m_code, m_ssp = code_re.match(t), SSP_RE.match(t)
            if m_code or m_ssp:
                flush()
                in_overview = in_desc = False
                apply_heads()
                cur_kind = "ssp" if m_ssp else "std"
                cur = {"code": t, "lines": [], "strand": "", "era": era,
                       "overview": overview, "topic": topic, "page": pno + 1}
                continue

            # A strand cell can wrap across two lines ("C, G, H, P, T," / "TCA").
            # Keep consuming while the accumulated cell ends on a separator.
            if cur is not None and cur_kind == "std" and (
                    not cur["strand"] or cur["strand"].rstrip().endswith((",", "."))):
                hit = match_strand(t, ln["size"])
                if hit:
                    cur["strand"] = (cur["strand"] + " " + hit).strip()
                    continue

            if in_desc:
                description = (description + " " + t).strip()
            elif in_overview:
                overview = (overview + " " + t).strip()
            elif cur is not None:
                cur["lines"].append(t)
            else:
                orphans.append({"page": pno + 1, "text": t})
    flush()
    return {
        "practices": practices,
        "standards": standards,
        "description": re.sub(r"\s+", " ", description).strip(),
        "orphans": orphans,
    }


def table_codes(doc, pfx, start, end):
    """Independent geometry parse, used only to cross-check the code set."""
    code_re = re.compile(r"(?:^|\s)(" + re.escape(pfx) + r"\.\d{2,3})\s*$")
    found = set()
    for pno in range(start, end):
        pg = doc[pno]
        for tab in pg.find_tables().tables:
            for row in tab.rows:
                for cell in row.cells:
                    if not cell:
                        continue
                    txt = norm(pg.get_textbox(pymupdf.Rect(cell)).replace("\n", " "))
                    m = code_re.search(txt)
                    if m:
                        found.add(m.group(1))
    return found


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    pdf, outdir = Path(sys.argv[1]), Path(sys.argv[2])
    doc = pymupdf.open(pdf)
    outdir.mkdir(parents=True, exist_ok=True)

    courses, failures = {}, []
    for pfx, title, start, end in find_sections(doc):
        parsed = parse_course(doc, pfx, start, end)
        c = courses.setdefault(pfx, {"prefix": pfx, "printedTitles": [], "practices": [],
                                     "standards": [], "description": "",
                                     "pageRange": [start + 1, end], "tableCodes": set()})
        c["printedTitles"].append(title)
        c["pageRange"][1] = end
        c["description"] = c["description"] or parsed["description"]
        for p in parsed["practices"]:
            if not any(x["code"] == p["code"] for x in c["practices"]):
                c["practices"].append(p)
        c["standards"].extend(parsed["standards"])
        c["tableCodes"] |= table_codes(doc, pfx, start, end)
        if pfx not in MERGE_PREFIXES and len(c["printedTitles"]) > 1:
            failures.append(f"{pfx}: appears in {len(c['printedTitles'])} sections but is not "
                            f"declared mergeable")

    anomalies, index = [], []
    for pfx, c in courses.items():
        slug, title, level = SLUGS[pfx]
        c["standards"].sort(key=lambda s: int(s["code"].split(".")[1]))
        codes = [s["code"] for s in c["standards"]]
        nums = sorted(int(x.split(".")[1]) for x in codes)

        missed = sorted(c["tableCodes"] - set(codes))
        if missed:
            failures.append(f"{pfx}: table parse found codes the line parse missed: {missed}")
        gaps = [n for n in range(1, nums[-1] + 1) if n not in nums]
        if gaps:
            failures.append(f"{pfx}: code gaps {gaps}")
        dupes = [x for x in set(codes) if codes.count(x) > 1]
        if dupes:
            failures.append(f"{pfx}: duplicate codes {sorted(dupes)}")
        short = [s["code"] for s in c["standards"] if len(s["text"]) < 25]
        if short:
            failures.append(f"{pfx}: suspiciously short text for {short}")
        # A wrapped strand cell whose tail leaked into the standard text.
        bled = [s["code"] for s in c["standards"] if TRAILING_STRAND.search(s["text"])]
        if bled:
            failures.append(f"{pfx}: strand letters left in standard text for {bled}")

        has_strand_col = any(s["strand"] for s in c["standards"])
        for s in c["standards"]:
            if has_strand_col and not s["strand"]:
                anomalies.append({
                    "course": slug, "code": s["code"], "page": s["sourcePage"],
                    "issue": "no Content Strand printed for this standard in the source PDF",
                })
            if s["strandRaw"] and not STRAND_STRICT.match(s["strandRaw"]):
                anomalies.append({
                    "course": slug, "code": s["code"], "page": s["sourcePage"],
                    "issue": f"Content Strand punctuation typo in the source PDF: "
                             f"{s['strandRaw']!r}",
                })

        payload = {
            "course": slug,
            "title": title,
            "printedTitle": " / ".join(c["printedTitles"]),
            "level": level,
            "standardsPrefix": pfx,
            "standardsYear": "2027-28",
            "description": c["description"],
            "source": {
                "document": "Tennessee Social Studies Standards",
                "file": pdf.name,
                "pages": c["pageRange"],
            },
            "provenance": "Official TDOE PDF — verbatim",
            "practices": c["practices"],
            "standardCount": len(c["standards"]),
            "geoCount": sum(1 for s in c["standards"] if s["geo"]),
            "tcaCount": sum(1 for s in c["standards"] if s["tca"]),
            "hasContentStrand": has_strand_col,
            "standards": c["standards"],
        }
        (outdir / f"{slug}.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        index.append({
            "course": slug, "title": title, "level": level, "standardsPrefix": pfx,
            "file": f"standards/{slug}.json", "standardCount": len(c["standards"]),
            "geoCount": payload["geoCount"], "tcaCount": payload["tcaCount"],
            "practiceCount": len(c["practices"]), "hasContentStrand": has_strand_col,
            "codeRange": [codes[0], codes[-1]], "sourcePages": c["pageRange"],
        })

    index.sort(key=lambda x: (["Elementary", "Middle", "High School"].index(x["level"]),
                              x["course"]))
    (outdir.parent / "index.json").write_text(json.dumps({
        "standardsYear": "2027-28",
        "document": "Tennessee Social Studies Standards",
        "sourceFile": f"source/{pdf.name}",
        "courseCount": len(index),
        "standardCount": sum(x["standardCount"] for x in index),
        "courses": index,
        "documentAnomalies": anomalies,
    }, indent=2, ensure_ascii=False) + "\n")

    for x in index:
        print(f"{x['standardsPrefix']:>3} | {x['title'][:38]:<38} {x['level']:<11} "
              f"{x['codeRange'][0]}-{x['codeRange'][1]:<7} std={x['standardCount']:>3} "
              f"geo={x['geoCount']:>3} tca={x['tcaCount']:>2} "
              f"strandCol={'y' if x['hasContentStrand'] else 'n'}")
    print(f"\n{len(index)} courses, {sum(x['standardCount'] for x in index)} standards")
    if anomalies:
        print(f"\n{len(anomalies)} source-document anomalies recorded in index.json:")
        for a in anomalies:
            print(f"  {a['code']:<8} p{a['page']:<4} {a['issue']}")
    if failures:
        print("\nPARSE FAILURES:")
        for f in failures:
            print("  -", f)
        return 1
    print("\nParse clean: table cross-check passed, no code gaps, no duplicates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
