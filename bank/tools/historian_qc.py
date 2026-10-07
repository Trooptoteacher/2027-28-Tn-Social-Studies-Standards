#!/usr/bin/env python3
"""Turn "review this item" into "confirm these assertions".

WHAT THIS IS NOT. It does not verify history. It has no access to a library —
the egress policy denies every scholarly host — and a citation written from
recollection on a district-facing item is worse than no citation, because it
looks checked. Nothing here affirms anything: it never writes
`historianReview`, never clears `requiresHistorianReview`, never sets
`alignmentStatus` to human-verified. Verdicts land in a `historianQc`
namespace that counts toward nothing, the same guardrail `ai_review.py` keeps
and for the same reason — an approval record looks identical whoever wrote it.

WHY IT EXISTS. The review state machine was built and the historian content
check was not. `ai_review.py` triages four things — rubric shape, key
contradiction, translation defects, citation form — and not one of them looks
at a date, an actor, a sequence or an attribution. The cost of that gap is on
the record: PSTIM-0041's misconception label read "invents a negotiated
settlement for the blockade" when the Berlin Blockade WAS ended by negotiation
(the Jessup-Malik talks at the UN and the New York Agreement of May 1949). A
false historical claim, teacher-facing, in a field no gate reads, and every
gate was green. It was found by a person reading the option.

So this extracts the claims, sorts them by how badly they fail if wrong, and
cross-checks the three things the repo can actually check. The historian still
decides everything; what changes is that the pass is a sequence of confirms
rather than an investigation.

Usage:
  python3 tools/historian_qc.py                      # whole queue
  python3 tools/historian_qc.py --standard US.01     # one standard
  python3 tools/historian_qc.py --apply              # also stamp historianQc
"""
from __future__ import annotations

import argparse, collections, hashlib, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import binding as binding_mod
import itemio

OUT = os.path.join(itemio.BANK_ROOT, "reviewed", "HISTORIAN_QC_WORKSHEET.md")
REC = os.path.join(itemio.BANK_ROOT, "reviewed", "historian-qc.json")

# ---------------------------------------------------------------- claim shapes
# Ordered worst-first. The order IS the review order, and it is not arbitrary:
# a negative-existence claim is the cheapest sentence to write and the most
# expensive to check, which is exactly the combination that let the Jessup-Malik
# label through.
NEGATIVE_EXISTENCE = re.compile(
    r"\b(invents?|invented|never (?:happened|occurred|existed|was|did)|did not (?:happen|occur|exist)"
    r"|no such|nothing like|was never|were never|had never)\b", re.I)
SUPERLATIVE = re.compile(
    r"\b(first|last|only|sole|all|every|none|never|always|unprecedented|unanimous"
    r"|largest|smallest|earliest|latest)\b", re.I)
CAUSAL = re.compile(
    r"\b(because|caused|led to|resulted in|brought about|so that|therefore|as a result"
    r"|which is why|in order to)\b", re.I)
YEAR = re.compile(r"\b(1[6-9]\d{2}|20[0-2]\d)\b")
FULL_DATE = re.compile(
    r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+\d{1,2},?\s+\d{4}\b|\b\d{1,2}\s+"
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+\d{4}\b")
QUANTITY = re.compile(r"\$\s?[\d,.]+\s*(?:million|billion|thousand)?|\b\d[\d,]{2,}\b"
                      r"|\b\d+\s*(?:acres|miles|percent|hours|days|years)\b", re.I)
# A capitalised run of 2+ words, not sentence-initial — people, acts, treaties,
# places. Crude on purpose: a historian reading a slightly long list costs less
# than one reading a list with the key name missing.
PROPER = re.compile(r"(?<![.!?]\s)(?<!^)\b([A-Z][a-z]+(?:\s+(?:of|the|de|van|von))?"
                    r"(?:\s+[A-Z][a-zA-Z.'’-]+)+)\b")

# Fields a historian is being asked about, and whether a student ever sees them.
FIELDS = [
    ("stem", "student"), ("explanation", "student"),
    ("dokRationale", "teacher"),
]
CHOICE_FIELDS = [
    ("text", "student"), ("explanation", "teacher"), ("misconception", "teacher"),
]


def era_years(era: str):
    """The year range a standard's era declares, if it declares one."""
    m = re.search(r"\((\d{4})\s*[-–]\s*(\d{4})\)", era or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def claims_in(text, where, audience):
    """Every confirmable assertion in one field, worst-first."""
    out = []
    if not text:
        return out
    t = str(text)

    def add(kind, quote, note):
        out.append({"kind": kind, "where": where, "audience": audience,
                    "quote": quote.strip(), "why": note})

    for m in NEGATIVE_EXISTENCE.finditer(t):
        add("negative-existence", _window(t, m),
            "asserts something did NOT happen. The cheapest claim to write and the "
            "costliest to check — this is the shape that produced the Jessup-Malik error. "
            "Confirm the negative, not just the positive around it.")
    for m in FULL_DATE.finditer(t):
        add("precise-date", m.group(0), "a date to the day is either right or wrong.")
    for m in QUANTITY.finditer(t):
        add("quantity", m.group(0), "a figure is either right or wrong.")
    for m in SUPERLATIVE.finditer(t):
        add("superlative", _window(t, m),
            "one counterexample falsifies it. 'first', 'only' and 'never' are the "
            "words most often wrong in an otherwise sound sentence.")
    for m in CAUSAL.finditer(t):
        add("causal", _window(t, m),
            "a causal claim can be wrong while every fact in it is right.")
    for m in PROPER.finditer(t):
        add("named-entity", m.group(1),
            "confirm the name, and that the action beside it belongs to it.")
    return out


def _window(t, m, pad=46):
    a, b = max(0, m.start() - pad), min(len(t), m.end() + pad)
    return ("…" if a else "") + t[a:b] + ("…" if b < len(t) else "")


def _content_hash(it):
    """Everything a historian would be signing off. A QC record whose hash no
    longer matches has been overtaken by an edit and must not read as current."""
    payload = [it.get(f) for f, _ in FIELDS] + [
        [c.get(f) for f, _ in CHOICE_FIELDS] for c in itemio.choices(it)
        if isinstance(c, dict)]
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]


def review(it, std):
    """One item's QC record. No verdict — a list of things to confirm."""
    claims = []
    for f, aud in FIELDS:
        claims += claims_in(it.get(f), f, aud)
    for c in itemio.choices(it):
        if not isinstance(c, dict):
            continue
        for f, aud in CHOICE_FIELDS:
            claims += claims_in(c.get(f), f"choice {c.get('id')}.{f}", aud)

    flags, context = [], []
    # CONTEXT, NOT A FLAG — and it was a flag until its first run, which was
    # wrong 5 times out of 5.
    #
    # `era` is where TDOE PLACES a standard in the course, not a boundary on
    # its content. US.01's era reads 1877-1900 and its cluster is literally
    # "Reconstruction"; the Ku Klux Klan, founded 1866, is named in the
    # standard's own text. US.05 is the Dawes Act of 1887 and its land-loss
    # figure runs to 1934, which is the standard terminus for measuring that
    # Act. Every year the check flagged was correct history.
    #
    # A flag that is 100% false on its first run is worse than no flag: it
    # teaches the reader to skip the section headed "look at these first",
    # which is where the one real finding lives. So the span is reported as
    # orientation — here is the period this item actually covers — and claims
    # nothing about whether that is wrong.
    rng = era_years((std or {}).get("era", ""))
    years = sorted({int(y) for f, _ in FIELDS for y in YEAR.findall(str(it.get(f) or ""))}
                   | {int(y) for c in itemio.choices(it) if isinstance(c, dict)
                      for f, _ in CHOICE_FIELDS for y in YEAR.findall(str(c.get(f) or ""))})
    if years:
        context.append({"kind": "year-span",
                        "detail": f"this item spans {min(years)}-{max(years)}"
                                  + (f"; the standard is placed in the era {rng[0]}-{rng[1]}"
                                     f" (cluster {(std or {}).get('cluster')!r})" if rng else "")
                                  + ". Placement is not a content boundary — stated for "
                                    "orientation, not as a problem.",
                        "years": years, "era": list(rng) if rng else None})
    # CROSS-CHECK 2 — a teacher-facing field carrying a negative-existence claim.
    for c in claims:
        if c["kind"] == "negative-existence" and c["audience"] == "teacher":
            flags.append({"kind": "unreviewed-negative-claim",
                          "detail": f"{c['where']} asserts a negative. No gate reads this field "
                                    f"for historical truth, and a false negative here is "
                                    f"exactly the defect PSTIM-0041 shipped.",
                          "quote": c["quote"]})
    return {"itemId": it["id"], "standard": (it.get("standardCodes") or [None])[0],
            "contentHash": _content_hash(it),
            "claimCount": len(claims),
            "byKind": dict(collections.Counter(c["kind"] for c in claims)),
            "flags": flags, "context": context, "claims": claims}


def queue(items, b, only=None):
    stds = b.standards()
    out = []
    for it in sorted(items, key=lambda i: i["id"]):
        if not itemio.servable(it):
            continue
        if not (it.get("requiresHistorianReview") or (it.get("provenance") or {}).get("generated")):
            continue
        code = (it.get("standardCodes") or [None])[0]
        if only and code != only:
            continue
        out.append(review(it, stds.get(code)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--standard")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    b = binding_mod.load(); print(b.declaration())
    items = itemio.load_dir(b.output_dir)
    recs = queue(items, b, a.standard)
    if not recs:
        print("\nNothing in the historian queue. That is a FAILURE to report, not a pass: "
              "authored content always needs a person.")
        return 1

    kinds = collections.Counter(k for r in recs for k in r["byKind"])
    flags = collections.Counter(f["kind"] for r in recs for f in r["flags"])
    print(f"\n{len(recs)} item(s) awaiting historian review · "
          f"{sum(r['claimCount'] for r in recs)} confirmable claim(s)")
    print("  by kind: " + ", ".join(f"{k}={sum(r['byKind'].get(k,0) for r in recs)}"
                                    for k in sorted(kinds)))
    print("  flags:   " + (", ".join(f"{k}={v}" for k, v in flags.most_common())
                            or "none — and none is the honest answer more often than not; "
                               "the claim list is the product, not the flags"))

    write_worksheet(recs)
    print(f"\nwrote {os.path.relpath(OUT, itemio.BANK_ROOT)}")

    doc = {"$comment":
           "A QUEUE, NOT A VERDICT. Generated by tools/historian_qc.py, which verifies no "
           "history and affirms nothing. Each row lists what a historian must confirm, "
           "worst-first, with the content hash it was computed against — a row whose hash no "
           "longer matches the item has been overtaken by an edit and is stale.",
           "generatedBy": "tools/historian_qc.py",
           "affirms": "nothing — historianReview and requiresHistorianReview are untouched",
           "items": recs}
    if a.apply:
        with open(REC, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
        print(f"wrote {os.path.relpath(REC, itemio.BANK_ROOT)}")
    else:
        print("DRY RUN — worksheet written, record not. Re-run with --apply.")
    return 0


def write_worksheet(recs):
    L = ["# Historian QC worksheet", "",
         "**Nothing here is verified and nothing here is approved.** Every line is a claim to "
         "confirm, generated from the item text. This tool has no access to a library; it "
         "cannot tell you whether a date is right, only that the date is a thing that is "
         "either right or wrong. The verdict is yours.", "",
         "Claims are ordered worst-first. A **negative-existence** claim leads because it is "
         "the cheapest sentence to write and the costliest to check — `PSTIM-0041`'s "
         "misconception label asserted the Berlin Blockade was never ended by negotiation, "
         "which is false, and no gate read that field.", ""]
    flagged = [r for r in recs if r["flags"]]
    if flagged:
        L += ["## Look at these first", "",
              "*This section is kept SHORT on purpose. An `outside-declared-era` check sat here "
              "until its first run flagged five items and all five were correct history — a "
              "standard's era is where TDOE places it in the course, not a boundary on its "
              "content. A heading that is wrong five times out of five teaches you to skip it, "
              "so year spans moved to orientation and only claims that genuinely need a "
              "verdict appear here.*", ""]
        for r in flagged:
            L.append(f"### `{r['itemId']}` ({r['standard']})")
            for f in r["flags"]:
                L.append(f"- **{f['kind']}** — {f['detail']}")
                if f.get("quote"):
                    L.append(f"  - > {f['quote']}")
            L.append("")
    L += ["## Every item in the queue", ""]
    for r in recs:
        L.append(f"### `{r['itemId']}` ({r['standard']}) — {r['claimCount']} claim(s)")
        L.append(f"*content hash* `{r['contentHash']}` — if the item is edited after you sign, "
                 f"this changes and the review is stale.")
        for c in r.get("context", []):
            L.append(f"*{c['kind']}* — {c['detail']}")
        L.append("")
        order = ["negative-existence", "precise-date", "quantity", "superlative",
                 "causal", "named-entity"]
        for kind in order:
            rows = [c for c in r["claims"] if c["kind"] == kind]
            if not rows:
                continue
            L.append(f"**{kind}** ({len(rows)})")
            for c in rows:
                L.append(f"- [ ] `{c['where']}` · *{c['audience']}-facing* — {c['quote']}")
            L.append("")
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


if __name__ == "__main__":
    sys.exit(main())
