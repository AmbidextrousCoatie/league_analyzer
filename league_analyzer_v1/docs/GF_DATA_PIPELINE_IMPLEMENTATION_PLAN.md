# Gravity Forms Data Pipeline Implementation Plan

## Goal

Build a robust ingestion pipeline in `league_analyzer_v1` that:

- Pulls Bowling Bayern source data from Gravity Forms REST API.
- Supports full sync, incremental sync (up to timestamp), and event-driven delta ingestion.
- Stages raw incoming data before transformations.
- Applies existing sanitization and conversion logic to legacy-compatible CSV.
- Recomputes points by league season.
- Stores all intermediate and final CSV artifacts in a dedicated directory tree.
- Supports scheduled polling, daily forced full sync, and manual trigger (API + frontend button).

---

## Scope and Non-Goals

### In Scope

- GF REST pull jobs for selected forms.
- Change detection using remote timestamps + persisted watermarks.
- Staging area and deterministic transformation pipeline.
- Operational triggers: scheduler + forced daily + manual.
- Auditability and observability.

### Out of Scope (for now)

- Replacing legacy CSV consumer in `league_analyzer_v1`.
- Final relational UUID-native production model (future relaunch).
- Complex bidirectional sync back to Gravity Forms.

---

## Use Cases to Implement

1. **Batch dump from GF REST**
   - For selected forms.
   - Modes:
     - Full dump.
     - Incremental dump up to/after a timestamp.

2. **Delta ingestion from GF events**
   - Receive event notifications (webhook/plugin hook) from GF environment.
   - Pull changed entries and apply same staging/transform pipeline.

3. **Operational control**
   - Parameterized interval polling job.
   - Forced full sync once daily.
   - Manual sync trigger:
     - Backend endpoint.
     - Frontend button calling that endpoint.

---

## Proposed Directory Layout (inside `league_analyzer_v1`)

Use a dedicated root to keep artifacts isolated and auditable:

`database/pipeline/bowling_bayern/`

- `incoming/`
  - Raw pulls from GF API (JSON and/or CSV export snapshots).
  - Suggested naming: `form_<id>__<UTC_ISO>__<mode>.json`
- `staging/`
  - Normalized tabular CSV per form and batch.
  - Minimal schema aligned to current input mapping.
- `sanitized/`
  - Deduplicated/canonicalized CSV (current "hacky" cleanup logic formalized).
- `legacy_out/`
  - Final legacy format CSV artifacts.
  - Includes "latest" and timestamped snapshots.
- `state/`
  - Watermarks/checkpoints per form.
  - Last successful run metadata.
- `logs/`
  - Structured job logs / run manifests.
- `failed/`
  - Quarantined payloads and transform errors.

---

## Pipeline Stages

### Stage 1: Extract (GF API client)

- Input config:
  - Site base URL.
  - Consumer key/secret.
  - Form IDs to track.
  - Optional `_field_ids` subset per form.
- Fetch modes:
  - `full`: pull all pages.
  - `incremental`: pull entries by search filter on `date_updated` (or fallback logic).
  - `event`: pull by specific entry IDs from incoming event payload.
- Persist raw response per page/batch under `incoming/`.

### Stage 2: Normalize to Staging

- Convert GF payload shapes into deterministic tabular rows.
- Keep source columns required by mapping.
- Include ingestion metadata columns:
  - `source_form_id`, `source_entry_id`, `ingested_at_utc`, `batch_id`, `source_date_updated`.
- Write to `staging/`.

### Stage 3: Sanitize

Apply existing rules (currently in converter logic) in a reusable module:

- Duplicate perspective handling (`_Re` / `_Li`) with deterministic tie-break.
- Canonical player naming by EDV (first non-empty seen per batch/run policy).
- Deterministic synthetic IDs when EDV missing.
- Stable sort order for reproducibility.

Write sanitized output to `sanitized/`.

### Stage 4: Legacy Conversion

- Reuse/port existing `convert_bowlingbayern_to_legacy.py` transformations.
- Produce legacy flat rows exactly matching expected schema.
- Write timestamped + latest files in `legacy_out/`.

### Stage 5: Points Awarding by League Season

- Run points calculation as an explicit step after legacy conversion.
- Inputs:
  - league season definitions (`database/relational_csv`).
  - scoring rules by season/league level.
- Output:
  - enriched legacy CSV and calculation audit (optional sidecar CSV for traceability).

---

## Change Detection Strategy

### Is there a "latest timestamp" remotely?

Yes, practically: use `date_updated` from entries and query latest update with:

- `sorting[key]=date_updated`
- `sorting[direction]=DESC`
- `paging[page_size]=1`

Use this as a cheap pre-check before pulling all changes.

### Watermark model

Persist per form:

- `last_seen_date_updated`
- `last_seen_entry_id` (tie-break when timestamps equal)
- `last_successful_run_utc`
- `last_full_sync_utc`

Incremental fetch filter:

- Search for entries with `date_updated >= watermark`.
- Deduplicate using `(entry_id, date_updated)` to avoid misses/duplicates across equal timestamps.

### Safety net

- Daily forced full sync regardless of watermark.
- Compare counts/hash summaries to detect drift.

---

## Triggering and Scheduling

## 1) Polling job (parameterized interval)

- Run loop every `N` minutes (configurable).
- Per cycle:
  - Pre-check latest remote timestamp.
  - If changed since watermark, run incremental sync.
  - Else no-op.

## 2) Daily forced sync

- Once per day (configurable time, e.g. 03:00 local/UTC), run full sync all configured forms.

## 3) Manual sync

- Backend API endpoint in legacy app, e.g.:
  - `POST /admin/sync/gf` with payload:
    - mode: `incremental|full`
    - optional `form_ids`
    - optional `since`
- Frontend button (admin/test page) calling endpoint.
- Endpoint returns run id and immediate status; long runs tracked asynchronously.

---

## Component Design (Suggested Modules)

Inside `league_analyzer_v1` (example package: `pipeline/`):

- `pipeline/gf_client.py`
  - Auth, pagination, search/sorting params.
- `pipeline/state_store.py`
  - Watermark persistence (`state/*.json` or sqlite).
- `pipeline/extract.py`
  - Full/incremental/event extract orchestration.
- `pipeline/normalize.py`
  - GF payload -> staging table.
- `pipeline/sanitize.py`
  - Dedup/canonicalization rules.
- `pipeline/legacy_convert.py`
  - Call/refactor existing converter logic.
- `pipeline/points.py`
  - Award points by season.
- `pipeline/jobs.py`
  - Scheduled job runner and manual run entrypoint.
- `pipeline/api.py`
  - Flask routes for manual trigger/status.

---

## Data Contract for Mapping

Minimum semantic attributes required for reconstruction are documented in:

- `database/input/INPUT_TO_LEGACY_CSV_MAPPING.md`

When using `_field_ids`, include at least:

- Entry metadata: `id`, `form_id`, `date_created`, `date_updated`, `status`
- Required form fields mapped to:
  - `Spiel-ID` / `Game-ID`
  - `Datum des Eintrags` / `Aktualisierungsdatum`
  - `Teamname`, `Gegner`
  - `Spieler 1..4`, `EDV 1..4`
  - `Pins 1..4`, `Pins Gesamt`, `Pins Gegner 1..4`, `Pins Gegner`

---

## Idempotency, Reliability, and Auditing

- Every run gets a `run_id`.
- Each stage writes deterministic file names with run_id + timestamp.
- Re-running same input should produce identical sanitized/legacy output.
- Keep raw payload snapshots for replay/debug.
- Track per-run stats:
  - forms processed
  - entries fetched
  - entries changed/new
  - rows output
  - duration per stage
  - failure reason if any

---

## Security and Operations

- Credentials only from environment/secret store (never committed).
- Least-privilege GF API key.
- Retry policy with exponential backoff on transient HTTP errors.
- Timeout + circuit break for GF outages.
- Optional lock file / distributed lock to prevent overlapping sync runs.

---

## Phased Activity Plan

## Phase 0 - Foundation (1-2 days)

- Create directory tree under `database/pipeline/bowling_bayern/`.
- Implement config model and credential handling.
- Define run manifest schema and state schema.

Deliverable: pipeline scaffolding + smoke test against one form.

## Phase 1 - Extract + Staging (2-3 days)

- Implement GF client pagination and full/incremental fetch.
- Implement latest timestamp pre-check and watermark updates.
- Write raw payload snapshots and normalized staging CSV.

Deliverable: reproducible staged CSV from form(s) with run logs.

## Phase 2 - Sanitize + Legacy Convert (2-3 days)

- Move current sanitization logic into modular stage.
- Integrate/refactor converter to run from staged data.
- Produce `legacy_out/latest.csv` + timestamped output.

Deliverable: legacy CSV parity with current manual workflow.

## Phase 3 - Points + Validation (2 days)

- Integrate points awarding step by season.
- Add validation checks (row counts, required fields, duplicates).
- Add failure quarantine path.

Deliverable: fully processed final CSV with validation report.

## Phase 4 - Scheduling + Manual Trigger (2 days)

- Add interval polling job.
- Add forced daily full sync.
- Add backend manual trigger endpoint + minimal frontend button.

Deliverable: autonomous sync + on-demand sync.

## Phase 5 - Event Delta (optional, depends on GF capabilities) (2-4 days)

- Discover event hook/webhook options in GF environment.
- Implement event receiver endpoint.
- Convert event payload to entry fetch queue.

Deliverable: near-real-time delta ingestion path.

---

## Testing Plan

- Unit tests:
  - pagination, query construction, watermark comparisons.
  - sanitization determinism.
  - legacy conversion invariants.
- Integration tests:
  - mocked GF responses for full/incremental/event runs.
  - end-to-end run producing expected legacy rows.
- Regression test:
  - compare generated legacy output against known baseline for sample period.

---

## Open Questions / Decisions Needed

1. Exact GF form IDs for production ingest.
2. Which timestamp is authoritative for incremental (`date_updated` vs custom field).
3. Event mechanism available in GF hosting (webhook/add-on/custom hook).
4. Desired scheduler runtime context:
   - same Flask process
   - separate worker process/service
   - system task scheduler
5. Retention policy for raw payload and intermediate CSV artifacts.

---

## Recommended First Sprint (Practical)

Implement **Phase 0 + Phase 1 + minimal Phase 2** first:

- one form (e.g., 92),
- full + incremental fetch,
- staging CSV + sanitized CSV + legacy CSV output,
- manual trigger endpoint only.

Then add scheduler and forced daily full sync once data quality is stable.
