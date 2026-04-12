"""
CLI: Bowling Bayern `liga_*_ergebnisse-*.csv` (file export) → legacy flat CSV.

Pure conversion lives in `database/conversion/bowlingbayern_legacy_core.py`.
Filesystem loading lives in `database/sources/bowlingbayern_liga_csv.py`.

Gravity Forms / pipeline code must not be edited when changing conversion rules here;
conversely, GF ingest changes must not modify the conversion core.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from database.conversion import bowlingbayern_legacy_core as _core
from database.sources import bowlingbayern_liga_csv as _liga

INPUT_DIR = ROOT / "database" / "input"
OUTPUT_CSV = ROOT / "database" / "data" / "bowling_ergebnisse_real_from_bowlingbayern.csv"

# --- Backwards-compatible re-exports (importlib / tests) ---
DEFAULT_SEASON = _core.DEFAULT_SEASON
DEFAULT_PLAYERS_PER_TEAM = _core.DEFAULT_PLAYERS_PER_TEAM
LEAGUE_CODE_MAP = _core.LEAGUE_CODE_MAP
OUTPUT_HEADERS = _core.OUTPUT_HEADERS
ParsedIds = _core.ParsedIds
parse_timestamp = _core.parse_timestamp
parse_game_id = _core.parse_game_id
to_int = _core.to_int
mapped_player_id = _core.mapped_player_id
points_for_duel = _core.points_for_duel
points_for_team_total = _core.points_for_team_total
row_effective_timestamp = _core.row_effective_timestamp
build_week_dates = _core.build_week_dates


def load_and_deduplicate() -> List[Dict[str, str]]:
    raw = _liga.load_liga_ergebnisse_rows(INPUT_DIR)
    return _core.dedupe_source_rows(raw)


def convert() -> List[Dict[str, str]]:
    return _core.convert_source_rows_to_legacy(load_and_deduplicate())


def write_output(rows: List[Dict[str, str]]) -> None:
    _core.write_legacy_csv(rows, OUTPUT_CSV)


def main() -> None:
    rows = convert()
    write_output(rows)
    print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
