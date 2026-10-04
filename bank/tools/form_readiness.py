#!/usr/bin/env python3
"""What would it take to make a green form for each standard?

The pilot discovered its authoring cost item by item. That cost is measurable
in advance: for every standard, whether it has the depth and mix a form needs,
and exactly how many rationales, DOK notes and translations authoring it would
require. Scope the work before starting it.

Usage: python3 tools/form_readiness.py [--top N] [--csv path]
"""
from __future__ import annotations

import argparse, collections, copy, csv, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import alignment
import binding as binding_mod
import itemio
from gates import content, record


def reachable_tier(pool, form):
    """The highest tier this pool can fill, and the items that fill it.

    Shares the builder's ladder. This tool measured a FLAT blueprint and broke
    silently when the blueprint became tiered — its CSV was regenerated with
    output suppressed and the failure shipped.
    """
    for tier in form["tiers"]:
        used, got = set(), []
        for slot in tier["slots"]:
            cand = [i for i in pool if i["id"] not in used
                    and i.get("itemType") in slot["types"]
                    and i.get("dokLevel") == slot["dok"]]
            if not cand:
                got = None
                break
            used.add(cand[0]["id"]); got.append(cand[0])
        if got:
            return tier, got
    return None, []


def _as_authored(items):
    """The selection as it will be once a repair touches it.

    `apply_authoring.py` stamps `provenance.authoring` unconditionally — even a
    repair writing nothing but Spanish — and several gates only begin judging
    an item once it carries that stamp. An invoice priced against the untouched
    item therefore bills nothing for the obligations the repair creates.
    """
    out = []
    for it in items:
        c = copy.deepcopy(it)
        c.setdefault("provenance", {})["authoring"] = {"record": "(invoice estimate)"}
        out.append(c)
    return out


def cost(items, want=None):
    """Authoring needed to bring this selection to Grade A.

    EVERY line that a gate owns is charged BY CALLING THAT GATE. The first
    version re-implemented three of them and was wrong on all three, in both
    directions at once — which is worse than a wrong total, because the plan
    that reads it picks the next standard by this number:

      * `choiceRebalance` had its own length-cue rule: a flat 25% chance for
        every item whatever its option count, no cohort split, no MIN_COHORT
        floor, and `len(mcq)` units whenever it fired. It charged US.33 three
        units for a rebalance `choice-length-cue` DECLINES to ask for, and it
        charged a whole 6-item form to move two distractors.
      * `explanationRewrite` reproduced one of `explanation-quality`'s two
        defects. Across the bank the gate finds 918; the copy found 93. The
        825 it could not see are explanations that OPEN BY RESTATING THE KEY —
        the commoner defect of the two, missing from every estimate.
      * nothing at all was charged for the misconception taxonomy, and that is
        not an omission of a nice-to-have. `apply_authoring.py` stamps
        `provenance.authoring`, which is exactly what makes
        `misconception-taxonomy` start judging an item. So paying the
        `distractorRationale` line CREATES the taxonomy obligation: 66
        distractors across 22 items already carry free text with no family and
        fail the gate today, 20 of those 22 written by the repair path itself.
        An invoice that bills the rationale and not the family describes a
        state the gates reject.
      * choice Spanish was never charged either. `translation` covered
        `stemEs` and `explanationEs` only, while 2,432 choices in the bank
        carry a blank `textEs` — a form whose options are half English.

    `dokRationale` stays a PRESENCE count, and there is deliberately no
    `dokRationaleQuality` line: no gate judges the quality of a DOK rationale,
    and a column computed here with no gate behind it would be this same
    mistake in a new place.

    `stimulusDebt` is the ONE LINE AUTHORING CANNOT DISCHARGE. An item whose
    stem says "use the photograph" and carries none needs a rights-cleared
    image or a rewritten stem; both are decisions, not units of writing, and
    the image half waits on Sean (see HANDOFF §6). It is counted here anyway,
    because an invoice that omits the work it cannot do reads as a smaller
    invoice rather than a blocked one.
    """
    c = collections.Counter()
    for it in items:
        if not (it.get("dokRationale") or "").strip():
            c["dokRationale"] += 1
        for f in ("stemEs", "explanationEs"):
            if not (it.get(f) or "").strip():
                c["translation"] += 1
        if content.worst_translation_defect(it):
            c["translation"] += 1
        for ch in itemio.choices(it):
            if not isinstance(ch, dict):
                continue
            if not (ch.get("textEs") or "").strip():
                c["choiceTranslation"] += 1
            if ch.get("id") == it.get("correctAnswer"):
                continue
            if not (ch.get("explanation") or "").strip():
                c["distractorRationale"] += 1

    # Charged from the gates that own these rules — never re-derived here.
    #
    # `distractorTaxonomy` is priced against the selection AS IF ALREADY
    # AUTHORED, which is what the invoice is for: `apply_authoring.py` stamps
    # `provenance.authoring`, and that stamp is what makes
    # `misconception-taxonomy` begin judging the item. Pricing the untouched
    # item would bill nothing for work the repair itself creates.
    #
    # It was a direct read of `misconceptionFamily` until taxonomyVersion 2
    # split the field in two, and then it billed 3 units FOREVER on any
    # distractor correctly tagged `partial-truth` — a complete option with no
    # family by design, charged as if the family were missing. A bill that can
    # never be paid. That is L72 recurring in this same function three commits
    # later: every other line here is charged by calling its gate, and this was
    # the one left reading a field. Changing a gate's contract means
    # re-deriving the invoice FROM it, not editing the invoice to match.
    c["distractorTaxonomy"] = len(
        content.gate_misconception_taxonomy(_as_authored(items)).findings)
    c["explanationRewrite"] = len(content.gate_explanation_quality(items).findings)
    c["choiceRebalance"] = content.length_cue_rebalance_units(items)

    # Two item-level gates the invoice did not price at all, and forms SELECT
    # the items that fail them: 28 buildable standards draw 60 such items.
    # The invoice would say a standard costs N units, and the form would then
    # carry an item that cannot reach Grade A for any N — no amount of
    # rationale-writing attaches a photograph that is not there, and no
    # rationale finishes a stem that stops mid-sentence.
    #
    # Measured honestly, this is SMALL: 175 items bank-wide (111 stimulus, 64
    # truncation), and skipping them would cost exactly one standard its
    # buildability (US.50). The first version of this measurement swept ALL
    # item-level gates and reported buildability collapsing 73 -> 1, which was
    # `distractor-coverage` and `explanation-quality` — the debt this invoice
    # already prices — restated as a discovery. Decomposing is what made the
    # number mean anything.
    c["stimulusDebt"] = len(content.gate_stimulus_integrity(items).findings)
    c["truncationDebt"] = len(record.gate_truncation(items).findings)
    return c


def rows(b):
    """One row per standard — THE readiness computation.

    Extracted because the handoff-number check re-derived it and got a
    different total (1,763 against the tool's 1,867): the copy pooled items by
    standardCodes alone, skipping the per-standard relevance rule below. Two
    implementations of one number is L22, and here the copy was the checker
    that was supposed to be catching drift.
    """
    with open(b.blueprint_file, encoding="utf-8") as fh:
        form = json.load(fh)["form"]

    # Same placement rule the FORM BUILDER uses — an item counts toward a
    # standard only if it is relevant to THAT standard. Two implementations of
    # one rule is L22.
    stds = b.standards()
    items = itemio.load_dir(b.output_dir)
    by_std = collections.defaultdict(list)
    for it in items:
        if not itemio.aligned(it):
            continue
        hay = alignment.subject_text(it)
        for c in (it.get("standardCodes") or []):
            t = stds.get(c, {}).get("text")
            if t and alignment.relevant_to(hay, t):
                by_std[c].append(it)

    out = []
    for code in sorted(b.valid_codes()):
        pool = sorted(by_std.get(code, []), key=lambda i: i["id"])
        tier, got = reachable_tier(pool, form)
        buildable = tier is not None
        c = cost(got) if buildable else collections.Counter()
        out.append({"standard": code, "aligned": len(pool), "buildable": buildable,
                     "tier": tier["id"] if tier else "none",
                     "identifyingSignals": alignment.identifiability(stds[code]["text"]),
                     "weaklyIdentifiable": alignment.identifiability(stds[code]["text"]) < 2,
                     "dokCeiling": tier["dokCeiling"] if tier else None,
                     "distractorRationale": c["distractorRationale"],
                     "distractorTaxonomy": c["distractorTaxonomy"],
                     "dokRationale": c["dokRationale"], "translation": c["translation"],
                     "choiceTranslation": c["choiceTranslation"],
                     "explanationRewrite": c["explanationRewrite"],
                     "choiceRebalance": c["choiceRebalance"],
                     "stimulusDebt": c["stimulusDebt"],
                     "truncationDebt": c["truncationDebt"],
                     "totalAuthoringUnits": sum(c.values())})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--csv")
    a = ap.parse_args()
    b = binding_mod.load(); print(b.declaration())
    rws = rows(b)

    ok = [r for r in rws if r["buildable"]]
    print(f"\n{len(ok)}/{len(rws)} standards can fill a form from aligned items.\n")
    ok.sort(key=lambda r: r["totalAuthoringUnits"])
    print(f"{'standard':<9}{'tier':<16}{'aligned':>8}{'distract':>9}{'taxon':>7}"
          f"{'dok':>5}{'transl':>7}{'chEs':>6}{'rewrite':>8}{'rebal':>7}{'stim':>6}"
          f"{'trunc':>7}{'TOTAL':>7}")
    for r in ok[:a.top]:
        print(f"{r['standard']:<9}{r['tier']:<16}{r['aligned']:>8}"
              f"{r['distractorRationale']:>9}{r['distractorTaxonomy']:>7}"
              f"{r['dokRationale']:>5}{r['translation']:>7}{r['choiceTranslation']:>6}"
              f"{r['explanationRewrite']:>8}{r['choiceRebalance']:>7}"
              f"{r['stimulusDebt']:>6}{r['truncationDebt']:>7}"
              f"{r['totalAuthoringUnits']:>7}")
    tiers = collections.Counter(r["tier"] for r in rws)
    print("\ntier reached: " + ", ".join(f"{k}={v}" for k, v in tiers.most_common()))
    tot = sum(r["totalAuthoringUnits"] for r in ok)
    print(f"\nauthoring units to green ONE form for each of the {len(ok)} buildable "
          f"standards: {tot:,}")
    notb = [r for r in rws if not r["buildable"]]
    print(f"{len(notb)} standard(s) cannot fill a form yet: "
          + ", ".join(f"{r['standard']}({r['aligned']})" for r in notb[:12])
          + (" …" if len(notb) > 12 else ""))

    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rws[0].keys())); w.writeheader()
            w.writerows(rws)
        print(f"\nwrote {a.csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
