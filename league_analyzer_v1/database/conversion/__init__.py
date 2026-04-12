"""
Pure Bowling Bayern → legacy flat CSV conversion.

Must not import Gravity Forms client, pipeline runners, or Flask.
Other code should adapt external feeds into the canonical input row shape, then call
`bowlingbayern_legacy_core.convert_source_rows_to_legacy`.
"""
