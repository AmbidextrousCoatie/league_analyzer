from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List


def utc_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def rows_from_entries(entries: Iterable[Dict[str, Any]], form_id: int, batch_id: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    for e in entries:
        base: Dict[str, str] = {
            "source_form_id": str(form_id),
            "source_entry_id": str(e.get("id") or ""),
            "source_date_updated": str(e.get("date_updated") or ""),
            "ingested_at_utc": now,
            "batch_id": batch_id,
        }
        for k, v in e.items():
            if isinstance(v, (dict, list)):
                base[str(k)] = json.dumps(v, ensure_ascii=False, separators=(",", ":"))
            elif v is None:
                base[str(k)] = ""
            else:
                base[str(k)] = str(v)
        rows.append(base)
    return rows


def write_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    headers = sorted({k for r in rows for k in r.keys()})
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

