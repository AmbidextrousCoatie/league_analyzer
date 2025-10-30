import os
from pathlib import Path

import pandas as pd

try:
	from data_access.schema_validator import (
		load_schema,
		get_table_spec,
		coerce_dtypes,
		validate_dataframe_against_schema,
		get_ordered_column_names,
		ensure_schema_columns,
	)
except ImportError:
	from schema_validator import (
		load_schema,
		get_table_spec,
		coerce_dtypes,
		validate_dataframe_against_schema,
		get_ordered_column_names,
		ensure_schema_columns,
	)


ROOT = Path(__file__).resolve().parents[1]
REAL_DATA = ROOT / "database" / "data" / "bowling_ergebnisse_real.csv"
SCHEMA_JSON = ROOT / "database" / "schema.json"
OUT_DIR = ROOT / "database" / "relational_csv"
TARGET_TABLE = "league"


def ensure_out_dir() -> None:

	OUT_DIR.mkdir(parents=True, exist_ok=True)


def build_venue() -> pd.DataFrame:

	# Read real dataset (semicolon-separated)
	df = pd.read_csv(REAL_DATA, sep=";", dtype=str)

	# Extract distinct location names
	if "Location" not in df.columns:
		raise KeyError("Expected column 'Location' in real dataset")

	venues = (
		df[["Location"]]
		.rename(columns={"Location": "name"})
		.dropna()
		.drop_duplicates()
		.sort_values(by=["name"]) 
		.reset_index(drop=True)
	)

	# Assign surrogate integer ID, city/country unknown at extraction time
	venues.insert(0, "id", range(1, len(venues) + 1))

	# Load schema and conform columns strictly to definition (order + presence)
	schema = load_schema(str(SCHEMA_JSON))
	table_spec = get_table_spec(schema, "venue")
	venues = ensure_schema_columns(venues, table_spec)

	venues = coerce_dtypes(venues, table_spec)
	errors = validate_dataframe_against_schema(venues, table_spec)
	if errors:
		raise ValueError("Venue validation failed: " + "; ".join(errors))

	# Final column order exactly as schema
	return venues[get_ordered_column_names(table_spec)]


def main() -> None:

	ensure_out_dir()

	if TARGET_TABLE == "venue":
		out_df = build_venue()
	elif TARGET_TABLE == "league":
		# Build league table using mapping file
		df = pd.read_csv(REAL_DATA, sep=";", dtype=str)
		if "League" not in df.columns:
			raise KeyError("Expected column 'League' in real dataset")
		ids = (
			df[["League"]]
			.rename(columns={"League": "id"})
			.dropna()
			.drop_duplicates()
			.sort_values(by=["id"]) 
			.reset_index(drop=True)
		)
		schema = load_schema(str(SCHEMA_JSON))
		table_spec = get_table_spec(schema, "league")
		mapping_path = OUT_DIR / "league_mapping.csv"
		if not mapping_path.exists():
			template = ids.copy()
			template["long_name"] = template["id"]
			template["level"] = pd.NA
			template["division"] = pd.NA
			template.to_csv(mapping_path, index=False)
			raise FileNotFoundError(f"Created template mapping at {mapping_path}. Fill it and rerun.")
		mapping = pd.read_csv(mapping_path, dtype={"id": str, "long_name": str, "level": "Int64", "division": str})
		leagues = ids.merge(mapping, on="id", how="left", validate="one_to_one")
		missing = leagues[leagues[["long_name", "level", "division"]].isna().any(axis=1)]
		if not missing.empty:
			raise ValueError("League mapping incomplete for ids: " + ", ".join(missing["id"].astype(str).tolist()))
		leagues = ensure_schema_columns(leagues, table_spec)
		leagues = coerce_dtypes(leagues, table_spec)
		errors = validate_dataframe_against_schema(leagues, table_spec)
		if errors:
			raise ValueError("League validation failed: " + "; ".join(errors))
		out_df = leagues[get_ordered_column_names(table_spec)]
	else:
		raise ValueError(f"Unsupported TARGET_TABLE: {TARGET_TABLE}")

	out_path = OUT_DIR / f"{TARGET_TABLE}_new.csv"
	out_df.to_csv(out_path, index=False)
	print(f"Wrote {len(out_df)} rows to {out_path}")


if __name__ == "__main__":

	main()


