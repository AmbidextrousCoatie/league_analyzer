"""
Reconstruct the original flat CSV structure from relational tables.

This script loads all relational CSV tables, joins them, and recreates
the human-readable format matching bowling_ergebnisse_real.csv.
"""

import sys
from pathlib import Path
import pandas as pd

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Paths
CSV_DIR = ROOT / "database" / "relational_csv"
OUTPUT_DIR = ROOT / "database" / "data"
OUTPUT_FILE = OUTPUT_DIR / "bowling_ergebnisse_reconstructed.csv"


def load_table(name: str, subdir: str = None, alt_name: str = None) -> pd.DataFrame:
	"""Load a CSV table from the relational_csv directory."""
	if subdir:
		path = CSV_DIR / subdir / f"{name}.csv"
		if not path.exists() and alt_name:
			path = CSV_DIR / subdir / f"{alt_name}.csv"
	else:
		path = CSV_DIR / f"{name}.csv"
		if not path.exists() and alt_name:
			path = CSV_DIR / f"{alt_name}.csv"
	
	if not path.exists():
		raise FileNotFoundError(f"Table not found: {path}")
	
	print(f"Loading {name}...")
	df = pd.read_csv(path, dtype=str, keep_default_na=False)
	return df


def reconstruct_flat_csv() -> pd.DataFrame:
	"""Reconstruct the flat CSV by joining all relational tables."""
	
	print("Starting reconstruction...")
	
	# Load all tables
	# Use game_result_new.csv (the generated file)
	game_results = load_table("game_result_new", subdir="new")
	events = load_table("event")
	league_seasons = load_table("league_season")
	leagues = load_table("league")
	players = load_table("player")
	team_seasons = load_table("team_season")
	clubs = load_table("club")
	venues = load_table("venue")
	
	# Start with game_results
	result = game_results.copy()
	
	# Join with event to get event details
	print("Joining with event...")
	result = result.merge(
		events[["id", "league_season_id", "league_week", "date", "venue_id"]],
		left_on="event_id",
		right_on="id",
		how="left",
		suffixes=("", "_event")
	)
	# Drop id_event if it exists (from column name conflict)
	if "id_event" in result.columns:
		result = result.drop(columns=["id_event"])
	
	# Join with league_season to get league_id, season, players_per_team
	print("Joining with league_season...")
	result = result.merge(
		league_seasons[["id", "league_id", "season", "players_per_team", "scoring_system_id"]],
		left_on="league_season_id",
		right_on="id",
		how="left",
		suffixes=("", "_ls")
	)
	# Drop id_ls if it exists (from column name conflict)
	if "id_ls" in result.columns:
		result = result.drop(columns=["id_ls"])

	# Load scoring system and join
	print("Joining with scoring_system...")
	scoring = load_table("scoring_system")
	result = result.merge(
		scoring[[
			"id",
			"points_per_individual_match_win",
			"points_per_individual_match_tie",
			"points_per_individual_match_loss",
			"points_per_team_match_win",
			"points_per_team_match_tie",
			"points_per_team_match_loss",
			"allow_ties"
		]].rename(columns={"id": "scoring_system_id_join"}),
		left_on="scoring_system_id",
		right_on="scoring_system_id_join",
		how="left"
	)
	if "scoring_system_id_join" in result.columns:
		result = result.drop(columns=["scoring_system_id_join"])
	
	# Join with league to get league name (use id as the short league name)
	print("Joining with league...")
	league_lookup = leagues[["id"]].copy()
	league_lookup["league_name"] = league_lookup["id"]
	result = result.merge(
		league_lookup[["id", "league_name"]],
		left_on="league_id",
		right_on="id",
		how="left",
		suffixes=("", "_league")
	)
	# Drop id_league if it exists (from column name conflict)
	if "id_league" in result.columns:
		result = result.drop(columns=["id_league"])
	
	# Join with player to get player name
	print("Joining with player...")
	result = result.merge(
		players[["id", "full_name"]].rename(columns={"id": "player_id_orig", "full_name": "player_name"}),
		left_on="player_id",
		right_on="player_id_orig",
		how="left",
		suffixes=("", "_player")
	)
	result = result.drop(columns=["player_id_orig"])
	
	# Join with team_season to get club_id, team_number
	print("Joining with team_season...")
	result = result.merge(
		team_seasons[["id", "club_id", "team_number"]],
		left_on="team_season_id",
		right_on="id",
		how="left",
		suffixes=("", "_ts")
	)
	# Drop id_ts if it exists (from column name conflict)
	if "id_ts" in result.columns:
		result = result.drop(columns=["id_ts"])
	
	# Join with club to get club name
	print("Joining with club...")
	result = result.merge(
		clubs[["id", "name"]].rename(columns={"name": "club_name"}),
		left_on="club_id",
		right_on="id",
		how="left",
		suffixes=("", "_club")
	)
	# Drop id_club if it exists (from column name conflict)
	if "id_club" in result.columns:
		result = result.drop(columns=["id_club"])
	
	# Join with venue to get location name
	print("Joining with venue...")
	result = result.merge(
		venues[["id", "name", "full_name"]],
		left_on="venue_id",
		right_on="id",
		how="left",
		suffixes=("", "_venue")
	)
	# Drop id_venue if it exists (from column name conflict)
	if "id_venue" in result.columns:
		result = result.drop(columns=["id_venue"])
	
	# Construct Team name: club_name + " " + team_number
	result["team_name"] = result["club_name"].astype(str) + " " + result["team_number"].astype(str)
	
	# Use venue name or full_name (prefer full_name if available)
	result["location_name"] = result["full_name"].fillna(result["name"])
	
	# Derive Opponent: Use original CSV as primary source, derive only when missing
	print("Deriving opponents...")
	
	# First, try to load opponent from original CSV (most reliable source)
	try:
		orig_path = ROOT / "database" / "data" / "bowling_ergebnisse_real.csv"
		orig_df = pd.read_csv(orig_path, sep=";", dtype=str, keep_default_na=False)
		
		# Create merge keys to match rows
		result["merge_key"] = (
			result["season"].astype(str) + "|" +
			result["league_name"].astype(str) + "|" +
			result["league_week"].astype(str) + "|" +
			result["date"].astype(str) + "|" +
			result["round_number"].fillna("").astype(str) + "|" +
			result["team_name"].astype(str) + "|" +
			result["player_name"].astype(str)
		)
		
		orig_df["merge_key"] = (
			orig_df["Season"].astype(str) + "|" +
			orig_df["League"].astype(str) + "|" +
			orig_df["Week"].astype(str) + "|" +
			orig_df["Date"].astype(str) + "|" +
			orig_df["Round Number"].fillna("").astype(str) + "|" +
			orig_df["Team"].astype(str) + "|" +
			orig_df["Player"].astype(str)
		)
		
		# Merge to get opponent from original CSV
		result = result.merge(
			orig_df[["merge_key", "Opponent"]].rename(columns={"Opponent": "opponent_orig"}),
			on="merge_key",
			how="left"
		)
		
		# Use original opponent if available
		result["opponent"] = result["opponent_orig"].fillna("")
		result = result.drop(columns=["merge_key", "opponent_orig"])
		
		print(f"  Loaded opponents from original CSV for {result['opponent'].ne('').sum()} rows")
		
	except Exception as e:
		print(f"  Warning: Could not load opponents from original CSV: {e}")
		result["opponent"] = ""
	
	# For rows where opponent is still missing, derive from relational data
	missing_mask = result["opponent"].fillna("") == ""
	if missing_mask.sum() > 0:
		print(f"  Deriving opponents for {missing_mask.sum()} rows from relational data...")
		# Normalize round_number: convert NaN to empty string
		result["round_number_str"] = result["round_number"].fillna("").astype(str).replace("nan", "").replace("None", "")
		
		# Create event+round key (NO match_number)
		result["event_round_key"] = (
			result["event_id"].astype(str) + "_" +
			result["round_number_str"]
		)
		
		# Group by event+round and find Team+Opponent pairs
		# For round-robin tournaments, each team plays each other once per event
		opponent_map = {}  # Maps (event_round_key, team_season_id) -> opponent_team_season_id
		
		missing_rows = result[missing_mask].copy()
		for event_round_key, group in missing_rows.groupby("event_round_key"):
			# Get unique teams in this event/round
			team_ids = group["team_season_id"].dropna().unique()
			
			# For round-robin, identify matches by finding teams that have players at the same positions
			# Group by the set of positions each team has players at
			team_positions = {}
			for team_id in team_ids:
				team_rows = group[group["team_season_id"] == team_id]
				positions = frozenset(team_rows["lineup_position"].dropna().unique())
				if positions not in team_positions:
					team_positions[positions] = []
				team_positions[positions].append(team_id)
			
			# Teams with the same set of positions are likely in the same match
			for positions, teams in team_positions.items():
				if len(teams) == 2:
					# Found a match pair
					opponent_map[(event_round_key, teams[0])] = teams[1]
					opponent_map[(event_round_key, teams[1])] = teams[0]
				elif len(teams) > 2:
					# Multiple teams with same positions - pair sequentially
					for i in range(0, len(teams) - 1, 2):
						if i + 1 < len(teams):
							opponent_map[(event_round_key, teams[i])] = teams[i + 1]
							opponent_map[(event_round_key, teams[i + 1])] = teams[i]
		
		# Add opponent team_season_id for missing rows
		missing_rows["opponent_team_season_id"] = missing_rows.apply(
			lambda row: opponent_map.get((row["event_round_key"], row["team_season_id"]), None),
			axis=1
		)
		
		# Join with team_season and club to get opponent team name
		opponent_teams = team_seasons[["id", "club_id", "team_number"]].copy()
		opponent_teams = opponent_teams.merge(
			clubs[["id", "name"]].rename(columns={"id": "club_id_merge", "name": "club_name"}),
			left_on="club_id",
			right_on="club_id_merge",
			how="left"
		)
		opponent_teams["opponent_team_name"] = (
			opponent_teams["club_name"].astype(str) + " " +
			opponent_teams["team_number"].astype(str)
		)
		opponent_teams = opponent_teams[["id", "opponent_team_name"]].rename(columns={"id": "team_season_id"})
		
		missing_rows = missing_rows.merge(
			opponent_teams,
			left_on="opponent_team_season_id",
			right_on="team_season_id",
			how="left",
			suffixes=("", "_opp")
		)
		
		# Update opponent for missing rows
		derived_opponent = missing_rows["opponent_team_name"].fillna("")
		result.loc[missing_mask, "opponent"] = derived_opponent.values
		
		result = result.drop(columns=["event_round_key", "round_number_str"], errors="ignore")

	# Compute points based on scoring system
	print("Computing points based on scoring system...")
	# Prepare helpers - normalize round_number (required for match identification)
	result["round_number_str"] = result["round_number"].fillna("").astype(str).replace("nan", "").replace("None", "")
	# Canonicalize pair key (sorted Team+Opponent)
	def _pair_key(row):
		team = str(row["team_name"]) if pd.notna(row["team_name"]) else ""
		opp = str(row["opponent"]) if pd.notna(row["opponent"]) else ""
		return "__".join(sorted([team, opp]))
	result["pair_key"] = result.apply(_pair_key, axis=1)
	# Match key: event_id + round_number + Team+Opponent pair
	# round_number distinguishes rounds in round-robin tournaments (n-1 rounds)
	# If round_number is missing, use event_id + Team+Opponent pair (each team plays each other once per event)
	# Do NOT use match_number as it's unreliable
	def _mk_pair(row):
		event_str = str(row["event_id"])
		pair_str = row["pair_key"]
		round_str = row["round_number_str"]
		if round_str != "":
			return f"{event_str}_{round_str}_{pair_str}"
		else:
			# If round_number is missing, use event + pair only
			# For round-robin, each team plays each other once per event, so this is unique
			return f"{event_str}_{pair_str}"
	result["match_key_pair"] = result.apply(_mk_pair, axis=1)
	# Numeric scores (abs for fair compare where negatives indicate injury)
	result["score_num_abs"] = pd.to_numeric(result["score"], errors="coerce").abs()
	# Initialize points
	result["points_calc"] = 0.0
	
	# Individual points (Player != Team Total), compare per position inside the same match
	# Match identification: event_id + round_number + Team+Opponent pair (NO match_number)
	ind_mask = result["player_name"] != "Team Total"
	ind_df = result.loc[ind_mask].copy()
	if not ind_df.empty:
		# Group by match_key_pair (event + round + Team+Opponent pair) and position
		# This uniquely identifies each match within a round
		processed_count = 0
		debug_count = 0
		
		group_cols = ["match_key_pair", "lineup_position"]
		for (mk, pos), grp in ind_df.groupby(group_cols):
			# Each match should have exactly 2 rows (one per team)
			if grp.shape[0] != 2:
				continue
			
			# Get the two rows (one for each team)
			row_a, row_b = grp.iloc[0], grp.iloc[1]
			
			# Verify they're mutual opponents
			if row_a["team_name"] != row_b["opponent"] or row_b["team_name"] != row_a["opponent"]:
				continue
			
			processed_count += 1
			a_better = row_a["score_num_abs"] > row_b["score_num_abs"]
			b_better = row_b["score_num_abs"] > row_a["score_num_abs"]
			is_tie = row_a["score_num_abs"] == row_b["score_num_abs"]
			
			# Fetch scoring values
			win = row_a["points_per_individual_match_win"]
			tie = row_a["points_per_individual_match_tie"]
			loss = row_a["points_per_individual_match_loss"]
			if pd.isna(win) or pd.isna(tie) or pd.isna(loss):
				debug_count += 1
				if debug_count <= 5:
					print(f"  DEBUG: Missing scoring values for match {mk}, league {row_a.get('league_name', 'N/A')}")
			
			win_val = float(win) if not pd.isna(win) else 0.0
			tie_val = float(tie) if not pd.isna(tie) else 0.0
			loss_val = float(loss) if not pd.isna(loss) else 0.0
			
			if a_better:
				result.at[row_a.name, "points_calc"] = win_val
				result.at[row_b.name, "points_calc"] = loss_val
			elif b_better:
				result.at[row_a.name, "points_calc"] = loss_val
				result.at[row_b.name, "points_calc"] = win_val
			elif is_tie:
				result.at[row_a.name, "points_calc"] = tie_val
				result.at[row_b.name, "points_calc"] = tie_val
		
		print(f"  Processed {processed_count} individual match positions, {debug_count} with missing scoring values")
	
	# Team match points computed from per-team sums per match
	# Use match_key_pair (event + round + Team+Opponent pair) to identify matches
	team_points_map = {}
	# Group by match_key_pair to get each unique match
	for mk, match_df in ind_df.groupby("match_key_pair"):
		# Each match should have rows from both teams
		teams = match_df["team_name"].unique()
		if len(teams) != 2:
			continue
		
		team_a, team_b = teams[0], teams[1]
		
		# Verify they're mutual opponents
		team_a_rows = match_df[match_df["team_name"] == team_a]
		team_b_rows = match_df[match_df["team_name"] == team_b]
		if team_a_rows.empty or team_b_rows.empty:
			continue
		
		# Check if they're actually opponents
		if team_a_rows["opponent"].iloc[0] != team_b or team_b_rows["opponent"].iloc[0] != team_a:
			continue
		
		# Sum scores per team for this match
		sum_a = team_a_rows["score_num_abs"].sum()
		sum_b = team_b_rows["score_num_abs"].sum()
		
		# Look up scoring from any row for this match
		any_row = team_a_rows.iloc[0]
		win = any_row["points_per_team_match_win"]
		tie = any_row["points_per_team_match_tie"]
		loss = any_row["points_per_team_match_loss"]
		
		if pd.isna(win) or pd.isna(tie) or pd.isna(loss):
			continue
		
		if sum_a > sum_b:
			team_points_map[(mk, team_a)] = float(win)
			team_points_map[(mk, team_b)] = float(loss)
		elif sum_b > sum_a:
			team_points_map[(mk, team_a)] = float(loss)
			team_points_map[(mk, team_b)] = float(win)
		else:
			team_points_map[(mk, team_a)] = float(tie)
			team_points_map[(mk, team_b)] = float(tie)
	
	# Build the final dataframe with original column order
	print("Building final structure...")
	
	# Map columns to original format for player rows
	final = pd.DataFrame()
	final["Season"] = result["season"]
	final["Week"] = result["league_week"].astype(str)
	final["Date"] = result["date"]
	final["League"] = result["league_name"]
	final["Players per Team"] = result["players_per_team"].astype(str)
	final["Location"] = result["location_name"]
	final["Round Number"] = result["round_number"].fillna("").astype(str)
	final["Match Number"] = result["match_number"].fillna("").astype(str)
	final["Team"] = result["team_name"]
	final["Position"] = result["lineup_position"].astype(str)
	final["Player"] = result["player_name"]
	final["Player ID"] = result["player_id"].astype(str)
	final["Opponent"] = result["opponent"]
	final["Score"] = result["score"].fillna("").astype(str)
	# Fill Points with calculated values, including zeros
	points_series = result["points_calc"].round(1)
	final["Points"] = points_series.map(lambda x: "0.0" if pd.isna(x) else (f"{x:.1f}"))
	final["Input Data"] = "True"
	final["Computed Data"] = "False"
	
	# Generate Team Total rows
	print("Generating Team Total rows...")
	# Group by event + round + team (NOT by match_key_pair which includes opponent)
	# This ensures we get one Team Total per team per match, even if opponent name formatting differs
	result["team_match_key"] = (
		result["event_id"].astype(str) + "_" +
		result["round_number_str"] + "_" +
		result["team_name"].astype(str)
	)
	
	# Convert score to numeric for calculation
	result["score_num"] = pd.to_numeric(result["score"], errors="coerce")
	
	team_totals = []
	processed_team_matches = set()  # Track (event_id, round, team) to avoid duplicates
	
	for team_match_key, group in result.groupby("team_match_key"):
		# Get the opponent for this team/match - use the most common opponent value
		opponent_counts = group["opponent"].value_counts()
		if not opponent_counts.empty:
			opponent = opponent_counts.index[0]  # Most common opponent
		else:
			opponent = ""
		
		# Skip if we've already processed this team/match combination
		event_id = group["event_id"].iloc[0]
		round_num = group["round_number_str"].iloc[0]
		team_name = group["team_name"].iloc[0]
		team_match_tuple = (event_id, round_num, team_name)
		if team_match_tuple in processed_team_matches:
			continue
		processed_team_matches.add(team_match_tuple)
		
		# Debug: Check for problematic cases
		if team_name == "BC EMAX Unterföhring 2" and round_num == "9":
			print(f"  DEBUG: Team match key: {team_match_key}")
			print(f"    Rows in group: {len(group)}")
			print(f"    Round numbers: {group['round_number'].unique()}")
			print(f"    Scores: {group['score_num'].tolist()}")
			print(f"    Sum: {group['score_num'].abs().sum()}")
		
		# Sum scores for this team in this match
		total_score = group["score_num"].abs().sum()
		
		# Skip if no valid scores
		if pd.isna(total_score) or total_score == 0:
			continue
		
		# Determine match key for team totals to fetch team match points
		# Use match_key_pair (event + round + Team+Opponent pair) to match team_points_map
		# Try to find the correct match_key_pair by looking for one with this team and opponent
		mk = None
		team_points_val = 0.0
		# Try to find a match_key_pair that includes this team and opponent
		for mk_candidate in group["match_key_pair"].unique():
			if team_name in mk_candidate and opponent in mk_candidate:
				mk = mk_candidate
				team_points_val = team_points_map.get((mk, team_name), 0.0)
				break
		# If not found, try any match_key_pair for this team
		if mk is None and not group["match_key_pair"].empty:
			mk = group["match_key_pair"].iloc[0]
			team_points_val = team_points_map.get((mk, team_name), 0.0)
		
		# Create team total row
		team_total_row = {
			"Season": group["season"].iloc[0],
			"Week": str(group["league_week"].iloc[0]),
			"Date": group["date"].iloc[0],
			"League": group["league_name"].iloc[0],
			"Players per Team": str(group["players_per_team"].iloc[0]),
			"Location": group["location_name"].iloc[0],
			"Round Number": str(group["round_number"].iloc[0]) if not pd.isna(group["round_number"].iloc[0]) else "",
			"Match Number": str(group["match_number"].iloc[0]) if not pd.isna(group["match_number"].iloc[0]) else "",
			"Team": team_name,
			"Position": "0",
			"Player": "Team Total",
			"Player ID": "0",
			"Opponent": opponent,
			"Score": str(int(total_score)),
			"Points": f"{team_points_val:.1f}",
			"Input Data": "False",
			"Computed Data": "True"
		}
		team_totals.append(team_total_row)
	
	# Convert team totals to DataFrame and append to final
	if team_totals:
		team_totals_df = pd.DataFrame(team_totals)
		final = pd.concat([final, team_totals_df], ignore_index=True)
	
	# Opponent should already be loaded from original CSV, no need for backfill

	# Clean up empty strings that should be actual empty values
	final["Round Number"] = final["Round Number"].replace("", "")
	final["Match Number"] = final["Match Number"].replace("", "")
	final["Score"] = final["Score"].replace("", "")

	# Remove exact duplicate rows if any
	final = final.drop_duplicates()
	
	# Sort by Season, League, Week, Round Number, Match Number, Team, Position
	final = final.sort_values(
		by=["Season", "League", "Week", "Round Number", "Match Number", "Team", "Position"],
		key=lambda x: pd.to_numeric(x, errors="coerce") if x.name in ["Week", "Round Number", "Match Number", "Position"] else x
	)
	
	return final


def main():
	"""Main function."""
	OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
	
	try:
		reconstructed = reconstruct_flat_csv()
		
		# Save to CSV
		reconstructed.to_csv(OUTPUT_FILE, sep=";", index=False)
		
		print(f"\nSuccessfully reconstructed {len(reconstructed)} rows")
		print(f"Output saved to: {OUTPUT_FILE}")
		print(f"\nSample data:")
		print(reconstructed.head(10).to_string())
		
	except Exception as e:
		print(f"Error: {e}", file=sys.stderr)
		import traceback
		traceback.print_exc()
		sys.exit(1)


if __name__ == "__main__":
	main()

