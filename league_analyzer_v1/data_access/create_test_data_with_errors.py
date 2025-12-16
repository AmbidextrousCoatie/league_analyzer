"""
Create a test CSV file with errors of all validation categories.

This script takes the real data and introduces intentional errors
to test the validation script.
"""

import sys
from pathlib import Path
import pandas as pd

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Paths
DATA_DIR = ROOT / "database" / "data"
REAL_DATA = DATA_DIR / "bowling_ergebnisse_real.csv"
TEST_DATA = DATA_DIR / "bowling_ergebnisse_test_with_errors.csv"
CSV_DIR = ROOT / "database" / "relational_csv"


def load_table(name: str, subdir: str = None) -> pd.DataFrame:
    """Load a CSV table from the relational_csv directory."""
    if subdir:
        path = CSV_DIR / subdir / f"{name}.csv"
    else:
        path = CSV_DIR / f"{name}.csv"
    
    if not path.exists():
        raise FileNotFoundError(f"Table not found: {path}")
    
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    return df


def create_test_data_with_errors():
    """Create a test CSV with errors of all categories."""
    
    print("Loading real data...")
    df = pd.read_csv(REAL_DATA, sep=";", dtype=str, keep_default_na=False)
    print(f"Loaded {len(df)} rows")
    
    # Make a copy to modify
    test_df = df.copy()
    
    print("\nIntroducing errors...")
    
    # ============================================================================
    # ERROR 1: Missing team in a week
    # Remove all rows for a specific team in a specific week
    # ============================================================================
    print("  [1] Missing team error: Removing a team from one week...")
    league_seasons = load_table("league_season")
    team_seasons = load_table("team_season")
    clubs = load_table("club")
    
    # Find a league_season with teams
    test_league_season = league_seasons.iloc[0]
    league_id = str(test_league_season["league_id"])
    season = str(test_league_season["season"])
    
    # Get teams for this league_season
    teams_in_ls = team_seasons[team_seasons["league_season_id"].astype(str) == str(test_league_season["id"])]
    teams_in_ls = teams_in_ls.merge(
        clubs[["id", "name"]],
        left_on="club_id",
        right_on="id",
        how="left"
    )
    teams_in_ls["team_name"] = (
        teams_in_ls["name"].astype(str) + " " +
        teams_in_ls["team_number"].astype(str)
    )
    
    if not teams_in_ls.empty:
        # Find a week with this team
        test_team = teams_in_ls.iloc[0]["team_name"]
        team_rows = test_df[
            (test_df["League"] == league_id) &
            (test_df["Season"] == season) &
            (test_df["Team"] == test_team)
        ]
        
        if not team_rows.empty:
            # Get the first week this team appears
            first_week = team_rows["Week"].iloc[0]
            # Remove all rows for this team in this week
            mask = (
                (test_df["League"] == league_id) &
                (test_df["Season"] == season) &
                (test_df["Week"] == first_week) &
                (test_df["Team"] == test_team)
            )
            removed_count = mask.sum()
            test_df = test_df[~mask]
            print(f"      Removed {removed_count} rows for team '{test_team}' in {league_id} {season} Week {first_week}")
    
    # ============================================================================
    # ERROR 2: Match points sum mismatch
    # Change points so they don't add up correctly
    # ============================================================================
    print("  [2] Match points sum error: Incorrectly calculating match points...")
    # Find a match (Team, Opponent, Round Number)
    match_rows = test_df[
        (test_df["Player"] != "Team Total") &
        (test_df["Team"].notna()) &
        (test_df["Opponent"].notna()) &
        (test_df["Round Number"].notna()) &
        (test_df["Round Number"] != "")
    ]
    
    if not match_rows.empty:
        # Get first match
        first_match = match_rows.iloc[0]
        league = str(first_match["League"])
        season = str(first_match["Season"])
        week = str(first_match["Week"])
        round_num = str(first_match["Round Number"])
        team = str(first_match["Team"])
        opponent = str(first_match["Opponent"])
        
        # Find all rows for this match
        match_mask = (
            (test_df["League"] == league) &
            (test_df["Season"] == season) &
            (test_df["Week"] == week) &
            (test_df["Round Number"] == round_num) &
            (
                ((test_df["Team"] == team) & (test_df["Opponent"] == opponent)) |
                ((test_df["Team"] == opponent) & (test_df["Opponent"] == team))
            )
        )
        
        # Add extra points to one player to break the sum
        player_rows = test_df[match_mask & (test_df["Player"] != "Team Total")]
        if not player_rows.empty:
            idx = player_rows.index[0]
            current_points = pd.to_numeric(test_df.at[idx, "Points"], errors="coerce") or 0.0
            test_df.at[idx, "Points"] = str(current_points + 10.0)  # Add 10 extra points
            print(f"      Added 10 extra points to player in {league} {season} Week {week} Round {round_num}, {team} vs {opponent}")
    
    # ============================================================================
    # ERROR 3: Round points sum mismatch (wrong number of matches)
    # Remove one match from a round
    # ============================================================================
    print("  [3] Round points sum error: Removing a match from a round...")
    # Find a round with multiple matches
    round_groups = test_df[
        (test_df["Player"] != "Team Total") &
        (test_df["Round Number"].notna()) &
        (test_df["Round Number"] != "")
    ].groupby(["League", "Season", "Week", "Round Number"])
    
    for (league, season, week, round_num), round_df in round_groups:
        matches = round_df[
            (round_df["Team"].notna()) &
            (round_df["Opponent"].notna())
        ][["Team", "Opponent"]].drop_duplicates()
        
        if len(matches) > 1:  # Need at least 2 matches to remove one
            # Remove first match
            match_to_remove = matches.iloc[0]
            team = str(match_to_remove["Team"])
            opponent = str(match_to_remove["Opponent"])
            
            mask = (
                (test_df["League"] == league) &
                (test_df["Season"] == season) &
                (test_df["Week"] == week) &
                (test_df["Round Number"] == round_num) &
                (
                    ((test_df["Team"] == team) & (test_df["Opponent"] == opponent)) |
                    ((test_df["Team"] == opponent) & (test_df["Opponent"] == team))
                )
            )
            removed_count = mask.sum()
            test_df = test_df[~mask]
            print(f"      Removed {removed_count} rows (one match) from {league} {season} Week {week} Round {round_num}")
            break
    
    # ============================================================================
    # ERROR 4: Week points sum mismatch (wrong number of opponents)
    # Remove one opponent for a team in a week
    # ============================================================================
    print("  [4] Week points sum error: Removing an opponent for a team...")
    # Find a week with a team that has multiple opponents
    week_groups = test_df[
        (test_df["Player"] != "Team Total") &
        (test_df["Team"].notna()) &
        (test_df["Opponent"].notna())
    ].groupby(["League", "Season", "Week", "Team"])
    
    for (league, season, week, team), team_week_df in week_groups:
        opponents = team_week_df["Opponent"].unique()
        if len(opponents) > 1:  # Need at least 2 opponents
            # Remove all rows for one opponent
            opponent_to_remove = opponents[0]
            mask = (
                (test_df["League"] == league) &
                (test_df["Season"] == season) &
                (test_df["Week"] == week) &
                (test_df["Team"] == team) &
                (test_df["Opponent"] == opponent_to_remove)
            )
            removed_count = mask.sum()
            test_df = test_df[~mask]
            print(f"      Removed {removed_count} rows (opponent '{opponent_to_remove}') for team '{team}' in {league} {season} Week {week}")
            break
    
    # ============================================================================
    # ERROR 5: Player not associated with team
    # Change a player ID to one that doesn't belong to that team
    # ============================================================================
    print("  [5] Player-team association error: Using wrong player ID...")
    # Load game_result to see player-team associations
    try:
        game_results = load_table("game_result_new", subdir="new")
    except FileNotFoundError:
        try:
            game_results = load_table("game_result")
        except FileNotFoundError:
            game_results = None
    
    if game_results is not None:
        # Get a player-team pair
        player_rows = test_df[
            (test_df["Player"] != "Team Total") &
            (test_df["Player ID"].notna()) &
            (test_df["Player ID"] != "0")
        ]
        
        if not player_rows.empty:
            # Get all unique player IDs
            all_player_ids = game_results["player_id"].unique()
            
            # Find a row to modify
            row_to_modify = player_rows.iloc[0]
            original_player_id = str(row_to_modify["Player ID"])
            original_team = str(row_to_modify["Team"])
            
            # Find a player ID that's NOT associated with this team
            team_season_id = None
            # Try to find team_season_id for this team
            # team_seasons has columns: id, league_season_id, club_id, team_number
            # clubs has columns: id, name, short_name
            # After merge, team_seasons.id is the team_season_id we want
            team_seasons_with_club = team_seasons.merge(
                clubs[["id", "name"]],
                left_on="club_id",
                right_on="id",
                how="left",
                suffixes=("", "_club")
            )
            team_seasons_with_club["team_name"] = (
                team_seasons_with_club["name"].astype(str) + " " +
                team_seasons_with_club["team_number"].astype(str)
            )
            
            team_row = team_seasons_with_club[team_seasons_with_club["team_name"] == original_team]
            if not team_row.empty:
                # The "id" column from team_seasons (before merge) is the team_season_id
                # After merge with suffixes, it should still be "id"
                team_season_id = str(team_row.iloc[0]["id"])
            
            # Find a player ID that's not associated with this team_season_id
            if team_season_id:
                players_for_team = set(
                    game_results[game_results["team_season_id"].astype(str) == team_season_id]["player_id"].astype(str)
                )
                wrong_player_ids = [pid for pid in all_player_ids if str(pid) not in players_for_team]
                
                if wrong_player_ids:
                    idx = row_to_modify.name
                    test_df.at[idx, "Player ID"] = str(wrong_player_ids[0])
                    print(f"      Changed Player ID from {original_player_id} to {wrong_player_ids[0]} for team '{original_team}'")
    
    # ============================================================================
    # ERROR 6: Multiple players same position
    # Duplicate a player at the same position in a match
    # ============================================================================
    print("  [6] Multiple players same position error: Duplicating a player...")
    # Find a match with a player
    player_rows = test_df[
        (test_df["Player"] != "Team Total") &
        (test_df["Position"].notna()) &
        (test_df["Team"].notna()) &
        (test_df["Opponent"].notna())
    ]
    
    if not player_rows.empty:
        # Get first player row
        first_row = player_rows.iloc[0]
        
        # Create a duplicate row with a different player name but same position
        new_row = first_row.copy()
        new_row["Player"] = "Duplicate Player, Test"  # Different player name
        new_row["Player ID"] = "99999"  # Fake player ID
        new_row["Score"] = "150"  # Different score
        
        # Insert the duplicate row
        test_df = pd.concat([test_df, pd.DataFrame([new_row])], ignore_index=True)
        print(f"      Added duplicate player at position {first_row['Position']} in {first_row['League']} {first_row['Season']} Week {first_row['Week']} Round {first_row['Round Number']}")
    
    # ============================================================================
    # Save the test file
    # ============================================================================
    print(f"\nSaving test data to {TEST_DATA}...")
    test_df.to_csv(TEST_DATA, sep=";", index=False)
    print(f"Saved {len(test_df)} rows (removed {len(df) - len(test_df)} rows for errors)")
    print(f"\nTest file created: {TEST_DATA}")
    print("\nYou can now test the validation script with:")
    print(f"  python data_access/validate_data.py --source test_with_errors")


if __name__ == "__main__":
    create_test_data_with_errors()

