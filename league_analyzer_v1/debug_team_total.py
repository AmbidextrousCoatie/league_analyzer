import pandas as pd
from pathlib import Path

# Load the relational data to see what's happening
ROOT = Path(__file__).resolve().parents[0]
game_results = pd.read_csv(ROOT / "database" / "relational_csv" / "new" / "game_result_new.csv", dtype=str)
events = pd.read_csv(ROOT / "database" / "relational_csv" / "event.csv", dtype=str)
league_seasons = pd.read_csv(ROOT / "database" / "relational_csv" / "league_season.csv", dtype=str)
leagues = pd.read_csv(ROOT / "database" / "relational_csv" / "league.csv", dtype=str)
team_seasons = pd.read_csv(ROOT / "database" / "relational_csv" / "team_season.csv", dtype=str)
clubs = pd.read_csv(ROOT / "database" / "relational_csv" / "club.csv", dtype=str)
players = pd.read_csv(ROOT / "database" / "relational_csv" / "player.csv", dtype=str)

# Join to get the data
result = game_results.copy()
result = result.merge(events[["id", "league_season_id", "league_week", "date"]], left_on="event_id", right_on="id", how="left", suffixes=("", "_event"))
result = result.merge(league_seasons[["id", "league_id", "season"]], left_on="league_season_id", right_on="id", how="left", suffixes=("", "_ls"))
result = result.merge(leagues[["id"]].rename(columns={"id": "league_name"}), left_on="league_id", right_on="league_name", how="left")
result = result.merge(team_seasons[["id", "club_id", "team_number"]], left_on="team_season_id", right_on="id", how="left", suffixes=("", "_ts"))
result = result.merge(clubs[["id", "name"]], left_on="club_id", right_on="id", how="left", suffixes=("", "_club"))
result["team_name"] = result["name"].astype(str) + " " + result["team_number"].astype(str)

# Filter for the problematic match
mask = (result["season"] == "25/26") & (result["league_name"] == "BayL") & (result["league_week"] == "2")
result_filtered = result[mask].copy()

# Check round_number values
print("Round numbers for BayL Week 2:")
print(result_filtered["round_number"].value_counts().sort_index())

# Check BC EMAX Unterföhring 2 specifically
emax_mask = result_filtered["team_name"] == "BC EMAX Unterföhring 2"
emax_data = result_filtered[emax_mask].copy()
print(f"\nBC EMAX Unterföhring 2 rows: {len(emax_data)}")
print("\nBy round_number:")
for rnd in sorted(emax_data["round_number"].dropna().unique()):
    rnd_data = emax_data[emax_data["round_number"] == rnd]
    print(f"Round {rnd}: {len(rnd_data)} rows, event_ids: {rnd_data['event_id'].unique()}")

# Check if there are multiple events
print(f"\nUnique event_ids for BayL Week 2: {result_filtered['event_id'].nunique()}")
print(f"Event IDs: {result_filtered['event_id'].unique()}")

