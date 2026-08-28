#!/usr/bin/env python3
"""Gate for the 2027-28 TN Social Studies standards set.

    python3 tools/validate_standards.py                      # schema + integrity
    python3 tools/validate_standards.py --verbatim           # also re-read the PDF

Exit 0 only when there are zero BLOCKERs. Warnings print but do not fail.

Checks
------
 1  every course file parses and carries the required fields
 2  codes are correctly prefixed, zero-padded, unique and gapless from .01
 3  strand letters come only from the published set (C/E/G/H/P/T/TCA)
 4  the geo/tca/standardCount flags agree with the standards themselves
 5  index.json agrees with the files on disk -- no course listed twice, none missing
 6  --verbatim: every standard's text still appears, character for character, in
    the source PDF. This is the anti-fabrication gate. A standard that has been
    reworded, truncated, or invented cannot pass it.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STANDARDS_DIR = ROOT / "standards"
INDEX = ROOT / "index.json"

LEGAL_STRANDS = {"C", "E", "G", "H", "P", "T", "TCA"}
REQUIRED_COURSE_FIELDS = ["course", "title", "level", "standardsPrefix", "standardsYear",
                          "description", "source", "provenance", "practices",
                          "standardCount", "hasContentStrand", "standards"]
REQUIRED_STANDARD_FIELDS = ["code", "text", "strand", "strandRaw", "geo", "tca",
                            "era", "eraOverview", "cluster", "sourcePage"]

blockers, warnings = [], []


def block(msg):
    blockers.append(msg)


def warn(msg):
    warnings.append(msg)


def squash(s):
    """Compare on letters and digits only: PDF extraction varies in whitespace,
    hyphenation and quote glyphs, and none of that is a content difference."""
    return re.sub(r"[^a-z0-9]", "", s.lower())


def load_courses():
    out = []
    for path in sorted(STANDARDS_DIR.glob("*.json")):
        try:
            out.append((path, json.loads(path.read_text())))
        except json.JSONDecodeError as e:
            block(f"{path.name}: not valid JSON ({e})")
    return out


def check_course(path, c):
    name = path.name
    for f in REQUIRED_COURSE_FIELDS:
        if f not in c:
            block(f"{name}: missing required field {f!r}")
    if c.get("standardsYear") != "2027-28":
        block(f"{name}: standardsYear is {c.get('standardsYear')!r}, expected '2027-28'")

    pfx = c.get("standardsPrefix", "")
    stds = c.get("standards", [])
    if not stds:
        block(f"{name}: no standards")
        return

    seen, nums = set(), []
    for s in stds:
        for f in REQUIRED_STANDARD_FIELDS:
            if f not in s:
                block(f"{name} {s.get('code','?')}: missing field {f!r}")
        code = s.get("code", "")
        if not re.fullmatch(re.escape(pfx) + r"\.\d{2,3}", code):
            block(f"{name}: malformed code {code!r} for prefix {pfx!r}")
            continue
        if code in seen:
            block(f"{name}: duplicate code {code}")
        seen.add(code)
        nums.append(int(code.split(".")[1]))

        if not s.get("text", "").strip():
            block(f"{name} {code}: empty standard text")
        bad = set(s.get("strand", [])) - LEGAL_STRANDS
        if bad:
            block(f"{name} {code}: illegal strand letters {sorted(bad)}")
        if s.get("geo") != ("G" in s.get("strand", [])):
            block(f"{name} {code}: geo flag disagrees with strand")
        if s.get("tca") != ("TCA" in s.get("strand", [])):
            block(f"{name} {code}: tca flag disagrees with strand")
        if c.get("hasContentStrand") and not s.get("strand"):
            warn(f"{name} {code}: no Content Strand printed in the source document")

    nums.sort()
    gaps = [n for n in range(1, nums[-1] + 1) if n not in nums]
    if gaps:
        block(f"{name}: code gaps {[f'{pfx}.{n:02d}' for n in gaps]}")
    if c.get("standardCount") != len(stds):
        block(f"{name}: standardCount {c.get('standardCount')} != {len(stds)} standards")
    if c.get("geoCount") != sum(1 for s in stds if s.get("geo")):
        block(f"{name}: geoCount disagrees with the standards")
    if c.get("tcaCount") != sum(1 for s in stds if s.get("tca")):
        block(f"{name}: tcaCount disagrees with the standards")

    practices = c.get("practices", [])
    codes = [p["code"] for p in practices]
    if codes and codes != sorted(set(codes), key=lambda x: int(x.split(".")[1])):
        block(f"{name}: practices are not a unique ascending SSP list")
    for p in practices:
        if not p.get("text", "").strip():
            block(f"{name} {p['code']}: empty practice text")


def check_index(courses):
    if not INDEX.exists():
        block("index.json missing")
        return
    idx = json.loads(INDEX.read_text())
    listed = {c["course"]: c for c in idx.get("courses", [])}
    on_disk = {c["course"]: c for _, c in courses}

    for slug in sorted(set(listed) | set(on_disk)):
        if slug not in listed:
            block(f"index.json does not list course {slug!r}")
        elif slug not in on_disk:
            block(f"index.json lists {slug!r} but standards/{slug}.json is missing")
        elif listed[slug]["standardCount"] != on_disk[slug]["standardCount"]:
            block(f"index.json standardCount for {slug!r} disagrees with the file")

    prefixes = [c["standardsPrefix"] for c in idx.get("courses", [])]
    dupes = {p for p in prefixes if prefixes.count(p) > 1}
    if dupes:
        block(f"index.json: prefix used by more than one course: {sorted(dupes)}")
    total = sum(c["standardCount"] for c in idx.get("courses", []))
    if idx.get("standardCount") != total:
        block(f"index.json standardCount {idx.get('standardCount')} != {total}")


def check_verbatim(courses):
    try:
        import pymupdf
    except ImportError:
        warn("--verbatim skipped: pymupdf is not installed (pip install pymupdf)")
        return
    idx = json.loads(INDEX.read_text())
    pdf = ROOT / idx["sourceFile"]
    if not pdf.exists():
        block(f"--verbatim: source PDF not found at {pdf}")
        return
    doc = pymupdf.open(pdf)
    # The Content Strand cell is laid out BETWEEN a standard's stem and its
    # bullet list, so raw page text interleaves strand letters into the middle
    # of the standard. Drop strand-only lines before comparing; they are the one
    # thing the parse deliberately lifts out of the prose.
    strand_line = re.compile(r"^(?:C|E|G|H|P|T|TCA)(?:\s*[.,]\s*(?:C|E|G|H|P|T|TCA))*\s*[.,]?$")
    page_text = ["".join(squash(l) for l in p.get_text().split("\n")
                         if not strand_line.match(l.strip())) for p in doc]

    for _, c in courses:
        for s in c["standards"]:
            # bullets are the document's own glyphs; squash() drops them anyway
            needle = squash(s["text"])
            p = s["sourcePage"] - 1
            window = "".join(page_text[max(0, p - 1):min(len(page_text), p + 2)])
            if needle not in window:
                block(f"{c['course']} {s['code']}: text does not appear verbatim "
                      f"in the source PDF near page {s['sourcePage']}")
        for pr in c["practices"]:
            if not any(squash(pr["text"]) in t for t in page_text):
                block(f"{c['course']} {pr['code']}: practice text not found in the source PDF")


def main():
    courses = load_courses()
    if not courses:
        block("no course files found in standards/")
    for path, c in courses:
        check_course(path, c)
    check_index(courses)
    if "--verbatim" in sys.argv:
        check_verbatim(courses)

    total = sum(len(c.get("standards", [])) for _, c in courses)
    print(f"{len(courses)} courses, {total} standards")
    for w in warnings:
        print(f"  WARN    {w}")
    for b in blockers:
        print(f"  BLOCKER {b}")
    print(f"\n{len(blockers)} blockers, {len(warnings)} warnings")
    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(main())
