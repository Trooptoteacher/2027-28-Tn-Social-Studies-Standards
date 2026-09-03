"""The binding. Loaded by every generator and every gate.

One shared toolchain, many walled courses. The assertion here is the wall.
It is deliberately a hard exception, not a warning: a generator that will
happily emit another course's prefix will eventually do it.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field

BANK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class BindingViolation(Exception):
    """Raised when output contains a standard code outside the declared binding."""


@dataclass
class Binding:
    course: str
    course_title: str
    prefix: str
    standards_year: str
    standards_file: str
    crosswalk_file: str
    output_dir: str
    quarantine_dir: str
    blueprint_file: str
    reporting_category_file: str
    forbidden_prefixes: list = field(default_factory=list)
    forbidden_years: list = field(default_factory=list)
    disclosure_line: str = ""
    _valid_codes: set = field(default_factory=set, repr=False)

    # ---- code shape -------------------------------------------------
    @property
    def code_re(self) -> re.Pattern:
        return re.compile(rf"^{re.escape(self.prefix)}\.\d{{2}}$")

    def valid_codes(self) -> set:
        """Every code the declared standards file actually defines.

        Membership is checked against the file, never against the regex alone:
        `US.99` matches the prefix and does not exist.
        """
        if not self._valid_codes:
            with open(self.standards_file, encoding="utf-8") as fh:
                doc = json.load(fh)
            if doc.get("standardsPrefix") != self.prefix:
                raise BindingViolation(
                    f"standards file declares prefix {doc.get('standardsPrefix')!r}, "
                    f"binding declares {self.prefix!r} — refusing to build"
                )
            if doc.get("standardsYear") != self.standards_year:
                raise BindingViolation(
                    f"standards file declares year {doc.get('standardsYear')!r}, "
                    f"binding declares {self.standards_year!r} — refusing to build"
                )
            self._valid_codes = {s["code"] for s in doc["standards"]}
        return self._valid_codes

    def standards(self) -> dict:
        with open(self.standards_file, encoding="utf-8") as fh:
            return {s["code"]: s for s in json.load(fh)["standards"]}

    # ---- the assertion ----------------------------------------------
    def assert_codes(self, codes, where="output") -> None:
        """Fail if any code falls outside the declared course.

        Called by every generator before it writes and by the binding gate
        after. Checked in three ways, because each catches a different way
        this goes wrong:
          1. shape  — a foreign prefix (GC.01 in a US bank)
          2. existence — a well-shaped code the standards file never defines
          3. year   — a code carrying a superseded standards year
        """
        bad_shape, unknown = [], []
        for code in codes:
            if not self.code_re.match(str(code)):
                bad_shape.append(code)
            elif code not in self.valid_codes():
                unknown.append(code)
        problems = []
        if bad_shape:
            problems.append(
                f"{len(bad_shape)} code(s) outside declared prefix "
                f"{self.prefix!r}: {sorted(set(bad_shape))[:10]}"
            )
        if unknown:
            problems.append(
                f"{len(unknown)} code(s) match the prefix but are not defined in "
                f"{os.path.relpath(self.standards_file, BANK_ROOT)}: "
                f"{sorted(set(unknown))[:10]}"
            )
        if problems:
            raise BindingViolation(
                f"BINDING VIOLATION in {where} "
                f"[{self.course} · {self.prefix} · {self.standards_year}]: "
                + "; ".join(problems)
            )

    def assert_year(self, declared_year, where="output") -> None:
        if declared_year in self.forbidden_years:
            raise BindingViolation(
                f"BINDING VIOLATION in {where}: standards year {declared_year!r} is "
                f"superseded. A code is not a stable identifier across years — "
                f"84 of 94 US codes changed meaning. Declared year is "
                f"{self.standards_year!r}."
            )
        if declared_year != self.standards_year:
            raise BindingViolation(
                f"BINDING VIOLATION in {where}: standards year {declared_year!r} "
                f"does not match declared {self.standards_year!r}."
            )

    def declaration(self) -> str:
        """The line a build prints before it does anything else."""
        return (
            f"BINDING — course: {self.course_title} ({self.course}) · "
            f"prefix: {self.prefix} · standards year: {self.standards_year} · "
            f"standards file: {os.path.relpath(self.standards_file, BANK_ROOT)} · "
            f"output: {self.output_dir}"
        )


def load(path=None) -> Binding:
    path = path or os.path.join(BANK_ROOT, "binding.json")
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    here = os.path.dirname(os.path.abspath(path))
    resolve = lambda p: os.path.normpath(os.path.join(here, p))
    return Binding(
        course=raw["course"],
        course_title=raw["courseTitle"],
        prefix=raw["standardsPrefix"],
        standards_year=raw["standardsYear"],
        standards_file=resolve(raw["standardsFile"]),
        crosswalk_file=resolve(raw["crosswalkFile"]),
        output_dir=resolve(raw["outputDir"]),
        quarantine_dir=resolve(raw["quarantineDir"]),
        blueprint_file=resolve(raw["blueprintFile"]),
        reporting_category_file=resolve(raw["reportingCategoryFile"]),
        forbidden_prefixes=raw.get("forbiddenPrefixes", {}).get("prefixes", []),
        forbidden_years=raw.get("forbiddenStandardsYears", {}).get("years", []),
        disclosure_line=raw.get("disclosureLine", ""),
    )
