"""
Check if the issues exist in the original input data:
1. Team total scores being wrong
2. Opponent data being wrong
"""

import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REAL_DATA = ROOT / "database" / "data" / "bowling_ergebnisse_real.csv"


def check_team_totals():
	"""Check if team totals in original data are correct."""
	print("="*60)
	print("CHECKING TEAM TOTALS IN ORIGINAL DATA")
	print("="*60)
	
	orig = pd.read_csv(REAL_DATA, sep=";", dtype=str)
	
	# Find the two problematic cases from the comparison
	problem_cases = [
		{"Season": "24/25", "League": "BayL", "Week": "2", "expected": "683", "got": "411"},
		{"Season": "24/25", "League": "BayL", "Week": "4", "expected": "640", "got": "326"},
	]
	
	for case in problem_cases:
		print(f"\n--- Checking: {case['Season']}, {case['League']}, Week {case['Week']} ---")
		
		# Find team total rows in original
		mask = (
			(orig["Season"] == case["Season"]) &
			(orig["League"] == case["League"]) &
			(orig["Week"] == case["Week"]) &
			(orig["Player"] == "Team Total")
		)
		team_totals = orig[mask].copy()
		
		print(f"Found {len(team_totals)} team total rows in original")
		
		# Check each team total
		for _, tt_row in team_totals.iterrows():
			# Find all player rows for this match
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
			calculated_total = players["Score_num"].abs().sum()
			reported_total = pd.to_numeric(tt_row["Score"], errors="coerce")
			
			if pd.isna(calculated_total):
				print(f"  [WARN] Match: Round {tt_row['Round Number']}, Match {tt_row['Match Number']}, Team {tt_row['Team']}")
				print(f"     Cannot calculate total (no valid player scores)")
				continue
			
			if abs(calculated_total - reported_total) > 0.1:  # Allow for floating point
				print(f"  [X] MISMATCH: Round {tt_row['Round Number']}, Match {tt_row['Match Number']}, Team {tt_row['Team']}")
				print(f"     Reported total: {reported_total}")
				print(f"     Calculated total: {calculated_total}")
				print(f"     Difference: {calculated_total - reported_total}")
				print(f"     Player scores: {players['Score'].tolist()}")
			else:
				print(f"  [OK] Match: Round {tt_row['Round Number']}, Match {tt_row['Match Number']}, Team {tt_row['Team']}")
				print(f"     Total: {reported_total} (matches calculated {calculated_total})")


def check_opponent_data():
	"""Check if opponent data in original data is correct."""
	print("\n" + "="*60)
	print("CHECKING OPPONENT DATA IN ORIGINAL DATA")
	print("="*60)
	
	orig = pd.read_csv(REAL_DATA, sep=";", dtype=str)
	
	# Focus on the problematic case: Season=25/26, League=BZL N2, Week=1
	print("\n--- Checking: Season=25/26, League=BZL N2, Week=1 ---")
	
	mask = (
		(orig["Season"] == "25/26") &
		(orig["League"] == "BZL N2") &
		(orig["Week"] == "1")
	)
	event_rows = orig[mask].copy()
	
	if event_rows.empty:
		print("  No rows found for this event")
		return
	
	print(f"Found {len(event_rows)} rows for this event")
	
	# Group by match (Round Number, Match Number) and check opponent consistency
	event_rows["match_key"] = (
		event_rows["Round Number"].fillna("").astype(str) + "_" +
		event_rows["Match Number"].fillna("").astype(str)
	)
	
	# Check each match
	matches_checked = 0
	matches_with_issues = 0
	
	for match_key, group in event_rows.groupby("match_key"):
		matches_checked += 1
		
		# Get unique teams in this match
		teams = group[group["Player"] != "Team Total"]["Team"].unique()
		opponents = group[group["Player"] != "Team Total"]["Opponent"].unique()
		
		# For each team, check if their opponent is consistent
		team_opponent_map = {}
		issues = []
		
		for team in teams:
			team_rows = group[group["Team"] == team]
			team_opponents = team_rows["Opponent"].unique()
			
			if len(team_opponents) > 1:
				issues.append(f"Team {team} has multiple opponents: {team_opponents.tolist()}")
			elif len(team_opponents) == 1:
				team_opponent_map[team] = team_opponents[0]
		
		# Check if teams are each other's opponents
		if len(teams) == 2:
			team1, team2 = teams
			opp1 = team_opponent_map.get(team1, "")
			opp2 = team_opponent_map.get(team2, "")
			
			if opp1 != team2 or opp2 != team1:
				issues.append(f"Teams {team1} and {team2} are not each other's opponents")
				issues.append(f"  {team1} -> {opp1} (expected {team2})")
				issues.append(f"  {team2} -> {opp2} (expected {team1})")
		
		if issues:
			matches_with_issues += 1
			print(f"\n  [X] Match {match_key} (Round {group['Round Number'].iloc[0]}, Match {group['Match Number'].iloc[0]}):")
			for issue in issues:
				print(f"     {issue}")
		else:
			print(f"  [OK] Match {match_key}: Teams {teams.tolist()} correctly paired")
	
	print(f"\nSummary: {matches_checked} matches checked, {matches_with_issues} with issues")
	
	# Also check the specific case mentioned in comparison output
	print("\n--- Checking specific problematic rows from comparison ---")
	# The comparison showed all opponents as "Albrecht Dürer 71 Stein 1"
	# Let's see what the original data says
	problem_rows = event_rows[
		(event_rows["Player"] != "Team Total") &
		(event_rows["Opponent"] == "Albrecht Dürer 71 Stein 1")
	]
	
	if not problem_rows.empty:
		print(f"Found {len(problem_rows)} rows with opponent 'Albrecht Dürer 71 Stein 1'")
		print("Sample teams and their opponents:")
		sample = problem_rows[["Team", "Opponent", "Round Number", "Match Number"]].drop_duplicates().head(10)
		for _, row in sample.iterrows():
			print(f"  Team: {row['Team']}, Opponent: {row['Opponent']}, Round: {row['Round Number']}, Match: {row['Match Number']}")
		
		# Check if this is correct
		teams_in_match = problem_rows["Team"].unique()
		print(f"\nTeams involved: {teams_in_match.tolist()}")
		print(f"All opponents are: {problem_rows['Opponent'].unique().tolist()}")


if __name__ == "__main__":
	check_team_totals()
	check_opponent_data()

