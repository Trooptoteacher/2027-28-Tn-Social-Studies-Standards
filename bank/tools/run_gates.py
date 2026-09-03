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
    coverage.gate_key_position,
    coverage.gate_serveability,
    coverage.gate_reporting_category,
    # Content gates: what the bank is ABOUT, not how it was made.
    content.gate_standard_relevance,
    content.gate_choice_length_cue,
    content.gate_duplicate_stems,
    content.gate_citation_integrity,
    content.gate_translation_claim,
    content.gate_explanation_quality,
    content.gate_embedded_key,
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
                  formgates.gate_form_key_leakage, formgates.gate_form_disclosure):
            r = g(pdfs, b); r.gate = f"{fid}/{r.gate}"; results.append(r)
        if os.path.exists(os.path.join(fd, "student-surface.json")):
            surface = itemio.load_dir(fd)
            r = coverage.gate_teacher_side_isolation(surface, b)
            r.gate = f"{fid}/teacher-side-isolation"
            results.append(r)
            man = os.path.join(fd, "manifest.json")
            decl = (json.load(open(man, encoding="utf-8")).get("standards")
                    if os.path.exists(man) else None)
            r = coverage.gate_form_blueprint(surface, b, standards=decl)
            r.gate = f"{fid}/form-blueprint"
            results.append(r)

    results.append(coverage.unmeasured_gates(results))
    return items, results


def main(argv):
    b = binding_mod.load()
    print(b.declaration())
    print()
    target = argv[1] if len(argv) > 1 else b.output_dir
    items, results = collect(b, target)
    print(f"Scanning {os.path.relpath(target, itemio.BANK_ROOT)} — {len(items)} item(s)\n")
    for r in results:
        print(r.report())
    # NOT MEASURED is not a pass. Counting it as one is how a vacuous gate
    # inflates the tally and reads exactly like a clean result.
    failed = [r for r in results if not (r.passed and r.measured)]
    print()
    print(f"{len(results) - len(failed)}/{len(results)} gates pass "
          f"({sum(1 for r in results if not r.measured)} not measured).")
    if failed:
        print("HELD — " + ", ".join(r.gate for r in failed))
        print('Grade A requires ALL gates pass. "Close" is not "A."')
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
