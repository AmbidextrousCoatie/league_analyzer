from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PipelinePaths:
    root: Path
    incoming: Path
    staging: Path
    sanitized: Path
    canonical: Path
    legacy_out: Path
    state: Path
    logs: Path
    failed: Path

    @staticmethod
    def default() -> "PipelinePaths":
        base = Path(__file__).resolve().parents[1] / "database" / "pipeline" / "bowling_bayern"
        return PipelinePaths(
            root=base,
            incoming=base / "incoming",
            staging=base / "staging",
            sanitized=base / "sanitized",
            canonical=base / "canonical",
            legacy_out=base / "legacy_out",
            state=base / "state",
            logs=base / "logs",
            failed=base / "failed",
        )

    def ensure(self) -> None:
        for p in (
            self.root,
            self.incoming,
            self.staging,
            self.sanitized,
            self.canonical,
            self.legacy_out,
            self.state,
            self.logs,
            self.failed,
        ):
            p.mkdir(parents=True, exist_ok=True)

