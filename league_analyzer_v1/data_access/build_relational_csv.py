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
OUT_DIR = ROOT / "database" / "relational_csv" / "new"
TARGET_TABLE = "game_result"  # options: "venue", "league", "scoring_system", "league_season", "event", "player", "club", "team_season", "game_result"


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


def _split_player_name(raw: str) -> tuple[str, str]:

	if pd.isna(raw) or not str(raw).strip():
		return ("", "")
	text = str(raw).strip()
	# Expected format: "Family, Given"
	if "," in text:
		parts = [p.strip() for p in text.split(",", 1)]
		family = parts[0]
		given = parts[1]
		return (given, family)
	# Fallback: last token as family name
	parts = text.split()
	if len(parts) >= 2:
		family = parts[-1]
		given = " ".join(parts[:-1])
		return (given, family)
	return (text, "")


def build_player() -> pd.DataFrame:

	df_all = pd.read_csv(REAL_DATA, sep=";", dtype=str)

	# Build skipped entries report (Team Total and invalid/missing IDs)
	skipped_lines: list[str] = []
	# Team Total occurrences
	if "Player" in df_all.columns:
		team_total_count = df_all[df_all["Player"] == "Team Total"].shape[0]
		if team_total_count > 0:
			skipped_lines.append(f"- Team Total, {team_total_count} times")

	# Missing or invalid Player IDs (<=0, NaN, non-numeric) among player rows (excluding Team Total)
	player_mask = df_all["Player"].notna() & (df_all["Player"] != "Team Total")
	ids_all = pd.to_numeric(df_all.loc[player_mask, "Player ID"], errors="coerce")
	invalid_id_mask = ids_all.isna() | (ids_all.astype("Int64").fillna(0) <= 0)
	if invalid_id_mask.any():
		invalid_players = (
			df_all.loc[player_mask, ["Player"]]
			.assign(_invalid=invalid_id_mask.values)
			.query("_invalid == True")["Player"]
		)
		counts = invalid_players.value_counts().sort_index()
		for name, cnt in counts.items():
			skipped_lines.append(f"- {name}, {int(cnt)} times")

	# Continue with valid players only
	df = df_all[player_mask].copy()
	ids = pd.to_numeric(df["Player ID"], errors="coerce")
	df = df[ids.notna() & (ids.astype(int) > 0)].copy()
	df["player_id_int"] = ids.astype(int)

	# Build base unique by (Player ID)
	base = df[["player_id_int", "Player"]].drop_duplicates().copy()
	base["given_name"], base["family_name"] = zip(*base["Player"].map(_split_player_name))
	base["full_name"] = (base["family_name"].fillna("").str.strip() + ", " + base["given_name"].fillna("").str.strip()).str.strip()
	base = base.rename(columns={"player_id_int": "id"})

	# Conform to schema and validate
	schema = load_schema(str(SCHEMA_JSON))
	table_spec = get_table_spec(schema, "player")
	players = base[["id", "given_name", "family_name", "full_name"]].copy()
	players = ensure_schema_columns(players, table_spec)
	players = coerce_dtypes(players, table_spec)
	errors = validate_dataframe_against_schema(players, table_spec)
	if errors:
		raise ValueError("Player validation failed: " + "; ".join(errors))

	# Consistency report: ID→multiple names, Name→multiple IDs
	problems: list[str] = []
	# ID to full_name uniqueness
	id_name = df[["Player ID", "Player"]].dropna().drop_duplicates()
	id_name["Player ID"] = pd.to_numeric(id_name["Player ID"], errors="coerce").astype("Int64")
	# Normalize full name
	id_name["full_name"] = id_name["Player"].map(lambda s: (lambda g,f: f"{g} {f}".strip())(*_split_player_name(s)))
	conflict_ids = (
		id_name.groupby("Player ID")["full_name"].nunique().reset_index(name="name_count")
	)
	conflict_ids = conflict_ids[conflict_ids["name_count"] > 1]
	if not conflict_ids.empty:
		problems.append("IDs with multiple full_names:")
		merged = id_name.merge(conflict_ids[["Player ID"]], on="Player ID", how="inner")
		lines = merged.sort_values(["Player ID", "full_name"]).apply(lambda r: f"  ID={r['Player ID']}: {r['full_name']}", axis=1).unique()
		problems.extend(lines.tolist())

	# full_name to ID uniqueness
	name_ids = id_name.groupby("full_name")["Player ID"].nunique().reset_index(name="id_count")
	name_ids = name_ids[name_ids["id_count"] > 1]
	if not name_ids.empty:
		problems.append("Full names mapped to multiple IDs:")
		merged2 = id_name.merge(name_ids[["full_name"]], on="full_name", how="inner")
		lines2 = merged2.sort_values(["full_name", "Player ID"]).apply(lambda r: f"  full_name={r['full_name']}: ID={r['Player ID']}", axis=1).unique()
		problems.extend(lines2.tolist())

	# Write report if any
	report_path = OUT_DIR / "player_consistency_report.txt"
	if problems:
		with open(report_path, "w", encoding="utf-8") as f:
			f.write("\n".join(problems) + "\n")
		print(f"Wrote consistency report to {report_path}")
	else:
		# Ensure any previous report is cleared
		try:
			os.remove(report_path)
		except OSError:
			pass

	# Write skipped entries report
	skipped_path = OUT_DIR / "player_skipped_report.txt"
	if skipped_lines:
		with open(skipped_path, "w", encoding="utf-8") as f:
			f.write("\n".join(skipped_lines) + "\n")
		print(f"Wrote skipped entries report to {skipped_path}")
	else:
		try:
			os.remove(skipped_path)
		except OSError:
			pass

	return players[get_ordered_column_names(table_spec)]


def _extract_team_parts(team_name: str) -> tuple[str, int]:

	if pd.isna(team_name):
		return ("", 0)
	name = str(team_name).strip()
	if not name or name == "Team Total":
		return ("", 0)
	# Trailing integer indicates team number
	import re
	m = re.match(r"^(.*?)[\s]+(\d+)$", name)
	if m:
		club_name = m.group(1).strip()
		team_number = int(m.group(2))
		return (club_name, team_number)
	# No explicit number → default to 1
	return (name, 1)


def build_club() -> pd.DataFrame:

	df = pd.read_csv(REAL_DATA, sep=";", dtype=str)
	print("--- input data:", REAL_DATA)
	team_col = "Team"
	opp_col = "Opponent"
	if team_col not in df.columns or opp_col not in df.columns:
		raise KeyError("Expected 'Team' and 'Opponent' columns in real dataset")

	all_names = pd.concat([df[team_col], df[opp_col]], ignore_index=True)
	parts = all_names.dropna().unique()
	print("--- parts:", parts)
	clubs: list[str] = []
	for raw in parts:
		club, num = _extract_team_parts(raw)
		if club:
			clubs.append(club)

	clubs_df = pd.DataFrame({"name": sorted(set(clubs))})
	clubs_df.insert(0, "id", range(1, len(clubs_df) + 1))

	schema = load_schema(str(SCHEMA_JSON))
	table_spec = get_table_spec(schema, "club")
	clubs_df = ensure_schema_columns(clubs_df, table_spec)
	clubs_df = coerce_dtypes(clubs_df, table_spec)
	errors = validate_dataframe_against_schema(clubs_df, table_spec)
	print(clubs_df.sort_values(by="name").to_string())
	if errors:
		raise ValueError("Club validation failed: " + "; ".join(errors))
	return clubs_df[get_ordered_column_names(table_spec)]


def build_team_season() -> pd.DataFrame:

	df = pd.read_csv(REAL_DATA, sep=";", dtype=str)
	team_col = "Team"
	opp_col = "Opponent"
	if team_col not in df.columns or opp_col not in df.columns:
		raise KeyError("Expected 'Team' and 'Opponent' columns in real dataset")

	# Determine season key
	if "League" not in df.columns or "Season" not in df.columns:
		raise KeyError("Expected 'League' and 'Season' columns in real dataset")

	# Prepare unique season teams: (league_id, season, club_name, team_number)
	def iter_team_rows(series: pd.Series) -> list[tuple[str, str, str, int]]:
		rows: list[tuple[str, str, str, int]] = []
		for league, season, team in zip(df["League"], df["Season"], series):
			if pd.isna(team):
				continue
			club, num = _extract_team_parts(team)
			if club and num > 0:
				rows.append((league, season, club, num))
		return rows

	rows_all = iter_team_rows(df[team_col]) + iter_team_rows(df[opp_col])
	season_teams = pd.DataFrame(rows_all, columns=["league_id", "season", "club_name", "team_number"]).drop_duplicates()

	# Map to league_season_id and club_id
	league_season_csv = OUT_DIR / "league_season.csv"
	club_csv = OUT_DIR / "club.csv"
	if not league_season_csv.exists():
		raise FileNotFoundError("league_season.csv not found. Generate league_season first.")
	if not club_csv.exists():
		raise FileNotFoundError("club.csv not found. Generate clubs first.")

	ls_df = pd.read_csv(league_season_csv, dtype={"id": "Int64", "league_id": str, "season": str})
	clubs = pd.read_csv(club_csv, dtype={"id": "Int64", "name": str, "short_name": str})

	season_teams = season_teams.merge(ls_df[["id", "league_id", "season"]].rename(columns={"id": "league_season_id"}), on=["league_id", "season"], how="left", validate="many_to_one")
	if season_teams["league_season_id"].isna().any():
		missing = season_teams[season_teams["league_season_id"].isna()][["league_id", "season"]].drop_duplicates().values.tolist()
		raise ValueError(f"Missing league_season rows for: {missing}")
	season_teams = season_teams.merge(clubs, left_on="club_name", right_on="name", how="left", validate="many_to_one")
	if season_teams["id"].isna().any():
		missing_clubs = season_teams[season_teams["id"].isna()]["club_name"].drop_duplicates().tolist()
		raise ValueError(f"Missing clubs for team_season: {missing_clubs}")

	team_season = season_teams.rename(columns={"id": "club_id"})[["league_season_id", "club_id", "team_number"]].copy()
	team_season.insert(0, "id", range(1, len(team_season) + 1))

	schema = load_schema(str(SCHEMA_JSON))
	table_spec = get_table_spec(schema, "team_season")
	team_season = ensure_schema_columns(team_season, table_spec)
	team_season = coerce_dtypes(team_season, table_spec)
	errors = validate_dataframe_against_schema(team_season, table_spec)
	if errors:
		raise ValueError("Team season validation failed: " + "; ".join(errors))
	return team_season[get_ordered_column_names(table_spec)]


def build_game_result() -> pd.DataFrame:

	df = pd.read_csv(REAL_DATA, sep=";", dtype=str)
	print(f"Loaded {len(df)} rows from raw CSV")
	
	# Filter valid player rows (exclude Team Total, invalid IDs)
	player_mask = df["Player"].notna() & (df["Player"] != "Team Total")
	print(f"After filtering Team Total: {player_mask.sum()} rows")
	ids = pd.to_numeric(df.loc[player_mask, "Player ID"], errors="coerce")
	valid_mask = ids.notna() & (ids.astype(int) > 0)
	print(f"After filtering invalid IDs: {valid_mask.sum()} rows")
	df = df.loc[player_mask][valid_mask].copy()
	df["player_id_int"] = ids[valid_mask].astype(int)
	
	# Load reference tables (from parent directory, not "new" subdirectory)
	ref_dir = OUT_DIR.parent
	event_csv = ref_dir / "event.csv"
	player_csv = ref_dir / "player.csv"
	team_season_csv = ref_dir / "team_season.csv"
	league_season_csv = ref_dir / "league_season.csv"
	club_csv = ref_dir / "club.csv"
	
	for path, name in [(event_csv, "event"), (player_csv, "player"), (team_season_csv, "team_season"), (league_season_csv, "league_season"), (club_csv, "club")]:
		if not path.exists():
			raise FileNotFoundError(f"{name}.csv not found. Generate {name} first.")
	
	events_df = pd.read_csv(event_csv, dtype={"id": "Int64", "league_season_id": "Int64", "league_week": "Int64", "date": str})
	players_df = pd.read_csv(player_csv, dtype={"id": "Int64"})
	team_seasons_df = pd.read_csv(team_season_csv, dtype={"id": "Int64", "league_season_id": "Int64", "club_id": "Int64", "team_number": "Int64"})
	league_seasons_df = pd.read_csv(league_season_csv, dtype={"id": "Int64", "league_id": str, "season": str})
	clubs_df = pd.read_csv(club_csv, dtype={"id": "Int64", "name": str})
	
	# Map to event_id: join via league_season, then match (League, Season, Week, Date, Location)
	events_with_ls = events_df.merge(league_seasons_df[["id", "league_id", "season"]].rename(columns={"id": "league_season_id"}), on="league_season_id", how="left")
	events_with_ls["league_week"] = events_with_ls["league_week"].astype("Int64")
	events_with_ls["date_parsed"] = pd.to_datetime(events_with_ls["date"], errors="coerce").dt.date
	
	df["date_parsed"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
	df["Week_num"] = pd.to_numeric(df["Week"], errors="coerce").astype("Int64")
	
	df = df.merge(
		events_with_ls[["id", "league_id", "season", "league_week", "date_parsed"]].rename(columns={"id": "event_id"}),
		left_on=["League", "Season", "Week_num", "date_parsed"],
		right_on=["league_id", "season", "league_week", "date_parsed"],
		how="left",
		validate="many_to_one",
	)
	
	missing_events = df[df["event_id"].isna()]
	if not missing_events.empty:
		missing = missing_events[["League", "Season", "Week", "Date"]].drop_duplicates().head(5)
		print(f"Warning: {len(missing_events)} rows have missing events. Sample: {missing.to_dict('records')}")
		# Drop rows with missing events for now
		df = df[df["event_id"].notna()].copy()
		print(f"After dropping missing events: {len(df)} rows")
	
	# Map to player_id: merge df.player_id_int to players_df.id
	players_lookup = players_df[["id"]].rename(columns={"id": "player_id"})
	players_lookup["player_id_int"] = players_lookup["player_id"]  # Add join key
	df = df.merge(players_lookup[["player_id", "player_id_int"]], on="player_id_int", how="left", validate="many_to_one")
	missing_players = df[df["player_id"].isna()]
	if not missing_players.empty:
		raise ValueError(f"Missing players for IDs: {missing_players['player_id_int'].drop_duplicates().tolist()}")
	
	# Map to team_season_id: extract club/team_number, join via league_season
	df["club_name"], df["team_number_raw"] = zip(*df["Team"].map(_extract_team_parts))
	df["team_number_raw"] = pd.to_numeric(df["team_number_raw"], errors="coerce").astype("Int64")
	
	# Build team_season lookup with club names
	team_seasons_with_club = team_seasons_df.merge(
		league_seasons_df[["id", "league_id", "season"]].rename(columns={"id": "league_season_id"}),
		on="league_season_id",
		how="left"
	).merge(
		clubs_df[["id", "name"]].rename(columns={"id": "club_id_check", "name": "club_name"}),
		left_on="club_id",
		right_on="club_id_check",
		how="left"
	)
	
	df = df.merge(
		team_seasons_with_club[["id", "league_id", "season", "club_name", "team_number"]].rename(columns={"id": "team_season_id"}),
		left_on=["League", "Season", "club_name", "team_number_raw"],
		right_on=["league_id", "season", "club_name", "team_number"],
		how="left",
		validate="many_to_one",
	)
	missing_team_seasons = df[df["team_season_id"].isna()]
	if not missing_team_seasons.empty:
		print(f"Warning: {len(missing_team_seasons)} rows have missing team_season_id. Sample teams: {missing_team_seasons[['Team', 'League', 'Season']].drop_duplicates().head(5).to_dict('records')}")
	
	# Extract fields
	df["lineup_position"] = pd.to_numeric(df["Position"], errors="coerce").astype("Int64")
	df["score"] = pd.to_numeric(df["Score"], errors="coerce").astype("Int64")
	df["round_number"] = pd.to_numeric(df["Round Number"], errors="coerce").astype("Int64")
	df["match_number"] = pd.to_numeric(df["Match Number"], errors="coerce").astype("Int64")
	
	# Determine disqualification: score is NULL (not 0, as 0 might be valid)
	df["is_disqualified"] = df["score"].isna()
	df["handicap"] = pd.NA  # Not in source data
	
	# Prepare final result
	result = df[[
		"event_id",
		"player_id",
		"team_season_id",
		"lineup_position",
		"score",
		"is_disqualified",
		"round_number",
		"match_number",
		"handicap",
	]].copy()
	
	# Check for duplicates on unique constraint columns before assigning IDs
	# Include match_number, round_number, and team_season_id in uniqueness check
	unique_cols = ["event_id", "player_id", "lineup_position", "match_number", "round_number", "team_season_id"]
	duplicate_mask = result.duplicated(subset=unique_cols, keep=False)
	if duplicate_mask.any():
		duplicates = result[duplicate_mask].copy()
		duplicate_groups = duplicates.groupby(unique_cols).size()
		print(f"Warning: Found {len(duplicate_groups)} duplicate groups violating unique constraint:")
		# Show first 10 examples with details
		for idx, (key, count) in enumerate(list(duplicate_groups.items())[:10]):
			eid, pid, pos, match, round_num, team = key
			print(f"  event_id={eid}, player_id={pid}, lineup_position={pos}, match_number={match}, round_number={round_num}, team_season_id={team}: {count} rows")
		if len(duplicate_groups) > 10:
			print(f"  ... and {len(duplicate_groups) - 10} more groups")
		
		# Show sample duplicate rows to understand what's different
		sample_dups = duplicates.head(6)
		print(f"\nSample duplicate rows (showing first 6):")
		print(sample_dups[["event_id", "player_id", "team_season_id", "lineup_position", "round_number", "match_number", "score"]].to_string())
		
		# Keep first occurrence, drop rest
		result = result.drop_duplicates(subset=unique_cols, keep="first")
		print(f"\nDropped {duplicate_mask.sum() - len(duplicate_groups)} duplicate rows, keeping first occurrence.")
	else:
		print("No duplicates found - all rows are unique.")
	
	result.insert(0, "id", range(1, len(result) + 1))
	
	print(f"Final result rows before validation: {len(result)}")
	
	schema = load_schema(str(SCHEMA_JSON))
	table_spec = get_table_spec(schema, "game_result")
	result = ensure_schema_columns(result, table_spec)
	result = coerce_dtypes(result, table_spec)
	errors = validate_dataframe_against_schema(result, table_spec)
	if errors:
		raise ValueError("Game result validation failed: " + "; ".join(errors))
	print(f"Final result rows: {len(result)}")
	return result[get_ordered_column_names(table_spec)]


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
	elif TARGET_TABLE == "player":
		out_df = build_player()
	elif TARGET_TABLE == "club":
		out_df = build_club()
	elif TARGET_TABLE == "team_season":
		out_df = build_team_season()
	elif TARGET_TABLE == "game_result":
		out_df = build_game_result()
	else:
		raise ValueError(f"Unsupported TARGET_TABLE: {TARGET_TABLE}")

	out_path = OUT_DIR / f"{TARGET_TABLE}_new.csv"
	out_df.to_csv(out_path, index=False)
	print(f"Wrote {len(out_df)} rows to {out_path}")


if __name__ == "__main__":

	main()


