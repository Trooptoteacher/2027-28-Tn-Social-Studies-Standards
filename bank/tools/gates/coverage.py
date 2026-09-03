"""Bank-level gates: blueprint conformance, answer-position de-bias,
serveability, reporting-category provenance, teacher-side leakage."""
from __future__ import annotations

import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import itemio
from gates import Finding, Result, empty_scan_guard


# --------------------------------------------------- blueprint conformance
def gate_blueprint(items, binding=None) -> Result:
    """The bank matches the committed blueprint per standard, per DOK, per item
    type. Fails on drift in EITHER direction.

    Only servable items count. A quarantined item is not coverage.
    """
    name = "blueprint-conformance"
    if (r := empty_scan_guard(name, items)):
        return r
    with open(binding.blueprint_file, encoding="utf-8") as fh:
        bp = json.load(fh)
    per = bp["perStandard"]
    live = [i for i in items if itemio.servable(i)]
    if not live:
        return Result(name, False, len(items),
                      [Finding("(none)", "no servable items — every item is quarantined or "
                                         "unauthored, so measured coverage is zero")],
                      note="EMPTY SCAN after servability filter")

    by_std = collections.defaultdict(list)
    for it in live:
        for c in (it.get("standardCodes") or []):
            by_std[c].append(it)

    findings = []
    for code in sorted(per):
        want = per[code]
        got = by_std.get(code, [])
        if len(got) != want["itemCount"]:
            findings.append(Finding(code, f"item count {len(got)} != blueprint {want['itemCount']}"))
        gd = collections.Counter(str(i.get("dokLevel")) for i in got)
        for lvl, n in sorted(want["dok"].items()):
            if gd.get(lvl, 0) != n:
                findings.append(Finding(code, f"DOK-{lvl} count {gd.get(lvl, 0)} != blueprint {n}"))
        gt = collections.Counter(i.get("itemType") for i in got)
        for typ, n in sorted(want["itemType"].items()):
            if gt.get(typ, 0) != n:
                findings.append(Finding(code, f"itemType {typ!r} count {gt.get(typ, 0)} != blueprint {n}"))
    return Result(name, not findings, len(live), findings,
                  note=f"{len(by_std)}/{len(per)} standards have >=1 servable item")


# ------------------------------------------------------ answer-position bias
# Chi-square critical values at p=0.01, df = k-1. No scipy in this toolchain.
_CHI2_CRIT_01 = {1: 6.635, 2: 9.210, 3: 11.345, 4: 13.277, 5: 15.086}


def gate_key_position(items, binding=None) -> Result:
    """Key positions distributed across the form.

    A bank where 60% of keys are C is a bank a student can beat without reading.
    Measured per position-count cohort (4-choice items judged against 4
    positions), chi-square against uniform at p<0.01.
    """
    name = "key-position-debias"
    if (r := empty_scan_guard(name, items)):
        return r
    live = [i for i in items if itemio.servable(i) and itemio.is_single_select(i)]
    if not live:
        return Result(name, False, len(items),
                      [Finding("(none)", "no servable single-select items to measure")],
                      note="EMPTY SCAN after servability filter")

    cohorts = collections.defaultdict(collections.Counter)
    positions = collections.defaultdict(set)
    for it in live:
        ids = [c.get("id") for c in itemio.choices(it) if isinstance(c, dict)]
        if not ids:
            continue
        cohorts[len(ids)][it.get("correctAnswer")] += 1
        positions[len(ids)].update(ids)

    findings, notes = [], []
    for k, counts in sorted(cohorts.items()):
        n = sum(counts.values())
        if k < 2:
            continue
        expected = n / k
        chi2 = sum((counts.get(p, 0) - expected) ** 2 / expected for p in positions[k])
        crit = _CHI2_CRIT_01.get(k - 1)
        share = {p: counts[p] / n for p in counts}
        worst = max(share, key=share.get) if share else None
        notes.append(f"{k}-choice n={n} worst={worst}@{share.get(worst, 0):.0%}")
        if crit and chi2 > crit:
            findings.append(Finding(f"{k}-choice cohort",
                f"key positions not uniform: chi2={chi2:.1f} > {crit} (p<0.01), n={n}, "
                f"distribution {dict(sorted(counts.items()))}"))
    return Result(name, not findings, len(live), findings, note="; ".join(notes))


# ----------------------------------------------------------- serveability
def gate_serveability(items, binding=None) -> Result:
    """Every item the app can route to actually resolves.

    An item that exists in a file and cannot be served is a coverage number
    that lies.
    """
    name = "serveability"
    if (r := empty_scan_guard(name, items)):
        return r
    live = [i for i in items if itemio.servable(i)]
    if not live:
        return Result(name, False, len(items),
                      [Finding("(none)", "no servable items in bank")],
                      note="EMPTY SCAN after servability filter")
    valid = binding.valid_codes()
    findings = []
    for it in live:
        for code in (it.get("standardCodes") or []):
            if code not in valid:
                findings.append(Finding(it.get("id", "?"),
                    f"routes to standard {code!r} which does not exist", it.get("_file", "")))
        for f in ("stemEs", "explanationEs"):
            if not (it.get(f) or "").strip():
                findings.append(Finding(it.get("id", "?"),
                    f"bilingual field {f} absent — item cannot be served in Spanish",
                    it.get("_file", "")))
        img = it.get("image")
        if img:
            src = img.get("src", "")
            root = os.path.dirname(binding.blueprint_file)
            path = os.path.join(itemio.BANK_ROOT, src.lstrip("/"))
            if not os.path.exists(path):
                findings.append(Finding(it.get("id", "?"),
                    f"image {src!r} does not resolve on disk", it.get("_file", "")))
            for a in ("alt", "altEs"):
                if not (img.get(a) or "").strip():
                    findings.append(Finding(it.get("id", "?"),
                        f"image carries no {a} text", it.get("_file", "")))
        if it.get("calibrationStatus") != "pre-field-test" and not it.get("irtParameters"):
            findings.append(Finding(it.get("id", "?"),
                f"calibrationStatus {it.get('calibrationStatus')!r} claimed with no irtParameters",
                it.get("_file", "")))
    return Result(name, not findings, len(live), findings)


# --------------------------------------------- reporting-category provenance
def gate_reporting_category(items, binding=None) -> Result:
    """Provenance, not plausibility.

    A plausibility check built on the standards' strand letters was measured
    against the existing 2026-27 bank: it flagged 11 items of 4,189 and PASSED
    the known-bad one (a Bessemer-process stem filed under Government and
    Civics, whose standard carries strands C and P). A gate that passes the
    defect it exists to catch is worse than no gate.

    So: every item's category must match the committed mapping file for its
    standard, and the mapping's source must be declared. Drift becomes
    impossible; a wrong category becomes a reviewable decision in a file.
    """
    name = "reporting-category-provenance"
    if (r := empty_scan_guard(name, items)):
        return r
    with open(binding.reporting_category_file, encoding="utf-8") as fh:
        rc = json.load(fh)
    mapping = rc["standards"]
    findings = []
    unmapped = 0
    for it in items:
        src = it.get("reportingCategorySource")
        if src not in ("tdoe-blueprint", "interim-district", "UNMAPPED"):
            findings.append(Finding(it.get("id", "?"),
                f"reportingCategorySource {src!r} is not a declared source", it.get("_file", "")))
            continue
        for code in (it.get("standardCodes") or []):
            row = mapping.get(code)
            if row is None:
                findings.append(Finding(it.get("id", "?"),
                    f"standard {code!r} has no row in the reporting-category mapping",
                    it.get("_file", "")))
                continue
            if row["source"] == "UNMAPPED":
                unmapped += 1
                if src != "UNMAPPED" or it.get("reportingCategory") is not None:
                    findings.append(Finding(it.get("id", "?"),
                        f"claims category {it.get('reportingCategory')!r} for {code}, but the "
                        f"mapping has no source for it — an unsourced category is a "
                        f"psychometric claim the bank cannot support", it.get("_file", "")))
            else:
                if it.get("reportingCategory") != row["category"]:
                    findings.append(Finding(it.get("id", "?"),
                        f"category {it.get('reportingCategory')!r} disagrees with mapping "
                        f"{row['category']!r} for {code}", it.get("_file", "")))
                if src != row["source"]:
                    findings.append(Finding(it.get("id", "?"),
                        f"source {src!r} disagrees with mapping source {row['source']!r} for {code}",
                        it.get("_file", "")))
    note = (f"{unmapped} item/standard pair(s) awaiting a category source "
            f"(mapping sourceOfRecord={rc.get('sourceOfRecord')!r})") if unmapped else ""
    return Result(name, not findings, len(items), findings, note=note)


# ---------------------------------------------------- teacher-side leakage
_TEACHER_ONLY = ("correctAnswer", "explanation", "explanationEs", "dokRationale", "reteach")


def gate_teacher_side_isolation(items, binding=None) -> Result:
    """Answer keys, rationales and reteach guidance are teacher-side only and
    never reachable from a student path.

    Enforced on the artifact: a student-tier FORM must carry no key material.
    Hiding a link leaves the file one request away — this measures the file.
    """
    name = "teacher-side-isolation"
    if (r := empty_scan_guard(name, items)):
        return r
    findings = []
    for it in items:
        if it.get("bankTier") != "student":
            continue
        if it.get("_surface") != "student-form":
            continue
        leaked = [f for f in _TEACHER_ONLY if it.get(f) not in (None, "")]
        leaked += [f"choice.{c.get('id')}.explanation" for c in itemio.choices(it)
                   if isinstance(c, dict) and (c.get("explanation") or "").strip()]
        if leaked:
            findings.append(Finding(it.get("id", "?"),
                f"student-facing surface carries teacher-only field(s) {leaked}",
                it.get("_file", "")))
    return Result(name, not findings, len(items), findings,
                  note="measures rendered student surfaces; items at rest are teacher-side by default")
