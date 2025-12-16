"""
Investigate the two issues:
1. Team total scores being wrong
2. Opponent data being wrong (match_number issue)
"""

import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REAL_DATA = ROOT / "database" / "data" / "bowling_ergebnisse_real.csv"
RECONSTRUCTED = ROOT / "database" / "data" / "bowling_ergebnisse_reconstructed.csv"
GAME_RESULT = ROOT / "database" / "relational_csv" / "new" / "game_result_new.csv"


def investigate_team_totals():
	"""Investigate why team totals are wrong."""
	print("="*60)
	print("INVESTIGATING TEAM TOTAL ISSUES")
	print("="*60)
	
	# Load original data
	orig = pd.read_csv(REAL_DATA, sep=";", dtype=str)
	
	# Find the two problematic team totals
	# Week 2: 683 vs 411
	# Week 4: 640 vs 326
	problem_cases = [
		{"Season": "24/25", "League": "BayL", "Week": "2", "expected": "683"},
		{"Season": "24/25", "League": "BayL", "Week": "4", "expected": "640"},
	]
	
	for case in problem_cases:
		print(f"\n--- Investigating: {case['Season']}, {case['League']}, Week {case['Week']} ---")
		
		# Find team total rows in original
		mask = (
			(orig["Season"] == case["Season"]) &
			(orig["League"] == case["League"]) &
			(orig["Week"] == case["Week"]) &
			(orig["Player"] == "Team Total")
		)
		team_totals = orig[mask].copy()
		
		print(f"Found {len(team_totals)} team total rows in original:")
		for _, row in team_totals.iterrows():
			print(f"  Round {row['Round Number']}, Match {row['Match Number']}, Team {row['Team']}, Opponent {row['Opponent']}, Score {row['Score']}")
		
		# Find all player rows for these matches to calculate expected totals
		for _, tt_row in team_totals.iterrows():
			player_mask = (
				(orig["Season"] == tt_row["Season"]) &
				(orig["League"] == tt_row["League"]) &
				(orig["Week"] == tt_row["Week"]) &
				(orig["Round Number"] == tt_row["Round Number"]) &
				(orig["Match Number"] == tt_row["Match Number"]) &
				(orig["Team"] == tt_row["Team"]) &
				(orig["Player"] != "Team Total")
			)
			players = orig[player_mask].copy()
			players["Score_num"] = pd.to_numeric(players["Score"], errors="coerce")
			calculated_total = players["Score_num"].sum()
			print(f"\n  Match: Round {tt_row['Round Number']}, Match {tt_row['Match Number']}, Team {tt_row['Team']}")
			print(f"    Expected total: {tt_row['Score']} (from Team Total row)")
			print(f"    Calculated total: {calculated_total} (sum of {len(players)} player scores)")
			print(f"    Player scores: {players['Score'].tolist()}")


def investigate_opponent_matching():
	"""Investigate why opponent matching is wrong."""
	print("\n" + "="*60)
	print("INVESTIGATING OPPONENT MATCHING ISSUES")
	print("="*60)
	
	# Load game_result data
	game_results = pd.read_csv(GAME_RESULT, dtype=str)
	
	# Load events to get event details
	events = pd.read_csv(ROOT / "database" / "relational_csv" / "event.csv", dtype=str)
	league_seasons = pd.read_csv(ROOT / "database" / "relational_csv" / "league_season.csv", dtype=str)
	
	# Join to get event context
	game_results = game_results.merge(
		events[["id", "league_season_id", "league_week", "date"]].rename(columns={"id": "event_id_join"}),
		left_on="event_id",
		right_on="event_id_join",
		how="left"
	)
	game_results = game_results.merge(
		league_seasons[["id", "league_id", "season"]].rename(columns={"id": "league_season_id_join"}),
		left_on="league_season_id",
		right_on="league_season_id_join",
		how="left"
	)
	
	# Focus on the problematic case: Season=25/26, League=BZL N2, Week=1
	print("\n--- Investigating: Season=25/26, League=BZL N2, Week=1 ---")
	
	# Find all rows for this event
	mask = (
		(game_results["season"] == "25/26") &
		(game_results["league_id"] == "BZL N2") &
		(game_results["league_week"] == "1")
	)
	event_rows = game_results[mask].copy()
	
	if event_rows.empty:
		print("  No rows found for this event in game_result")
		return
	
	print(f"Found {len(event_rows)} rows for this event")
	
	# Group by match_key (event_id, round_number, match_number)
	event_rows["match_key"] = (
		event_rows["event_id"].astype(str) + "_" +
		event_rows["round_number"].fillna("").astype(str) + "_" +
		event_rows["match_number"].fillna("").astype(str)
	)
	
	print(f"\nUnique match_keys: {event_rows['match_key'].nunique()}")
	print(f"Unique team_season_ids: {event_rows['team_season_id'].nunique()}")
	
	# Show grouping by match_key
	for match_key, group in event_rows.groupby("match_key"):
		team_ids = group["team_season_id"].dropna().unique()
		print(f"\n  Match key: {match_key}")
		print(f"    Teams in match: {len(team_ids)}")
		print(f"    Team IDs: {team_ids.tolist()}")
		print(f"    Rows: {len(group)}")
		
		# Show round_number and match_number distribution
		rounds = group["round_number"].unique()
		matches = group["match_number"].unique()
		print(f"    Round numbers: {rounds.tolist()}")
		print(f"    Match numbers: {matches.tolist()}")
		
		if len(team_ids) != 2:
			print(f"    ⚠️  WARNING: Expected 2 teams, found {len(team_ids)}")
	
	# Check if match_number is consistent within a match
	print("\n--- Checking match_number consistency ---")
	for match_key, group in event_rows.groupby("match_key"):
		match_nums = group["match_number"].dropna().unique()
		if len(match_nums) > 1:
			print(f"  Match key {match_key}: Multiple match_numbers {match_nums.tolist()}")
	
	# Check original data for comparison
	orig = pd.read_csv(REAL_DATA, sep=";", dtype=str)
	orig_mask = (
		(orig["Season"] == "25/26") &
		(orig["League"] == "BZL N2") &
		(orig["Week"] == "1")
	)
	orig_rows = orig[orig_mask].copy()
	
	print(f"\nOriginal CSV has {len(orig_rows)} rows for this event")
	print(f"Unique Round Numbers: {orig_rows['Round Number'].unique().tolist()}")
	print(f"Unique Match Numbers: {orig_rows['Match Number'].unique().tolist()}")
	print(f"Unique Teams: {orig_rows['Team'].nunique()}")
	
	# Show sample of original data
	print("\nSample original rows (first 10):")
	for _, row in orig_rows.head(10).iterrows():
		print(f"  Round {row['Round Number']}, Match {row['Match Number']}, Team {row['Team']}, Opponent {row['Opponent']}")


if __name__ == "__main__":
	investigate_team_totals()
	investigate_opponent_matching()

