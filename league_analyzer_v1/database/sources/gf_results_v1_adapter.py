"""
Gravity Forms **results** staging rows → canonical Bowling Bayern columns.

**v1 contract:** every GF “results” form wired into the pipeline is expected to share this
numeric field-id layout (validated against `liga_*_ergebnisse-*.csv` using form 92 entry 28386).
If a form diverges, align it upstream or fork this module (e.g. ``gf_results_v2_adapter``).

Timestamps: ``Datum des Eintrags`` / ``Aktualisierungsdatum`` come from GF
``date_created`` / ``date_updated`` on the entry row (staging), not from duplicate-value field matching.
"""

from __future__ import annotations

from typing import Dict, List

# GF field id → canonical column (string keys as in GF REST / staging CSV)
GF_RESULTS_V1_NUMERIC_TO_CANONICAL: Dict[str, str] = {
    "1": "Spiel-ID",
    "57": "Game-ID",
    "3": "Teamname",
    "24": "Gegner",
    "6": "EDV 1",
    "5": "Spieler 1",
    "22": "Pins 1",
    "23": "Pins Gegner 1",
    "26": "EDV 2",
    "28": "Spieler 2",
    "29": "Pins 2",
    "30": "Pins Gegner 2",
    "27": "EDV 3",
    "31": "Spieler 3",
    "32": "Pins 3",
    "33": "Pins Gegner 3",
    "35": "EDV 4",
    "36": "Spieler 4",
    "37": "Pins 4",
    "38": "Pins Gegner 4",
    "39": "Pins Gegner",
    "40": "Pins Gesamt",
}

CANONICAL_HEADERS: List[str] = [
    "Spiel-ID",
    "Game-ID",
    "Teamname",
    "Gegner",
    "EDV 1",
    "Spieler 1",
    "Pins 1",
    "Pins Gegner 1",
    "EDV 2",
    "Spieler 2",
    "Pins 2",
    "Pins Gegner 2",
    "EDV 3",
    "Spieler 3",
    "Pins 3",
    "Pins Gegner 3",
    "EDV 4",
    "Spieler 4",
    "Pins 4",
    "Pins Gegner 4",
    "Pins Gesamt",
    "Pins Gegner",
    "Datum des Eintrags",
    "Aktualisierungsdatum",
    "source_entry_id",
]


def staging_row_to_canonical_gf_results_v1(row: Dict[str, str]) -> Dict[str, str]:
    out: Dict[str, str] = {h: "" for h in CANONICAL_HEADERS}
    for fid, col in GF_RESULTS_V1_NUMERIC_TO_CANONICAL.items():
        val = row.get(fid)
        if val is not None and col in out:
            out[col] = (str(val) or "").strip()
    out["Datum des Eintrags"] = (row.get("date_created") or "").strip()
    out["Aktualisierungsdatum"] = (row.get("date_updated") or "").strip()
    out["source_entry_id"] = (row.get("source_entry_id") or row.get("id") or "").strip()
    return out
