from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def _add_repo_root_to_path() -> None:
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Sprint-1 GF ingestion pipeline")
    parser.add_argument("--mode", choices=("incremental", "full"), default="incremental")
    parser.add_argument("--forms", required=True, help="Comma-separated form IDs, e.g. 92,113")
    parser.add_argument("--site", required=False, help="WordPress site base URL, e.g. https://bowlingbayern.de")
    parser.add_argument("--ck", required=False, help="GF consumer key")
    parser.add_argument("--cs", required=False, help="GF consumer secret")
    parser.add_argument("--field-ids", default="", help="Optional _field_ids subset")
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--insecure", action="store_true", help="Disable TLS verification")
    args = parser.parse_args()

    _add_repo_root_to_path()
    from pipeline.config import GfConfig
    from pipeline.runner import run_ingest

    site = args.site or os.getenv("GF_SITE_BASE_URL", "")
    ck = args.ck or os.getenv("GF_CONSUMER_KEY", "")
    cs = args.cs or os.getenv("GF_CONSUMER_SECRET", "")
    if not site or not ck or not cs:
        print("Missing credentials/site. Provide --site --ck --cs or set GF_SITE_BASE_URL/GF_CONSUMER_KEY/GF_CONSUMER_SECRET.")
        return 2

    forms = [int(x.strip()) for x in args.forms.split(",") if x.strip()]
    cfg = GfConfig(
        site_base_url=site.strip(),
        consumer_key=ck.strip(),
        consumer_secret=cs.strip(),
        verify_ssl=not args.insecure,
        page_size=max(1, min(200, int(args.page_size))),
        forms=forms,
    )
    result = run_ingest(config=cfg, mode=args.mode, field_ids=args.field_ids)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

