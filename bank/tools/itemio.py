"""Load a built bank from disk. Gates read the ARTIFACT, never the generator source.

Reading a builder tells you what was supposed to happen. The output tells you
what did.
"""
from __future__ import annotations

import glob
import json
import os

BANK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(BANK_ROOT, "schema", "item.schema.json")

SINGLE_SELECT = {"mcq"}
CONSTRUCTED = {"constructed-response", "document-based", "extended-response", "short-answer"}


def schema() -> dict:
    with open(SCHEMA_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def required_fields() -> list:
    return schema()["required"]


def required_choice_fields() -> list:
    return schema()["properties"]["choices"]["items"]["required"]


def load_dir(path: str) -> list:
    """Every item under `path`, each tagged with the file it came from."""
    items = []
    if not os.path.isdir(path):
        return items
    for fp in sorted(glob.glob(os.path.join(path, "**", "*.json"), recursive=True)):
        with open(fp, encoding="utf-8") as fh:
            doc = json.load(fh)
        found = doc if isinstance(doc, list) else (doc.get("items") or doc.get("questions") or [])
        for it in found:
            it["_file"] = os.path.relpath(fp, BANK_ROOT)
            items.append(it)
    return items


def choices(item: dict) -> list:
    c = item.get("choices")
    return c if isinstance(c, list) else []


def is_single_select(item: dict) -> bool:
    return item.get("itemType") in SINGLE_SELECT


def servable(item: dict) -> bool:
    """Quarantined and unauthored items are not servable and not counted as coverage."""
    return item.get("status") in {"authored", "migrated", "provisional"}


def student_facing(item: dict) -> bool:
    return item.get("bankTier") == "student"


ALIGNED = {"evidenced", "rehomed", "human-verified"}


def aligned(item: dict) -> bool:
    """Counts toward STANDARDS COVERAGE and may appear on a standards-aligned form.

    An `unverified` item is still servable content — it is kept, intact, and
    usable. It simply may not be counted as evidence that a standard is covered,
    because nobody has established that it tests that standard.
    """
    return servable(item) and item.get("alignmentStatus") in ALIGNED
