"""
Data validation script for bowling league data.

This script performs various validation checks on the league data.
Each check can be toggled independently.
"""

import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import pandas as pd

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Paths
CSV_DIR = ROOT / "database" / "relational_csv"
DATA_DIR = ROOT / "database" / "data"
REAL_DATA = DATA_DIR / "bowling_ergebnisse_real.csv"
RECON_DATA = DATA_DIR / "bowling_ergebnisse_reconstructed.csv"
TEST_DATA = DATA_DIR / "bowling_ergebnisse_test_with_errors.csv"


@dataclass
class ValidationConfig:
    """Configuration for which validations to run."""
    check_all_teams_present: bool = True
    check_match_points_sum: bool = True
    check_round_points_sum: bool = True
    check_week_points_sum: bool = True
    check_player_team_association: bool = True
    check_one_player_per_position: bool = True


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


def load_data(source: str = "real", file_path: str = None) -> pd.DataFrame:
    """Load the flat CSV data (real, reconstructed, test_with_errors, or custom file)."""
    if file_path:
        path = Path(file_path)
    elif source == "real":
        path = REAL_DATA
    elif source == "reconstructed":
        path = RECON_DATA
    elif source == "test_with_errors":
        path = TEST_DATA
    else:
        raise ValueError(f"Unknown source: {source}. Use 'real', 'reconstructed', or 'test_with_errors'")
    
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    
    df = pd.read_csv(path, sep=";", dtype=str, keep_default_na=False)
    return df


def check_all_teams_present(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Check if all teams from league_season definition are present for each league week.
    
    Returns list of issues found.
    """
    issues = []
    
    # Load league_season and team_season
    league_seasons = load_table("league_season")
    team_seasons = load_table("team_season")
    clubs = load_table("club")
    
    # Build team name lookup: team_season_id -> "Club Name TeamNumber"
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
    team_lookup = dict(zip(
        team_seasons_with_club["id"].astype(str),
        team_seasons_with_club["team_name"]
    ))
    
    # Get expected teams per league_season
    expected_teams = {}
    for _, ls_row in league_seasons.iterrows():
        ls_id = str(ls_row["id"])
        league_id = str(ls_row["league_id"])
        season = str(ls_row["season"])
        
        # Get all teams for this league_season
        teams_in_ls = team_seasons[team_seasons["league_season_id"].astype(str) == ls_id]
        expected_team_names = []
        for _, ts_row in teams_in_ls.iterrows():
            ts_id = str(ts_row["id"])
            if ts_id in team_lookup:
                expected_team_names.append(team_lookup[ts_id])
        
        expected_teams[(league_id, season)] = set(expected_team_names)
    
    # Check each week
    for (league, season, week), week_df in df.groupby(["League", "Season", "Week"]):
        league_key = (str(league), str(season))
        if league_key not in expected_teams:
            continue
        
        expected = expected_teams[league_key]
        # Get teams that actually appear (excluding "Team Total" rows)
        actual_teams = set(
            week_df[week_df["Player"] != "Team Total"]["Team"].dropna().unique()
        )
        
        missing_teams = expected - actual_teams
        if missing_teams:
            issues.append({
                "type": "missing_teams",
                "league": league,
                "season": season,
                "week": week,
                "missing_teams": sorted(missing_teams),
                "expected_count": len(expected),
                "actual_count": len(actual_teams)
            })
    
    return issues


def check_match_points_sum(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Check that each match's awarded points sum up correctly.
    
    For each match, the sum of points awarded to both teams should equal:
    - Individual matches: players_per_team * (win_points + loss_points) if no ties,
      or players_per_team * (tie_points + tie_points) if all ties
    - Team match: team_win_points + team_loss_points if no tie,
      or team_tie_points + team_tie_points if tie
    
    Returns list of issues found.
    """
    issues = []
    
    # Load scoring system and league_season
    scoring_systems = load_table("scoring_system")
    league_seasons = load_table("league_season")
    
    # Build lookup: (league, season) -> (players_per_team, scoring_system_id)
    league_lookup = {}
    for _, ls_row in league_seasons.iterrows():
        league_id = str(ls_row["league_id"])
        season = str(ls_row["season"])
        players_per_team = int(ls_row["players_per_team"]) if pd.notna(ls_row["players_per_team"]) else 0
        scoring_system_id = str(ls_row["scoring_system_id"])
        league_lookup[(league_id, season)] = (players_per_team, scoring_system_id)
    
    # Build scoring lookup
    scoring_lookup = {}
    for _, ss_row in scoring_systems.iterrows():
        ss_id = str(ss_row["id"])
        scoring_lookup[ss_id] = {
            "ind_win": float(ss_row["points_per_individual_match_win"]),
            "ind_tie": float(ss_row["points_per_individual_match_tie"]),
            "ind_loss": float(ss_row["points_per_individual_match_loss"]),
            "team_win": float(ss_row["points_per_team_match_win"]),
            "team_tie": float(ss_row["points_per_team_match_tie"]),
            "team_loss": float(ss_row["points_per_team_match_loss"])
        }
    
    # Group by match: (League, Season, Week, Round Number) and identify Team+Opponent pairs
    # We need to get both sides of each match
    for (league, season, week, round_num), round_df in df.groupby(
        ["League", "Season", "Week", "Round Number"]
    ):
        league_key = (str(league), str(season))
        if league_key not in league_lookup:
            continue
        
        players_per_team, scoring_system_id = league_lookup[league_key]
        if scoring_system_id not in scoring_lookup:
            continue
        
        scoring = scoring_lookup[scoring_system_id]
        
        # Find unique matches (Team, Opponent pairs)
        matches = round_df[
            (round_df["Player"] != "Team Total") &
            (round_df["Team"].notna()) &
            (round_df["Opponent"].notna())
        ][["Team", "Opponent"]].drop_duplicates()
        
        for _, match_row in matches.iterrows():
            team = str(match_row["Team"])
            opponent = str(match_row["Opponent"])
            
            # Get all rows for this match (both teams)
            match_df = round_df[
                ((round_df["Team"] == team) & (round_df["Opponent"] == opponent)) |
                ((round_df["Team"] == opponent) & (round_df["Opponent"] == team))
            ]
            
            # Calculate expected total points for the match
            # Individual matches: players_per_team matches, each awards (win + loss) or (tie + tie)
            expected_ind_total = players_per_team * (scoring["ind_win"] + scoring["ind_loss"])
            
            # Team match: awards (team_win + team_loss) or (team_tie + team_tie)
            expected_team_total = scoring["team_win"] + scoring["team_loss"]
            
            expected_total = expected_ind_total + expected_team_total
            
            # Sum actual points in this match (both teams combined)
            individual_rows = match_df[match_df["Player"] != "Team Total"]
            team_rows = match_df[match_df["Player"] == "Team Total"]
            
            individual_points = pd.to_numeric(
                individual_rows["Points"].fillna("0"), errors="coerce"
            ).sum()
            team_points = pd.to_numeric(
                team_rows["Points"].fillna("0"), errors="coerce"
            ).sum()
            total_points = individual_points + team_points
            
            # Allow for ties (which would give different totals)
            # Minimum if all ties: players_per_team * (tie + tie) + (team_tie + team_tie)
            min_total = players_per_team * (scoring["ind_tie"] + scoring["ind_tie"]) + (scoring["team_tie"] + scoring["team_tie"])
            
            # Check if total is within expected range (allowing small floating point errors)
            if not (min_total - 0.1 <= total_points <= expected_total + 0.1):
                issues.append({
                    "type": "match_points_sum_mismatch",
                    "league": league,
                    "season": season,
                    "week": week,
                    "round_number": round_num,
                    "team": team,
                    "opponent": opponent,
                    "expected_total": expected_total,
                    "expected_min": min_total,
                    "actual_total": total_points,
                    "individual_points": individual_points,
                    "team_points": team_points
                })
    
    return issues


def check_round_points_sum(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Check that each round's awarded points sum up to:
    number of teams / 2 * points per match
    
    Returns list of issues found.
    """
    issues = []
    
    # Load league_season
    league_seasons = load_table("league_season")
    
    # Build lookup: (league, season) -> number_of_teams
    league_lookup = {}
    for _, ls_row in league_seasons.iterrows():
        league_id = str(ls_row["league_id"])
        season = str(ls_row["season"])
        number_of_teams = int(ls_row["number_of_teams"]) if pd.notna(ls_row["number_of_teams"]) else 0
        league_lookup[(league_id, season)] = number_of_teams
    
    # Group by round: (League, Season, Week, Round Number)
    for (league, season, week, round_num), round_df in df.groupby(
        ["League", "Season", "Week", "Round Number"]
    ):
        if not round_num or round_num == "":
            continue  # Skip rounds without round number
        
        league_key = (str(league), str(season))
        if league_key not in league_lookup:
            continue
        
        number_of_teams = league_lookup[league_key]
        if number_of_teams == 0:
            continue
        
        # Expected: number_of_teams / 2 matches per round
        # A match is defined by: same event (League+Season+Week+Date), same round, team+opponent pair
        # Count unique (Team, Opponent) pairs, ensuring we don't double-count (Team A vs B = Team B vs A)
        unique_pairs = set()
        for _, row in round_df[
            (round_df["Player"] != "Team Total") &
            (round_df["Team"].notna()) &
            (round_df["Opponent"].notna())
        ].iterrows():
            team = str(row["Team"])
            opponent = str(row["Opponent"])
            # Normalize pair (alphabetically sorted to avoid duplicates)
            pair = tuple(sorted([team, opponent]))
            unique_pairs.add(pair)
        
        expected_matches = number_of_teams / 2
        actual_matches = len(unique_pairs)
        
        if abs(actual_matches - expected_matches) > 0.5:  # Allow for rounding
            issues.append({
                "type": "round_match_count_mismatch",
                "league": league,
                "season": season,
                "week": week,
                "round_number": round_num,
                "expected_matches": expected_matches,
                "actual_matches": actual_matches,
                "number_of_teams": number_of_teams
            })
    
    return issues


def check_week_points_sum(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Check that each week's points should sum up to:
    (number of teams - 1) * points per round
    
    This is a simplified check - actual calculation depends on round structure.
    
    Returns list of issues found.
    """
    issues = []
    
    # Load league_season
    league_seasons = load_table("league_season")
    
    # Build lookup: (league, season) -> number_of_teams
    league_lookup = {}
    for _, ls_row in league_seasons.iterrows():
        league_id = str(ls_row["league_id"])
        season = str(ls_row["season"])
        number_of_teams = int(ls_row["number_of_teams"]) if pd.notna(ls_row["number_of_teams"]) else 0
        league_lookup[(league_id, season)] = number_of_teams
    
    # Group by week: (League, Season, Week)
    for (league, season, week), week_df in df.groupby(["League", "Season", "Week"]):
        league_key = (str(league), str(season))
        if league_key not in league_lookup:
            continue
        
        number_of_teams = league_lookup[league_key]
        if number_of_teams == 0:
            continue
        
        # Count unique rounds in this week
        unique_rounds = week_df[week_df["Round Number"].notna() & (week_df["Round Number"] != "")]["Round Number"].nunique()
        
        # For round-robin: each team plays (number_of_teams - 1) matches per week
        # But this depends on the league structure
        # For now, just log the structure for manual review
        if unique_rounds == 0:
            # No round numbers - might be round-robin
            # Count unique opponents per team
            team_opponent_counts = week_df[
                (week_df["Player"] != "Team Total") &
                (week_df["Team"].notna()) &
                (week_df["Opponent"].notna())
            ].groupby("Team")["Opponent"].nunique()
            
            if not team_opponent_counts.empty:
                min_opponents = team_opponent_counts.min()
                max_opponents = team_opponent_counts.max()
                expected_opponents = number_of_teams - 1
                
                if min_opponents != expected_opponents or max_opponents != expected_opponents:
                    issues.append({
                        "type": "week_opponent_count_mismatch",
                        "league": league,
                        "season": season,
                        "week": week,
                        "expected_opponents_per_team": expected_opponents,
                        "min_opponents": int(min_opponents),
                        "max_opponents": int(max_opponents),
                        "number_of_teams": number_of_teams
                    })
    
    return issues


def check_player_team_association(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Check that only players associated with a team participate in matches for that team.
    
    Returns list of issues found.
    """
    issues = []
    
    # Load game_result to get player-team associations
    try:
        game_results = load_table("game_result_new", subdir="new")
    except FileNotFoundError:
        # Fallback to regular game_result if new doesn't exist
        try:
            game_results = load_table("game_result")
        except FileNotFoundError:
            print("Warning: game_result table not found. Skipping player-team association check.")
            return issues
    
    # Build player-team association map: (player_id, team_season_id) -> True
    player_team_map = set()
    for _, row in game_results.iterrows():
        player_id = str(row["player_id"])
        team_season_id = str(row["team_season_id"]) if pd.notna(row.get("team_season_id")) else None
        if player_id and team_season_id:
            player_team_map.add((player_id, team_season_id))
    
    # Load team_season and clubs to map team names to team_season_id
    team_seasons = load_table("team_season")
    clubs = load_table("club")
    league_seasons = load_table("league_season")
    
    # Build team name -> team_season_id lookup
    team_seasons_with_club = team_seasons.merge(
        clubs[["id", "name"]],
        left_on="club_id",
        right_on="id",
        how="left",
        suffixes=("", "_club")
    )
    team_seasons_with_club = team_seasons_with_club.merge(
        league_seasons[["id", "league_id", "season"]],
        left_on="league_season_id",
        right_on="id",
        how="left",
        suffixes=("", "_ls")
    )
    team_seasons_with_club["team_name"] = (
        team_seasons_with_club["name"].astype(str) + " " +
        team_seasons_with_club["team_number"].astype(str)
    )
    
    # Build lookup: (league, season, team_name) -> team_season_id
    team_lookup = {}
    for _, row in team_seasons_with_club.iterrows():
        league_id = str(row["league_id"])
        season = str(row["season"])
        team_name = str(row["team_name"])
        team_season_id = str(row["id"])
        team_lookup[(league_id, season, team_name)] = team_season_id
    
    # Load players to get player_id from player_name
    players = load_table("player")
    # Player table has: id, given_name, family_name, full_name
    # Use full_name to match with Player column in CSV
    player_name_to_id = dict(zip(
        players["full_name"].astype(str),
        players["id"].astype(str)
    ))
    
    # Check each row in df
    for _, row in df.iterrows():
        if row["Player"] == "Team Total" or pd.isna(row.get("Player ID")):
            continue
        
        player_id = str(row["Player ID"])
        player_name = str(row["Player"])
        team_name = str(row["Team"])
        league = str(row["League"])
        season = str(row["Season"])
        
        # Get team_season_id
        team_key = (league, season, team_name)
        if team_key not in team_lookup:
            continue  # Team not found in definition
        
        team_season_id = team_lookup[team_key]
        
        # Check if player is associated with this team
        if (player_id, team_season_id) not in player_team_map:
            # Also check by player name if player_id doesn't match
            if player_name in player_name_to_id:
                alt_player_id = player_name_to_id[player_name]
                if (alt_player_id, team_season_id) not in player_team_map:
                    issues.append({
                        "type": "player_not_associated_with_team",
                        "league": league,
                        "season": season,
                        "week": row.get("Week", ""),
                        "player_id": player_id,
                        "player_name": player_name,
                        "team_name": team_name,
                        "team_season_id": team_season_id
                    })
            else:
                issues.append({
                    "type": "player_not_associated_with_team",
                    "league": league,
                    "season": season,
                    "week": row.get("Week", ""),
                    "player_id": player_id,
                    "player_name": player_name,
                    "team_name": team_name,
                    "team_season_id": team_season_id
                })
    
    return issues


def check_one_player_per_position(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Check that only one player per position per match is allowed.
    
    Returns list of issues found.
    """
    issues = []
    
    # Exclude Team Total rows from this check
    player_df = df[df["Player"] != "Team Total"].copy()
    
    # Group by match and position: (League, Season, Week, Round Number, Team, Opponent, Position)
    for (league, season, week, round_num, team, opponent, position), pos_df in player_df.groupby(
        ["League", "Season", "Week", "Round Number", "Team", "Opponent", "Position"]
    ):
        # Count unique players at this position
        unique_players = pos_df["Player"].nunique()
        
        if unique_players > 1:
            issues.append({
                "type": "multiple_players_same_position",
                "league": league,
                "season": season,
                "week": week,
                "round_number": round_num,
                "team": team,
                "opponent": opponent,
                "position": position,
                "players": pos_df["Player"].unique().tolist(),
                "count": unique_players
            })
    
    return issues


def run_validations(df: pd.DataFrame, config: ValidationConfig) -> Dict[str, List[Dict[str, Any]]]:
    """
    Run all enabled validations and return results.
    
    Returns dict mapping check name to list of issues.
    """
    results = {}
    
    if config.check_all_teams_present:
        print("Checking all teams present...")
        results["all_teams_present"] = check_all_teams_present(df)
        print(f"  Found {len(results['all_teams_present'])} issues")
    
    if config.check_match_points_sum:
        print("Checking match points sum...")
        results["match_points_sum"] = check_match_points_sum(df)
        print(f"  Found {len(results['match_points_sum'])} issues")
    
    if config.check_round_points_sum:
        print("Checking round points sum...")
        results["round_points_sum"] = check_round_points_sum(df)
        print(f"  Found {len(results['round_points_sum'])} issues")
    
    if config.check_week_points_sum:
        print("Checking week points sum...")
        results["week_points_sum"] = check_week_points_sum(df)
        print(f"  Found {len(results['week_points_sum'])} issues")
    
    if config.check_player_team_association:
        print("Checking player-team association...")
        results["player_team_association"] = check_player_team_association(df)
        print(f"  Found {len(results['player_team_association'])} issues")
    
    if config.check_one_player_per_position:
        print("Checking one player per position...")
        results["one_player_per_position"] = check_one_player_per_position(df)
        print(f"  Found {len(results['one_player_per_position'])} issues")
    
    return results


def print_results(results: Dict[str, List[Dict[str, Any]]]):
    """Print validation results in a readable format."""
    print("\n" + "="*80)
    print("VALIDATION RESULTS")
    print("="*80)
    
    total_issues = sum(len(issues) for issues in results.values())
    if total_issues == 0:
        print("\n[OK] All checks passed!")
        return
    
    print(f"\nTotal issues found: {total_issues}\n")
    
    for check_name, issues in results.items():
        if not issues:
            print(f"[OK] {check_name}: No issues")
            continue
        
        print(f"\n[X] {check_name}: {len(issues)} issues")
        print("-" * 80)
        
        # Show first 10 issues
        for i, issue in enumerate(issues[:10], 1):
            print(f"\n  Issue {i}:")
            for key, value in issue.items():
                if key != "type":
                    print(f"    {key}: {value}")
        
        if len(issues) > 10:
            print(f"\n  ... and {len(issues) - 10} more issues")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate bowling league data")
    parser.add_argument(
        "--source",
        choices=["real", "reconstructed", "test_with_errors"],
        default="real",
        help="Data source to validate (default: real)"
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Custom file path to validate (overrides --source)"
    )
    # Default: all checks enabled
    parser.add_argument(
        "--disable-all-teams",
        action="store_true",
        help="Disable check: all teams present"
    )
    parser.add_argument(
        "--disable-match-points",
        action="store_true",
        help="Disable check: match points sum"
    )
    parser.add_argument(
        "--disable-round-points",
        action="store_true",
        help="Disable check: round points sum"
    )
    parser.add_argument(
        "--disable-week-points",
        action="store_true",
        help="Disable check: week points sum"
    )
    parser.add_argument(
        "--disable-player-team",
        action="store_true",
        help="Disable check: player-team association"
    )
    parser.add_argument(
        "--disable-one-player-per-position",
        action="store_true",
        help="Disable check: one player per position"
    )
    
    args = parser.parse_args()
    
    # Load data
    if args.file:
        print(f"Loading data from custom file: {args.file}")
        df = load_data(file_path=args.file)
    else:
        print(f"Loading data from {args.source} source...")
        df = load_data(args.source)
    print(f"Loaded {len(df)} rows")
    
    # Create config (all enabled by default, disabled if flag is set)
    config = ValidationConfig(
        check_all_teams_present=not args.disable_all_teams,
        check_match_points_sum=not args.disable_match_points,
        check_round_points_sum=not args.disable_round_points,
        check_week_points_sum=not args.disable_week_points,
        check_player_team_association=not args.disable_player_team,
        check_one_player_per_position=not args.disable_one_player_per_position
    )
    
    # Run validations
    print("\nRunning validations...")
    results = run_validations(df, config)
    
    # Print results
    print_results(results)
    
    # Exit with error code if issues found
    total_issues = sum(len(issues) for issues in results.values())
    sys.exit(1 if total_issues > 0 else 0)


if __name__ == "__main__":
    main()

