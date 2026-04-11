from __future__ import annotations

import base64
import json
import ssl
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from .config import GfConfig


def _dt(raw: str) -> datetime:
    return datetime.strptime(raw, "%Y-%m-%d %H:%M:%S")


@dataclass
class PageResult:
    page: int
    url: str
    payload: Dict[str, Any]
    entries: List[Dict[str, Any]]


class GfClient:
    def __init__(self, config: GfConfig) -> None:
        self.config = config
        token = f"{config.consumer_key}:{config.consumer_secret}".encode("utf-8")
        self._auth_header = "Basic " + base64.b64encode(token).decode("ascii")

    def _request_json(self, path: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        base = self._normalize_site_base(self.config.site_base_url)
        query = urlencode(params or {}, doseq=True)
        url = f"{base}/wp-json/gf/v2/{path}"
        if query:
            url += f"?{query}"
        req = Request(url=url, method="GET")
        req.add_header("Authorization", self._auth_header)
        req.add_header("Accept", "application/json")
        ssl_ctx = None
        if not self.config.verify_ssl:
            ssl_ctx = ssl._create_unverified_context()
        with urlopen(req, timeout=self.config.timeout_seconds, context=ssl_ctx) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)

    @staticmethod
    def _normalize_site_base(raw: str) -> str:
        """
        Accept common user input forms:
        - www.example.com
        - https://example.com
        - https://example.com/wp-json/gf/v2
        """
        s = (raw or "").strip()
        if not s:
            return s
        if "://" not in s:
            s = "https://" + s
        parts = urlsplit(s)
        path = (parts.path or "").replace("//", "/").rstrip("/")
        clean = urlunsplit((parts.scheme, parts.netloc, path, "", "")).rstrip("/")
        lower = clean.lower()
        for suffix in ("/wp-json/gf/v2", "/wp-json"):
            if lower.endswith(suffix):
                clean = clean[: -len(suffix)].rstrip("/")
                lower = clean.lower()
        return clean

    @staticmethod
    def _extract_entries(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        entries = payload.get("entries")
        if isinstance(entries, list):
            return entries
        if isinstance(entries, dict):
            return [v for v in entries.values() if isinstance(v, dict)]
        if isinstance(payload, dict):
            vals = list(payload.values())
            if vals and all(isinstance(v, dict) for v in vals):
                return vals
        return []

    def fetch_forms(self) -> Dict[str, Any]:
        return self._request_json("forms")

    def fetch_entries_page(
        self,
        form_id: int,
        page: int,
        page_size: int,
        field_ids: str = "",
        sort_desc_by_updated: bool = True,
    ) -> PageResult:
        params: Dict[str, Any] = {
            "form_ids": str(form_id),
            "paging[page_size]": str(page_size),
            "paging[current_page]": str(page),
        }
        if field_ids.strip():
            params["_field_ids"] = field_ids.strip()
        if sort_desc_by_updated:
            params["sorting[key]"] = "date_updated"
            params["sorting[direction]"] = "DESC"
        payload = self._request_json("entries", params=params)
        return PageResult(
            page=page,
            url=f"/entries?page={page}",
            payload=payload,
            entries=self._extract_entries(payload),
        )

    def fetch_incremental_entries(self, form_id: int, since_date_updated: str, page_size: int, field_ids: str = "") -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        page = 1
        while True:
            current = self.fetch_entries_page(form_id, page=page, page_size=page_size, field_ids=field_ids, sort_desc_by_updated=True)
            if not current.entries:
                break
            stop = False
            for e in current.entries:
                du = str(e.get("date_updated") or "")
                if du and since_date_updated:
                    try:
                        if _dt(du) <= _dt(since_date_updated):
                            stop = True
                            continue
                    except ValueError:
                        pass
                out.append(e)
            if stop or len(current.entries) < page_size:
                break
            page += 1
        return out

