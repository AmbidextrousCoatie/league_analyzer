from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List


@dataclass
class GfConfig:
    site_base_url: str
    consumer_key: str
    consumer_secret: str
    verify_ssl: bool = True
    timeout_seconds: float = 60.0
    page_size: int = 100
    forms: List[int] | None = None

    @staticmethod
    def from_env() -> "GfConfig":
        forms_raw = os.getenv("GF_FORMS", "").strip()
        forms: List[int] | None = None
        if forms_raw:
            forms = [int(x.strip()) for x in forms_raw.split(",") if x.strip()]
        verify = os.getenv("GF_SSL_VERIFY", "true").strip().lower() not in ("0", "false", "no")
        return GfConfig(
            site_base_url=os.getenv("GF_SITE_BASE_URL", "").strip(),
            consumer_key=os.getenv("GF_CONSUMER_KEY", "").strip(),
            consumer_secret=os.getenv("GF_CONSUMER_SECRET", "").strip(),
            verify_ssl=verify,
            timeout_seconds=float(os.getenv("GF_TIMEOUT_SECONDS", "60")),
            page_size=max(1, min(200, int(os.getenv("GF_PAGE_SIZE", "100")))),
            forms=forms,
        )

