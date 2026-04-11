from __future__ import annotations

from typing import Dict, List, Tuple


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
        game_id = row.get("Game-ID") or row.get("Spiel-ID") or ""
        team = row.get("Teamname") or ""
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

