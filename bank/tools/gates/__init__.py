"""Gates. Each one is written against a defect it has actually caught.

Two rules hold for every gate in this package:

  1. It reads the BUILT ARTIFACT, never the generator source.
  2. It FAILS on an empty scan. A gate green against nothing is the most
     dangerous result there is, and it reads exactly like a clean pass.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Finding:
    item_id: str
    detail: str
    file: str = ""

    def __str__(self):
        loc = f" [{self.file}]" if self.file else ""
        return f"{self.item_id}{loc}: {self.detail}"


@dataclass
class Result:
    gate: str
    passed: bool
    scanned: int = 0
    findings: list = field(default_factory=list)
    note: str = ""
    inapplicable: str = ""
    """Why this gate has nothing to judge in THIS artifact — never blank when set.

    A narrow and dangerous distinction. `NOT MEASURED` exists because a gate
    whose filter never matches anything reports a meaningless PASS (L11:
    teacher-side-isolation over 3,986 items, judging none). But a gate can also
    have nothing to judge for an honest reason — citation-integrity on a form
    whose items carry no citations. That is N/A, not a failure of the form.

    The loophole this could open is obvious, so: the reason is REQUIRED, N/A is
    never reported as PASS, and tests/test_regressions.py pins that a gate
    cannot claim inapplicable while its population exists.
    """
    judged: int = None
    """How many records the gate actually JUDGED, after its own filtering.

    `scanned` is the outer population; `judged` is the sub-population the gate
    forms an opinion about. They differ, and the difference is dangerous:
    teacher-side-isolation reported PASS over 3,986 scanned while judging ZERO
    records, because no artifact yet carried the surface tag it filters on. The
    empty-scan guard did its job on the outer scan and the gate was still
    meaningless. A gate that judged nothing is NOT a pass.
    """

    @property
    def measured(self) -> bool:
        return self.judged is None or self.judged > 0

    @property
    def status(self) -> str:
        if self.inapplicable:
            return "N/A"
        if not self.measured:
            return "NOT MEASURED"
        return "PASS" if self.passed else "FAIL"

    @property
    def counts_as_pass(self) -> bool:
        """N/A is not a pass and not a failure — it is excluded from the tally."""
        return self.passed and self.measured and not self.inapplicable

    def report(self, limit=8) -> str:
        head = f"[{self.status}] {self.gate} — scanned {self.scanned}"
        if self.judged is not None and self.judged != self.scanned:
            head += f", judged {self.judged}"
        if self.note:
            head += f" — {self.note}"
        if self.inapplicable:
            return head + f"\n        N/A — {self.inapplicable}"
        if not self.measured:
            return head + "\n        judged 0 records — a gate that formed no opinion is not a pass"
        if self.passed:
            return head
        lines = [head, f"        {len(self.findings)} finding(s):"]
        for f in self.findings[:limit]:
            lines.append(f"          - {f}")
        if len(self.findings) > limit:
            lines.append(f"          … and {len(self.findings) - limit} more")
        return "\n".join(lines)


def empty_scan_guard(gate_name: str, items: list):
    """Every gate must fail when it scans zero items.

    Returns a failing Result, or None if there is something to measure.
    """
    if not items:
        return Result(
            gate=gate_name,
            passed=False,
            scanned=0,
            note="EMPTY SCAN — refusing to report green against nothing",
            findings=[Finding("(none)", "gate scanned 0 items; a green gate over an "
                                        "empty set reads exactly like a clean pass")],
        )
    return None
