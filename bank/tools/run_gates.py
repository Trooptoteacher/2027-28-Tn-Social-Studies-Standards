#!/usr/bin/env python3
"""Run every gate against a built bank. Exit non-zero on any failure.

Usage:  python3 tools/run_gates.py [items_dir]

Prints the binding declaration first, always. First message of any build
session states the course, its standard-code prefix, the standards file being
read, and the output directory.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import binding as binding_mod
import itemio
from gates import record, coverage

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
    coverage.gate_teacher_side_isolation,
    coverage.gate_release_readiness,
]


def run(items, b, gates=GATES):
    return [g(items, b) for g in gates]


def main(argv):
    b = binding_mod.load()
    print(b.declaration())
    print()
    target = argv[1] if len(argv) > 1 else b.output_dir
    items = itemio.load_dir(target)
    print(f"Scanning {os.path.relpath(target, itemio.BANK_ROOT)} — {len(items)} item(s)\n")
    results = run(items, b)
    for r in results:
        print(r.report())
    failed = [r for r in results if not r.passed]
    print()
    print(f"{len(results) - len(failed)}/{len(results)} gates pass.")
    if failed:
        print("HELD — " + ", ".join(r.gate for r in failed))
        print('Grade A requires ALL gates pass. "Close" is not "A."')
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
