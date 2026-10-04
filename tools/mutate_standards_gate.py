#!/usr/bin/env python3
"""Mutation-test the eraOverview and document-fingerprint blockers.

A self-test proves a blocker fires on the case someone wrote for it. It cannot
prove the blocker is load-bearing: a rule weakened, widened until it matches
everything, or disabled outright still passes a suite whose cases were written
against the strong version. So each mutation below breaks the gate the way a
careless edit plausibly would, and the self-test must notice.

A SURVIVOR IS NOT A FAILING TEST -- it is a rule nothing is holding in place.
Two survivors in a sibling harness turned out to be one rule implemented three
times, each copy quietly covering for the others.

    python3 tools/mutate_standards_gate.py
"""
import atexit
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "tools" / "validate_standards.py"
SELFTEST = ROOT / "tools" / "validate_standards_selftest.py"

#: (name, find, replace). Each must break something the suite pins.
MUTATIONS = [
    ("the empty-overview blocker is disabled outright",
     '        if not ov:\n            block(f"{name} {code}: eraOverview is empty',
     '        if False:\n            block(f"{name} {code}: eraOverview is empty'),
    ("whitespace passes as a value, so '   ' reads as an overview",
     '        ov = (s.get("eraOverview") or "").strip()',
     '        ov = (s.get("eraOverview") or "")'),
    ("a page of 0 is accepted, so a derived value needs no page",
     "        if not isinstance(pg, int) or pg <= 0:",
     "        if False:"),
    ("a string page is accepted, so the type is unchecked",
     "        if not isinstance(pg, int) or pg <= 0:",
     "        if not isinstance(pg, (int, str)) or not pg:"),
    ("the one-heading-one-overview check is disabled",
     "        if len(vals) > 1:\n            block(f\"{name}: heading {cluster!r}",
     "        if False:\n            block(f\"{name}: heading {cluster!r}"),
    ("agreement is measured on the TEXT only, so a disagreeing page passes",
     '            ((s.get("eraOverview") or "").strip(), s.get("eraOverviewSourcePage")))',
     '            ((s.get("eraOverview") or "").strip(),))'),
    ("agreement is scoped to the ERA again -- the version that blocked 12 courses",
     '        key = (s.get("era", ""), s.get("cluster", ""))',
     '        key = (s.get("era", ""),)'),
    ("the contiguity check is disabled",
     "        if ix != list(range(ix[0], ix[-1] + 1)):",
     "        if False:"),
    ("an era may inherit the previous era's Overview -- the silent-wrong shape",
     "        if ov and len(eras) > 1:",
     "        if False:"),
    # WITHDRAWN MUTATION -- "widen the inheritance check to the CLUSTER".
    # It SURVIVED, and it is an invalid mutation rather than a hole. The parser
    # keys each eraOverviews row on (era, overview, page), so two rows sharing
    # (overview, page) must differ in ERA and both versions block: provably
    # equivalent. Its stated effect was also false -- TDOE's Sociology
    # duplicate sits on two DIFFERENT pages (p194/p195), so neither version
    # ever compares those rows. And `cluster` is not an identifying field of a
    # row at all: it is merely the first standard's cluster, and one Overview
    # legitimately serves several (US History's first era spans Reconstruction,
    # Westward Expansion and Gilded Age). A mutation no fixture can distinguish,
    # named for a behaviour it does not have, teaches the next reader something
    # untrue.
    ("a standard may point at a triple the table does not carry",
     "        if key not in rows:",
     "        if False:"),
    ("a table row nothing uses is allowed",
     "    for key in sorted(rows - used, key=lambda k: str(k)):",
     "    for key in sorted(set() - used, key=lambda k: str(k)):"),
    ("the table's row counts need not add up",
     "    if stds and counted != len(stds):",
     "    if False:"),
    ("any string is accepted as a sha256",
     '    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha or ""):\n'
     '        block(f"{name}: source.sha256 is missing or malformed',
     '    if False:\n'
     '        block(f"{name}: source.sha256 is missing or malformed'),
    ("a course hash may disagree with index.json",
     '            if (c.get("source") or {}).get("sha256") != sha:',
     "            if False:"),
    ("the extraction event needs no date",
     '    if not idx.get("extractedAt"):',
     "    if False:"),
    ("--verbatim: an overview is looked for anywhere in the document, "
     "so a wrong page passes",
     "            window = \"\".join(page_text[pg - 1:min(len(page_text), pg + 1)])",
     "            window = \"\".join(page_text)"),
    ("--verbatim: the overview check is disabled",
     "            if squash(ov) not in window:",
     "            if False:"),
    ("--verbatim: a page outside the document is accepted",
     "            if not 1 <= pg <= len(page_text):",
     "            if False:"),
    ("--verbatim: the document may move underneath its page references",
     '    if idx.get("sourceSha256") and on_disk != idx["sourceSha256"]:',
     "    if False:"),
]


def purge_pycache():
    """A SAME-SIZE MUTATION CAN OUTLIVE ITS RESTORE, THROUGH BYTECODE.

    Flipping one comparison leaves the file the same SIZE, and a restore landing
    inside the same clock second leaves the cached bytecode's recorded
    (size, mtime) still matching -- so CPython reuses bytecode compiled from the
    MUTATED source. A sibling harness fired a blocker on correct data while
    reading the source said the comparison was right.
    """
    for d in (ROOT / "tools" / "__pycache__",):
        shutil.rmtree(d, ignore_errors=True)


def main():
    orig = GATE.read_text()
    if "if False:" in orig:
        print("REFUSING TO START: the gate already carries a mutation marker.\n"
              "A previous run died before restoring it. Check out a clean copy first.",
              file=sys.stderr)
        return 2
    atexit.register(lambda: (GATE.write_text(orig), purge_pycache()))

    #: A LOCK FILE, because the harness holds the gate MUTATED for most of its
    #: run and anything that reads -- or COMMITS -- the gate meanwhile gets the
    #: mutation. A stray lock file means a run died and the gate beside it is
    #: the file to check.
    lock = GATE.with_suffix(".py.mutating")
    if lock.exists():
        print(f"REFUSING TO START: {lock.name} exists — another run is working, or one "
              f"died mid-run. Check {GATE.name} against git before continuing.",
              file=sys.stderr)
        return 2
    lock.write_text("mutation run in progress; the gate beside this file is not trustworthy\n")
    atexit.register(lambda: lock.unlink(missing_ok=True))

    survived = 0
    for name, find, repl in MUTATIONS:
        if find not in orig:
            print(f"  SKIP     {name}  (anchor not found — the gate moved)")
            survived += 1
            continue
        GATE.write_text(orig.replace(find, repl, 1))
        purge_pycache()
        # -B so the run itself writes no bytecode for the next one to reuse.
        r = subprocess.run([sys.executable, "-B", str(SELFTEST)],
                           capture_output=True, text=True, cwd=ROOT)
        GATE.write_text(orig)
        purge_pycache()
        if r.returncode == 0:
            print(f"  SURVIVED {name}")
            survived += 1
        else:
            print(f"  caught   {name}")

    print(f"\nmutations: {len(MUTATIONS)}  survived: {survived}")
    if survived:
        print("\nA SURVIVOR IS A HOLE, NOT A TEST GAP: that rule can be deleted "
              "and nothing notices.")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main())
