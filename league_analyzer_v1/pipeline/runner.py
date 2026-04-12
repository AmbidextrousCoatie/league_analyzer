from __future__ import annotations

import csv
import json
import platform
import sys
from pathlib import Path
from time import perf_counter
from typing import Dict, List
from urllib.parse import urlsplit

from database.conversion.bowlingbayern_legacy_core import (
    convert_source_rows_to_legacy,
    dedupe_source_rows,
    write_legacy_csv,
)
from database.sources.gf_results_v1_adapter import CANONICAL_HEADERS
from database.sources.gf_form_registry import has_legacy_adapter, staging_row_to_canonical_for_merge

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


MERGED_GF_CANONICAL_CSV = "merged_gf_canonical.csv"
LEGACY_MERGED_FORM_92 = "merged_form_92.csv"


def _merged_gf_canonical_path(paths: PipelinePaths) -> Path:
    """Single deduped canonical CSV for all GF forms that have a legacy adapter."""
    return paths.canonical / MERGED_GF_CANONICAL_CSV


def _read_merged_canonical_prior(paths: PipelinePaths) -> List[Dict[str, str]]:
    rows = _read_canonical_rows(_merged_gf_canonical_path(paths))
    if rows:
        return rows
    legacy = paths.canonical / LEGACY_MERGED_FORM_92
    if legacy.is_file():
        return _read_canonical_rows(legacy)
    return []


def _read_canonical_rows(path: Path) -> List[Dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        rows: List[Dict[str, str]] = []
        for raw in reader:
            row = {h: (raw.get(h) or "").strip() for h in CANONICAL_HEADERS}
            rows.append(row)
        return rows


def _write_canonical_rows(path: Path, rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CANONICAL_HEADERS, delimiter=";", extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow({h: r.get(h, "") for h in CANONICAL_HEADERS})


def _run_gf_canonical_legacy(
    paths: PipelinePaths,
    run_id: str,
    form_id: int,
    staged_rows: List[Dict[str, str]],
    entries_fetched: int,
) -> Dict[str, object]:
    merged_path = _merged_gf_canonical_path(paths)
    legacy_latest = paths.legacy_out / "latest.csv"

    if entries_fetched > 0:
        canonical_batch = [staging_row_to_canonical_for_merge(r, form_id) for r in staged_rows]
        canonical_csv = paths.sanitized / f"form_{form_id}__{run_id}__canonical.csv"
        _write_canonical_rows(canonical_csv, canonical_batch)

        prior = _read_merged_canonical_prior(paths)
        combined = prior + canonical_batch
        deduped = dedupe_source_rows(combined)
        _write_canonical_rows(merged_path, deduped)

        legacy_rows = convert_source_rows_to_legacy(deduped)
        legacy_run = paths.legacy_out / f"bowling_legacy__{run_id}.csv"
        write_legacy_csv(legacy_rows, legacy_run)
        write_legacy_csv(legacy_rows, legacy_latest)

        return {
            "legacy_skipped": False,
            "canonical_csv": str(canonical_csv),
            "merged_canonical_csv": str(merged_path),
            "merged_row_count": len(deduped),
            "legacy_csv": str(legacy_run),
            "legacy_latest_csv": str(legacy_latest),
            "legacy_row_count": len(legacy_rows),
        }

    prior = _read_merged_canonical_prior(paths)
    if not prior:
        return {"legacy_skipped": True, "reason": "no_new_entries_no_merged_canonical"}
    deduped = dedupe_source_rows(prior)
    _write_canonical_rows(merged_path, deduped)
    legacy_rows = convert_source_rows_to_legacy(deduped)
    write_legacy_csv(legacy_rows, legacy_latest)
    return {
        "legacy_skipped": False,
        "refreshed_from_merged_only": True,
        "merged_canonical_csv": str(merged_path),
        "merged_row_count": len(deduped),
        "legacy_latest_csv": str(legacy_latest),
        "legacy_row_count": len(legacy_rows),
    }


def _ratio(num: float, den: float) -> float | None:
    if den <= 0:
        return None
    return round(float(num) / float(den), 4)


def _benchmark_metadata(config: GfConfig, mode: str, form_id: int) -> Dict[str, object]:
    site_norm = GfClient._normalize_site_base(config.site_base_url)
    host = urlsplit(site_norm).netloc if site_norm else ""
    return {
        "form_id": form_id,
        "mode": mode,
        "site_host": host,
        "page_size": config.page_size,
        "verify_ssl": config.verify_ssl,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "benchmark_note": (
            "seconds_new_data_probe = first GF /entries HTTP page (sorted by date_updated DESC); "
            "incremental uses this page to see newest rows vs last_seen. "
            "seconds_all_entry_fetch = sum of all /entries pages this run. "
            "seconds_table_sync = local staging/sanitize/merge/legacy/state after fetch."
        ),
    }


def run_ingest(
    config: GfConfig,
    mode: str = "incremental",
    field_ids: str = "",
    skip_legacy: bool = False,
) -> Dict[str, object]:
    paths = PipelinePaths.default()
    paths.ensure()
    state = StateStore(paths.state)
    client = GfClient(config)
    forms = config.forms or []
    run_id = utc_slug()
    result: Dict[str, object] = {"run_id": run_id, "mode": mode, "forms": []}
    totals_probe = 0.0
    totals_fetch = 0.0
    totals_sync = 0.0

    for form_id in forms:
        form_state = state.load(form_id)
        incoming_entries: List[Dict[str, str]] = []
        page_timings_seconds: List[float] = []
        if mode == "full" or not form_state.last_seen_date_updated:
            page = 1
            while True:
                t_http = perf_counter()
                page_res = client.fetch_entries_page(
                    form_id=form_id, page=page, page_size=config.page_size, field_ids=field_ids
                )
                page_timings_seconds.append(perf_counter() - t_http)
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
            incr = client.fetch_incremental_entries(
                form_id=form_id,
                since_date_updated=form_state.last_seen_date_updated,
                page_size=config.page_size,
                field_ids=field_ids,
            )
            incoming_entries = incr.entries
            page_timings_seconds = incr.page_timings_seconds
            raw_path = paths.incoming / f"form_{form_id}__{run_id}__incremental.json"
            write_json(raw_path, {"entries": incoming_entries, "since": form_state.last_seen_date_updated})

        seconds_new_data_probe = float(page_timings_seconds[0]) if page_timings_seconds else 0.0
        seconds_all_entry_fetch = float(sum(page_timings_seconds))

        t_sync = perf_counter()
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

        form_result: Dict[str, object] = {
            "form_id": form_id,
            "entries_fetched": len(incoming_entries),
            "staged_rows": len(staged_rows),
            "sanitized_rows": len(sanitized_rows),
            "staging_csv": str(staged_csv),
            "sanitized_csv": str(sanitized_csv),
            "last_seen_date_updated": form_state.last_seen_date_updated,
        }
        if not skip_legacy and has_legacy_adapter(form_id):
            form_result["legacy"] = _run_gf_canonical_legacy(
                paths, run_id, form_id, staged_rows, len(incoming_entries)
            )
        elif not skip_legacy:
            form_result["legacy"] = {
                "legacy_skipped": True,
                "reason": "invalid_form_id_for_legacy",
            }
        else:
            form_result["legacy"] = {"legacy_skipped": True, "reason": "skip_legacy_flag"}

        seconds_table_sync = perf_counter() - t_sync
        legacy_info = form_result.get("legacy") or {}
        bench_meta = _benchmark_metadata(config, mode, form_id)
        bench_meta["pages_fetched"] = len(page_timings_seconds)
        bench_meta["legacy_skipped"] = bool(legacy_info.get("legacy_skipped"))
        if legacy_info.get("merged_row_count") is not None:
            bench_meta["merged_row_count"] = legacy_info.get("merged_row_count")
        if legacy_info.get("legacy_row_count") is not None:
            bench_meta["legacy_row_count"] = legacy_info.get("legacy_row_count")

        form_result["benchmark"] = {
            "seconds_new_data_probe": round(seconds_new_data_probe, 6),
            "seconds_all_entry_fetch": round(seconds_all_entry_fetch, 6),
            "seconds_table_sync": round(seconds_table_sync, 6),
            "ratio_all_entry_fetch_to_sync": _ratio(seconds_all_entry_fetch, seconds_table_sync),
            "ratio_probe_to_sync": _ratio(seconds_new_data_probe, seconds_table_sync),
            "metadata": bench_meta,
        }
        totals_probe += seconds_new_data_probe
        totals_fetch += seconds_all_entry_fetch
        totals_sync += seconds_table_sync
        result["forms"].append(form_result)

    result["benchmark_totals"] = {
        "seconds_new_data_probe": round(totals_probe, 6),
        "seconds_all_entry_fetch": round(totals_fetch, 6),
        "seconds_table_sync": round(totals_sync, 6),
        "ratio_all_entry_fetch_to_sync": _ratio(totals_fetch, totals_sync) if forms else None,
        "ratio_probe_to_sync": _ratio(totals_probe, totals_sync) if forms else None,
        "forms_processed": len(forms),
    }

    manifest_path = _run_manifest_path(paths, run_id)
    manifest_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result

