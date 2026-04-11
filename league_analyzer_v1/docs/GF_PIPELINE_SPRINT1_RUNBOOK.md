# GF Pipeline Sprint 1 Runbook

This is the first runnable slice of the Gravity Forms pipeline described in `GF_DATA_PIPELINE_IMPLEMENTATION_PLAN.md`.

## Included in Sprint 1

- Pipeline directories under `database/pipeline/bowling_bayern/`
- Full and incremental extraction from GF REST API
- Raw payload archival (`incoming/`)
- Staging CSV output (`staging/`)
- Minimal sanitization step (`sanitized/`)
- Per-form watermark state (`state/`)
- Run manifest logs (`logs/`)

Not included yet:
- Event/webhook ingestion
- Scheduler/cron orchestration
- Automated legacy conversion + points stage wiring

## CLI Command

Run from repository root:

```bash
python "league_analyzer_v1/scripts/run_gf_pipeline.py" --mode incremental --forms 92 --site "https://bowlingbayern.de" --ck "ck_..." --cs "cs_..."
```

Useful options:

- `--mode full` for forced full pull.
- `--forms 92,113` for multiple forms.
- `--field-ids "id,form_id,date_updated,..."` to limit payload size.
- `--page-size 100` (max 200).
- `--insecure` only if TLS verification must be disabled temporarily.

## Output Locations

- Raw GF pages: `database/pipeline/bowling_bayern/incoming/`
- Staging CSV: `database/pipeline/bowling_bayern/staging/`
- Sanitized CSV: `database/pipeline/bowling_bayern/sanitized/`
- Watermarks: `database/pipeline/bowling_bayern/state/`
- Run manifests: `database/pipeline/bowling_bayern/logs/`

## Incremental Logic

- Uses stored `last_seen_date_updated` per form.
- Pulls entries sorted descending by `date_updated`.
- Stops paging once fetched entries are no longer newer than watermark.
- Updates watermark after successful run.

## Next Step (Sprint 2)

- Add conversion bridge from sanitized staging into the current legacy converter path.
- Add manual sync endpoint + frontend trigger.
- Add interval + daily full sync scheduler.

