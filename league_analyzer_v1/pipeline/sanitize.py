from __future__ import annotations

from typing import Dict, List, Tuple


def _game_id_and_team_for_dedup(row: Dict[str, str]) -> Tuple[str, str]:
    """
    Canonical CSV uses ``Game-ID`` / ``Teamname``; GF staging rows use numeric field ids
    (``57`` = Game-ID, ``1`` = Spiel-ID label, ``3`` = team).
    """
    game_id = (row.get("Game-ID") or row.get("Spiel-ID") or "").strip()
    team = (row.get("Teamname") or "").strip()
    if not game_id:
        game_id = (row.get("57") or row.get("1") or "").strip()
    if not team:
        team = (row.get("3") or "").strip()
    return game_id, team


def _trim(row: Dict[str, str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for k, v in row.items():
        out[k] = v.strip() if isinstance(v, str) else v
    return out


def sanitize_rows(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Sprint-1 minimal sanitization:
    - trim whitespace
    - deterministic dedup by (Game-ID/Spiel-ID, Teamname, source_entry_id), keep earliest source_date_updated
    """
    dedup: Dict[Tuple[str, str, str], Dict[str, str]] = {}
    for raw in rows:
        row = _trim(raw)
        game_id, team = _game_id_and_team_for_dedup(row)
        entry_id = row.get("source_entry_id") or ""
        key = (game_id, team, entry_id)
        existing = dedup.get(key)
        if existing is None:
            dedup[key] = row
            continue
        ex_ts = existing.get("source_date_updated", "")
        cur_ts = row.get("source_date_updated", "")
        if cur_ts and (not ex_ts or cur_ts < ex_ts):
            dedup[key] = row
    return sorted(dedup.values(), key=lambda r: (r.get("source_date_updated", ""), r.get("source_entry_id", "")))

