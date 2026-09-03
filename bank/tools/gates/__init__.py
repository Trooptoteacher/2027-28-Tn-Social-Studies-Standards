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

    @property
    def status(self) -> str:
        return "PASS" if self.passed else "FAIL"

    def report(self, limit=8) -> str:
        head = f"[{self.status}] {self.gate} — scanned {self.scanned}"
        if self.note:
            head += f" — {self.note}"
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
