# GF Pipeline Runbook

Operator notes for the Gravity Forms → Bowling Bayern pipeline. Product intent and full roadmap live in `GF_DATA_PIPELINE_IMPLEMENTATION_PLAN.md`.

**Status:** Sprint 1 and Sprint 2 are **done** (GF results forms → shared **v1** canonical map → legacy CSV + app source). **Sprint 3 (final)** covers operations (manual trigger, scheduling) and downstream processing (points, validation); optional event ingestion is out of band.

---

## Sprint 1 (extract + stage)

- Pipeline root: `database/pipeline/bowling_bayern/`
- Full and incremental GF REST extraction
- Raw payloads: `incoming/`
- Wide staging CSV: `staging/`
- Trim/dedupe wide rows: `sanitized/` (`*_staging.csv` / `*_sanitized.csv` naming)
- Watermarks: `state/form_<id>.json`
- Run manifests: `logs/run_<run_id>.json`

**Not in Sprint 1:** webhooks, scheduler, points after legacy.

---

## Sprint 2 (GF → canonical → legacy) — complete

### Architecture (multiple forms)

There is **one pipeline job** (`run_ingest`): it loops configured `form_id`s. For **each** form you still get **separate** wide artifacts (`incoming/`, `staging/`, `sanitized/` per form and run).

Rows are **not** merged at the “sanitized wide CSV” layer (different forms may use different GF field ids in principle). **All** configured result forms are mapped with the **same** v1 layout in `database/sources/gf_results_v1_adapter.py` (pipeline glue in `gf_form_registry.py`). Staging → canonical rows are appended into **one** deduped file:

`canonical/merged_gf_canonical.csv`

Legacy conversion runs on that combined set → `legacy_out/latest.csv`. If a form’s fields diverge from v1, fix the GF forms upstream or add a new adapter version module and point the registry at it.

If an older `canonical/merged_form_92.csv` exists, it is read **once** as a migration source when `merged_gf_canonical.csv` is still empty; new writes go only to `merged_gf_canonical.csv`.

### Behaviour

For each **form_id** in `--forms` (positive integer), unless `--skip-legacy`:

1. **Map** staging → canonical via **`gf_results_v1_adapter`** (shared numeric field map).
2. **Write** per-run slice: `sanitized/form_<id>__<run_id>__canonical.csv`.
3. **Merge** into `canonical/merged_gf_canonical.csv`, **dedupe** with `database/conversion/bowlingbayern_legacy_core.dedupe_source_rows`.
4. **Write** `legacy_out/bowling_legacy__<run_id>.csv` (when new entries were fetched) and always refresh `legacy_out/latest.csv` when merge output is non-empty.

**Incremental run with zero new entries:** merge file is **not** updated from that form’s batch. If **`merged_gf_canonical.csv`** (or legacy `merged_form_92.csv` for migration) **already has rows**, legacy is still **regenerated** so `latest.csv` stays aligned (`refreshed_from_merged_only`). If there is **no** merge data yet, legacy is skipped (`no_new_entries_no_merged_canonical`).

### CLI

From repository root:

```bash
python "league_analyzer_v1/scripts/run_gf_pipeline.py" --mode incremental --site "https://bowlingbayern.de" --ck "ck_..." --cs "cs_..."
```

If you omit `--forms`, the CLI uses the default Bowling Bayern form id set in `pipeline/bowling_bayern_gf_forms.py` (currently **21, 92, 95, 100, 102, 105, 113, 115, 117**). Override with `--forms 92,95` or env **`GF_FORMS=92,95`**.

Options:

| Flag | Purpose |
|------|--------|
| `--mode full` | Full paginated pull |
| `--forms` | Comma-separated ids; omit for default set (same **v1** results field map for all) |
| `--field-ids "..."` | GF `_field_ids` subset |
| `--page-size 100` | Page size (max 200) |
| `--insecure` | Disable TLS verify (temporary only) |
| `--skip-legacy` | Ingest/stage/sanitize only; no canonical merge or legacy CSV |

### Backfill without calling GF

If you have `staging/form_92__*_staging.csv` but no merge/legacy yet (or an empty incremental staging file should not win):

```bash
python "league_analyzer_v1/scripts/rebuild_form92_legacy_from_staging.py"
```

Loads **all non-empty** `staging/form_*__*_staging.csv` files, maps each through **v1** results adapter, rebuilds `canonical/merged_gf_canonical.csv`, and writes `legacy_out/latest.csv` plus a timestamped `bowling_legacy__<run_id>__from_staging.csv`.

### Artifact layout

| Path | Role |
|------|------|
| `incoming/` | Raw JSON pages / incremental payloads |
| `staging/` | Wide GF staging CSV per run |
| `sanitized/` | Wide sanitized + per-run **canonical** slice (per form) |
| `canonical/merged_gf_canonical.csv` | Deduplicated canonical rows (all result forms) |
| `legacy_out/latest.csv` | Current legacy flat file for consumers |
| `legacy_out/bowling_legacy__<run_id>.csv` | Per-ingest snapshot (when new entries fetched) |
| `state/` | Watermarks |
| `logs/` | Run JSON |

### App integration

- Flask data source **Real Data (Pipeline GF)** → `legacy_out/latest.csv` (see `app/config/database_config.py`).
- If the file did not exist yet, startup creates a **header-only stub** so the source appears in the selector; run the pipeline or the staging rebuild script to fill data.

---

## Sprint 3 (final) — scope

Goal: close the loop in `GF_DATA_PIPELINE_IMPLEMENTATION_PLAN.md` for **operations and downstream CSV quality**, without blocking on optional webhooks.

**Planned deliverables (in rough order):**

1. **Manual sync** — Backend route (e.g. `POST` admin/sync) that runs the same logic as `run_gf_pipeline.py` (mode, forms, credentials from env/secret). Returns `run_id` and summary JSON. **Frontend:** button (e.g. admin or API test page) calling that route.
2. **Scheduling** — Parameterized interval incremental job + **daily forced full** sync (implementation context: same host vs worker vs OS scheduler — decide per deployment).
3. **Points + validation (Phase 3 in plan)** — Explicit step after legacy: season/league scoring inputs, optional validation report, optional `failed/` quarantine for bad rows.
4. **Hardening (as needed)** — Remote “has anything changed?” pre-check, overlap lock, retries/timeouts (plan §Security and Operations).

**Optional later (not Sprint 3):** GF event/webhook delta path (plan Phase 5); if the shared v1 field map stops fitting new forms, add `gf_results_v2_adapter.py` (or align forms with the data owner).

---

## Incremental behaviour (reminder)

- Watermark: `last_seen_date_updated` per form in `state/`.
- Incremental fetch uses GF search/sort on `date_updated`.
- Watermark advances after a successful run when new `date_updated` values were seen.

---

## References

- `GF_DATA_PIPELINE_IMPLEMENTATION_PLAN.md` — full design and phased plan
- `database/input/INPUT_TO_LEGACY_CSV_MAPPING.md` — canonical column contract
- `database/sources/gf_results_v1_adapter.py` — shared GF results → canonical mapping
- `database/conversion/bowlingbayern_legacy_core.py` — pure legacy transform
- Dev helpers: `scripts/infer_gf92_field_map.py`, `scripts/dump_staging_row.py` (field-id discovery; not required at runtime)
