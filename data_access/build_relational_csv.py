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
TARGET_TABLE = "event"  # options: "venue", "league", "scoring_system", "league_season", "event"


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


def build_scoring_system() -> pd.DataFrame:

	data = [
		{
			"id": "liga_bayern_2pt",
			"name": "Liga Bayern 2pt",
			"points_per_individual_match_win": 1,
			"points_per_individual_match_tie": 0.5,
			"points_per_individual_match_loss": 0,
			"points_per_team_match_win": 2,
			"points_per_team_match_tie": 1,
			"points_per_team_match_loss": 0,
			"allow_ties": True,
		},
		{
			"id": "liga_bayern_3pt",
			"name": "Liga Bayern 3pt",
			"points_per_individual_match_win": 1,
			"points_per_individual_match_tie": 0.5,
			"points_per_individual_match_loss": 0,
			"points_per_team_match_win": 3,
			"points_per_team_match_tie": 1.5,
			"points_per_team_match_loss": 0,
			"allow_ties": True,
		},
	]

	df = pd.DataFrame(data)
	schema = load_schema(str(SCHEMA_JSON))
	table_spec = get_table_spec(schema, "scoring_system")
	df = ensure_schema_columns(df, table_spec)
	df = coerce_dtypes(df, table_spec)
	errors = validate_dataframe_against_schema(df, table_spec)
	if errors:
		raise ValueError("Scoring system validation failed: " + "; ".join(errors))
	return df[get_ordered_column_names(table_spec)]


def _season_prefix_int(season: str) -> int:

	try:
		return int(str(season).split("/")[0])
	except Exception:
		return -1


def build_league_season() -> pd.DataFrame:

	df = pd.read_csv(REAL_DATA, sep=";", dtype=str)
	for col in ("League", "Season"):
		if col not in df.columns:
			raise KeyError(f"Expected column '{col}' in real dataset")
	base = (
		df[["League", "Season"]]
		.rename(columns={"League": "league_id", "Season": "season"})
		.dropna()
		.drop_duplicates()
		.sort_values(by=["league_id", "season"]) 
		.reset_index(drop=True)
	)

	base["_season_num"] = base["season"].map(_season_prefix_int)
	base["scoring_system_id"] = base["_season_num"].apply(
		lambda n: "liga_bayern_3pt" if n >= 25 else "liga_bayern_2pt"
	)
	base = base.drop(columns=["_season_num"]) 

	players_per_team = (
		df.groupby(["League", "Season"]).agg({"Players per Team": "max"}).reset_index()
		.rename(columns={"League": "league_id", "Season": "season", "Players per Team": "players_per_team"})
	)

	teams_counts = (
		df[df["Team"].notna() & (df["Team"] != "Team Total")]
		.groupby(["League", "Season"])["Team"].nunique()
		.reset_index()
		.rename(columns={"League": "league_id", "Season": "season", "Team": "number_of_teams"})
	)

	merged = base.merge(players_per_team, on=["league_id", "season"], how="left", validate="one_to_one")
	merged = merged.merge(teams_counts, on=["league_id", "season"], how="left", validate="one_to_one")

	merged.insert(0, "id", range(1, len(merged) + 1))
	schema = load_schema(str(SCHEMA_JSON))
	table_spec = get_table_spec(schema, "league_season")
	merged = ensure_schema_columns(merged, table_spec)
	merged = coerce_dtypes(merged, table_spec)
	errors = validate_dataframe_against_schema(merged, table_spec)
	if errors:
		raise ValueError("League season validation failed: " + "; ".join(errors))
	return merged[get_ordered_column_names(table_spec)]


def build_event() -> pd.DataFrame:

	df = pd.read_csv(REAL_DATA, sep=";", dtype=str)
	for col in ("League", "Season", "Date"):
		if col not in df.columns:
			raise KeyError(f"Expected column '{col}' in real dataset")
	# Always use league Week from the dataset (ignore any 'Round Number' columns)
	week_col = "Week"
	if week_col not in df.columns:
		raise KeyError("Expected 'Week' column in real dataset")
	if "Location" not in df.columns:
		raise KeyError("Expected column 'Location' in real dataset")

	events_raw = (
		df[["League", "Season", week_col, "Date", "Location"]]
		.rename(columns={"League": "league_id", "Season": "season", week_col: "league_week", "Date": "date"})
		.dropna()
		.drop_duplicates()
		.sort_values(by=["league_id", "season", "league_week", "date", "Location"]) 
		.reset_index(drop=True)
	)
    
	league_season_csv = OUT_DIR / "league_season.csv"
	venue_csv = OUT_DIR / "venue.csv"
	if not league_season_csv.exists():
		raise FileNotFoundError("league_season.csv not found. Generate league_season first.")
	if not venue_csv.exists():
		raise FileNotFoundError("venue.csv not found. Generate or curate venues first.")
	league_season_df = pd.read_csv(league_season_csv, dtype={"id": "Int64", "league_id": str, "season": str})
	venue_df = pd.read_csv(venue_csv, dtype=str)

	events = events_raw.merge(
		league_season_df[["id", "league_id", "season"]].rename(columns={"id": "league_season_id"}),
		on=["league_id", "season"],
		how="left",
		validate="many_to_one",
	)
	missing_ls = events[events["league_season_id"].isna()]
	if not missing_ls.empty:
		missing_keys = missing_ls[["league_id", "season"]].drop_duplicates().astype(str).values.tolist()
		raise ValueError(f"Missing league_season rows for: {missing_keys}")

	# Deterministic mapping from Location → venue_id using exact matches on 'name' or 'full_name'
	name_map = venue_df[["name", "id"]].rename(columns={"name": "Location", "id": "venue_id"})
	full_map = venue_df[["full_name", "id"]].dropna().rename(columns={"full_name": "Location", "id": "venue_id"})
	mapping = pd.concat([name_map, full_map], ignore_index=True).drop_duplicates(subset=["Location"])
	events = events.merge(mapping, on="Location", how="left", validate="many_to_one")
	missing_v = events[events["venue_id"].isna()]
	if not missing_v.empty:
		missing_names_df = missing_v[["Location"]].drop_duplicates().rename(columns={"Location": "unmatched_location"})
		out_path = OUT_DIR / "unmatched_event_locations.csv"
		missing_names_df.to_csv(out_path, index=False)
		raise ValueError(f"Unmapped venue names written to {out_path}. Add these as venue.name or venue.full_name and rerun.")

	events["status"] = "completed"
	events["event_type"] = "league"
	events["tournament_stage"] = pd.NA
	events["oil_pattern_id"] = pd.NA
	events["notes"] = pd.NA

	events.insert(0, "id", range(1, len(events) + 1))
	schema = load_schema(str(SCHEMA_JSON))
	table_spec = get_table_spec(schema, "event")
	events = events[[
		"id",
		"league_season_id",
		"event_type",
		"league_week",
		"tournament_stage",
		"date",
		"venue_id",
		"oil_pattern_id",
		"status",
		"notes",
	]]
	events = ensure_schema_columns(events, table_spec)
	events = coerce_dtypes(events, table_spec)
	# Final safeguard: if any venue_id are still NULL, recompute unmatched from events_raw before column reduction
	if events["venue_id"].isna().any():
		unmatched_merge = events_raw.merge(mapping, on="Location", how="left")
		unmatched = unmatched_merge[unmatched_merge["venue_id"].isna()][["Location"]].drop_duplicates().rename(columns={"Location": "unmatched_location"})
		out_path = OUT_DIR / "unmatched_event_locations.csv"
		unmatched.to_csv(out_path, index=False)
		raise ValueError(f"Unmapped venue names written to {out_path}. Add these as venue.name or venue.full_name and rerun.")
	errors = validate_dataframe_against_schema(events, table_spec)
	if errors:
		raise ValueError("Event validation failed: " + "; ".join(errors))
	return events[get_ordered_column_names(table_spec)]
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
	elif TARGET_TABLE == "scoring_system":
		out_df = build_scoring_system()
	elif TARGET_TABLE == "league_season":
		ss_path = OUT_DIR / "scoring_system.csv"
		if not ss_path.exists():
			ss_df = build_scoring_system()
			ss_df.to_csv(ss_path, index=False)
		out_df = build_league_season()
	elif TARGET_TABLE == "event":
		out_df = build_event()
	else:
		raise ValueError(f"Unsupported TARGET_TABLE: {TARGET_TABLE}")

	out_path = OUT_DIR / f"{TARGET_TABLE}_new.csv"
	out_df.to_csv(out_path, index=False)
	print(f"Wrote {len(out_df)} rows to {out_path}")


if __name__ == "__main__":

	main()


