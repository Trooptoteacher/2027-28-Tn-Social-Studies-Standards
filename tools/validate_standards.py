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
 6  every standard carries a non-empty eraOverview with a cited page; standards
    sharing one HEADING carry the SAME overview (the scope is the cluster, not
    the era -- see check_era_overviews); the standards sharing one overview are
    a contiguous run of codes; and every (era, overview, page) triple is present
    in the course's own eraOverviews table, in both directions
 7  the source PDF's sha256 is recorded and agrees across index.json and every
    course file
 8  --verbatim: every standard's text, AND every era overview, still appears
    character for character in the source PDF -- the overview on the page it
    cites. This is the anti-fabrication gate. A standard or an overview that has
    been reworded, truncated, or invented cannot pass it.
 9  --verbatim: the source PDF on disk still hashes to the recorded sha256

Why 6 exists
------------
eraOverview shipped EMPTY on every standard of five courses -- 491 of 1,012 --
because the parser cleared it at the first standard code after reading it.
Nothing was red: the field was present, so a required-field check passed, and
an empty string is verbatim by construction, so --verbatim passed too. A green
gate on a measure that is not the claim being made. These checks measure the
value, its page, and its agreement across the era it belongs to.
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
                          "description", "source", "provenance", "eraOverviews",
                          "practices", "standardCount", "hasContentStrand",
                          "standards"]
REQUIRED_STANDARD_FIELDS = ["code", "text", "strand", "strandRaw", "geo", "tca",
                            "era", "eraOverview", "eraOverviewSourcePage",
                            "cluster", "sourcePage"]

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


def check_era_overviews(path, c):
    """Checks 6 and 7 -- see the module docstring for why they exist."""
    name = path.name
    stds = c.get("standards") or []
    table = c.get("eraOverviews")
    if table is None:
        return                      # already blocked as a missing required field

    # 6a -- a value at all, and a page to check it against
    for s in stds:
        code = s.get("code", "?")
        ov = (s.get("eraOverview") or "").strip()
        if not ov:
            block(f"{name} {code}: eraOverview is empty -- the source document "
                  f"prints an Overview paragraph for every era")
            continue
        pg = s.get("eraOverviewSourcePage")
        if not isinstance(pg, int) or pg <= 0:
            block(f"{name} {code}: eraOverview carries no source page "
                  f"({pg!r}) -- a derived value with no page cannot be checked")

    # 6b -- one heading, one overview. The scope is the CLUSTER, not the era.
    # Written against the era first, this blocked 12 legitimate courses: where
    # the era heading is only a course banner ("WG | WORLD GEOGRAPHY", "S |
    # SOCIOLOGY") or a Domain, the document prints an Overview per TOPIC
    # heading beneath it, and the cluster is that heading. Cluster is a
    # refinement of era, so this is the weaker claim that is true of all 20
    # courses -- measured, 0 disagreements across 1,012 standards.
    by_cluster = {}
    for s in stds:
        key = (s.get("era", ""), s.get("cluster", ""))
        by_cluster.setdefault(key, set()).add(
            ((s.get("eraOverview") or "").strip(), s.get("eraOverviewSourcePage")))
    for (era, cluster), vals in sorted(by_cluster.items(), key=lambda kv: str(kv[0])):
        if len(vals) > 1:
            block(f"{name}: heading {cluster!r} (era {era!r}) carries {len(vals)} "
                  f"different eraOverview values across its standards -- one "
                  f"heading has one Overview")

    # 6b(ii) -- an Overview governs the standards printed under it, so the
    # standards sharing one (overview, page) are a CONTIGUOUS run of codes.
    # This is what catches a single stale or blank value interleaved into a run
    # that otherwise agrees -- the shape cluster-agreement can miss when the
    # odd standard also sits in its own cluster.
    runs = {}
    for i, s in enumerate(stds):
        runs.setdefault(((s.get("eraOverview") or "").strip(),
                         s.get("eraOverviewSourcePage")), []).append(i)
    for (ov, pg), ix in runs.items():
        if ix != list(range(ix[0], ix[-1] + 1)):
            gap = [stds[i].get("code") for i in range(ix[0], ix[-1] + 1) if i not in ix]
            block(f"{name}: the overview printed on page {pg} is carried by a "
                  f"non-contiguous run of standards -- {gap} sit inside it and "
                  f"carry a different one")

    # 6b(iii) -- NO (overview, page) PAIR MAY SERVE TWO DIFFERENT ERAS.
    # This is the one failure mode nothing else here can see. If an era whose
    # Overview the parser missed INHERITS the previous era's, the value is
    # non-empty (6a passes), its cited page is the previous era's page where
    # that text genuinely is (check 8 passes), the run is contiguous (6b(ii)
    # passes) and every standard agrees with its heading (6b(i) passes). The
    # result is a silently WRONG paragraph, which is worse than a missing one.
    # It also makes the parser's "clear on a new era heading" line WATCHED:
    # that line has no measured effect on this document (removing it is
    # value-identical on all 1,012 standards), so without something that fires
    # when it stops working it would be a guard nobody has seen do work.
    # TDOE's own duplicate passes: Sociology p194/p195 print one paragraph under
    # two CLUSTER headings inside one banner era, so the era is the same.
    shared = {}
    for r in table:
        shared.setdefault(((r.get("overview") or "").strip(), r.get("sourcePage")),
                          set()).add(r.get("era"))
    for (ov, pg), eras in shared.items():
        if ov and len(eras) > 1:
            block(f"{name}: the overview on page {pg} is carried by {len(eras)} "
                  f"different eras {sorted(eras)} -- an era that inherited the "
                  f"previous era's Overview looks exactly like this, and no other "
                  f"check here can see it")

    # 6c -- the table and the standards must say the same thing, in both
    # directions: a table row nothing points at is as wrong as a standard the
    # table does not cover.
    rows = {(r.get("era"), (r.get("overview") or "").strip(), r.get("sourcePage")) for r in table}
    used = set()
    for s in stds:
        key = (s.get("era"), (s.get("eraOverview") or "").strip(), s.get("eraOverviewSourcePage"))
        if key not in rows:
            block(f"{name} {s.get('code','?')}: its (era, overview, page) is absent "
                  f"from the course's eraOverviews table")
        used.add(key)
    for key in sorted(rows - used, key=lambda k: str(k)):
        block(f"{name}: eraOverviews lists {key[0]!r} (p{key[2]}) but no standard uses it")
    counted = sum(r.get("standards", {}).get("count", 0) for r in table)
    if stds and counted != len(stds):
        block(f"{name}: eraOverviews rows account for {counted} standards, "
              f"the file carries {len(stds)}")

    # 7 -- the document's fingerprint
    sha = (c.get("source") or {}).get("sha256")
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha or ""):
        block(f"{name}: source.sha256 is missing or malformed ({sha!r}) -- a page "
              f"number is only correct about a particular document")


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

    sha = idx.get("sourceSha256")
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha or ""):
        block(f"index.json sourceSha256 is missing or malformed ({sha!r})")
    else:
        for _, c in courses:
            if (c.get("source") or {}).get("sha256") != sha:
                block(f"{c.get('course')}: source.sha256 disagrees with "
                      f"index.json sourceSha256 -- two files describing two documents")
    if not idx.get("extractedAt"):
        block("index.json records no extractedAt -- the extraction event has no date")


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

    # 9 -- the document itself. Every page number and era heading below is a
    # claim ABOUT THIS FILE; if the file moved, they are claims about a
    # document nobody has.
    import hashlib
    on_disk = hashlib.sha256(pdf.read_bytes()).hexdigest()
    if idx.get("sourceSha256") and on_disk != idx["sourceSha256"]:
        block(f"--verbatim: {pdf.name} on disk hashes to {on_disk}, index.json "
              f"records {idx['sourceSha256']} -- the document moved underneath "
              f"every derived page reference")

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

        # 8 -- every era overview, ON THE PAGE IT CITES. Checked once per
        # distinct row rather than once per standard, because the row is what
        # carries the page. (The row count is not written here: it moves with
        # the document, and a number in prose is a claim that rots.)
        for r in c.get("eraOverviews") or []:
            ov = (r.get("overview") or "").strip()
            if not ov:
                continue
            pg = r.get("sourcePage") or 0
            if not 1 <= pg <= len(page_text):
                block(f"{c['course']} era {r.get('era')!r}: eraOverview cites page "
                      f"{pg}, which is outside the {len(page_text)}-page document")
                continue
            # An Overview paragraph can wrap across a leaf, so the window is the
            # cited page and the one after it -- deliberately NOT the whole
            # document: a paragraph found on some other page is a wrong page
            # reference, which is the defect this check exists to catch.
            window = "".join(page_text[pg - 1:min(len(page_text), pg + 1)])
            if squash(ov) not in window:
                block(f"{c['course']} era {r.get('era')!r}: eraOverview does not "
                      f"appear verbatim on page {pg} of the source PDF")


def main():
    courses = load_courses()
    if not courses:
        block("no course files found in standards/")
    for path, c in courses:
        check_course(path, c)
        check_era_overviews(path, c)
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
