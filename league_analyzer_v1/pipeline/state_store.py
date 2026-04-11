from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class FormState:
    form_id: int
    last_seen_date_updated: str = ""
    last_seen_entry_id: str = ""
    last_successful_run_utc: str = ""
    last_full_sync_utc: str = ""


class StateStore:
    def __init__(self, state_dir: Path) -> None:
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, form_id: int) -> Path:
        return self.state_dir / f"form_{form_id}.json"

    def load(self, form_id: int) -> FormState:
        p = self._path(form_id)
        if not p.exists():
            return FormState(form_id=form_id)
        data = json.loads(p.read_text(encoding="utf-8"))
        return FormState(
            form_id=form_id,
            last_seen_date_updated=str(data.get("last_seen_date_updated", "")),
            last_seen_entry_id=str(data.get("last_seen_entry_id", "")),
            last_successful_run_utc=str(data.get("last_successful_run_utc", "")),
            last_full_sync_utc=str(data.get("last_full_sync_utc", "")),
        )

    def save(self, state: FormState) -> None:
        p = self._path(state.form_id)
        p.write_text(json.dumps(asdict(state), indent=2, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def now_utc() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

