#!/usr/bin/env python3
"""Proves every eraOverview / document-fingerprint blocker actually fires.

    python3 tools/validate_standards_selftest.py

A gate nobody has watched fail is indistinguishable from one that cannot fail.
eraOverview shipped empty on 491 of 1,012 standards while `validate_standards.py`
exited 0 the whole time -- the field was PRESENT, which is all the required-field
check measured, and an empty string is verbatim by construction. So each case
below takes the real shipped data, breaks exactly one thing, and requires the
named blocker.

Half the cases are NEGATIVE CONTROLS. A blocker that rejects legitimate work
looks identical to one that works until something exercises the allowed shape:
two eras may legitimately share one Overview paragraph, a course's standards all
sit on different pages from their Overview, and an overview paragraph may wrap
across a leaf. Those must PASS.
"""
import copy
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_standards as V

ROOT = Path(__file__).resolve().parent.parent
BASE_FILE = ROOT / "standards" / "us-history-geography.json"
INDEX_FILE = ROOT / "index.json"

cases, failures = [], []


def case(name, fn, expect):
    """expect: a substring of the blocker that must fire, or None for a control."""
    cases.append((name, fn, expect))


def run_checks(course, index=None, verbatim=False):
    """Run the gate against one in-memory course file.

    The index is trimmed to the course under test: check_index compares the
    listing against the courses handed to it, so a full 20-course index beside
    a single fixture blocks on the nineteen it cannot see -- which is a
    property of the harness, not a finding.
    """
    V.blockers, V.warnings = [], []
    path = Path("fixture.json")
    V.check_course(path, course)
    V.check_era_overviews(path, course)
    if index is not None:
        slug = course.get("course")
        idx = dict(index)
        if "courses" in idx:
            idx["courses"] = [c for c in idx["courses"] if c["course"] == slug]
            idx["courseCount"] = len(idx["courses"])
            idx["standardCount"] = sum(c["standardCount"] for c in idx["courses"])
        orig = V.INDEX
        tmp = ROOT / ".selftest-index.json"
        tmp.write_text(json.dumps(idx))
        V.INDEX = tmp
        try:
            V.check_index([(path, course)])
            if verbatim:
                V.check_verbatim([(path, course)])
        finally:
            V.INDEX = orig
            tmp.unlink(missing_ok=True)
    return list(V.blockers)


def base():
    return json.loads(BASE_FILE.read_text())


def base_index():
    return json.loads(INDEX_FILE.read_text())


# ----- 6a: a value at all -------------------------------------------------
def c_empty_overview():
    c = base()
    c["standards"][0]["eraOverview"] = ""
    return run_checks(c)


def c_whitespace_overview():
    c = base()
    c["standards"][0]["eraOverview"] = "   "
    return run_checks(c)


def c_no_page():
    c = base()
    c["standards"][0]["eraOverviewSourcePage"] = 0
    return run_checks(c)


def c_page_is_a_string():
    c = base()
    c["standards"][0]["eraOverviewSourcePage"] = "225"
    return run_checks(c)


def c_field_absent():
    c = base()
    del c["standards"][0]["eraOverviewSourcePage"]
    return run_checks(c)


# ----- 6b: one heading, one overview; contiguous runs --------------------
def _cluster_with_several(c):
    counts = {}
    for s in c["standards"]:
        counts.setdefault(s["cluster"], []).append(s)
    for cl, ss in counts.items():
        if len(ss) >= 3:
            return ss
    raise AssertionError("fixture no longer has a cluster of 3+ standards")


def c_cluster_reworded():
    """REWORDED on one standard of a heading -- not empty, so 6a cannot see it.
    One heading has one Overview, so this is two claims about one paragraph
    even though both look like content."""
    c = base()
    ss = _cluster_with_several(c)
    ss[1]["eraOverview"] = ss[1]["eraOverview"].replace("Students will", "Pupils will")
    return run_checks(c)


def c_cluster_page_disagrees():
    """Same text, different cited page, inside one heading. The text check
    alone passes it; the page is what a reader would open."""
    c = base()
    ss = _cluster_with_several(c)
    ss[1]["eraOverviewSourcePage"] = ss[1]["eraOverviewSourcePage"] + 1
    return run_checks(c)


def c_run_not_contiguous():
    """A single stale value in the MIDDLE of a run. Given its own cluster it
    slips past 6b(i), which is why contiguity exists as well."""
    c = base()
    # take a standard in the middle of the first era's run and give it both a
    # different overview and a cluster of its own
    first_era = c["standards"][0]["era"]
    run = [s for s in c["standards"] if s["era"] == first_era]
    assert len(run) >= 5
    victim = run[2]
    other = next(s for s in c["standards"] if s["era"] != first_era)
    victim["eraOverview"] = other["eraOverview"]
    victim["eraOverviewSourcePage"] = other["eraOverviewSourcePage"]
    victim["cluster"] = "A Cluster Of Its Own"
    # keep the table honest so the failure under test is the contiguity one
    import copy as _c
    row = _c.deepcopy(next(r for r in c["eraOverviews"]
                           if r["overview"] == other["eraOverview"]))
    row["standards"] = {"first": victim["code"], "last": victim["code"], "count": 1}
    row["cluster"] = victim["cluster"]
    c["eraOverviews"].append(row)
    for r in c["eraOverviews"]:
        if r["overview"] == c["standards"][0]["eraOverview"]:
            r["standards"]["count"] -= 1
    return run_checks(c)


def c_overview_shared_across_eras():
    """An era INHERITING the previous era's Overview -- the silent-wrong shape.

    Every other check here passes it: the value is non-empty, its cited page is
    where that text really is, the run is contiguous, and each heading agrees
    with itself. This is the only case that catches it, and it is what makes the
    parser's clear-on-a-new-era line watched.
    """
    c = base()
    a, b = c["eraOverviews"][0], c["eraOverviews"][1]
    b["overview"], b["sourcePage"] = a["overview"], a["sourcePage"]
    for s in c["standards"]:
        if s["era"] == b["era"]:
            s["eraOverview"], s["eraOverviewSourcePage"] = a["overview"], a["sourcePage"]
    return run_checks(c, index=base_index(), verbatim=True)


# ----- 6c: the table and the standards must agree ------------------------
def c_table_row_unused():
    c = base()
    r = copy.deepcopy(c["eraOverviews"][0])
    r["era"] = "An Era Nothing Points At (1900-1901)"
    c["eraOverviews"].append(r)
    return run_checks(c)


def c_table_overview_reworded():
    """The table is what a reader checks a value against, so a table that has
    drifted from the standards is worse than no table."""
    c = base()
    c["eraOverviews"][0]["overview"] = c["eraOverviews"][0]["overview"].replace(
        "Students", "Learners")
    return run_checks(c)


def c_table_page_moved():
    c = base()
    c["eraOverviews"][0]["sourcePage"] = 999
    return run_checks(c)


def c_table_count_wrong():
    c = base()
    c["eraOverviews"][0]["standards"]["count"] += 1
    return run_checks(c)


def c_table_absent():
    c = base()
    del c["eraOverviews"]
    return run_checks(c)


# ----- 7: the document's fingerprint ------------------------------------
def c_no_sha():
    c = base()
    del c["source"]["sha256"]
    return run_checks(c)


def c_malformed_sha():
    c = base()
    c["source"]["sha256"] = "not-a-hash"
    return run_checks(c)


def c_sha_disagrees_with_index():
    c = base()
    c["source"]["sha256"] = "0" * 64
    return run_checks(c, index=base_index())


def c_index_no_sha():
    c = base()
    idx = base_index()
    del idx["sourceSha256"]
    return run_checks(c, index=idx)


def c_index_no_extracted_at():
    c = base()
    idx = base_index()
    del idx["extractedAt"]
    return run_checks(c, index=idx)


# ----- 8: --verbatim, the overview on the page it cites -----------------
def c_verbatim_wrong_page():
    """A page reference is correct when written and silently wrong afterwards.
    The window is the cited page and the next one ONLY, so a paragraph that is
    really elsewhere in the document still fails."""
    c = base()
    c["eraOverviews"][0]["sourcePage"] = 100
    for s in c["standards"]:
        if s["era"] == c["eraOverviews"][0]["era"]:
            s["eraOverviewSourcePage"] = 100
    return run_checks(c, index=base_index(), verbatim=True)


def c_verbatim_page_off_document():
    c = base()
    c["eraOverviews"][0]["sourcePage"] = 9999
    for s in c["standards"]:
        if s["era"] == c["eraOverviews"][0]["era"]:
            s["eraOverviewSourcePage"] = 9999
    return run_checks(c, index=base_index(), verbatim=True)


def c_verbatim_fabricated_overview():
    """The anti-fabrication case: a plausible Overview sentence in the state's
    own register that the document does not contain."""
    c = base()
    txt = ("Students will analyze the enduring significance of the period and "
           "evaluate its legacy for the modern United States.")
    c["eraOverviews"][0]["overview"] = txt
    for s in c["standards"]:
        if s["era"] == c["eraOverviews"][0]["era"]:
            s["eraOverview"] = txt
    return run_checks(c, index=base_index(), verbatim=True)


def c_verbatim_truncated_overview():
    """Truncation, not invention -- still a differing claim, and the shape a
    character cap produces."""
    c = base()
    ov = c["eraOverviews"][0]["overview"]
    bad = ov[:len(ov) // 2] + " and other topics."
    c["eraOverviews"][0]["overview"] = bad
    for s in c["standards"]:
        if s["era"] == c["eraOverviews"][0]["era"]:
            s["eraOverview"] = bad
    return run_checks(c, index=base_index(), verbatim=True)


# ----- 9: the document moved underneath the references ------------------
def c_document_moved():
    c = base()
    idx = base_index()
    idx["sourceSha256"] = "f" * 64
    c["source"]["sha256"] = "f" * 64
    return run_checks(c, index=idx, verbatim=True)


# ----- NEGATIVE CONTROLS ------------------------------------------------
def n_shipped_data_passes():
    """The whole point. If this fires, the gate is rejecting the document's own
    content and every case above is measuring noise."""
    return run_checks(base(), index=base_index(), verbatim=True)


# WITHDRAWN CONTROL -- "two eras may share one overview".
#
# It asserted that nothing in the document forbids two ERAS printing the same
# Overview paragraph, and it passed for as long as nothing contradicted it. The
# premise was never measured. Measured across all 20 courses: ZERO
# (overview, page) pairs serve two different eras, and the one real duplicate
# TDOE prints is inside a SINGLE era under two CLUSTER headings (Sociology
# p194/p195) -- which is the control two functions below, built from the
# shipped file rather than from an assumption.
#
# So the shape this control defended is not a shape the document contains, and
# it is exactly what an era inheriting the previous era's Overview produces.
# It is now the FAILURE case c_overview_shared_across_eras. Recorded here in
# place rather than deleted, because a control removed without its reason looks
# like a gate that was loosened to make something pass.


def n_overview_page_differs_from_standard_page():
    """Legitimate and universal: the Overview is printed once at the head of an
    era and the standards run for pages after it, so the two page numbers are
    SUPPOSED to differ. A gate requiring them equal would fail all 1,012."""
    c = base()
    off = [s for s in c["standards"] if s["sourcePage"] != s["eraOverviewSourcePage"]]
    if not off:
        raise AssertionError("fixture no longer exercises the allowed shape")
    return run_checks(c, index=base_index(), verbatim=True)


def n_course_with_one_era():
    """A course whose whole standard set sits under one era heading is the
    document's own shape for several courses, not a parse failure."""
    c = base()
    era = c["standards"][0]["era"]
    row = copy.deepcopy(c["eraOverviews"][0])
    for s in c["standards"]:
        s["era"] = era
        s["eraOverview"] = row["overview"]
        s["eraOverviewSourcePage"] = row["sourcePage"]
        s["cluster"] = s["cluster"] or era
    row["standards"] = {"first": c["standards"][0]["code"],
                        "last": c["standards"][-1]["code"],
                        "count": len(c["standards"])}
    c["eraOverviews"] = [row]
    return run_checks(c, index=base_index(), verbatim=True)


def n_same_overview_under_two_headings():
    """THE SHAPE THAT FAILED THE FIRST VERSION OF THIS GATE, and it is the
    document's own: TDOE prints one Overview paragraph verbatim under both
    "Self and Socialization" (p194) and "Functions and Structures of Social
    Institutions" (p195) in Sociology. Two headings, two pages, one paragraph.
    A gate keyed on the text alone gives the second printing no table row and
    then blocks all thirteen standards citing it."""
    path = ROOT / "standards" / "sociology.json"
    c = json.loads(path.read_text())
    pages = {}
    for s in c["standards"]:
        pages.setdefault(s["eraOverview"], set()).add(s["eraOverviewSourcePage"])
    if not any(len(v) > 1 for v in pages.values()):
        raise AssertionError("sociology no longer exercises the allowed shape")
    return run_checks(c, index=base_index(), verbatim=True)


def n_era_may_hold_many_overviews():
    """Also the document's own: where the era heading is only a course banner
    ("S | SOCIOLOGY") the document prints an Overview per TOPIC heading under
    it. Scoping the check to the era blocked 12 of the 20 courses."""
    path = ROOT / "standards" / "world-geography.json"
    c = json.loads(path.read_text())
    eras = {}
    for s in c["standards"]:
        eras.setdefault(s["era"], set()).add(s["eraOverview"])
    if not any(len(v) > 1 for v in eras.values()):
        raise AssertionError("world-geography no longer exercises the allowed shape")
    return run_checks(c, index=base_index(), verbatim=True)


def n_sha_case_is_lowercase_hex():
    """Control on the hash FORMAT check: the real recorded hash must pass it."""
    c = base()
    assert re.fullmatch(r"[0-9a-f]{64}", c["source"]["sha256"])
    return run_checks(c)


case("empty eraOverview blocks", c_empty_overview, "eraOverview is empty")
case("whitespace-only eraOverview blocks", c_whitespace_overview, "eraOverview is empty")
case("eraOverview with page 0 blocks", c_no_page, "carries no source page")
case("non-integer page blocks", c_page_is_a_string, "carries no source page")
case("absent eraOverviewSourcePage blocks", c_field_absent, "missing field")
case("a reworded overview on one standard of a heading blocks", c_cluster_reworded,
     "different eraOverview")
case("same text, disagreeing page inside one heading blocks", c_cluster_page_disagrees,
     "different eraOverview")
case("a stale value mid-run blocks on contiguity", c_run_not_contiguous,
     "non-contiguous run")
case("one overview serving two different eras blocks", c_overview_shared_across_eras,
     "different eras")
case("a table row no standard uses blocks", c_table_row_unused, "no standard uses it")
case("a drifted table overview blocks", c_table_overview_reworded, "absent "
     "from the course's eraOverviews table")
case("a drifted table page blocks", c_table_page_moved, "absent "
     "from the course's eraOverviews table")
case("a wrong table count blocks", c_table_count_wrong, "rows account for")
case("an absent eraOverviews table blocks", c_table_absent, "missing required field")
case("missing source.sha256 blocks", c_no_sha, "source.sha256 is missing")
case("malformed source.sha256 blocks", c_malformed_sha, "source.sha256 is missing or malformed")
case("course sha disagreeing with index blocks", c_sha_disagrees_with_index,
     "disagrees with")
case("index.json with no sourceSha256 blocks", c_index_no_sha, "sourceSha256 is missing")
case("index.json with no extractedAt blocks", c_index_no_extracted_at, "no extractedAt")
case("--verbatim: overview on the wrong page blocks", c_verbatim_wrong_page,
     "does not appear verbatim on page")
case("--verbatim: page off the end of the document blocks", c_verbatim_page_off_document,
     "outside the")
case("--verbatim: a fabricated overview blocks", c_verbatim_fabricated_overview,
     "does not appear verbatim on page")
case("--verbatim: a truncated overview blocks", c_verbatim_truncated_overview,
     "does not appear verbatim on page")
case("--verbatim: a moved source document blocks", c_document_moved,
     "the document moved underneath")
case("CONTROL: the shipped data passes", n_shipped_data_passes, None)
case("CONTROL: overview page may differ from the standard's page",
     n_overview_page_differs_from_standard_page, None)
case("CONTROL: a course with a single era passes", n_course_with_one_era, None)
case("CONTROL: one Overview under two headings passes (Sociology p194/p195)",
     n_same_overview_under_two_headings, None)
case("CONTROL: a banner era holding many Overviews passes (World Geography)",
     n_era_may_hold_many_overviews, None)
case("CONTROL: the real hash passes the format check", n_sha_case_is_lowercase_hex, None)


def main():
    print(f"{len(cases)} cases "
          f"({sum(1 for _, _, e in cases if e is None)} negative controls)\n")
    for name, fn, expect in cases:
        try:
            got = fn()
        except Exception as e:                      # a crash is a failure
            failures.append(f"{name}: raised {e!r}")
            print(f"  ERROR {name}: {e!r}")
            continue
        if expect is None:
            if got:
                failures.append(f"{name}: expected no blocker, got {got}")
                print(f"  FAIL  {name}")
                for b in got[:4]:
                    print(f"          {b}")
            else:
                print(f"  ok    {name}")
        else:
            if any(expect in b for b in got):
                print(f"  ok    {name}")
            else:
                failures.append(f"{name}: no blocker containing {expect!r}; got {got}")
                print(f"  FAIL  {name}: no blocker containing {expect!r}")
                for b in got[:4]:
                    print(f"          {b}")
    print(f"\n{len(cases) - len(failures)}/{len(cases)} passed")
    if failures:
        print("\nSELFTEST FAILED")
        return 1
    print("SELFTEST PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
