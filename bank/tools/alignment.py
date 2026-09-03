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
