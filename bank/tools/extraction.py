"""Never let an extractor's silence count as evidence of absence.

Scanning the TDOE standards PDF for "reporting category" returned zero hits.
So did "assessment", "blueprint", "TCAP" — and so did "Compromise of 1877",
which is unquestionably in that document. The extractor was broken, not the
document empty. Zero hits from a broken extractor is indistinguishable from
zero hits from a document that truly lacks the term, and it reads like an
answer.

So: an extractor must PROVE itself against control strings known to be present
before any "not found" it reports may be believed.
"""
from __future__ import annotations


class UnprovenExtractor(Exception):
    """The extractor failed its controls, so its findings mean nothing."""


def prove(text: str, controls, source: str = "source") -> None:
    """Raise unless every control string is present in the extracted text.

    `controls` are strings you KNOW the source contains. Pick them from a
    different part of the document than the thing you are looking for, and
    prefer distinctive phrases over common words.
    """
    if not controls:
        raise UnprovenExtractor(
            f"no control strings supplied for {source}: an extractor that has not "
            f"proved itself cannot report an absence")
    low = (text or "").lower()
    missing = [c for c in controls if c.lower() not in low]
    if missing:
        raise UnprovenExtractor(
            f"extraction from {source} is UNPROVEN: control string(s) {missing!r} are "
            f"known to be present and were not found in {len(text or '')} extracted "
            f"characters. Any 'not found' from this extractor is meaningless — fix the "
            f"extractor or use a different tool before concluding anything.")


def absent(text: str, needle: str, controls, source: str = "source") -> bool:
    """True only if `needle` is genuinely absent from a PROVEN extraction."""
    prove(text, controls, source)
    return needle.lower() not in (text or "").lower()


def find_all(text: str, needles, controls, source: str = "source") -> dict:
    """{needle: count} from a proven extraction. Raises if unproven."""
    prove(text, controls, source)
    low = (text or "").lower()
    return {n: low.count(n.lower()) for n in needles}
