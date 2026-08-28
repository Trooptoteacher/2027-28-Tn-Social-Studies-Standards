#!/usr/bin/env python3
"""Build the 2026-27 -> 2027-28 standards crosswalk.

    python3 tools/build_crosswalk.py <path-to-2026-27-standards-repo>

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
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NEW_DIR = ROOT / "standards"
OUT_DIR = ROOT / "crosswalk"

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
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


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


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    old_root = Path(sys.argv[1]) / "standards"
    if not old_root.is_dir():
        print(f"2026-27 standards not found at {old_root}")
        return 2
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    collisions, summary = [], []
    for old_stem, new_slug in COURSE_MAP.items():
        old_path, new_path = old_root / f"{old_stem}.json", NEW_DIR / f"{new_slug}.json"
        if not old_path.exists() or not new_path.exists():
            print(f"  skip {old_stem}: missing file")
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
        out = OUT_DIR / f"{new_slug}.csv"
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
        print(f"{new_slug:<26} 2026-27={len(o_stds):>3} 2027-28={len(n_stds):>3}  "
              f"unchanged={counts['unchanged']:>3} revised={counts['revised']:>3} "
              f"retired={counts['retired']:>3} new={counts['new']:>3}  code-moved={moved:>3}")

    with (OUT_DIR / "collisions.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["course", "code", "meaning_2026_27",
                                           "meaning_2027_28"])
        w.writeheader()
        w.writerows(collisions)

    (OUT_DIR / "summary.json").write_text(json.dumps({
        "note": "A standard code is NOT stable between 2026-27 and 2027-28. "
                "Never carry an asset forward by code alone.",
        "courses": [{"course": c, "count_2026_27": a, "count_2027_28": b,
                     "dispositions": d, "codeMoved": m} for c, a, b, d, m in summary],
        "codeCollisions": len(collisions),
    }, indent=2, ensure_ascii=False) + "\n")

    print(f"\n{len(collisions)} code collisions -> crosswalk/collisions.csv")
    print("Courses with no 2026-27 counterpart are new builds; see README.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
