#!/usr/bin/env python3
"""Propose a real, rights-cleared image for each item that references one and has none.

111 servable items say "Use the photograph to answer the question" and carry no
photograph — the stimulus is a PROSE DESCRIPTION of one. As printed the student
is told to read an image that was never there, so the item does not test source
analysis at all; it tests reading a caption.

162 rights-cleared image records exist in history-hack-web-app, every one public
domain with commercial use permitted and carrying its own citation, rights
statement verbatim, holding institution and bilingual alt text.

MATCHING IS ON CONTENT ONLY. The image bank's `standardIds` are 2026-27 codes
and 84 of the 94 US codes changed meaning between 2026-27 and 2027-28, so a
shared code there is not evidence of anything — using it would import the exact
cross-year confusion this repo's binding exists to prevent.

NOTHING IS ATTACHED. A wrong image on an assessment item is worse than no image:
the student analyses the wrong source and the item still looks complete. Every
match is a PROPOSAL with its evidence and its score, written to a review sheet.

Usage: python3 tools/match_stimulus.py [--min-score 3]
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import binding as binding_mod
import itemio

IMAGE_BANK = "/home/user/history-hack-web-app/public/data/us-history/primary-sources/images"
SHEET = os.path.join(itemio.BANK_ROOT, "reviewed", "stimulus-matches.json")
STIM_RX = re.compile(r"use the (image|photograph|cartoon|chart|graph|map|table)", re.I)
STOP = {"this", "that", "shows", "showing", "image", "photograph", "picture", "question",
        "answer", "following", "which", "what", "were", "with", "from", "have", "their",
        "they", "these", "those", "used", "using", "about", "would", "there", "into"}


def load_images():
    out = []
    for p in sorted(glob.glob(os.path.join(IMAGE_BANK, "*.json"))):
        with open(p, encoding="utf-8") as fh:
            d = json.load(fh)
        out += d if isinstance(d, list) else (d.get("images") or d.get("items") or [])
    return out


def words(s):
    return {w for w in re.findall(r"[a-zA-Z]{4,}", (s or "").lower()) if w not in STOP}


def years(s):
    return set(re.findall(r"\b(1[6-9]\d{2}|20[0-2]\d)\b", s or ""))


def described(stem):
    """The sentence(s) describing the absent stimulus — not the whole stem.

    Matching on the whole stem would score on the QUESTION's vocabulary, which
    is about the history rather than about the picture.
    """
    m = STIM_RX.search(stem or "")
    if not m:
        return ""
    tail = stem[m.end():]
    # Skip the rest of the INSTRUCTION sentence ("...to answer the question.")
    # before reading the description. Cutting at the first paragraph break
    # instead landed inside the instruction and matched on no content at all.
    dot = tail.find(".")
    tail = tail[dot + 1:] if dot != -1 else tail
    # Then keep sentences until the actual question starts.
    keep = []
    for sent in re.split(r"(?<=[.!?])\s+", tail):
        st = sent.strip()
        if not st:
            continue
        if st.endswith("?") or re.match(r"^(How|What|Why|Which|Based on|According to|In which|"
                                        r"The excerpt|Use the)\b", st):
            break
        keep.append(st)
    return " ".join(keep)[:600]


PROP_RX = re.compile(r"\b([A-Z][a-z]{3,})\b")
PROP_GENERIC = {"This", "Photograph", "Public", "Domain", "Library", "Congress", "National",
                "Archives", "American", "Americans", "United", "States", "Collection",
                "Records", "Division", "Prints", "Photographs", "Group", "Image", "Portrait",
                "Location", "February", "January", "March", "April", "August", "September",
                "October", "November", "December", "June", "July"}


DATE_RX = re.compile(r"\b(January|February|March|April|May|June|July|August|September|"
                     r"October|November|December)\s+(\d{1,2}),?\s+(1[6-9]\d{2}|20[0-2]\d)\b")


def full_dates(s):
    return {f"{m[0]} {int(m[1])}, {m[2]}" for m in DATE_RX.findall(s or "")}


def proper(s):
    return {w for w in PROP_RX.findall(s or "") if w not in PROP_GENERIC}


def conflicts(desc, img):
    """Distinctive names present on one side and absent from the other.

    A score is an agreement count and cannot see a DISAGREEMENT. An item
    describing the bombing of HIROSHIMA scored 7 against a photograph of
    NAGASAKI — same month, same war, same vocabulary, different city, different
    date, different bomb — and would have shipped as a confident match. The
    student analyses the wrong source and the item still looks complete.

    So a name on one side that the other never mentions demotes the match to a
    human read. It is deliberately over-cautious: the cost of a wrong image on
    an assessment item is a student assessed on something they were never
    shown, against the cost of one more row on a review sheet.
    """
    # TITLE and creator only. The caption is context and often mentions the
    # neighbouring event — a Nagasaki photograph's caption says "three days
    # after Hiroshima", which made the contradiction look like agreement. The
    # title is what the image IS.
    dp, ip = proper(desc), proper(f"{img.get('title')} {img.get('creator')}")
    only_item, only_img = sorted(dp - ip), sorted(ip - dp)
    # A full date on both sides that disagrees is decisive on its own: same
    # month and year, three days apart, is two different events.
    dd, di = full_dates(desc), full_dates(f"{img.get('title')} {img.get('year')}")
    if dd and di and not (dd & di):
        only_item = sorted(set(only_item) | dd)
        only_img = sorted(set(only_img) | di)
    return only_item, only_img


def score(desc, img):
    """Overlap evidence. A year agreement is worth more than a shared noun."""
    dw, iw = words(desc), words(" ".join(str(img.get(k) or "") for k in
                                        ("title", "caption", "creator", "historicalContext")))
    shared = dw & iw
    dy, iy = years(desc), years(f"{img.get('year')} {img.get('caption')}")
    year_hit = bool(dy & iy)
    return (len(shared) + (3 if year_hit else 0)), sorted(shared), sorted(dy & iy)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-score", type=int, default=3)
    a = ap.parse_args()
    b = binding_mod.load()
    print(b.declaration())

    if not os.path.isdir(IMAGE_BANK):
        print(f"image bank not reachable at {IMAGE_BANK} — cannot propose matches")
        return 1
    imgs = load_images()
    items = [i for i in itemio.load_dir(b.output_dir)
             if itemio.servable(i) and not i.get("image") and STIM_RX.search(i.get("stem") or "")]
    if not items or not imgs:
        print("EMPTY SCAN — refusing to report matches over nothing")
        return 1
    print(f"\n{len(items)} item(s) reference a stimulus they do not carry; "
          f"{len(imgs)} rights-cleared image(s) available")

    rows, tally = [], collections.Counter()
    for it in items:
        desc = described(it.get("stem") or "")
        ranked = []
        for im in imgs:
            sc, shared, yr = score(desc, im)
            if sc >= a.min_score:
                ranked.append((sc, shared, yr, im))
        ranked.sort(key=lambda r: -r[0])
        top = ranked[0] if ranked else None
        runner = ranked[1] if len(ranked) > 1 else None
        # A top match barely ahead of the next is not a match, it is a coin toss
        # between two pictures — and the cost of getting it wrong is a student
        # analysing the wrong source on an item that still looks complete.
        only_item, only_img = conflicts(desc, top[3]) if top else ([], [])
        decisive = (bool(top) and (not runner or top[0] - runner[0] >= 2)
                    and not (only_item and only_img))
        verdict = ("propose" if decisive else
                   "needs-care" if top and only_item and only_img else
                   "ambiguous" if top else "no-candidate")
        tally[verdict] += 1
        rows.append({
            "id": it["id"], "file": it.get("_file"), "standardCodes": it.get("standardCodes"),
            "describedStimulus": " ".join(desc.split())[:240],
            "verdict": verdict,
            # The top candidate is carried on needs-care rows TOO, with the
            # conflict attached. A row that says only "ambiguous" hands the
            # reviewer a search; a row that says "the item describes X, the best
            # candidate is Y, and these names disagree" hands them a decision.
            "proposed": None if not top else {
                "imageId": top[3].get("id"), "src": top[3].get("src"),
                "title": top[3].get("title"), "year": top[3].get("year"),
                "creator": top[3].get("creator"),
                "hostingInstitution": top[3].get("hostingInstitution"),
                "rightsLabel": top[3].get("rightsLabel"),
                "citationChicago": top[3].get("citationChicago"),
                "alt": top[3].get("alt"), "altEs": top[3].get("altEs"),
                "score": top[0], "sharedTerms": top[1], "yearAgreement": top[2],
                "runnerUpScore": runner[0] if runner else None,
            },
            "nameConflict": None if not (top and (only_item or only_img)) else {
                "namedByItemOnly": only_item, "namedByImageOnly": only_img,
                "why": ("a score counts agreements and cannot see a disagreement — check these "
                        "are the same subject before attaching"),
            },
            "alternatives": None if decisive or not ranked else [
                {"imageId": r[3].get("id"), "title": r[3].get("title"), "score": r[0]}
                for r in ranked[:3]],
            "ifNoImage": ("Rewrite the stem so it stops referencing a stimulus. The described "
                          "content is already in the prose, so the item survives as a "
                          "knowledge item — it simply stops claiming to test source analysis."),
            "humanVerdict": None,
        })

    for k, v in tally.most_common():
        print(f"   {v:5d}  {k}")
    with open(SHEET, "w", encoding="utf-8") as fh:
        json.dump({
            "$comment": ("PROPOSALS ONLY. Nothing is attached. A wrong image on an assessment "
                         "item is worse than no image: the student analyses the wrong source "
                         "and the item still looks complete. Matching is on CONTENT ONLY — the "
                         "image bank's standardIds are 2026-27 codes and 84 of 94 US codes "
                         "changed meaning between years. Set humanVerdict per row."),
            "imageBank": IMAGE_BANK, "minScore": a.min_score,
            "counts": dict(tally), "matches": rows,
        }, fh, indent=2, ensure_ascii=False)
    print(f"\nwrote {os.path.relpath(SHEET, itemio.BANK_ROOT)} — proposals only, nothing attached")
    return 0


if __name__ == "__main__":
    sys.exit(main())
