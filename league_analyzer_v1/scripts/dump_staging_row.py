from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    p = ROOT / "database/pipeline/bowling_bayern/staging/form_92__20260407T100150Z__staging.csv"
    with p.open(encoding="utf-8", newline="") as f:
        r = next(x for x in csv.DictReader(f, delimiter=";") if x.get("source_entry_id") == "28386")
    for k in sorted((int(x), x) for x in r if x.isdigit()):
        v = (r[k[1]] or "").strip()
        if v:
            print(f"{k[1]!s:>4} = {v!r}")


if __name__ == "__main__":
    main()
