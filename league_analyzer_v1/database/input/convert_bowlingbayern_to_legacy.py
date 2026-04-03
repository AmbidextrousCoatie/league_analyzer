from __future__ import annotations

import csv
import re
import zlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT / "database" / "input"
OUTPUT_CSV = ROOT / "database" / "data" / "bowling_ergebnisse_real_from_bowlingbayern.csv"

DEFAULT_SEASON = "25/26"
DEFAULT_PLAYERS_PER_TEAM = "4"
LEAGUE_CODE_MAP = {
    "BAYL-M": "BayL",
    "LL-S-M": "LL S",
    "LL-S-F": "LL S (D)",
    "KRL-S1": "KL S1",
    "KRL-N2": "KL N2",
    "BZOL-N2": "BZOL N2",
    "BZOL-N1": "BZOL N1",
}

OUTPUT_HEADERS = [
    "Season",
    "Week",
    "Date",
    "League",
    "Players per Team",
    "Location",
    "Round Number",
    "Match Number",
    "Team",
    "Position",
    "Player",
    "Player ID",
    "Opponent",
    "Score",
    "Points",
    "Input Data",
    "Computed Data",
]


@dataclass
class ParsedIds:
    league: str
    week: str
    round_number: str
    match_number: str


def parse_timestamp(raw: str) -> Optional[datetime]:
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def parse_game_id(game_id: str) -> ParsedIds:
    token = (game_id or "").strip()
    # Supported examples:
    # - BAYL-M-554
    # - LL-S-M_451
    # - KRL-S1_362
    m = re.match(r"^([A-Z]+(?:-[A-Z0-9]+)*)[_-](\d{3})(?:_.+)?$", token)
    if m:
        league_code, triple = m.group(1), m.group(2)
        raw_match = int(triple[2])
        zero_based_match = str(max(raw_match - 1, 0))
        return ParsedIds(
            league=LEAGUE_CODE_MAP.get(league_code, league_code),
            week=triple[0],
            round_number=triple[1],
            match_number=zero_based_match,
        )

    # Fallback for malformed IDs.
    return ParsedIds(
        league=LEAGUE_CODE_MAP.get(league_code, league_code),
        week="",
        round_number="",
        match_number="",
    )


def to_int(raw: str) -> Optional[int]:
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def mapped_player_id(raw_player_id: str, player_name: str) -> str:
    """
    Return a stable integer-like player id string for legacy output.
    - Numeric EDV values are normalized to integer strings.
    - Missing/invalid EDV values get deterministic synthetic IDs based on name.
    """
    parsed = to_int(raw_player_id)
    if parsed is not None:
        return str(parsed)

    # Deterministic fallback (7 digits) to avoid NaN/float conversions downstream.
    base = (player_name or "").strip().lower()
    synthetic = 9_000_000 + (zlib.crc32(base.encode("utf-8")) % 1_000_000)
    return str(synthetic)


def points_for_duel(team_score: Optional[int], opp_score: Optional[int]) -> str:
    if team_score is None or opp_score is None:
        return "0.0"
    if team_score > opp_score:
        return "1.0"
    if team_score < opp_score:
        return "0.0"
    return "0.5"


def points_for_team_total(team_score: Optional[int], opp_score: Optional[int]) -> str:
    if team_score is None or opp_score is None:
        return "0.0"
    if team_score > opp_score:
        return "3.0"
    if team_score < opp_score:
        return "0.0"
    return "1.5"


def row_effective_timestamp(row: Dict[str, str]) -> Optional[datetime]:
    ts_entry = parse_timestamp(row.get("Datum des Eintrags", ""))
    ts_update = parse_timestamp(row.get("Aktualisierungsdatum", ""))
    candidates = [ts for ts in (ts_entry, ts_update) if ts is not None]
    if not candidates:
        return None
    return min(candidates)


def load_and_deduplicate() -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for path in sorted(INPUT_DIR.glob("liga_*_ergebnisse-*.csv")):
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            rows.extend(list(csv.DictReader(f)))

    dedup: Dict[Tuple[str, str], Dict[str, str]] = {}
    for row in rows:
        key = ((row.get("Game-ID") or "").strip(), (row.get("Teamname") or "").strip())
        current_ts = row_effective_timestamp(row)

        existing = dedup.get(key)
        if existing is None:
            dedup[key] = row
            continue

        existing_ts = row_effective_timestamp(existing)
        # Keep earliest stable timestamp when duplicates exist.
        if existing_ts is None and current_ts is not None:
            dedup[key] = row
        elif existing_ts is not None and current_ts is not None and current_ts < existing_ts:
            dedup[key] = row

    return list(dedup.values())


def build_week_dates(rows: List[Dict[str, str]]) -> Dict[Tuple[str, str], str]:
    per_week_min: Dict[Tuple[str, str], datetime] = {}
    for row in rows:
        ids = parse_game_id(row.get("Game-ID", ""))
        if not ids.league or not ids.week:
            continue
        ts = row_effective_timestamp(row)
        if ts is None:
            continue
        key = (ids.league, ids.week)
        existing = per_week_min.get(key)
        if existing is None or ts < existing:
            per_week_min[key] = ts
    return {k: ts.date().isoformat() for k, ts in per_week_min.items()}


def convert() -> List[Dict[str, str]]:
    source_rows = load_and_deduplicate()
    week_dates = build_week_dates(source_rows)

    output_rows: List[Dict[str, str]] = []
    for row in source_rows:
        ids = parse_game_id(row.get("Game-ID", ""))
        team = (row.get("Teamname") or "").strip()
        opponent = (row.get("Gegner") or "").strip()

        common = {
            "Season": DEFAULT_SEASON,
            "Week": ids.week,
            "Date": week_dates.get((ids.league, ids.week), ""),
            "League": ids.league,
            "Players per Team": DEFAULT_PLAYERS_PER_TEAM,
            "Location": "",
            "Round Number": ids.round_number,
            "Match Number": ids.match_number,
            "Team": team,
            "Opponent": opponent,
        }

        # 4 player rows, slot 1 => position 0.
        for slot in (1, 2, 3, 4):
            player = (row.get(f"Spieler {slot}") or "").strip()
            player_id = mapped_player_id((row.get(f"EDV {slot}") or "").strip(), player)
            score_raw = (row.get(f"Pins {slot}") or "").strip()
            opp_raw = (row.get(f"Pins Gegner {slot}") or "").strip()
            score = to_int(score_raw)
            opp = to_int(opp_raw)

            output_rows.append(
                {
                    **common,
                    "Position": str(slot - 1),
                    "Player": player,
                    "Player ID": player_id,
                    "Score": score_raw,
                    "Points": points_for_duel(score, opp),
                    "Input Data": "True",
                    "Computed Data": "False",
                }
            )

        # Team total row.
        total_score_raw = (row.get("Pins Gesamt") or "").strip()
        total_opp_raw = (row.get("Pins Gegner") or "").strip()
        total_score = to_int(total_score_raw)
        total_opp = to_int(total_opp_raw)
        output_rows.append(
            {
                **common,
                "Position": "0",
                "Player": "Team Total",
                "Player ID": "0",
                "Score": total_score_raw,
                "Points": points_for_team_total(total_score, total_opp),
                "Input Data": "False",
                "Computed Data": "True",
            }
        )

    output_rows.sort(
        key=lambda r: (
            r["Season"],
            int(r["Week"]) if r["Week"].isdigit() else 999,
            int(r["Round Number"]) if r["Round Number"].isdigit() else 999,
            int(r["Match Number"]) if r["Match Number"].isdigit() else 999,
            r["Team"],
            int(r["Position"]) if r["Position"].isdigit() else 999,
            1 if r["Player"] == "Team Total" else 0,
        )
    )

    return output_rows


def write_output(rows: List[Dict[str, str]]) -> None:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_HEADERS, delimiter=";")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    rows = convert()
    write_output(rows)
    print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
