#!/usr/bin/env python3
"""Gate: the source PDF is the exact document PROVENANCE.md says it is.

    python3 tools/check_provenance.py

Why this exists
---------------
Every file in this repository is derived from one PDF, and every downstream
claim — 1,012 standards parsed verbatim, a crosswalk naming 416 colliding
codes, the standards synced into the web app under a sha256 pin — rests on that
PDF being the document Sean supplied on 2026-08-28.

Nothing recorded which document that was. PROVENANCE.md named the file and the
page count and asserted the rest. A different edition dropped into `source/`
under the same filename would have re-parsed cleanly, produced a plausible set
of standards, and passed the verbatim validator — because the validator checks
the standards against whatever PDF is sitting there, not against the right one.

So the hash is the anchor. The verbatim gate proves the standards match the PDF;
this proves the PDF is the one the provenance describes.
"""
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "source" / "TN-Social-Studies-Standards-2027-28.pdf"
DOC = ROOT / "PROVENANCE.md"


def main():
    if not PDF.exists():
        print(f"FAIL  the source document is missing: {PDF.relative_to(ROOT)}")
        return 1
    recorded = re.search(r"\*\*SHA-256\*\*\s*\|\s*`([0-9a-f]{64})`", DOC.read_text())
    if not recorded:
        print("FAIL  PROVENANCE.md records no SHA-256 for the source document")
        return 1
    actual = hashlib.sha256(PDF.read_bytes()).hexdigest()
    if actual != recorded.group(1):
        print("FAIL  the PDF in source/ is NOT the document PROVENANCE.md describes")
        print(f"      recorded  {recorded.group(1)}")
        print(f"      actual    {actual}")
        print("      Everything in this repository is derived from that document. Do not")
        print("      re-parse against a different one — establish which is correct first.")
        return 1
    print("check_provenance — the source document is the one on record\n")
    print(f"  ok   {PDF.name}")
    print(f"  ok   sha256 {actual}")
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
