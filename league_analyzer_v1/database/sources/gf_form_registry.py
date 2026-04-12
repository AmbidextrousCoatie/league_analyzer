"""
Pipeline entry for staging → canonical mapping.

All GF **results** forms in the ingest list are treated as sharing the **same** v1 field
layout (`gf_results_v1_adapter`). Per-form Python adapters are not maintained; if the
remote forms drift, align them with the data owner or introduce a new adapter version
module and switch imports here.
"""

from __future__ import annotations

from typing import Dict

from database.sources.gf_results_v1_adapter import staging_row_to_canonical_gf_results_v1


def has_legacy_adapter(form_id: int) -> bool:
    """Any configured form id participates in merge + legacy (shared v1 layout)."""
    return form_id > 0


def staging_row_to_canonical_for_merge(row: Dict[str, str], _form_id: int) -> Dict[str, str]:
    return staging_row_to_canonical_gf_results_v1(row)
