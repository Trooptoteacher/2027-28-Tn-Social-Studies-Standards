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
    """The BANK holds enough depth per standard, in roughly the right DOK mix.

    Exact-count conformance is a FORM property — see gate_form_blueprint, which
    fails in either direction as specified. Measuring a 3,986-item bank against
    a 564-item target can only ever fail, and "too many items" is not drift; it
    is depth, and depth is what lets forms be built without reusing an item.

    What the bank must not do is drift to recall. That is measured as a
    proportion, so it holds at any size.
    """
    name = "blueprint-conformance"
    if (r := empty_scan_guard(name, items)):
        return r
    with open(binding.blueprint_file, encoding="utf-8") as fh:
        bp = json.load(fh)
    bank = bp.get("bank") or {"minPerStandard": bp["defaults"]["itemCount"],
                              "dokProportion": {"1": .33, "2": .33, "3": .17, "4": .17},
                              "proportionTolerance": .12}
    live = [i for i in items if itemio.aligned(i)]
    if not live:
        return Result(name, False, len(items),
                      [Finding("(none)", "no items with established alignment — measured "
                                         "coverage is zero")],
                      note="EMPTY SCAN after alignment filter")

    by_std = collections.defaultdict(list)
    for it in live:
        for c in (it.get("standardCodes") or []):
            by_std[c].append(it)

    findings = []
    per = bp["perStandard"]
    thin = 0
    for code in sorted(per):
        n = len(by_std.get(code, []))
        if n < bank["minPerStandard"]:
            thin += 1
            findings.append(Finding(code,
                f"{n} aligned item(s), below the bank minimum of {bank['minPerStandard']}"))

    total = len(live)
    got = collections.Counter(str(i.get("dokLevel")) for i in live)
    tol = bank["proportionTolerance"]
    for lvl, want in sorted(bank["dokProportion"].items()):
        share = got.get(lvl, 0) / total
        if abs(share - want) > tol:
            findings.append(Finding(f"DOK-{lvl}",
                f"{share:.0%} of the bank, target {want:.0%} (±{tol:.0%}) — "
                f"{'over' if share > want else 'under'}weighted"))

    return Result(name, not findings, len(live), findings,
                  note=f"{len(by_std)}/{len(per)} standards have >=1 aligned item; "
                       f"{thin} below minimum depth; "
                       f"{sum(1 for i in items if itemio.servable(i) and not itemio.aligned(i))} "
                       f"servable items kept but not counted")


def gate_form_blueprint(form_items, binding=None, standards=None, tiers=None) -> Result:
    """A rendered FORM matches the tier it DECLARES, exactly, in either direction.

    Tiering is not a loosening. Within its declared tier a form must match slot
    for slot: 7 items where the tier says 6, or a DOK-2 where the tier says
    DOK-3, is still a defective form. What tiering removes is the requirement
    that a standard produce a document-based item that does not exist — and the
    form says on its face which tier it was built at and what DOK it reaches.
    """
    name = "form-blueprint"
    if (r := empty_scan_guard(name, form_items)):
        return r
    with open(binding.blueprint_file, encoding="utf-8") as fh:
        form = json.load(fh)["form"]
    by_tier = {t["id"]: t for t in form["tiers"]}
    declared = set(standards) if standards else None
    by_std = collections.defaultdict(list)
    for it in form_items:
        for c in (it.get("standardCodes") or []):
            if declared is None or c in declared:
                by_std[c].append(it)
    for c in (declared or set()):
        by_std.setdefault(c, [])

    findings = []
    for code, got in sorted(by_std.items()):
        tid = (tiers or {}).get(code)
        if not tid:
            findings.append(Finding(code, "the form declares no tier for this standard — a "
                                          "form that does not say what it is cannot be checked"))
            continue
        tier = by_tier.get(tid)
        if not tier:
            findings.append(Finding(code, f"declares unknown tier {tid!r}")); continue
        if len(got) != len(tier["slots"]):
            findings.append(Finding(code, f"{len(got)} items on the form, tier {tid!r} "
                                          f"specifies {len(tier['slots'])}"))
        want = collections.Counter((tuple(sorted(s["types"])), s["dok"]) for s in tier["slots"])
        have = collections.Counter()
        for i in got:
            slot = next((s for s in tier["slots"]
                         if i.get("itemType") in s["types"] and i.get("dokLevel") == s["dok"]
                         and have[(tuple(sorted(s["types"])), s["dok"])]
                             < want[(tuple(sorted(s["types"])), s["dok"])]), None)
            if slot is None:
                findings.append(Finding(code,
                    f"item {i.get('id')} ({i.get('itemType')} DOK{i.get('dokLevel')}) fills no "
                    f"remaining slot in tier {tid!r}"))
            else:
                have[(tuple(sorted(slot["types"])), slot["dok"])] += 1
        for k, n in want.items():
            if have[k] != n:
                findings.append(Finding(code, f"tier {tid!r} slot {k[0]}@DOK{k[1]}: "
                                              f"{have[k]} filled, {n} required"))
    note = f"{len(by_std)} standard(s); tiers " + ", ".join(
        f"{c}={(tiers or {}).get(c, '?')}" for c in sorted(by_std))
    return Result(name, not findings, len(form_items), findings, judged=len(by_std), note=note)


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
    # Judge on EFFECT SIZE, not p-value alone. At n=3,844 a chi-square test
    # flags a 27/25/24/24 split — statistically significant, practically
    # unbeatable by a student. A gate that fails on that trains people to
    # ignore the word FAIL. The defect this exists to catch is "60% of keys
    # are C", so the bar is a share more than 7 points off uniform.
    MAX_DEVIATION = 0.07
    for k, counts in sorted(cohorts.items()):
        n = sum(counts.values())
        if k < 2:
            continue
        expected = n / k
        uniform = 1.0 / k
        chi2 = sum((counts.get(p, 0) - expected) ** 2 / expected for p in positions[k])
        crit = _CHI2_CRIT_01.get(k - 1)
        share = {p: counts.get(p, 0) / n for p in positions[k]}
        worst = max(share, key=share.get) if share else None
        dev = max(abs(v - uniform) for v in share.values()) if share else 0.0
        flag = "" if not (crit and chi2 > crit) else f" chi2={chi2:.1f}>{crit} (advisory)"
        notes.append(f"{k}-choice n={n} worst={worst}@{share.get(worst, 0):.0%} "
                     f"max-dev={dev:.1%}{flag}")
        if dev > MAX_DEVIATION:
            findings.append(Finding(f"{k}-choice cohort",
                f"key position {worst!r} is {share[worst]:.0%} of keys, {dev:.1%} off the "
                f"{uniform:.0%} uniform share (bar: {MAX_DEVIATION:.0%}); "
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
    findings, judged = [], 0
    for it in items:
        if it.get("bankTier") != "student":
            continue
        if it.get("_surface") != "student-form":
            continue
        judged += 1
        leaked = [f for f in _TEACHER_ONLY if it.get(f) not in (None, "")]
        leaked += [f"choice.{c.get('id')}.explanation" for c in itemio.choices(it)
                   if isinstance(c, dict) and (c.get("explanation") or "").strip()]
        if leaked:
            findings.append(Finding(it.get("id", "?"),
                f"student-facing surface carries teacher-only field(s) {leaked}",
                it.get("_file", "")))
    return Result(name, not findings, len(items), findings, judged=judged,
                  note="measures rendered student surfaces; items at rest are teacher-side by default")


# ------------------------------------------------------- release readiness
def gate_release_readiness(items, binding=None) -> Result:
    """Grade A only. One unresolved gap holds the whole artifact.

    This gate exists because `reporting-category-provenance` reads GREEN when
    every row is honestly UNMAPPED — consistency is all it can check. A green
    column over 94 unsourced categories is the same trap as a gate green over
    an empty set: it reads exactly like a clean pass. So the release decision
    is measured separately and explicitly.
    """
    name = "release-readiness"
    if (r := empty_scan_guard(name, items)):
        return r
    with open(binding.reporting_category_file, encoding="utf-8") as fh:
        rc = json.load(fh)
    with open(binding.blueprint_file, encoding="utf-8") as fh:
        bp = json.load(fh)

    live = [i for i in items if itemio.servable(i)]
    findings = []

    unsourced = {c for i in live for c in (i.get("standardCodes") or [])
                 if rc["standards"].get(c, {}).get("source") == "UNMAPPED"}
    if unsourced:
        findings.append(Finding("reportingCategory",
            f"{len(unsourced)} standard(s) carry servable items with NO category source "
            f"(mapping sourceOfRecord={rc.get('sourceOfRecord')!r}). TDOE has published no "
            f"blueprint for {binding.standards_year}; until it does, this field cannot claim "
            f"to be the state's own category."))

    unmeasured = []
    if str(bp.get("status", "")).lower().startswith(("draft", "operating")):
        findings.append(Finding("blueprint",
            f"blueprint status is {bp.get('status')!r} — not signed off by the course owner"))

    unver = [i for i in live if i.get("alignmentStatus") == "unverified"]
    if unver:
        findings.append(Finding("alignment",
            f"{len(unver)} item(s) are kept and usable but their alignment is unverified, so "
            f"they are excluded from standards coverage. Not a defect in the items — a gap in "
            f"what can be claimed about coverage."))
    prov = [i for i in live if i.get("status") == "provisional"]
    if prov:
        findings.append(Finding("alignment",
            f"{len(prov)} item(s) are provisional: the standard's verb rose or elements were "
            f"added. Each needs a human alignment decision before it is Grade A."))

    debt = {
        "distractors with no rationale": sum(
            1 for i in live for c in itemio.choices(i)
            if c.get("id") != i.get("correctAnswer") and not (c.get("explanation") or "").strip()),
        "items with no dokRationale": sum(1 for i in live if not (i.get("dokRationale") or "").strip()),
        "items missing a bilingual field": sum(
            1 for i in live if not (i.get("stemEs") or "").strip()
            or not (i.get("explanationEs") or "").strip()),
    }
    for k, v in debt.items():
        if v:
            findings.append(Finding("authoring-debt", f"{v} {k}"))

    return Result(name, not findings, len(live), findings,
                  note='Grade A requires zero findings here. "Close" is not "A."')


def unmeasured_gates(results) -> Result:
    """Grade A cannot be claimed while any gate formed no opinion."""
    name = "all-gates-measured"
    # N/A is excluded: a gate with an honest reason for having nothing to judge
    # is not the L11 defect. The reason is required and shown in the report.
    un = [r.gate for r in results if not r.measured and not r.inapplicable]
    findings = [Finding(g, "gate judged 0 records — its PASS would have been vacuous")
                for g in un]
    return Result(name, not findings, len(results), findings,
                  note=f"{len(results) - len(un)}/{len(results)} gates actually measured something")


def gate_form_key_position(rendered_items, binding=None) -> Result:
    """Key positions AS RENDERED on this form.

    The bank-level gate reads each item's stored `correctAnswer` id, which is
    the position it happened to occupy in the source file. A form re-derives
    positions at render time, so running the bank gate over a form measured a
    distribution the student never sees: the form rendered 3/3/3/3 while the
    gate reported D at 42%.

    A gate must measure the artifact at the level the artifact exists.
    """
    name = "form-key-position"
    if (r := empty_scan_guard(name, rendered_items)):
        return r
    MAX_DEVIATION = 0.07
    counts = collections.Counter()
    for it in rendered_items:
        letter = it.get("_formKeyLetter")
        if letter:
            counts[letter] += 1
    if not counts:
        return Result(name, True, len(rendered_items), [], judged=0,
                      inapplicable="no selected-response items on this form carry a rendered "
                                   "key position")
    n = sum(counts.values())
    k = max(len(counts), 2)
    uniform = 1.0 / k
    share = {p: c / n for p, c in counts.items()}
    worst = max(share, key=share.get)
    dev = max(abs(v - uniform) for v in share.values())
    findings = []
    if dev > MAX_DEVIATION:
        findings.append(Finding(f"{k}-position cohort",
            f"rendered key position {worst!r} is {share[worst]:.0%} of keys, {dev:.1%} off the "
            f"{uniform:.0%} uniform share (bar: {MAX_DEVIATION:.0%}); "
            f"distribution {dict(sorted(counts.items()))}"))
    return Result(name, not findings, len(rendered_items), findings, judged=n,
                  note=f"{k}-position n={n} worst={worst}@{share[worst]:.0%} max-dev={dev:.1%}")


def gate_blueprint_achievability(items, binding=None) -> Result:
    """Can every standard reach at least the LOWEST tier the blueprint offers?

    Before tiering this failed on a flat requirement of one document-based item
    per standard — 94 needed against 30 in the bank — which blocked 71 standards
    with a shortage no amount of authoring on existing items could fix. Tiering
    made that a stated ceiling instead of a wall, so what remains worth failing
    on is a standard that cannot fill even the simplest form.
    """
    import alignment
    name = "blueprint-achievability"
    if (r := empty_scan_guard(name, items)):
        return r
    with open(binding.blueprint_file, encoding="utf-8") as fh:
        form = json.load(fh)["form"]
    stds = binding.standards()
    live = [i for i in items if itemio.aligned(i)]
    if not live:
        return Result(name, False, len(items),
                      [Finding("(none)", "no aligned items to measure against")],
                      note="EMPTY SCAN after alignment filter")
    by_std = collections.defaultdict(list)
    for it in live:
        hay = alignment.subject_text(it)
        for c in (it.get("standardCodes") or []):
            t = stds.get(c, {}).get("text")
            if t and alignment.relevant_to(hay, t):
                by_std[c].append(it)

    def fills(pool, tier):
        used = set()
        for slot in tier["slots"]:
            cand = [i for i in pool if i["id"] not in used
                    and i.get("itemType") in slot["types"] and i.get("dokLevel") == slot["dok"]]
            if not cand:
                return False
            used.add(cand[0]["id"])
        return True

    reached, findings = collections.Counter(), []
    for code in sorted(stds):
        pool = sorted(by_std.get(code, []), key=lambda i: i["id"])
        tid = next((t["id"] for t in form["tiers"] if fills(pool, t)), None)
        reached[tid or "none"] += 1
        if tid is None:
            findings.append(Finding(code,
                f"cannot fill even the lowest tier {form['tiers'][-1]['id']!r} "
                f"({len(pool)} relevant aligned item(s))"))
    return Result(name, not findings, len(live), findings, judged=len(stds),
                  note="; ".join(f"{k}={v}" for k, v in reached.most_common()))


def gate_form_standard_relevance(rendered_items, binding=None, standards=None) -> Result:
    """Every item on a form is about the standard it is PRINTED under.

    A form heading is a claim. An item carrying three standard codes is aligned
    if it matches any one of them, but printing it under the other two claims
    something the item does not support.
    """
    import alignment
    name = "form-standard-relevance"
    if (r := empty_scan_guard(name, rendered_items)):
        return r
    stds = binding.standards()
    declared = set(standards) if standards else None
    findings, judged = [], 0
    for it in rendered_items:
        codes = [c for c in (it.get("standardCodes") or [])
                 if c in stds and (declared is None or c in declared)]
        if not codes:
            continue
        hay = alignment.subject_text(it)
        for c in codes:
            judged += 1
            if not alignment.relevant_to(hay, stds[c]["text"]):
                findings.append(Finding(it.get("id", "?"),
                    f"printed under {c} but names nothing that identifies it — the heading "
                    f"claims more than the item supports", it.get("_file", "")))
    return Result(name, not findings, len(rendered_items), findings, judged=judged)


def gate_form_surface(items, binding=None, blueprint=None) -> Result:
    """An assessment form carries ONLY the item types its blueprint allows.

    Sean, 2026-09-03: "all the questions on the assessment builder need to be
    TCAP-style multiple choice, maybe multiple select." Before this, a form
    could reach its highest tier only by including a constructed response and a
    document-based question, so the builder was REQUIRED to produce the mixed
    packet he objected to. The blueprint now declares `allowedItemTypes` and
    this gate holds the artifact to it.

    Extended responses are not deleted and are not lesser — they leave the
    ASSESSMENT surface and become their own activity. A gate that only counted
    item types would have read green on the old form too; what makes this one
    real is that the blueprint states the surface it is measuring.
    """
    name = "form-surface"
    if (r := empty_scan_guard(name, items)):
        return r
    if blueprint is None:
        with open(binding.blueprint_file, encoding="utf-8") as fh:
            blueprint = json.load(fh)["form"]
    allowed = set(blueprint.get("allowedItemTypes") or [])
    if not allowed:
        return Result(name, False, len(items), [Finding("(blueprint)",
            "the blueprint declares no allowedItemTypes, so 'assessment form' means nothing "
            "and this gate cannot judge anything", binding.blueprint_file if binding else "")],
            judged=0)
    findings, judged = [], 0
    for it in items:
        if not itemio.servable(it) and it.get("_surface") is None:
            continue
        judged += 1
        t = it.get("itemType")
        if t not in allowed:
            findings.append(Finding(it.get("id", "?"),
                f"itemType {t!r} on an assessment form, which allows only "
                f"{', '.join(sorted(allowed))} — an extended response belongs on its own "
                f"activity, not inside a test form", it.get("_file", "")))
    return Result(name, not findings, len(items), findings, judged=judged,
                  note=f"surface: {blueprint.get('surface', 'unstated')}; "
                       f"allowed: {', '.join(sorted(allowed))}")
