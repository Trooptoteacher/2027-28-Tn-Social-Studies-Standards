#!/usr/bin/env python3
"""Build the 2026-27 -> 2027-28 standards crosswalk.

    python3 tools/build_crosswalk.py <path-to-2026-27-standards-repo>
    python3 tools/build_crosswalk.py <path-to-2026-27-standards-repo> --check

--check rebuilds into a scratch directory and compares it with crosswalk/,
writing nothing. Exit 1 if any file differs: the committed crosswalk is not
what this tool produces from these standards.

Every run also checks a REGRESSION ANCHOR: a pair whose true similarity is
known. If the scorer is ever changed back to difflib's default autojunk, the
anchor collapses (0.93 -> 0.44) and the run fails before anything is written.

Why this exists
---------------
The codes did not stay put. In 2026-27 US.01 is the Homestead Act and the
Transcontinental Railroad; in 2027-28 US.01 is Reconstruction and the Compromise
of 1877, and the Homestead Act moved to US.04. A code is therefore NOT a stable
identifier across the two years, and anything that assumes it is -- a deck, a
Cornell packet, a question bank row, a primary-source manifest -- will silently
teach the wrong standard under the right-looking label.

This tool writes, per shared course:

  crosswalk/<course>.csv    every 2026-27 standard -> its 2027-28 counterpart
                            (unchanged / revised / retired), plus every new
                            2027-28 standard with no 2026-27 origin
  crosswalk/collisions.csv  THE headline: codes that exist in both years but
                            mean different things. Reusing an asset by code
                            across these is the drift failure.

Matching is one-to-one and greedy by text similarity, so a standard cannot be
claimed as the origin of two different successors.
"""
import csv
import filecmp
import json
import re
import sys
import tempfile
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NEW_DIR = ROOT / "standards"
OUT_DIR = ROOT / "crosswalk"

# (2026-27 file stem, 2026-27 code, 2027-28 course, 2027-28 code, minimum score).
# 2027-28 US.09 keeps 2026-27 US.05's sentence word for word and adds Lewis
# Latimer: the same standard, revised. Scored with autojunk on it read 0.44 and
# was labelled retired, which blocked every asset hanging on it.
ANCHORS = [("hs-us-history", "US.05", "us-history-geography", "US.09", 0.90)]

# 2026-27 file stem -> 2027-28 course slug. Both sets use the same prefix.
COURSE_MAP = {
    "hs-us-history": "us-history-geography",
    "hs-world-history": "world-history-geography",
    "hs-government-civics": "us-government-civics",
    "tennessee-history": "tennessee-history",
    "grade-06-world-history-geography": "grade-06",
    "grade-07-world-history-geography": "grade-07",
    "grade-08-us-history-geography": "grade-08",
}

SAME = 0.95      # at or above: the text is the same standard, possibly re-coded
REVISED = 0.55   # at or above: recognisably the same standard, reworded
COLLISION = 0.55  # below: a shared code that means something else


def normalize(s):
    """Compare on words alone: punctuation and bullet glyphs are not content."""
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s.lower()).split())


def ratio(a, b):
    # autojunk=False is load-bearing. difflib's default autojunk treats any character
    # in more than 1% of a 200+ character string as junk, so long bulleted standards
    # lost their spaces and vowels and scored far too low: 2026-27 US.05 vs its own
    # successor 2027-28 US.09 read 0.44 (retired) instead of 0.93 (revised).
    return SequenceMatcher(None, normalize(a), normalize(b), autojunk=False).ratio()


def match_course(old_stds, new_stds):
    """Greedy one-to-one match, best pairs first."""
    pairs = []
    for i, o in enumerate(old_stds):
        for j, n in enumerate(new_stds):
            r = ratio(o["text"], n["text"])
            if r >= REVISED:
                pairs.append((r, i, j))
    pairs.sort(reverse=True)
    o_taken, n_taken, matched = set(), set(), {}
    for r, i, j in pairs:
        if i in o_taken or j in n_taken:
            continue
        o_taken.add(i)
        n_taken.add(j)
        matched[i] = (j, r)
    return matched, o_taken, n_taken


def check_anchors(old_root):
    """Fail if a pair of known similarity no longer scores as the same standard."""
    failures = []
    for old_stem, old_code, new_slug, new_code, floor in ANCHORS:
        try:
            old = {x["code"]: x["text"] for x in
                   json.loads((old_root / f"{old_stem}.json").read_text())["standards"]}
            new = {x["code"]: x["text"] for x in
                   json.loads((NEW_DIR / f"{new_slug}.json").read_text())["standards"]}
            r = ratio(old[old_code], new[new_code])
        except (OSError, KeyError) as err:
            failures.append(f"anchor {old_code} -> {new_code}: cannot be read ({err})")
            continue
        if r < floor:
            failures.append(f"anchor 2026-27 {old_code} -> 2027-28 {new_code} scored {r:.2f}, "
                            f"below {floor:.2f}. The similarity scorer is broken (is "
                            f"autojunk back on?). Nothing written.")
    return failures


def compare_dirs(built, committed):
    """Names of files that differ between a fresh build and crosswalk/."""
    names = sorted({p.name for p in built.iterdir()} | {p.name for p in committed.iterdir()})
    return [n for n in names
            if not (built / n).exists() or not (committed / n).exists()
            or not filecmp.cmp(built / n, committed / n, shallow=False)]


def main():
    args = [a for a in sys.argv[1:] if a != "--check"]
    check = "--check" in sys.argv[1:]
    if len(args) != 1:
        print(__doc__)
        return 2
    old_root = Path(args[0]) / "standards"
    if not old_root.is_dir():
        print(f"2026-27 standards not found at {old_root}")
        return 2
    failures = check_anchors(old_root)
    if failures:
        for f in failures:
            print(f"  BLOCKER  {f}")
        return 1
    if check:
        with tempfile.TemporaryDirectory() as tmp:
            code = build(old_root, Path(tmp), quiet=True)
            if code:
                return code
            diffs = compare_dirs(Path(tmp), OUT_DIR)
        if diffs:
            for n in diffs:
                print(f"  BLOCKER  crosswalk/{n} differs from a fresh build")
            print(f"\n{len(diffs)} file(s) stale. Re-run without --check and commit the result.")
            return 1
        print("crosswalk: fresh build matches crosswalk/ exactly; anchors hold. PASS")
        return 0
    return build(old_root, OUT_DIR, quiet=False)


def build(old_root, out_dir, quiet):
    say = (lambda *a, **k: None) if quiet else print
    out_dir.mkdir(parents=True, exist_ok=True)

    collisions, summary = [], []
    for old_stem, new_slug in COURSE_MAP.items():
        old_path, new_path = old_root / f"{old_stem}.json", NEW_DIR / f"{new_slug}.json"
        if not old_path.exists() or not new_path.exists():
            say(f"  skip {old_stem}: missing file")
            continue
        old = json.loads(old_path.read_text())
        new = json.loads(new_path.read_text())
        o_stds, n_stds = old["standards"], new["standards"]
        matched, o_taken, n_taken = match_course(o_stds, n_stds)

        rows = []
        for i, o in enumerate(o_stds):
            if i in matched:
                j, r = matched[i]
                n = n_stds[j]
                rows.append({
                    "disposition": "unchanged" if r >= SAME else "revised",
                    "code_2026_27": o["code"], "code_2027_28": n["code"],
                    "code_moved": "yes" if o["code"] != n["code"] else "no",
                    "similarity": f"{r:.2f}",
                    "text_2026_27": o["text"], "text_2027_28": n["text"],
                    "cluster_2027_28": n.get("cluster", ""), "era_2027_28": n.get("era", ""),
                })
            else:
                rows.append({
                    "disposition": "retired", "code_2026_27": o["code"], "code_2027_28": "",
                    "code_moved": "", "similarity": "",
                    "text_2026_27": o["text"], "text_2027_28": "",
                    "cluster_2027_28": "", "era_2027_28": "",
                })
        for j, n in enumerate(n_stds):
            if j not in n_taken:
                rows.append({
                    "disposition": "new", "code_2026_27": "", "code_2027_28": n["code"],
                    "code_moved": "", "similarity": "",
                    "text_2026_27": "", "text_2027_28": n["text"],
                    "cluster_2027_28": n.get("cluster", ""), "era_2027_28": n.get("era", ""),
                })

        rows.sort(key=lambda r: (r["code_2027_28"] or "zzz", r["code_2026_27"]))
        out = out_dir / f"{new_slug}.csv"
        with out.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

        # a code present in both years whose meaning changed
        o_by_code = {s["code"]: s for s in o_stds}
        for n in n_stds:
            o = o_by_code.get(n["code"])
            if o and ratio(o["text"], n["text"]) < COLLISION:
                collisions.append({
                    "course": new_slug, "code": n["code"],
                    "meaning_2026_27": o["text"], "meaning_2027_28": n["text"],
                })

        counts = {d: sum(1 for r in rows if r["disposition"] == d)
                  for d in ("unchanged", "revised", "retired", "new")}
        moved = sum(1 for r in rows if r["code_moved"] == "yes")
        summary.append((new_slug, len(o_stds), len(n_stds), counts, moved))
        say(f"{new_slug:<26} 2026-27={len(o_stds):>3} 2027-28={len(n_stds):>3}  "
              f"unchanged={counts['unchanged']:>3} revised={counts['revised']:>3} "
              f"retired={counts['retired']:>3} new={counts['new']:>3}  code-moved={moved:>3}")

    with (out_dir / "collisions.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["course", "code", "meaning_2026_27",
                                           "meaning_2027_28"])
        w.writeheader()
        w.writerows(collisions)

    (out_dir / "summary.json").write_text(json.dumps({
        "note": "A standard code is NOT stable between 2026-27 and 2027-28. "
                "Never carry an asset forward by code alone.",
        "courses": [{"course": c, "count_2026_27": a, "count_2027_28": b,
                     "dispositions": d, "codeMoved": m} for c, a, b, d, m in summary],
        "codeCollisions": len(collisions),
    }, indent=2, ensure_ascii=False) + "\n")

    say(f"\n{len(collisions)} code collisions -> crosswalk/collisions.csv")
    say("Courses with no 2026-27 counterpart are new builds; see README.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
