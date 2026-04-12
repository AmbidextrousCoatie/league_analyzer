"""
Default Gravity Forms IDs for Bowling Bayern **results** ingestion (shared v1 field map).

You can override per run with ``GF_FORMS`` (comma-separated) or ``run_gf_pipeline.py --forms``.
"""

from __future__ import annotations

# Youth LL (21), primary + regional/bayernliga forms — same staging→canonical contract as v1 adapter.
DEFAULT_BOWLING_BAYERN_GF_FORM_IDS: tuple[int, ...] = (
    21,
    92,
    95,
    100,
    102,
    105,
    113,
    115,
    117,
)
