"""Load canonical Bowling Bayern rows from exported `liga_*_ergebnisse-*.csv` files."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List


def load_liga_ergebnisse_rows(input_dir: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for path in sorted(input_dir.glob("liga_*_ergebnisse-*.csv")):
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            rows.extend(list(csv.DictReader(f)))
    return rows
