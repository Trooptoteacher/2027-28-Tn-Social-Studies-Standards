"""Element-level alignment between a 2026-27 standard and its 2027-28 successor.

Character similarity is the WRONG instrument and measurement showed it is
anti-correlated with what matters:

  US.16 -> US.17 scores 0.79 and is the SAME standard with its bullets
      reordered — identical named elements.
  US.12 -> US.12 scores 0.89 and DELETED the Clayton Antitrust Act of 1914.
  US.19 -> US.21 scores 0.89 and REPLACED "spread American democratic and
      moral ideals" with "American nationalism".
  US.60 scores 0.94 and changed its verb from Explain to ANALYZE — a DOK
      shift a text ratio cannot see.

So route on the CONTENT CHECKLIST instead. The words after "including" in the
state's sentence are a checklist, not decoration: an element dropped from the
new standard puts every item testing it out of scope, however similar the two
sentences read.
"""
from __future__ import annotations

import re

# Verbs, ordered by the cognitive demand they signal. A standard whose verb
# rises has raised its DOK ceiling, and items written to the old verb may now
# be under-levelled.
VERB_TIER = {
    "identify": 1, "list": 1, "define": 1, "locate": 1, "name": 1,
    "describe": 2, "summarize": 2, "explain": 2, "examine": 2, "discuss": 2,
    "compare": 3, "contrast": 3, "analyze": 3, "assess": 3, "evaluate": 3,
    "argue": 4, "synthesize": 4, "justify": 4,
}

_TCA = re.compile(r"\(?\s*T\.?C\.?A\.?\s*§[^)]*\)?", re.I)
_LEAD = re.compile(r"^(the|a|an)\s+", re.I)
_GENERIC = {"american", "americans", "america", "united states", "states united",
            "u.s.", "us", "states", "president", "congress", "government",
            "federal", "national", "state", "supreme court",
            # Bare category nouns identify nothing without their qualifier.
            "amendment", "act", "treaty", "war", "movement", "era", "plan",
            "doctrine", "court", "case", "policy", "policies", "decision"}
_STOP = {"the", "a", "an", "and", "or", "of", "in", "on", "to", "for", "with",
         "its", "their", "his", "her", "such", "as", "including", "e.g.", "i.e."}


def verb(text: str) -> str:
    m = re.match(r"\s*([A-Za-z]+)", text or "")
    return m.group(1).lower() if m else ""


def elements(text: str) -> list:
    """The standard's named content elements — its checklist."""
    if not text:
        return []
    t = _TCA.sub("", text).replace("•", "|").replace("\n", " ")
    # Everything after the first "including" / "such as" is the checklist.
    m = re.search(r"\b(including|such as)\b:?", t, re.I)
    tail = t[m.end():] if m else ""
    # Parenthetical example lists carry named elements too: (e.g., X, Y, Z)
    for p in re.findall(r"\((?:e\.g\.|i\.e\.)[,:]?\s*([^)]*)\)", t, re.I):
        tail += " | " + p
    if not tail.strip():
        return []
    # Strip parenthetical example groups BEFORE splitting — splitting first
    # breaks the parens and leaves "(e.g" fragments behind as elements.
    tail = re.sub(r"\((?:e\.g\.|i\.e\.)[^)]*\)", " ", tail, flags=re.I)
    parts = re.split(r"\|", tail) if "|" in tail else [tail]
    out = []
    for p in parts:
        # Split on commas AND " and ": conjoined named entities are separate
        # elements ("the Sherman Antitrust Act of 1890 and the Clayton
        # Antitrust Act of 1914" is two, and only one of them survived).
        for sub in re.split(r",|\band\b", p):
            s = _TCA.sub("", sub)
            s = _LEAD.sub("", s.strip(" .;:—–-\t")).strip()
            if len(s) > 3:
                out.append(s)
    return out


def _key(el: str) -> str:
    """Normalized comparison key: content words only, order-insensitive."""
    t = el.lower().replace("\u2019", "'")
    t = re.sub(r"\bvs?\.?\b", "v", t)          # v. / vs. / vs -> v
    words = [w for w in re.findall(r"[A-Za-z0-9']+", t) if w not in _STOP]
    return " ".join(sorted(words))


def signals(el: str) -> list:
    """Distinctive phrases that identify an item as testing this element.

    Proper nouns first — they are precise. An element with no proper noun
    falls back to its content words, and the caller requires two of them, so a
    generic element like "poor economy" cannot match on "economy" alone.
    """
    # A leading ordinal belongs to the name: the signal for "18th Amendment" is
    # "18th Amendment", not "Amendment" — which matches every amendment item in
    # the bank and quarantined a 17th Amendment question.
    props = re.findall(
        r"\b(?:\d+(?:st|nd|rd|th)\s+)?(?:[A-Z][\w'’.-]*)(?:\s+(?:of|the|and|de)?\s*[A-Z][\w'’.-]*)*",
        el)
    props = [p.strip() for p in props if len(p.strip()) > 3]
    # A demonym or a bare country name identifies nothing in a US History bank.
    props = [p for p in props if _key(p) not in _GENERIC]
    # Carry a trailing year into the phrase: "Antitrust Act" vs "Act of 1914".
    props = [p for p in props if len(p.split()) >= 2 or len(p) >= 6]
    if props:
        return props
    return [w for w in re.findall(r"[A-Za-z']{5,}", el.lower()) if w not in _STOP]


def _stem(w: str) -> str:
    """Crude prefix stem. 'suffragettes' and 'suffragists' are the same element
    reworded, not a deletion."""
    return w[:6]


def retained_in(el: str, new_elements: list) -> bool:
    """Is this old element still present, however reworded?

    Exact key comparison was too brittle and produced a false-positive class
    that mattered: "role of Tennessee as the 'Perfect 36.'" reads as DROPPED
    against "Passage of the 19th Amendment, including the role of Tennessee",
    when only the nickname went. Match on the element's SIGNAL instead — the
    thing that identifies it — not on its whole phrasing.
    """
    hay = " | ".join(new_elements).lower().replace("\u2019", "'")
    hay = re.sub(r"\bvs?\.?\b", "v", hay)
    hay_stems = {_stem(w) for w in re.findall(r"[A-Za-z']+", hay)}
    sigs = signals(el)
    named = [x for x in sigs if re.search(r"[A-Z]", x)]
    for sig in named:
        norm = re.sub(r"\bvs?\.?\b", "v", sig.lower().replace("\u2019", "'"))
        if norm in hay:                           # named entity survives verbatim
            return True
    if named:
        return False
    # Lowercase descriptive element: signals() returns individual words, so they
    # are judged TOGETHER. Judging them one at a time could never satisfy a
    # two-word rule, and "activities of suffragettes" read as dropped against
    # "Activities of suffragists" — a rewording, not a deletion.
    toks = [w for w in sigs if w not in _STOP]
    if not toks:
        return False
    hits = sum(1 for w in toks if _stem(w) in hay_stems)
    return hits >= max(2, len(toks) - 1) or (len(toks) == 1 and hits == 1)


def delta(old_text: str, new_text: str) -> dict:
    """What the revision did to the checklist."""
    o, n = elements(old_text), elements(new_text)
    ok = {_key(e): e for e in o if _key(e)}
    nk = {_key(e): e for e in n if _key(e)}
    meaningful = lambda e: bool(signals(e))
    dropped = [ok[k] for k in ok
               if k not in nk and meaningful(ok[k]) and not retained_in(ok[k], n)]
    added = [nk[k] for k in nk
             if k not in ok and meaningful(nk[k]) and not retained_in(nk[k], o)]
    ov, nv = verb(old_text), verb(new_text)
    return {
        "oldElements": o, "newElements": n,
        "dropped": dropped, "added": added,
        "retained": [ok[k] for k in ok if k in nk],
        "oldVerb": ov, "newVerb": nv,
        "verbRaised": VERB_TIER.get(nv, 0) > VERB_TIER.get(ov, 0),
        "verbChanged": ov != nv,
    }


def tests_dropped_element(item_text: str, dropped: list) -> list:
    """Which dropped elements this item appears to test.

    The caller passes the STEM, the KEY and the key's explanation — never the
    distractors. A distractor naming a dropped element is not evidence the item
    tests it: an item asking about the 17th Amendment was quarantined for the
    18th because a wrong choice mentioned it.
    """
    hay = (item_text or "").lower().replace("\u2019", "'")
    hay = re.sub(r"\bvs?\.?\b", "v", hay)
    hit = []
    for el in dropped:
        sig = signals(el)
        proper = any(re.search(r"[A-Z]", s) for s in sig)
        if proper:
            if any(re.sub(r"\bvs?\.?\b", "v", s.lower().replace("\u2019", "'")) in hay
                   for s in sig):
                hit.append(el)
        else:
            if sum(1 for s in sig if s in hay) >= 2:
                hit.append(el)
    return hit


def named_entities(text: str) -> list:
    """Every named entity in a standard's WHOLE sentence, not just its checklist.

    The checklist — the words after "including" — is what a REVISION changes, so
    delta() reads only that. But what a standard is ABOUT is often named in its
    stem: US.74 is "Examine the decision and impacts of Brown v. Board of
    Education...", and "Brown v. Board of Education" never appears after an
    "including". Matching items against the checklist alone flagged correctly
    filed Brown questions as off-standard, and then proposed moving them.

    Same rules as signals(): multi-word names, or a single capitalised word that
    does not merely open its phrase.
    """
    t = _TCA.sub("", text or "")
    # A bullet is a hard boundary: without one, "United States vs. Nixon" and the
    # next bullet's "Controversy" merge into a single phantom entity.
    t = re.sub(r"[•\n]", " ; ", t)
    # The standard opens with its verb ("Examine the Watergate scandal"), whose
    # capital is grammar, not a name.
    first = re.match(r"\s*([A-Za-z]+)", t)
    if first and first.group(1).lower() in VERB_TIER:
        t = t[first.end(1):]
    props = re.findall(
        r"\b(?:\d+(?:st|nd|rd|th)\s+)?(?:[A-Z][\w'’.-]*)(?:\s+(?:of|the|and|de|v\.|vs\.)?\s*[A-Z][\w'’.-]*)*",
        t)
    out, seen = [], set()
    for p in props:
        p = p.strip(" .,;:")
        if len(p) < 4 or _key(p) in _GENERIC:
            continue
        # Drop a single word that merely opens the sentence or a bullet.
        if len(p.split()) < 2 and re.search(r"(?:^|[•:;.]\s*)" + re.escape(p), t):
            continue
        if _key(p) in seen:
            continue
        seen.add(_key(p))
        out.append(p)
    return out


def standard_signals(text: str) -> list:
    """Everything that identifies a standard: checklist elements + named entities."""
    sigs = [s for el in elements(text) for s in signals(el)]
    return sigs + named_entities(text)


def identifying_signals(text: str) -> list:
    """Signals strong enough to say an item is ABOUT this standard.

    signals() falls back to bare content words when an element has no proper
    noun, which is right for comparing two revisions of a standard but wrong for
    deciding what an item is about: "Support for conservation" yields "Support",
    and a constructed response on the 19th Amendment matched Theodore
    Roosevelt's standard on that one word.

    Same rule the re-home matcher already used (L20): a multi-word name, or a
    single capitalised word that does not merely open its phrase.
    """
    out = []
    for el in elements(text):
        for sig in signals(el):
            if not re.search(r"[A-Z]", sig):
                continue
            if len(sig.split()) >= 2 or not el.strip().lower().startswith(sig.lower()):
                out.append(sig)
    return out + named_entities(text)


_ORDINAL_WORDS = {
    "first": "1st", "second": "2nd", "third": "3rd", "fourth": "4th", "fifth": "5th",
    "sixth": "6th", "seventh": "7th", "eighth": "8th", "ninth": "9th", "tenth": "10th",
    "eleventh": "11th", "twelfth": "12th", "thirteenth": "13th", "fourteenth": "14th",
    "fifteenth": "15th", "sixteenth": "16th", "seventeenth": "17th", "eighteenth": "18th",
    "nineteenth": "19th", "twentieth": "20th", "twenty-first": "21st",
    "twenty-second": "22nd", "twenty-fourth": "24th", "twenty-sixth": "26th",
}
_ORDINAL_RX = re.compile(r"\b(" + "|".join(sorted(_ORDINAL_WORDS, key=len, reverse=True)) + r")\b",
                         re.I)


def normalize_ordinals(text: str) -> str:
    """"Nineteenth Amendment" and "19th Amendment" are the same thing.

    Standards write the numeral; items commonly spell the word — 92 occurrences
    of a word-spelled ordinal sit in student-visible text. Literal substring
    matching read those items as naming nothing, which would flag a correctly
    filed 19th Amendment question as off-standard.
    """
    return _ORDINAL_RX.sub(lambda m: _ORDINAL_WORDS[m.group(1).lower()], text or "")




# ---------------------------------------------------------------------------
# TOPIC SIGNALS — the standards a proper noun cannot describe.
#
# identifying_signals() requires a capitalised name. Nine of the 94 standards
# have none: US.13 is "working conditions ... women and children as a labor
# source", US.69 is "atomic testing / civil defense / mutual assured
# destruction / fallout shelters", US.67 is "television and mass media". For
# those standards the matcher returned an EMPTY signal set, relevance_scan
# skipped every item claiming them without counting it, and the readiness
# report showed 0 aligned items where 351 items in fact claimed the standard.
# Nothing anywhere said the standard was unjudgeable. That is a gate green
# against nothing, in its per-standard shape (L51).
#
# A common noun is looser than a name, so the SUFFICIENCY BAR is higher: a
# multi-word topic phrase matched verbatim is evidence on its own; a single
# word is evidence only alongside a second one. Measured against 400 sampled
# items, topic signals claim FEWER standards per item than the proper-noun
# matcher already accepted (mean 0.77 vs 1.22), so this is not a loosening.
# ---------------------------------------------------------------------------

_TOPIC_STOP = {
    "the", "a", "an", "and", "or", "of", "in", "on", "to", "for", "with", "its",
    "their", "his", "her", "such", "as", "including", "by", "from", "that",
    "which", "during", "at", "between", "among", "this", "these", "those",
    "other", "more", "most", "new", "was", "were", "is", "are", "be", "been",
    "who", "whose", "what", "how", "why", "surrounding", "regarding",
    "concerning", "over", "about", "toward", "towards", "into", "through",
    "against", "after", "before", "under", "within",
    # VERBS BREAK A RUN — they are never part of a topic term. Held as merely
    # "generic" they stayed INSIDE the run, so "movies played" became a
    # two-word phrase no item would ever contain and "movies" was unreachable.
    "describe", "explain", "analyze", "analyse", "compare", "contrast", "assess",
    "examine", "summarize", "evaluate", "identify", "determine", "cite", "argue",
    "justify", "synthesize", "trace", "discuss", "interpret", "integrate", "draw",
    "use", "uses", "used", "using", "understand", "support", "include", "included",
    "played", "made", "make", "given",
}

# Words that never say what a standard is ABOUT. Three families: the Bloom
# verbs and analytic scaffolding a standard opens with; the contentless
# abstractions every standard shares ("impact", "causes", "significance"); and
# the bare category nouns _GENERIC already names ("amendment", "act", "war").
# The last group is curated from MEASUREMENT, not intuition — each word here
# was observed claiming items across unrelated standards. "civil" was the
# worst: on its own it matched civil war, civil rights and civil defense items
# indiscriminately, while "civil defense" and "civil rights act" are precise.
_TOPIC_GENERIC = {
    "impact", "impacts", "effect", "effects", "cause", "causes", "role", "roles",
    "importance", "significance", "development", "developments", "growth",
    "change", "changes", "result", "results", "response", "responses",
    "influence", "contribution", "contributions", "reason", "reasons", "factor",
    "factors", "event", "events", "period", "periods", "era", "eras", "time",
    "times", "century", "centuries", "decade", "decades", "way", "ways", "point",
    "points", "view", "views", "argument", "arguments", "idea", "ideas",
    "philosophy", "philosophies", "advantage", "advantages", "disadvantage",
    "disadvantages", "limitation", "limitations", "challenge", "challenges",
    "advancement", "advancements", "emergence", "rise", "spread", "increase",
    "increasing", "decline", "major", "various", "different", "desire", "advent",
    "debate", "debates", "fear", "fears", "status", "conditions", "condition",
    "group", "groups", "issue", "issues",
    "american", "americans", "america", "united", "states", "nation", "nations",
    "national", "country", "us", "government", "governments", "federal", "state",
    "president", "presidents", "congress", "people", "society", "social",
    "economy", "economic", "culture", "cultural", "political", "politics",
    "home", "homes", "life", "lives", "world", "history", "late", "early",
    "upon", "also",
    "crisis", "program", "programs", "legislation", "reform", "reforms",
    "system", "systems", "order", "orders", "policy", "policies", "movement",
    "movements", "amendment", "amendments", "act", "acts", "treaty", "war",
    "wars", "plan", "plans", "doctrine", "court", "courts", "case", "cases",
    "decision", "decisions", "law", "laws", "bill", "bills", "agency", "agencies",
    "civil", "action", "actions", "activity", "activities", "leader", "leaders",
    "figure", "figures", "outcome", "outcomes", "struggle", "trajectory",
    "geography", "geographic", "related", "spectrum", "broader", "significant",
    "key", "access", "effort", "efforts", "eventual", "aspect", "aspects",
    "feature", "features", "element", "elements", "example", "examples", "trend",
    "trends", "pattern", "patterns", "form", "forms", "type", "types", "kind",
    "kinds", "means", "method", "methods", "practice", "practices",
}

# Phrases that pass the word test and still identify nothing in a US History
# bank, because every unit's items say them.
_TOPIC_PHRASE_GENERIC = {
    "american economy", "american society", "american home", "american homes",
    "american people", "american culture", "american life", "world war",
}

_TOPIC_MIN_SINGLE = 5      # a whole run that is one word
_TOPIC_MIN_CORE = 8        # a single word left after trimming leading generics


def _topic_phrases(text: str) -> list:
    """The standard cut into phrases. Unlike elements(), this reads the WHOLE
    sentence — a standard with no "including" clause (US.22, US.65, US.67) has
    no elements at all, and its topic lives in the main clause."""
    t = _TCA.sub("", text or "")
    t = re.sub(r"[•\n]", " ; ", t)
    t = re.sub(r"\((?:e\.g\.|i\.e\.)[,:]?\s*", " ; ", t, flags=re.I).replace(")", " ; ")
    first = re.match(r"\s*([A-Za-z]+)", t)
    if first and first.group(1).lower() in VERB_TIER:
        t = t[first.end(1):]
    t = re.sub(r"\b(including|such as)\b:?", " ; ", t, flags=re.I)
    return [p for p in re.split(r"[;,:]|\band\b|\bor\b", t) if p.strip()]


def topic_signals(text: str) -> list:
    """Common-noun phrases that say what a standard is about.

    A run is a stretch of adjacent non-stopword words. Generic words stay
    INSIDE a run — "popular culture" and "working conditions" are real terms
    whose head noun is generic — but a run made only of generic words is
    dropped. Leading generics are also offered trimmed, so "american
    imperialism" additionally yields "imperialism".
    """
    out, seen = [], set()
    for p in _topic_phrases(text):
        words = re.findall(r"[A-Za-z'\u2019-]+", p.lower())
        run = []
        for w in words + [None]:
            if w is not None and w not in _TOPIC_STOP and len(w) > 2:
                run.append(w)
                continue
            if run and any(x not in _TOPIC_GENERIC for x in run):
                core = list(run)
                while core and core[0] in _TOPIC_GENERIC:
                    core.pop(0)
                for cand in ([run, core] if core != run else [run]):
                    floor = _TOPIC_MIN_SINGLE if cand is run else _TOPIC_MIN_CORE
                    if len(cand) >= 2 or (cand and len(cand[0]) >= floor):
                        term = " ".join(cand)
                        if term not in seen and term not in _TOPIC_PHRASE_GENERIC:
                            seen.add(term)
                            out.append(term)
            run = []
    return out


def topic_evidence(haystack: str, standard_text: str) -> list:
    """Topic terms of ONE standard this text carries, IF they meet the bar.

    The bar is what keeps a common noun honest: one multi-word phrase, or two
    distinct single words. One single word alone is not evidence — "radio" in
    a Fireside Chats item must not claim the standard on popular culture.
    """
    hay = normalize_ordinals(haystack or "").lower()
    hit = [t for t in topic_signals(standard_text) if t in hay]
    return hit if (any(" " in t for t in hit) or len(hit) >= 2) else []


def judgeable_signals(standard_text: str) -> list:
    """Everything this system can use to decide relevance for a standard.

    A standard with an EMPTY result cannot be judged at all, and that must be
    reported rather than skipped (gate_signal_coverage).
    """
    return identifying_signals(standard_text) + topic_signals(standard_text)


def relevant_to(haystack: str, standard_text: str) -> list:
    """Which signals of ONE standard this text carries — the ONE matcher.

    Proper-noun signals first; topic signals when the standard offers no name,
    or the item uses the plain words rather than the formal one. Every caller
    goes through here: re-deriving this rule is L22/L40/L46, and its copies
    have disagreed with the original four separate times.
    """
    hay = normalize_ordinals(haystack or "").lower()
    hits = [s for s in identifying_signals(standard_text)
            if normalize_ordinals(s).lower() in hay]
    return hits or topic_evidence(haystack, standard_text)


def subject_text(item) -> str:
    """THE text that says what an item is about. One definition, used everywhere.

    Stem plus the KEY. Not the distractors: they are deliberately wrong content,
    and a wrong choice mentioning "the Soviet Union" filed a Carter-era Panama
    Canal Treaties item under Cold War superpower competition. 141 items were
    relevant to a standard only through a distractor. This is L07 — the same
    rule the re-home matcher already used — arriving at the relevance layer.

    Not the key EXPLANATION either: that is authored, including by this system,
    and content written to explain an item must never prove where it belongs
    (L38).
    """
    parts = [item.get("stem") or ""]
    key = item.get("correctAnswer")
    for c in (item.get("choices") or []):
        if isinstance(c, dict) and c.get("id") == key:
            parts.append(c.get("text") or "")
    return " ".join(parts)


def identifiability(standard_text: str) -> int:
    """How many DISTINCT signals identify this standard.

    A standard identifiable by one coarse signal makes every relevance verdict
    on it soft: US.25's only signal is "World War I", so an essay on American
    imperialism 1890-1914 matched it. 19 of 94 standards sit below two signals,
    and that is a stated limitation rather than something to paper over.
    """
    return len(set(judgeable_signals(standard_text)))
