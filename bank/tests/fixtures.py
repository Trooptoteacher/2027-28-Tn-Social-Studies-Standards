"""Fixture factory.

The fixture reproduces the REAL record's structure — all 17 required fields,
bilingual twins, per-distractor explanations and misconceptions, IRT block.
A simplified fixture proves only that the gate can read a simplified fixture.
"""
from __future__ import annotations

import copy

# One fully-formed, blueprint-conformant item. Everything else is a mutation
# of this, so a defect fixture differs from the clean one by exactly its defect.
BASE = {
    "id": "US04-DOK2-001",
    "stem": "How did the Homestead Act change settlement patterns in the West?",
    "stemEs": "¿Cómo cambió la Ley de Asentamientos Rurales los patrones de asentamiento en el Oeste?",
    "itemType": "mcq",
    "correctAnswer": "B",
    "choices": [
        {"id": "A",
         "text": "It granted railroad companies title to all unsettled territory.",
         "textEs": "Otorgó a las compañías ferroviarias el título de todo el territorio no colonizado.",
         "explanation": "Land grants to railroads were a separate policy. The Homestead Act "
                        "transferred land to individual settlers, not to corporations.",
         "misconception": "conflates the Homestead Act with railroad land grants"},
        {"id": "B",
         "text": "It offered 160 acres to settlers who farmed the land for five years.",
         "textEs": "Ofreció 160 acres a los colonos que cultivaran la tierra durante cinco años.",
         "explanation": None, "misconception": None},
        {"id": "C",
         "text": "It returned reservation land to American Indian nations.",
         "textEs": "Devolvió las tierras de reserva a las naciones indígenas americanas.",
         "explanation": "Federal policy in this period moved in the opposite direction. The Dawes "
                        "Act divided reservation land rather than restoring it.",
         "misconception": "reverses the direction of federal American Indian land policy"},
        {"id": "D",
         "text": "It required settlers to purchase land at market price before farming.",
         "textEs": "Exigía a los colonos comprar tierras a precio de mercado antes de cultivar.",
         "explanation": "The filing fee was nominal. Reading the Act as a sale misses that its "
                        "purpose was to transfer land cheaply to encourage settlement.",
         "misconception": "treats the Homestead Act as a land sale rather than a grant"},
    ],
    "dokLevel": 2,
    "dokRationale": "The student must connect a policy's terms to a settlement outcome, which is a "
                    "relationship rather than a retrieved fact. Recalling the acreage alone would "
                    "be DOK-1; explaining the change in pattern is DOK-2.",
    "standardCodes": ["US.04"],
    "standardsYear": "2027-28",
    "reportingCategory": None,
    "reportingCategorySource": "UNMAPPED",
    "explanation": "The Act made land nearly free to anyone who improved it for five years, so "
                   "settlement spread in dispersed family farms rather than concentrating near "
                   "existing towns.",
    "explanationEs": "La ley hizo que la tierra fuera casi gratuita para quien la mejorara durante "
                     "cinco años, por lo que el asentamiento se extendió en granjas familiares "
                     "dispersas en lugar de concentrarse cerca de los pueblos existentes.",
    "translationStatus": "complete",
    "irtParameters": {"a": 1.12, "b": -0.34, "c": 0.21},
    "calibrationStatus": "pre-field-test",
    "bankTier": "teacher",
    "status": "authored",
    # Alignment confidence is its own axis — see schema/item.schema.json.
    "alignmentStatus": "evidenced",
    "image": None,
}


# Each choice id carries its own distractor rationale. When the key moves, the
# NEW key is nulled and the OLD key gets its rationale back — otherwise moving
# the key silently strands a distractor with no explanation, which is the
# de-bias defect in miniature. The fixture factory has to be as synced as the
# bank it stands in for.
DISTRACTOR_POOL = {
    "A": ("Land grants to railroads were a separate policy. The Homestead Act "
          "transferred land to individual settlers, not to corporations.",
          "conflates the Homestead Act with railroad land grants"),
    "B": ("160 acres after five years' cultivation is the Act's actual term, so a "
          "student choosing this for the wrong reason has the terms without the "
          "settlement consequence.",
          "recalls the acreage but not the resulting settlement pattern"),
    "C": ("Federal policy in this period moved in the opposite direction. The Dawes "
          "Act divided reservation land rather than restoring it.",
          "reverses the direction of federal American Indian land policy"),
    "D": ("The filing fee was nominal. Reading the Act as a sale misses that its "
          "purpose was to transfer land cheaply to encourage settlement.",
          "treats the Homestead Act as a land sale rather than a grant"),
}


def _sync_key(it, key):
    """Point every choice's rationale at the current key. The key carries none."""
    for c in it["choices"]:
        if c["id"] == key:
            c["explanation"], c["misconception"] = None, None
        else:
            c["explanation"], c["misconception"] = DISTRACTOR_POOL[c["id"]]
    it["correctAnswer"] = key
    return it


def item(**over):
    it = copy.deepcopy(BASE)
    it.update(over)
    return it


def clean_bank(codes, per_standard=6):
    """A blueprint-conformant bank: 6 items per standard, DOK 2/2/1/1,
    4 mcq + 1 constructed-response + 1 document-based, keys spread evenly."""
    plan = [(1, "mcq", "A"), (1, "mcq", "B"), (2, "mcq", "C"), (2, "mcq", "D"),
            (3, "constructed-response", None), (4, "document-based", None)]
    out = []
    for code in codes:
        for n, (dok, typ, key) in enumerate(plan, 1):
            it = item(id=f"{code.replace('.', '')}-{typ[:3].upper()}{n}",
                      standardCodes=[code], dokLevel=dok, itemType=typ)
            if typ == "mcq":
                _sync_key(it, key)
            else:
                it["choices"] = []
                it["correctAnswer"] = None
            out.append(it)
    return out
