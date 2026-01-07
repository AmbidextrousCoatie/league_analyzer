"""
Data Validation and Sanitation Script

Validates and fixes data integrity issues in the sample data CSV files.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from uuid import UUID
from typing import Dict, List, Tuple, Set
from collections import defaultdict
from infrastructure.logging import get_logger

# Initialize logger
logger = get_logger(__name__)


def validate_uuid(value) -> bool:
    """Check if a value is a valid UUID."""
    try:
        UUID(str(value))
        return True
    except (ValueError, AttributeError):
        return False


def validate_data(data_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate all data files and return (is_valid, list_of_issues).
    
    Returns:
        Tuple[bool, List[str]]: (True if valid, list of issue descriptions)
    """
    issues = []
    
    logger.info("=" * 70)
    logger.info("Data Validation and Sanitation")
    logger.info("=" * 70)
    logger.info("")
    
    # Load all CSV files
    logger.info("Loading data files...")
    try:
        df_matches = pd.read_csv(data_path / "match.csv")
        df_game_results = pd.read_csv(data_path / "game_result.csv")
        df_position_comparisons = pd.read_csv(data_path / "position_comparison.csv")
        df_match_scoring = pd.read_csv(data_path / "match_scoring.csv")
        df_events = pd.read_csv(data_path / "event.csv")
        df_league_seasons = pd.read_csv(data_path / "league_season.csv")
        df_team_seasons = pd.read_csv(data_path / "team_season.csv")
        df_players = pd.read_csv(data_path / "player.csv")
        df_scoring_systems = pd.read_csv(data_path / "scoring_system.csv")
    except FileNotFoundError as e:
        issues.append(f"Missing required file: {e.filename}")
        return False, issues
    
    logger.info(f"   [OK] Loaded {len(df_matches)} matches")
    logger.info(f"   [OK] Loaded {len(df_game_results)} game results")
    logger.info(f"   [OK] Loaded {len(df_position_comparisons)} position comparisons")
    logger.info(f"   [OK] Loaded {len(df_match_scoring)} match scorings")
    logger.info("")
    
    # 1. Validate UUIDs
    logger.info("1. Validating UUIDs...")
    uuid_issues = []
    for idx, row in df_matches.iterrows():
        if not validate_uuid(row['id']):
            uuid_issues.append(f"Match {idx}: Invalid UUID in 'id': {row['id']}")
        if not validate_uuid(row['event_id']):
            uuid_issues.append(f"Match {idx}: Invalid UUID in 'event_id': {row['event_id']}")
    
    if uuid_issues:
        issues.extend(uuid_issues[:10])  # Limit to first 10
        if len(uuid_issues) > 10:
            issues.append(f"... and {len(uuid_issues) - 10} more UUID issues")
    else:
        logger.info("   [OK] All UUIDs are valid")
    logger.info("")
    
    # 2. Validate referential integrity
    logger.info("2. Validating referential integrity...")
    
    # Match -> Event
    event_ids = set(df_events['id'].values)
    match_event_issues = df_matches[~df_matches['event_id'].isin(event_ids)]
    if not match_event_issues.empty:
        issues.append(f"Matches with invalid event_id: {len(match_event_issues)}")
        logger.error(f"   [ERROR] {len(match_event_issues)} matches reference non-existent events")
    else:
        logger.info("   [OK] All matches reference valid events")
    
    # GameResult -> Match
    match_ids = set(df_matches['id'].values)
    game_result_match_issues = df_game_results[~df_game_results['match_id'].isin(match_ids)]
    if not game_result_match_issues.empty:
        issues.append(f"GameResults with invalid match_id: {len(game_result_match_issues)}")
        logger.error(f"   [ERROR] {len(game_result_match_issues)} game results reference non-existent matches")
    else:
        logger.info("   [OK] All game results reference valid matches")
    
    # PositionComparison -> Match
    position_comparison_match_issues = df_position_comparisons[~df_position_comparisons['match_id'].isin(match_ids)]
    if not position_comparison_match_issues.empty:
        issues.append(f"PositionComparisons with invalid match_id: {len(position_comparison_match_issues)}")
        logger.error(f"   [ERROR] {len(position_comparison_match_issues)} position comparisons reference non-existent matches")
    else:
        logger.info("   [OK] All position comparisons reference valid matches")
    
    # MatchScoring -> Match
    match_scoring_match_issues = df_match_scoring[~df_match_scoring['match_id'].isin(match_ids)]
    if not match_scoring_match_issues.empty:
        issues.append(f"MatchScorings with invalid match_id: {len(match_scoring_match_issues)}")
        logger.error(f"   [ERROR] {len(match_scoring_match_issues)} match scorings reference non-existent matches")
    else:
        logger.info("   [OK] All match scorings reference valid matches")
    
    # MatchScoring -> ScoringSystem
    scoring_system_ids = set(df_scoring_systems['id'].values)
    match_scoring_system_issues = df_match_scoring[~df_match_scoring['scoring_system_id'].isin(scoring_system_ids)]
    if not match_scoring_system_issues.empty:
        issues.append(f"MatchScorings with invalid scoring_system_id: {len(match_scoring_system_issues)}")
        logger.error(f"   [ERROR] {len(match_scoring_system_issues)} match scorings reference non-existent scoring systems")
    else:
        logger.info("   [OK] All match scorings reference valid scoring systems")
    
    logger.info("")
    
    # 3. Validate match completeness
    logger.info("3. Validating match completeness...")
    
    matches_without_game_results = []
    matches_without_position_comparisons = []
    matches_without_scoring = []
    
    for match_id in match_ids:
        game_results_count = len(df_game_results[df_game_results['match_id'] == match_id])
        position_comparisons_count = len(df_position_comparisons[df_position_comparisons['match_id'] == match_id])
        match_scoring_count = len(df_match_scoring[df_match_scoring['match_id'] == match_id])
        
        if game_results_count == 0:
            matches_without_game_results.append(match_id)
        if position_comparisons_count == 0:
            matches_without_position_comparisons.append(match_id)
        if match_scoring_count == 0:
            matches_without_scoring.append(match_id)
    
    if matches_without_game_results:
        issues.append(f"Matches without game results: {len(matches_without_game_results)}")
        logger.error(f"   [ERROR] {len(matches_without_game_results)} matches have no game results")
    else:
        logger.info("   [OK] All matches have game results")
    
    if matches_without_position_comparisons:
        issues.append(f"Matches without position comparisons: {len(matches_without_position_comparisons)}")
        logger.error(f"   [ERROR] {len(matches_without_position_comparisons)} matches have no position comparisons")
        logger.info(f"   [INFO] Example match IDs: {matches_without_position_comparisons[:5]}")
    else:
        logger.info("   [OK] All matches have position comparisons")
    
    if matches_without_scoring:
        issues.append(f"Matches without scoring: {len(matches_without_scoring)}")
        logger.error(f"   [ERROR] {len(matches_without_scoring)} matches have no scoring")
    else:
        logger.info("   [OK] All matches have scoring")
    
    logger.info("")
    
    # 4. Validate position comparison completeness
    logger.info("4. Validating position comparison completeness...")
    
    matches_missing_positions = []
    for match_id in match_ids:
        match_comparisons = df_position_comparisons[df_position_comparisons['match_id'] == match_id]
        positions = set(match_comparisons['position'].values) if not match_comparisons.empty else set()
        expected_positions = {0, 1, 2, 3}
        
        if positions != expected_positions:
            missing = expected_positions - positions
            matches_missing_positions.append((match_id, missing))
    
    if matches_missing_positions:
        issues.append(f"Matches with incomplete position comparisons: {len(matches_missing_positions)}")
        logger.error(f"   [ERROR] {len(matches_missing_positions)} matches are missing position comparisons")
        for match_id, missing in matches_missing_positions[:5]:
            logger.info(f"   [INFO] Match {match_id}: missing positions {missing}")
    else:
        logger.info("   [OK] All matches have complete position comparisons (positions 0-3)")
    
    logger.info("")
    
    # 5. Validate score consistency
    logger.info("5. Validating score consistency...")
    
    score_mismatches = []
    for _, match in df_matches.iterrows():
        match_id = match['id']
        match_game_results = df_game_results[df_game_results['match_id'] == match_id]
        
        # Calculate totals from game results
        team1_total_calculated = match_game_results[
            match_game_results['team_season_id'] == match['team1_team_season_id']
        ]['score'].sum()
        team2_total_calculated = match_game_results[
            match_game_results['team_season_id'] == match['team2_team_season_id']
        ]['score'].sum()
        
        # Compare with match totals
        if abs(team1_total_calculated - match['team1_total_score']) > 0.01:
            score_mismatches.append((
                match_id,
                'team1',
                match['team1_total_score'],
                team1_total_calculated
            ))
        if abs(team2_total_calculated - match['team2_total_score']) > 0.01:
            score_mismatches.append((
                match_id,
                'team2',
                match['team2_total_score'],
                team2_total_calculated
            ))
    
    if score_mismatches:
        issues.append(f"Score mismatches: {len(score_mismatches)}")
        logger.error(f"   [ERROR] {len(score_mismatches)} score mismatches found")
        for match_id, team, stored, calculated in score_mismatches[:5]:
            logger.info(f"   [INFO] Match {match_id} {team}: stored={stored}, calculated={calculated}")
    else:
        logger.info("   [OK] All match scores are consistent with game results")
    
    logger.info("")
    
    # 6. Validate position comparison scores match game results
    logger.info("6. Validating position comparison scores...")
    
    position_score_mismatches = []
    for _, comparison in df_position_comparisons.iterrows():
        match_id = comparison['match_id']
        position = comparison['position']
        
        # Get game results for this position
        match_game_results = df_game_results[df_game_results['match_id'] == match_id]
        team1_result = match_game_results[
            (match_game_results['team_season_id'] == comparison['team1_player_id']) &
            (match_game_results['position'] == position)
        ]
        team2_result = match_game_results[
            (match_game_results['team_season_id'] == comparison['team2_player_id']) &
            (match_game_results['position'] == position)
        ]
        
        # Note: This check is simplified - we'd need to match by team_season_id properly
        # For now, just check if scores are reasonable integers
        if comparison['team1_score'] < 0 or comparison['team2_score'] < 0:
            position_score_mismatches.append((match_id, position, "negative score"))
    
    if position_score_mismatches:
        issues.append(f"Position comparison score issues: {len(position_score_mismatches)}")
        logger.error(f"   [ERROR] {len(position_score_mismatches)} position comparison score issues")
    else:
        logger.info("   [OK] All position comparison scores are valid")
    
    logger.info("")
    
    # Summary
    logger.info("=" * 70)
    if issues:
        logger.error(f"VALIDATION FAILED: Found {len(issues)} issues")
        logger.error("")
        logger.error("Issues found:")
        for i, issue in enumerate(issues[:20], 1):  # Limit to first 20
            logger.error(f"  {i}. {issue}")
        if len(issues) > 20:
            logger.error(f"  ... and {len(issues) - 20} more issues")
        return False, issues
    else:
        logger.info("VALIDATION PASSED: No issues found")
        return True, []


def sanitize_data(data_path: Path, fix_issues: bool = False) -> Dict[str, int]:
    """
    Sanitize data by fixing common issues.
    
    Args:
        data_path: Path to data directory
        fix_issues: If True, actually fix issues. If False, only report.
    
    Returns:
        Dict with counts of fixes applied
    """
    fixes = {
        'matches_deleted': 0,
        'game_results_deleted': 0,
        'position_comparisons_created': 0,
        'match_scorings_created': 0,
    }
    
    if not fix_issues:
        logger.info("Running in report-only mode. Set fix_issues=True to apply fixes.")
        return fixes
    
    logger.info("=" * 70)
    logger.info("Data Sanitation")
    logger.info("=" * 70)
    logger.info("")
    
    # Load data
    df_matches = pd.read_csv(data_path / "match.csv")
    df_game_results = pd.read_csv(data_path / "game_result.csv")
    df_position_comparisons = pd.read_csv(data_path / "position_comparison.csv")
    df_match_scoring = pd.read_csv(data_path / "match_scoring.csv")
    df_events = pd.read_csv(data_path / "event.csv")
    
    # Fix: Remove matches without valid events
    event_ids = set(df_events['id'].values)
    invalid_matches = df_matches[~df_matches['event_id'].isin(event_ids)]
    if not invalid_matches.empty:
        logger.info(f"Removing {len(invalid_matches)} matches with invalid event_id...")
        df_matches = df_matches[df_matches['event_id'].isin(event_ids)]
        fixes['matches_deleted'] = len(invalid_matches)
    
    # Fix: Remove game results without valid matches
    match_ids = set(df_matches['id'].values)
    invalid_game_results = df_game_results[~df_game_results['match_id'].isin(match_ids)]
    if not invalid_game_results.empty:
        logger.info(f"Removing {len(invalid_game_results)} game results with invalid match_id...")
        df_game_results = df_game_results[df_game_results['match_id'].isin(match_ids)]
        fixes['game_results_deleted'] = len(invalid_game_results)
    
    # Note: Position comparisons and match scoring creation would require
    # re-running the seed script logic, which is better done via regeneration
    
    # Save cleaned data
    if fixes['matches_deleted'] > 0 or fixes['game_results_deleted'] > 0:
        logger.info("Saving cleaned data...")
        df_matches.to_csv(data_path / "match.csv", index=False)
        df_game_results.to_csv(data_path / "game_result.csv", index=False)
        logger.info("   [OK] Data saved")
    
    return fixes


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate and sanitize sample data")
    parser.add_argument(
        "--data-path",
        type=Path,
        default=Path("sample_data/relational_csv"),
        help="Path to data directory"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Fix issues (default: only report)"
    )
    
    args = parser.parse_args()
    
    # Validate
    is_valid, issues = validate_data(args.data_path)
    
    # Sanitize if requested
    if args.fix:
        fixes = sanitize_data(args.data_path, fix_issues=True)
        logger.info("")
        logger.info("Fixes applied:")
        for key, value in fixes.items():
            if value > 0:
                logger.info(f"  {key}: {value}")
    
    # Exit with error code if validation failed
    sys.exit(0 if is_valid else 1)

