from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .config import GfConfig
from .gf_client import GfClient
from .paths import PipelinePaths
from .sanitize import sanitize_rows
from .staging import rows_from_entries, utc_slug, write_csv, write_json
from .state_store import StateStore


def _max_date_updated(entries: List[Dict[str, str]]) -> str:
    values = [str(e.get("date_updated") or "") for e in entries if e.get("date_updated")]
    return max(values) if values else ""


def _run_manifest_path(paths: PipelinePaths, run_id: str) -> Path:
    return paths.logs / f"run_{run_id}.json"


def run_ingest(config: GfConfig, mode: str = "incremental", field_ids: str = "") -> Dict[str, object]:
    paths = PipelinePaths.default()
    paths.ensure()
    state = StateStore(paths.state)
    client = GfClient(config)
    forms = config.forms or []
    run_id = utc_slug()
    result: Dict[str, object] = {"run_id": run_id, "mode": mode, "forms": []}

    for form_id in forms:
        form_state = state.load(form_id)
        incoming_entries: List[Dict[str, str]] = []
        if mode == "full" or not form_state.last_seen_date_updated:
            page = 1
            while True:
                page_res = client.fetch_entries_page(form_id=form_id, page=page, page_size=config.page_size, field_ids=field_ids)
                raw_path = paths.incoming / f"form_{form_id}__{run_id}__page_{page}.json"
                write_json(raw_path, page_res.payload)
                if not page_res.entries:
                    break
                incoming_entries.extend(page_res.entries)
                if len(page_res.entries) < config.page_size:
                    break
                page += 1
            form_state.last_full_sync_utc = state.now_utc()
        else:
            incoming_entries = client.fetch_incremental_entries(
                form_id=form_id,
                since_date_updated=form_state.last_seen_date_updated,
                page_size=config.page_size,
                field_ids=field_ids,
            )
            raw_path = paths.incoming / f"form_{form_id}__{run_id}__incremental.json"
            write_json(raw_path, {"entries": incoming_entries, "since": form_state.last_seen_date_updated})

        batch_id = f"{run_id}_form_{form_id}"
        staged_rows = rows_from_entries(incoming_entries, form_id=form_id, batch_id=batch_id)
        sanitized_rows = sanitize_rows(staged_rows)

        staged_csv = paths.staging / f"form_{form_id}__{run_id}__staging.csv"
        sanitized_csv = paths.sanitized / f"form_{form_id}__{run_id}__sanitized.csv"
        write_csv(staged_csv, staged_rows)
        write_csv(sanitized_csv, sanitized_rows)

        latest = _max_date_updated(incoming_entries)
        if latest:
            form_state.last_seen_date_updated = latest
        if incoming_entries:
            form_state.last_seen_entry_id = str(max((int(str(e.get("id") or "0")) for e in incoming_entries), default=0))
        form_state.last_successful_run_utc = state.now_utc()
        state.save(form_state)

        result["forms"].append(
            {
                "form_id": form_id,
                "entries_fetched": len(incoming_entries),
                "staged_rows": len(staged_rows),
                "sanitized_rows": len(sanitized_rows),
                "staging_csv": str(staged_csv),
                "sanitized_csv": str(sanitized_csv),
                "last_seen_date_updated": form_state.last_seen_date_updated,
            }
        )

    manifest_path = _run_manifest_path(paths, run_id)
    manifest_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result

