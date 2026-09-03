#!/usr/bin/env python3
"""Run every gate against a built bank. Exit non-zero on any failure.

Usage:  python3 tools/run_gates.py [items_dir]

Prints the binding declaration first, always. First message of any build
session states the course, its standard-code prefix, the standards file being
read, and the output directory.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import binding as binding_mod
import itemio
from gates import record, coverage, content
from gates import forms as formgates

GATES = [
    record.gate_record_complete,
    record.gate_binding,
    record.gate_key_integrity,
    record.gate_distractor_coverage,
    record.gate_truncation,
    coverage.gate_blueprint,
    coverage.gate_blueprint_achievability,
    coverage.gate_key_position,
    coverage.gate_serveability,
    coverage.gate_reporting_category,
    # Content gates: what the bank is ABOUT, not how it was made.
    content.gate_signal_coverage,
    content.gate_standard_relevance,
    content.gate_choice_length_cue,
    content.gate_duplicate_stems,
    content.gate_citation_integrity,
    content.gate_translation_claim,
    content.gate_explanation_quality,
    content.gate_embedded_key,
    content.gate_review_provenance,
    content.gate_tcap_format,
    content.gate_rubric,
    content.gate_bias_review,
    content.gate_key_contradiction,
    content.gate_ai_review_boundary,
    content.gate_review_debt,
    # teacher-side-isolation is a FORM gate, not a bank gate: items at rest
    # carry no surface, so running it here could only ever be vacuous. It runs
    # once per rendered form, below.
    coverage.gate_release_readiness,
]


def run(items, b, gates=GATES):
    return [g(items, b) for g in gates]


def collect(b, target=None):
    """Every gate result for the whole artifact — bank and forms.

    One composition, shared by the runner and the status report, so the two can
    never disagree about what was measured.
    """
    import glob

    target = target or b.output_dir
    items = itemio.load_dir(target)
    results = run(items, b)

    for fd in sorted(d for d in glob.glob(os.path.join(itemio.BANK_ROOT, "forms", "*"))
                     if os.path.isdir(d)):
        fid = os.path.basename(fd)
        pdfs = sorted(glob.glob(os.path.join(fd, "*.pdf")))
        for g in (formgates.gate_form_pagination, formgates.gate_form_type_size,
                  formgates.gate_form_key_leakage, formgates.gate_form_disclosure,
                  formgates.gate_form_key_contradiction,
                  formgates.gate_form_teacher_metadata):
            r = g(pdfs, b); r.gate = f"{fid}/{r.gate}"; results.append(r)
        if os.path.exists(os.path.join(fd, "student-surface.json")):
            surface = itemio.load_dir(fd)
            r = coverage.gate_teacher_side_isolation(surface, b)
            r.gate = f"{fid}/teacher-side-isolation"
            results.append(r)
            r = coverage.gate_form_surface(surface, b)
            r.gate = f"{fid}/form-surface"
            results.append(r)
            man = os.path.join(fd, "manifest.json")
            decl = (json.load(open(man, encoding="utf-8")).get("standards")
                    if os.path.exists(man) else None)
            r = coverage.gate_form_blueprint(surface, b, standards=decl)
            r.gate = f"{fid}/form-blueprint"
            results.append(r)

    results.extend(collect_activities(b))
    results.append(coverage.unmeasured_gates(results))
    return items, results


# Bank-level gates cannot pass on a form scope: blueprint-conformance measures
# depth across all 94 standards, and release-readiness is a whole-artifact call.
# key-position-debias reads each item's STORED correctAnswer id; a form
# re-derives positions at render time, so the form uses gate_form_key_position.
_BANK_ONLY = {"gate_blueprint", "gate_blueprint_achievability",
              "gate_release_readiness", "gate_key_position"}
ITEM_GATES = [g for g in GATES if g.__name__ not in _BANK_ONLY]


def collect_activities(b):
    """Every gate that applies to the DBQ ACTIVITIES — a different surface.

    An activity is not a form: it has no answer key, no key position and no
    blueprint tier. Running the form gates over it would report N/A eleven
    times and prove nothing; running nothing over it would mean the newest
    deliverable in the repo is the only unmeasured one.
    """
    import glob
    root = os.path.join(itemio.BANK_ROOT, "deliverables", "dbq")
    out = []
    dirs = sorted(d for d in glob.glob(os.path.join(root, "*")) if os.path.isdir(d))
    if not dirs:
        return out
    pdfs = sorted(glob.glob(os.path.join(root, "*", "*.pdf")))
    for g in (formgates.gate_form_pagination, formgates.gate_form_type_size,
              formgates.gate_activity_sourcing, formgates.gate_activity_teacher_isolation):
        r = g(pdfs, b)
        r.gate = f"dbq-activities/{r.gate}"
        out.append(r)
    return out


def collect_form(b, form_id):
    """Every gate that applies to ONE form: its items and its rendered PDFs.

    A bank-wide run cannot show that a single form is clean, and a form is the
    unit a teacher actually hands out.
    """
    import glob
    fd = os.path.join(itemio.BANK_ROOT, "forms", form_id)
    surface = os.path.join(fd, "student-surface.json")
    with open(surface, encoding="utf-8") as fh:
        ids = [i["id"] for i in json.load(fh)["items"]]
    by_id = {i["id"]: i for i in itemio.load_dir(b.output_dir)}
    sel = [by_id[i] for i in ids if i in by_id]
    results = [g(sel, b) for g in ITEM_GATES]
    pdfs = sorted(glob.glob(os.path.join(fd, "*.pdf")))
    for g in (formgates.gate_form_pagination, formgates.gate_form_type_size,
              formgates.gate_form_key_leakage, formgates.gate_form_disclosure,
              formgates.gate_form_key_contradiction,
              formgates.gate_form_teacher_metadata):
        results.append(g(pdfs, b))
    rendered = itemio.load_dir(fd)
    results.append(coverage.gate_teacher_side_isolation(rendered, b))
    man = os.path.join(fd, "manifest.json")
    decl = (json.load(open(man, encoding="utf-8")).get("standards")
            if os.path.exists(man) else None)
    tiers = (json.load(open(man, encoding="utf-8")).get("tierByStandard")
             if os.path.exists(man) else None)
    results.append(coverage.gate_form_blueprint(rendered, b, standards=decl, tiers=tiers))
    results.append(coverage.gate_form_key_position(rendered, b))
    results.append(coverage.gate_form_surface(rendered, b))
    # Measured on the SOURCE items, not the rendered student surface. That
    # surface strips the key by design, and an item whose identifying signal
    # lives in its correct answer then reads as naming nothing — the Marshall
    # Plan item asks about "Marshall's speech" and names the Plan only in its
    # key. Relevance is a property of the ITEM, not of the printed page.
    results.append(coverage.gate_form_standard_relevance(sel, b, standards=decl))
    results.append(coverage.unmeasured_gates(results))
    return sel, results


def main(argv):
    b = binding_mod.load()
    print(b.declaration())
    print()
    if len(argv) > 2 and argv[1] == "--form":
        sel, results = collect_form(b, argv[2])
        print(f"Form {argv[2]} — {len(sel)} item(s)\n")
        for r in results:
            print(r.report())
        failed = [r for r in results if not r.counts_as_pass and not r.inapplicable]
        na = sum(1 for r in results if r.inapplicable)
        print(f"\n{len(results) - len(failed) - na}/{len(results) - na} applicable gates pass"
              + (f" ({na} N/A)" if na else "") + ".")
        if failed:
            print("HELD — " + ", ".join(r.gate for r in failed))
        else:
            print(f"Form {argv[2]} is GREEN on every gate that applies to it.")
        return 1 if failed else 0
    target = argv[1] if len(argv) > 1 else b.output_dir
    items, results = collect(b, target)
    print(f"Scanning {os.path.relpath(target, itemio.BANK_ROOT)} — {len(items)} item(s)\n")
    for r in results:
        print(r.report())
    # NOT MEASURED is not a pass. Counting it as one is how a vacuous gate
    # inflates the tally and reads exactly like a clean result.
    failed = [r for r in results if not r.counts_as_pass and not r.inapplicable]
    na = sum(1 for r in results if r.inapplicable)
    print()
    print(f"{len(results) - len(failed) - na}/{len(results) - na} applicable gates pass "
          f"({sum(1 for r in results if not r.measured and not r.inapplicable)} not measured"
          + (f", {na} N/A" if na else "") + ").")
    if failed:
        print("HELD — " + ", ".join(r.gate for r in failed))
        print('Grade A requires ALL gates pass. "Close" is not "A."')
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
