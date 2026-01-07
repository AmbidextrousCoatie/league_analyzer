"""
Seed Sample Data from Legacy CSV Files

Reads legacy CSV files from league_analyzer_v1/database/relational_csv/
and transforms them to the new format with UUIDs in sample_data/relational_csv/
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import pandas as pd
import re
from uuid import uuid4, UUID
from datetime import datetime, date
from typing import Optional
from domain.entities.league import League, get_league_long_name
from domain.entities.league_season import LeagueSeason
from domain.entities.team_season import TeamSeason
from domain.entities.event import Event
from domain.entities.game_result import GameResult
from domain.entities.match import Match, MatchStatus
from domain.entities.position_comparison import PositionComparison, ComparisonOutcome
from domain.entities.match_scoring import MatchScoring
from domain.entities.player import Player
from domain.entities.club import Club
from domain.entities.scoring_system import ScoringSystem
from domain.entities.club_player import ClubPlayer
from domain.value_objects.season import Season
from domain.value_objects.event_status import EventStatus
from domain.value_objects.vacancy_status import VacancyStatus
from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
from infrastructure.persistence.mappers.csv.event_mapper import PandasEventMapper
from infrastructure.persistence.mappers.csv.league_season_mapper import PandasLeagueSeasonMapper
from infrastructure.persistence.mappers.csv.team_season_mapper import PandasTeamSeasonMapper
from infrastructure.persistence.mappers.csv.game_mapper import PandasGameMapper
from infrastructure.persistence.mappers.csv.player_mapper import PandasPlayerMapper
from infrastructure.persistence.mappers.csv.league_mapper import PandasLeagueMapper
from infrastructure.persistence.mappers.csv.club_mapper import PandasClubMapper
from infrastructure.persistence.mappers.csv.scoring_system_mapper import PandasScoringSystemMapper
from infrastructure.persistence.mappers.csv.match_mapper import PandasMatchMapper
from infrastructure.persistence.mappers.csv.game_result_mapper import PandasGameResultMapper
from infrastructure.persistence.mappers.csv.position_comparison_mapper import PandasPositionComparisonMapper
from infrastructure.persistence.mappers.csv.match_scoring_mapper import PandasMatchScoringMapper
from infrastructure.persistence.mappers.csv.club_player_mapper import PandasClubPlayerMapper
from infrastructure.persistence.repositories.csv.event_repository import PandasEventRepository
from infrastructure.persistence.repositories.csv.league_season_repository import PandasLeagueSeasonRepository
from infrastructure.persistence.repositories.csv.team_season_repository import PandasTeamSeasonRepository
from infrastructure.persistence.repositories.csv.game_repository import PandasGameRepository
from infrastructure.persistence.repositories.csv.player_repository import PandasPlayerRepository
from infrastructure.persistence.repositories.csv.league_repository import PandasLeagueRepository
from infrastructure.persistence.repositories.csv.club_repository import PandasClubRepository
from infrastructure.persistence.repositories.csv.scoring_system_repository import PandasScoringSystemRepository
from infrastructure.persistence.repositories.csv.match_repository import PandasMatchRepository
from infrastructure.persistence.repositories.csv.game_result_repository import PandasGameResultRepository
from infrastructure.persistence.repositories.csv.position_comparison_repository import PandasPositionComparisonRepository
from infrastructure.persistence.repositories.csv.match_scoring_repository import PandasMatchScoringRepository
from infrastructure.persistence.repositories.csv.club_player_repository import PandasClubPlayerRepository
from infrastructure.logging import get_logger

# Initialize logger
logger = get_logger(__name__)


async def seed_sample_data():
    """Transform legacy CSV data to new format with UUIDs."""
    logger.info("=" * 70)
    logger.info("Seeding Sample Data from Legacy CSV Files")
    logger.info("=" * 70)
    logger.info("")
    
    # Filter: Only process league season 25/26
    TARGET_SEASON = "25/26"
    logger.info(f"[FILTER] Restricting data generation to league season: {TARGET_SEASON}")
    logger.info("")
    
    # Paths
    legacy_path = Path("league_analyzer_v1/database/relational_csv")
    output_path = Path("sample_data/relational_csv")
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Clear existing data - delete all CSV files in output directory
    logger.info("Clearing existing data...")
    csv_files = list(output_path.glob("*.csv"))
    for csv_file in csv_files:
        csv_file.unlink()
        logger.debug(f"   [DELETED] {csv_file.name}")
    logger.info(f"   [OK] Cleared {len(csv_files)} existing CSV files")
    logger.info("")
    
    # Create adapter for output
    adapter = PandasDataAdapter(output_path)
    
    # Initialize mappers and repositories
    event_mapper = PandasEventMapper()
    league_season_mapper = PandasLeagueSeasonMapper()
    team_season_mapper = PandasTeamSeasonMapper()
    player_mapper = PandasPlayerMapper()
    league_mapper = PandasLeagueMapper()
    club_mapper = PandasClubMapper()
    scoring_system_mapper = PandasScoringSystemMapper()
    match_mapper = PandasMatchMapper()
    game_result_mapper = PandasGameResultMapper()
    position_comparison_mapper = PandasPositionComparisonMapper()
    match_scoring_mapper = PandasMatchScoringMapper()
    
    event_repo = PandasEventRepository(adapter, event_mapper)
    league_season_repo = PandasLeagueSeasonRepository(adapter, league_season_mapper)
    team_season_repo = PandasTeamSeasonRepository(adapter, team_season_mapper)
    player_repo = PandasPlayerRepository(adapter, player_mapper)
    league_repo = PandasLeagueRepository(adapter, league_mapper)
    club_repo = PandasClubRepository(adapter, club_mapper)
    scoring_system_repo = PandasScoringSystemRepository(adapter, scoring_system_mapper)
    match_repo = PandasMatchRepository(adapter, match_mapper)
    game_result_repo = PandasGameResultRepository(adapter, game_result_mapper)
    position_comparison_repo = PandasPositionComparisonRepository(adapter, position_comparison_mapper)
    match_scoring_repo = PandasMatchScoringRepository(adapter, match_scoring_mapper)
    club_player_mapper = PandasClubPlayerMapper()
    club_player_repo = PandasClubPlayerRepository(adapter, club_player_mapper)
    
    # Mapping dictionaries to track UUIDs for relationships
    scoring_system_id_map = {}  # legacy_id -> UUID
    league_id_map = {}  # legacy_id -> UUID
    club_id_map = {}    # legacy_id -> UUID
    league_season_id_map = {}  # legacy_id -> UUID
    event_id_map = {}   # legacy_id -> UUID
    player_id_map = {}  # legacy_id -> UUID
    team_season_id_map = {}  # legacy_id -> UUID
    
    logger.info("Loading legacy data...")
    logger.info("-" * 70)
    
    # 0. Load and transform Scoring Systems (needed for League Seasons)
    logger.info("0. Processing Scoring Systems...")
    legacy_scoring_system_path = legacy_path / "scoring_system.csv"
    if legacy_scoring_system_path.exists():
        df_scoring_systems = pd.read_csv(legacy_scoring_system_path)
        # Deduplicate by id
        df_scoring_systems = df_scoring_systems.drop_duplicates(subset=['id'], keep='first')
        scoring_systems_created = 0
        for _, row in df_scoring_systems.iterrows():
            legacy_id = str(row['id']).strip()
            
            # Skip if already processed
            if legacy_id in scoring_system_id_map:
                continue
            
            name = str(row.get('name', '')).strip()
            points_per_individual_match_win = float(row.get('points_per_individual_match_win', 1.0)) if pd.notna(row.get('points_per_individual_match_win')) else 1.0
            points_per_individual_match_tie = float(row.get('points_per_individual_match_tie', 0.5)) if pd.notna(row.get('points_per_individual_match_tie')) else 0.5
            points_per_individual_match_loss = float(row.get('points_per_individual_match_loss', 0.0)) if pd.notna(row.get('points_per_individual_match_loss')) else 0.0
            points_per_team_match_win = float(row.get('points_per_team_match_win', 2.0)) if pd.notna(row.get('points_per_team_match_win')) else 2.0
            points_per_team_match_tie = float(row.get('points_per_team_match_tie', 1.0)) if pd.notna(row.get('points_per_team_match_tie')) else 1.0
            points_per_team_match_loss = float(row.get('points_per_team_match_loss', 0.0)) if pd.notna(row.get('points_per_team_match_loss')) else 0.0
            allow_ties = bool(row.get('allow_ties', True)) if pd.notna(row.get('allow_ties')) else True
            
            scoring_system = ScoringSystem(
                id=uuid4(),
                name=name,
                points_per_individual_match_win=points_per_individual_match_win,
                points_per_individual_match_tie=points_per_individual_match_tie,
                points_per_individual_match_loss=points_per_individual_match_loss,
                points_per_team_match_win=points_per_team_match_win,
                points_per_team_match_tie=points_per_team_match_tie,
                points_per_team_match_loss=points_per_team_match_loss,
                allow_ties=allow_ties
            )
            scoring_system = await scoring_system_repo.add(scoring_system)
            scoring_system_id_map[legacy_id] = scoring_system.id
            scoring_systems_created += 1
            #print(f"   [OK] Created ScoringSystem: {scoring_system.name}")
        logger.info(f"   [SUMMARY] Created {scoring_systems_created} scoring systems")
    else:
        logger.warning(f"   [SKIP] Scoring system file not found: {legacy_scoring_system_path}")
    
    # 1. Load and transform Leagues
    logger.info("\n1. Processing Leagues...")
    legacy_league_path = legacy_path / "league.csv"
    if legacy_league_path.exists():
        df_leagues = pd.read_csv(legacy_league_path)
        # Deduplicate by abbreviation (id column)
        df_leagues = df_leagues.drop_duplicates(subset=['id'], keep='first')
        leagues_created = 0
        for _, row in df_leagues.iterrows():
            legacy_id = str(row['id']).strip()
            long_name = str(row.get('long_name', '')).strip()
            level = int(row.get('level', 3)) if pd.notna(row.get('level')) else 3
            
            # Get abbreviation (id column contains abbreviation)
            abbreviation = legacy_id
            
            # Skip if already processed (duplicate check)
            if abbreviation in league_id_map:
                continue
            
            # Get full name
            if long_name:
                name = long_name
            else:
                try:
                    name = get_league_long_name(abbreviation)
                except (KeyError, AttributeError):
                    name = abbreviation
            
            league = League(
                id=uuid4(),
                name=name,
                abbreviation=abbreviation,
                level=level
            )
            league = await league_repo.add(league)
            league_id_map[legacy_id] = league.id
            leagues_created += 1
            #print(f"   [OK] Created League: {league.name} ({league.abbreviation}, Level: {league.level})")
        logger.info(f"   [SUMMARY] Created {leagues_created} leagues")
    else:
        logger.warning(f"   [SKIP] League file not found: {legacy_league_path}")
    
    # 2. Load and transform Clubs
    logger.info("\n2. Processing Clubs...")
    legacy_club_path = legacy_path / "club.csv"
    if legacy_club_path.exists():
        df_clubs = pd.read_csv(legacy_club_path)
        # Deduplicate by id
        df_clubs = df_clubs.drop_duplicates(subset=['id'], keep='first')
        clubs_created = 0
        for _, row in df_clubs.iterrows():
            legacy_id = str(row['id']).strip()
            
            # Skip if already processed
            if legacy_id in club_id_map:
                continue
            
            name = str(row.get('name', '')).strip()
            # Handle column name with or without leading space (legacy CSV has " short_name")
            short_name_raw = row.get('short_name') or row.get(' short_name')
            short_name = str(short_name_raw).strip() if pd.notna(short_name_raw) and str(short_name_raw).strip() else None
            
            club = Club(
                id=uuid4(),
                name=name,
                short_name=short_name,
                home_alley_id=None,  # Will be set later if venue mapping exists
                address=None
            )
            club = await club_repo.add(club)
            club_id_map[legacy_id] = club.id
            clubs_created += 1
            #print(f"   [OK] Created Club: {club.name} ({club.short_name or 'N/A'})")
        logger.info(f"   [SUMMARY] Created {clubs_created} clubs")
    else:
        logger.warning(f"   [SKIP] Club file not found: {legacy_club_path}")
    
    # 3. Load and transform Players
    logger.info("\n3. Processing Players...")
    legacy_player_path = legacy_path / "player.csv"
    if legacy_player_path.exists():
        df_players = pd.read_csv(legacy_player_path)
        # Deduplicate by id
        df_players = df_players.drop_duplicates(subset=['id'], keep='first')
        players_created = 0
        for _, row in df_players.iterrows():
            legacy_id = str(row['id']).strip()
            
            # Skip if already processed
            if legacy_id in player_id_map:
                continue
            
            full_name = str(row.get('full_name', '')).strip()
            if not full_name:
                given = str(row.get('given_name', '')).strip()
                family = str(row.get('family_name', '')).strip()
                full_name = f"{family}, {given}".strip() if family else given
            
            player = Player(
                id=uuid4(),
                name=full_name or 'Unknown',
                dbu_id=legacy_id  # Store legacy ID
            )
            player = await player_repo.add(player)
            player_id_map[legacy_id] = player.id
            players_created += 1
            if players_created % 20 == 0:
                logger.debug(f"   [PROGRESS] Processed {players_created} players...")
        logger.info(f"   [SUMMARY] Created {players_created} players")
    else:
        logger.warning(f"   [SKIP] Player file not found: {legacy_player_path}")
    
    # 3.5. Process Club-Player relationships from bowling results
    logger.info("\n3.5. Processing Club-Player Relationships...")
    legacy_bowling_results_path = Path("league_analyzer_v1/database/data/bowling_ergebnisse_reconstructed_clean.csv")
    if legacy_bowling_results_path.exists():
        logger.info("   [INFO] Loading bowling results data...")
        df_bowling = pd.read_csv(legacy_bowling_results_path, sep=';')
        logger.info(f"   [INFO] Loaded {len(df_bowling)} bowling result rows")
        
        # Get all players and clubs for mapping
        all_players = await player_repo.get_all()
        all_clubs = await club_repo.get_all()
        
        # Create mappings
        player_dbu_map = {p.dbu_id: p.id for p in all_players if p.dbu_id}
        club_name_map = {}  # Map club names (various formats) to club UUIDs
        for club in all_clubs:
            # Map by name
            club_name_map[club.name.lower()] = club.id
            # Map by short_name if available
            if club.short_name:
                club_name_map[club.short_name.lower()] = club.id
        
        def extract_club_name_from_team(team_name: str) -> Optional[str]:
            """
            Extract club name from team name.
            Examples: "BC Comet Nürnberg 1" -> "BC Comet Nürnberg"
                      "BK München 3" -> "BK München"
            """
            if not team_name or pd.isna(team_name):
                return None
            
            team_name = str(team_name).strip()
            # Remove trailing team number (e.g., " 1", " 2", " 3")
            team_name = re.sub(r'\s+\d+$', '', team_name)
            return team_name
        
        def find_club_by_name(team_name: str) -> Optional[UUID]:
            """Find club UUID by team name."""
            club_name = extract_club_name_from_team(team_name)
            if not club_name:
                return None
            
            # Try exact match first
            club_id = club_name_map.get(club_name.lower())
            if club_id:
                return club_id
            
            # Try partial matches (e.g., "BC Comet" matches "BC Comet Nürnberg")
            for mapped_name, mapped_id in club_name_map.items():
                if mapped_name in club_name.lower() or club_name.lower() in mapped_name:
                    return mapped_id
            
            return None
        
        # Filter to only player rows (exclude "Team Total" rows)
        df_player_rows = df_bowling[
            (df_bowling['Player ID'].notna()) & 
            (df_bowling['Player ID'] != 0) &
            (df_bowling['Player'] != 'Team Total')
        ].copy()
        
        logger.info(f"   [INFO] Found {len(df_player_rows)} player game rows")
        
        # Group by player ID and club to find date ranges
        club_players_created = 0
        processed_combinations = set()  # Track (player_id, club_id) combinations
        
        for player_dbu_id, player_uuid in player_dbu_map.items():
            # Get all rows for this player
            player_rows = df_player_rows[df_player_rows['Player ID'].astype(str) == str(player_dbu_id)]
            
            if player_rows.empty:
                continue
            
            # Collect all games with club and date
            club_game_dates = []  # List of (club_id, date) tuples
            
            for _, row in player_rows.iterrows():
                team_name = str(row['Team']).strip()
                date_str = str(row.get('Date', '')).strip()
                
                # Find club for this team
                club_id = find_club_by_name(team_name)
                if not club_id:
                    continue  # Skip if club not found
                
                # Parse date
                try:
                    if date_str:
                        game_date = pd.to_datetime(date_str).date()
                        club_game_dates.append((club_id, game_date))
                except Exception:
                    continue
            
            if not club_game_dates:
                continue
            
            # Group by club and find date ranges
            club_dates = {}  # club_id -> list of dates
            for club_id, game_date in club_game_dates:
                if club_id not in club_dates:
                    club_dates[club_id] = []
                club_dates[club_id].append(game_date)
            
            # Determine club transitions chronologically
            # Sort clubs by their earliest date (when player first played for them)
            club_periods = []  # List of (club_id, date_entry, date_exit)
            
            for club_id, dates in club_dates.items():
                date_entry = min(dates)
                club_periods.append((club_id, date_entry, None))  # date_exit will be set later
            
            # Sort by entry date to determine chronological order
            club_periods.sort(key=lambda x: x[1])
            
            # Create ClubPlayer entries for all clubs
            for i in range(len(club_periods)):
                club_id, date_entry, _ = club_periods[i]
                
                # Determine exit date
                if len(club_periods) == 1:
                    # Player played for only one club - no exit date (still active)
                    date_exit = None
                else:
                    # Player played for multiple clubs
                    if i < len(club_periods) - 1:
                        # Not the last club - exit date is entry date of next club
                        _, next_date_entry, _ = club_periods[i + 1]
                        date_exit = next_date_entry
                    else:
                        # Last club - no exit date (still active)
                        date_exit = None
                
                # Create ClubPlayer entry
                combination_key = (player_uuid, club_id)
                if combination_key in processed_combinations:
                    continue  # Already processed this player-club combination
                
                processed_combinations.add(combination_key)
                
                club_player = ClubPlayer(
                    id=uuid4(),
                    club_id=club_id,
                    player_id=player_uuid,
                    date_entry=date_entry,
                    date_exit=date_exit
                )
                
                try:
                    club_player = await club_player_repo.add(club_player)
                    club_players_created += 1
                except Exception as e:
                    logger.warning(f"   [WARN] Failed to create ClubPlayer for player {player_dbu_id} and club {club_id}: {e}")
        
        logger.info(f"   [SUMMARY] Created {club_players_created} club-player relationships")
    else:
        logger.warning(f"   [SKIP] Bowling results file not found: {legacy_bowling_results_path}")
    
    # 4. Load and transform League Seasons
    logger.info("\n4. Processing League Seasons...")
    legacy_league_season_path = legacy_path / "league_season.csv"
    if legacy_league_season_path.exists():
        df_league_seasons = pd.read_csv(legacy_league_season_path)
        # Deduplicate by id
        df_league_seasons = df_league_seasons.drop_duplicates(subset=['id'], keep='first')
        league_seasons_created = 0
        for _, row in df_league_seasons.iterrows():
            legacy_id = str(row['id']).strip()
            
            # Skip if already processed
            if legacy_id in league_season_id_map:
                continue
            
            legacy_league_id = str(row['league_id']).strip()
            season_str = str(row.get('season', '')).strip()
            legacy_scoring_system_id = str(row.get('scoring_system_id', '')).strip()
            number_of_teams = int(row['number_of_teams']) if pd.notna(row.get('number_of_teams')) else None
            players_per_team = int(row['players_per_team']) if pd.notna(row.get('players_per_team')) else None
            
            # Get league UUID
            league_id = league_id_map.get(legacy_league_id)
            if not league_id:
                logger.warning(f"   [WARN] League {legacy_league_id} not found for league season {legacy_id}")
                continue
            
            # Get scoring system UUID
            scoring_system_uuid = scoring_system_id_map.get(legacy_scoring_system_id)
            if not scoring_system_uuid:
                logger.error(f"   [ERROR] Scoring system {legacy_scoring_system_id} not found for league season {legacy_id}. Skipping.")
                continue
            scoring_system_id = str(scoring_system_uuid)
            
            # Filter: Only process target season (25/26)
            # Normalize season string for comparison (handle variations like "25/26", "25-26", etc.)
            normalized_season_input = season_str.replace('-', '/').strip()
            if normalized_season_input != TARGET_SEASON:
                continue  # Skip this league season
            
            # Normalize season format from "25/26" to "2025-26"
            # The mapper has a helper function, but we'll normalize here for clarity
            normalized_season_str = season_str
            if re.match(r'^\d{2}[-/]\d{2}$', season_str):
                # Short format (YY/YY) - convert to full format (YYYY-YY)
                parts = season_str.split('/') if '/' in season_str else season_str.split('-')
                if len(parts) == 2:
                    start_short = int(parts[0])
                    end_short = int(parts[1])
                    # For recent data (2020s), assume 2000s
                    if start_short >= 50:
                        start_year = 1900 + start_short
                    else:
                        start_year = 2000 + start_short
                    normalized_season_str = f"{start_year}-{end_short:02d}"
            
            # Parse season
            try:
                season = Season(normalized_season_str)
            except Exception as e:
                logger.warning(f"   [WARN] Invalid season '{season_str}' (normalized to '{normalized_season_str}') for league season {legacy_id}: {e}")
                continue
            
            league_season = LeagueSeason(
                id=uuid4(),
                league_id=league_id,
                season=season,
                scoring_system_id=scoring_system_id,
                number_of_teams=number_of_teams,
                players_per_team=players_per_team
            )
            league_season = await league_season_repo.add(league_season)
            league_season_id_map[legacy_id] = league_season.id
            league_seasons_created += 1
            #logger.debug(f"   [OK] Created LeagueSeason: {season_str} for {legacy_league_id}")
        logger.info(f"   [SUMMARY] Created {league_seasons_created} league seasons")
    else:
        logger.warning(f"   [SKIP] League season file not found: {legacy_league_season_path}")
    
    # 5. Load and transform Team Seasons
    logger.info("\n5. Processing Team Seasons...")
    legacy_team_season_path = legacy_path / "team_season.csv"
    if legacy_team_season_path.exists():
        df_team_seasons = pd.read_csv(legacy_team_season_path)
        # Deduplicate by id
        df_team_seasons = df_team_seasons.drop_duplicates(subset=['id'], keep='first')
        team_seasons_created = 0
        for _, row in df_team_seasons.iterrows():
            legacy_id = str(row['id']).strip()
            
            # Skip if already processed
            if legacy_id in team_season_id_map:
                continue
            
            legacy_league_season_id = str(row['league_season_id']).strip()
            
            # Filter: Only process team seasons belonging to target season (25/26)
            if legacy_league_season_id not in league_season_id_map:
                continue  # Skip team seasons not in our filtered league seasons
            legacy_club_id = str(row['club_id']).strip()
            team_number = int(row['team_number']) if pd.notna(row.get('team_number')) else 1
            
            # Get UUIDs
            league_season_id = league_season_id_map.get(legacy_league_season_id)
            club_id = club_id_map.get(legacy_club_id)
            
            if not league_season_id:
                logger.warning(f"   [WARN] League season {legacy_league_season_id} not found for team season {legacy_id}")
                continue
            if not club_id:
                logger.warning(f"   [WARN] Club {legacy_club_id} not found for team season {legacy_id}")
                continue
            
            team_season = TeamSeason(
                id=uuid4(),
                league_season_id=league_season_id,
                club_id=club_id,
                team_number=team_number,
                vacancy_status=VacancyStatus.ACTIVE
            )
            team_season = await team_season_repo.add(team_season)
            team_season_id_map[legacy_id] = team_season.id
            team_seasons_created += 1
            #logger.debug(f"   [OK] Created TeamSeason: Club {legacy_club_id} Team {team_number}")
        logger.info(f"   [SUMMARY] Created {team_seasons_created} team seasons")
    else:
        logger.warning(f"   [SKIP] Team season file not found: {legacy_team_season_path}")
    
    # 6. Load and transform Events
    logger.info("\n7. Processing Events...")
    legacy_event_path = legacy_path / "event.csv"
    if legacy_event_path.exists():
        df_events = pd.read_csv(legacy_event_path)
        # Deduplicate by id
        df_events = df_events.drop_duplicates(subset=['id'], keep='first')
        events_created = 0
        for _, row in df_events.iterrows():
            legacy_id = str(row['id']).strip()
            
            # Skip if already processed
            if legacy_id in event_id_map:
                continue
            
            legacy_league_season_id = str(row['league_season_id']).strip()
            
            # Filter: Only process events belonging to target season (25/26)
            if legacy_league_season_id not in league_season_id_map:
                continue  # Skip events not in our filtered league seasons
            
            event_type = str(row.get('event_type', 'league')).strip()
            league_week = int(row['league_week']) if pd.notna(row.get('league_week')) else None
            tournament_stage = str(row.get('tournament_stage', '')).strip() if pd.notna(row.get('tournament_stage')) else None
            date_str = str(row.get('date', '')).strip()
            venue_id = str(row.get('venue_id', '')).strip() if pd.notna(row.get('venue_id')) else None
            oil_pattern_id = int(row['oil_pattern_id']) if pd.notna(row.get('oil_pattern_id')) else None
            status_str = str(row.get('status', 'scheduled')).strip()
            notes = str(row.get('notes', '')).strip() if pd.notna(row.get('notes')) else None
            
            # Get league season UUID
            league_season_id = league_season_id_map.get(legacy_league_season_id)
            if not league_season_id:
                logger.warning(f"   [WARN] League season {legacy_league_season_id} not found for event {legacy_id}")
                continue
            
            # Parse date
            try:
                if date_str:
                    date = pd.to_datetime(date_str).to_pydatetime()
                else:
                    date = datetime.utcnow()
            except Exception:
                date = datetime.utcnow()
            
            # Parse status
            try:
                status = EventStatus(status_str.lower())
            except ValueError:
                status = EventStatus.SCHEDULED
            
            event = Event(
                id=uuid4(),
                dbu_id=legacy_id,  # Store legacy ID
                league_season_id=league_season_id,
                event_type=event_type,
                league_week=league_week,
                tournament_stage=tournament_stage,
                date=date,
                venue_id=venue_id,
                oil_pattern_id=oil_pattern_id,
                status=status,
                notes=notes
            )
            event = await event_repo.add(event)
            event_id_map[legacy_id] = event.id
            events_created += 1
            #logger.debug(f"   [OK] Created Event: {event_type} Week {league_week or 'N/A'}")
        logger.info(f"   [SUMMARY] Created {events_created} events")
    else:
        logger.warning(f"   [SKIP] Event file not found: {legacy_event_path}")
    
    # 7. Load and transform Games to new data model (Match, GameResult, PositionComparison, MatchScoring)
    logger.info("\n8. Processing Games (New Data Model)...")
    legacy_game_path = legacy_path / "new" / "game_result_new.csv"
    if legacy_game_path.exists():
        logger.info("   [INFO] Loading game data...")
        df_games = pd.read_csv(legacy_game_path)
        logger.info(f"   [INFO] Loaded {len(df_games)} game rows")
        
        # Cache all data upfront to avoid repeated get_all() calls
        logger.info("   [INFO] Caching repository data...")
        all_events = await event_repo.get_all()
        all_players = await player_repo.get_all()
        all_league_seasons = await league_season_repo.get_all()
        all_scoring_systems = await scoring_system_repo.get_all()
        # Create lookup maps for O(1) access
        event_map = {e.id: e for e in all_events}
        player_map = {p.dbu_id: p.id for p in all_players if p.dbu_id}  # Map legacy player IDs to UUIDs
        league_season_map = {ls.id: ls for ls in all_league_seasons}
        scoring_system_map = {str(ss.id): ss for ss in all_scoring_systems}  # Map by string ID
        
        logger.info("   [INFO] Processing game rows and grouping into matches...")
        
        # Step 1: Collect raw game data and group by match
        from collections import defaultdict
        match_data = defaultdict(list)  # (event_id, round_number, match_number) -> list of game rows
        
        row_count = 0
        for _, row in df_games.iterrows():
            row_count += 1
            if row_count % 100 == 0:
                logger.debug(f"   [PROGRESS] Processing row {row_count}/{len(df_games)}...")
                await asyncio.sleep(0)  # Yield control
            
            legacy_event_id = str(row['event_id']).strip()
            legacy_player_id = str(row['player_id']).strip()
            legacy_team_season_id = str(row['team_season_id']).strip()
            position = int(row['lineup_position']) if pd.notna(row.get('lineup_position')) else 0
            match_number = int(row['match_number']) if pd.notna(row.get('match_number')) else 0
            round_number = int(row['round_number']) if pd.notna(row.get('round_number')) else 1
            
            # Read score and validate it's non-negative (skip invalid data)
            # Scores are always integers (pins knocked down)
            raw_score = row.get('score')
            if pd.isna(raw_score):
                score = 0
            else:
                score = int(float(raw_score))  # Convert to int (rounds down)
                if score < 0:
                    continue  # Skip negative scores
            
            # Get UUIDs
            event_id = event_id_map.get(legacy_event_id)
            player_id = player_map.get(legacy_player_id)
            team_season_id = team_season_id_map.get(legacy_team_season_id)
            
            # Filter: Only process games for events in target season (25/26)
            # Events are already filtered by league_season, so if event_id is None, 
            # the event was filtered out (not in 25/26 season)
            if not event_id:
                continue  # Skip games for events not in target season
            if not player_id:
                continue  # Skip if player not found
            if not team_season_id:
                continue  # Skip if team season not found (or filtered out)
            
            handicap = float(row['handicap']) if pd.notna(row.get('handicap')) else None
            is_disqualified = bool(row.get('is_disqualified', False)) if pd.notna(row.get('is_disqualified')) else False
            
            # Store game data for match grouping
            match_key = (event_id, round_number, match_number)
            match_data[match_key].append({
                'event_id': event_id,
                'player_id': player_id,
                'team_season_id': team_season_id,
                'position': position,
                'score': score,
                'handicap': handicap,
                'is_disqualified': is_disqualified,
                'legacy_event_id': legacy_event_id,
                'legacy_team_season_id': legacy_team_season_id
            })
        
        logger.info(f"   [INFO] Grouped into {len(match_data)} matches")
        
        # Step 2: Create Match entities and GameResult entities
        matches = []
        game_results = []
        match_id_map = {}  # (event_id, round_number, match_number) -> match_id
        
        for match_key, game_rows in match_data.items():
            event_id, round_number, match_number = match_key
            
            # Find unique teams in this match
            team_ids = set()
            for game_row in game_rows:
                team_ids.add(game_row['team_season_id'])
            
            if len(team_ids) == 2:
                # Normal case: exactly 2 teams
                team_list = sorted(list(team_ids))
                team1_id = team_list[0]
                team2_id = team_list[1]
                
                # Calculate team totals
                team1_total = sum(gr['score'] for gr in game_rows if gr['team_season_id'] == team1_id)
                team2_total = sum(gr['score'] for gr in game_rows if gr['team_season_id'] == team2_id)
                
                # Create Match entity
                match = Match(
                    id=uuid4(),
                    event_id=event_id,
                    round_number=round_number,
                    match_number=match_number,
                    team1_team_season_id=team1_id,
                    team2_team_season_id=team2_id,
                    team1_total_score=team1_total,
                    team2_total_score=team2_total,
                    status=MatchStatus.COMPLETED
                )
                
                matches.append(match)
                match_id_map[match_key] = match.id
                
                # Create GameResult entities for this match
                for game_row in game_rows:
                    game_result = GameResult(
                        id=uuid4(),
                        match_id=match.id,
                        player_id=game_row['player_id'],
                        team_season_id=game_row['team_season_id'],
                        position=game_row['position'],
                        score=game_row['score'],
                        handicap=game_row['handicap'],
                        is_disqualified=game_row['is_disqualified']
                    )
                    game_results.append(game_result)
            elif len(team_ids) > 2 and len(team_ids) % 2 == 0:
                # Multiple teams: split into pairs (round-robin concurrent matches)
                # Group games by team
                team_games = {}
                for game_row in game_rows:
                    team_id = game_row['team_season_id']
                    if team_id not in team_games:
                        team_games[team_id] = []
                    team_games[team_id].append(game_row)
                
                # Sort teams and pair them
                team_list = sorted(list(team_ids))
                num_matches = len(team_list) // 2
                
                for i in range(num_matches):
                    team1_id = team_list[i * 2]
                    team2_id = team_list[i * 2 + 1]
                    
                    # Calculate team totals
                    team1_total = sum(gr['score'] for gr in team_games[team1_id])
                    team2_total = sum(gr['score'] for gr in team_games[team2_id])
                    
                    # Create Match entity with adjusted match_number
                    adjusted_match_number = match_number + i if match_number == 0 else match_number
                    match = Match(
                        id=uuid4(),
                        event_id=event_id,
                        round_number=round_number,
                        match_number=adjusted_match_number,
                        team1_team_season_id=team1_id,
                        team2_team_season_id=team2_id,
                        team1_total_score=team1_total,
                        team2_total_score=team2_total,
                        status=MatchStatus.COMPLETED
                    )
                    
                    matches.append(match)
                    match_id_map[(event_id, round_number, adjusted_match_number)] = match.id
                    
                    # Create GameResult entities for this specific match pair
                    for game_row in team_games[team1_id] + team_games[team2_id]:
                        game_result = GameResult(
                            id=uuid4(),
                            match_id=match.id,
                            player_id=game_row['player_id'],
                            team_season_id=game_row['team_season_id'],
                            position=game_row['position'],
                            score=game_row['score'],
                            handicap=game_row['handicap'],
                            is_disqualified=game_row['is_disqualified']
                        )
                        game_results.append(game_result)
            else:
                logger.warning(f"   [WARN] Match (event={event_id}, round={round_number}, match={match_number}) "
                      f"has {len(team_ids)} teams, expected 2 or even number. Skipping.")
                continue
        
        logger.info(f"   [SUMMARY] Created {len(matches)} matches and {len(game_results)} game results")
        
        # Step 3: Create PositionComparison entities
        position_comparisons = []
        
        # Iterate directly over matches (not match_data.keys()) because matches may have been split
        for match in matches:
            # Get game results for this match
            match_game_results = [
                gr for gr in game_results
                if gr.match_id == match.id
            ]
            
            # Group by position and create comparisons
            for position in range(4):  # Positions 0-3
                team1_results = [
                    gr for gr in match_game_results
                    if gr.team_season_id == match.team1_team_season_id and gr.position == position
                ]
                team2_results = [
                    gr for gr in match_game_results
                    if gr.team_season_id == match.team2_team_season_id and gr.position == position
                ]
                
                if len(team1_results) == 1 and len(team2_results) == 1:
                    team1_result = team1_results[0]
                    team2_result = team2_results[0]
                    
                    # Determine outcome
                    if team1_result.score > team2_result.score:
                        outcome = ComparisonOutcome.TEAM1_WIN
                    elif team2_result.score > team1_result.score:
                        outcome = ComparisonOutcome.TEAM2_WIN
                    else:
                        outcome = ComparisonOutcome.TIE
                    
                    comparison = PositionComparison(
                        id=uuid4(),
                        match_id=match.id,
                        position=position,
                        team1_player_id=team1_result.player_id,
                        team2_player_id=team2_result.player_id,
                        team1_score=team1_result.score,
                        team2_score=team2_result.score,
                        outcome=outcome
                    )
                    
                    position_comparisons.append(comparison)
        
        logger.info(f"   [SUMMARY] Created {len(position_comparisons)} position comparisons")
        
        # Step 4: Create MatchScoring entities
        match_scorings = []
        
        for match in matches:
            # Get the event to find its league_season
            event = event_map.get(match.event_id)
            if not event:
                logger.warning(f"   [WARN] Event {match.event_id} not found for match {match.id}. Skipping match scoring.")
                continue
            
            # Get league season to find scoring system
            league_season = league_season_map.get(event.league_season_id)
            if not league_season:
                logger.warning(f"   [WARN] League season {event.league_season_id} not found for event {event.id}. Skipping match scoring.")
                continue
            
            # Get scoring system ID from league season
            scoring_system_id_str = str(league_season.scoring_system_id)
            scoring_system = scoring_system_map.get(scoring_system_id_str)
            
            if not scoring_system:
                logger.warning(f"   [WARN] Scoring system {scoring_system_id_str} not found for league season {league_season.id}. Using defaults.")
                # Use defaults (3pt system for 25/26)
                points_per_win = 3.0
                points_per_tie = 1.5
                points_per_loss = 0.0
            else:
                points_per_win = scoring_system.points_per_team_match_win
                points_per_tie = scoring_system.points_per_team_match_tie
                points_per_loss = scoring_system.points_per_team_match_loss
            
            # Get position comparisons for this match
            match_comparisons = [
                pc for pc in position_comparisons
                if pc.match_id == match.id
            ]
            
            # Calculate individual points
            team1_individual_points = 0.0
            team2_individual_points = 0.0
            
            for comparison in match_comparisons:
                if comparison.outcome == ComparisonOutcome.TEAM1_WIN:
                    team1_individual_points += 1.0
                elif comparison.outcome == ComparisonOutcome.TEAM2_WIN:
                    team2_individual_points += 1.0
                else:  # TIE
                    team1_individual_points += 0.5
                    team2_individual_points += 0.5
            
            # Calculate team match points using scoring system values
            if match.team1_total_score > match.team2_total_score:
                team1_match_points = points_per_win
                team2_match_points = points_per_loss
            elif match.team2_total_score > match.team1_total_score:
                team1_match_points = points_per_loss
                team2_match_points = points_per_win
            else:  # Tie
                team1_match_points = points_per_tie
                team2_match_points = points_per_tie
            
            scoring = MatchScoring(
                id=uuid4(),
                match_id=match.id,
                scoring_system_id=scoring_system_id_str,
                team1_individual_points=team1_individual_points,
                team2_individual_points=team2_individual_points,
                team1_match_points=team1_match_points,
                team2_match_points=team2_match_points
            )
            
            match_scorings.append(scoring)
        
        logger.info(f"   [SUMMARY] Created {len(match_scorings)} match scorings")
        
        # Step 5: Save to CSV files using repositories
        logger.info("   [INFO] Saving to CSV files using repositories...")
        
        # Save matches using repository
        logger.info("   [INFO] Saving matches...")
        matches_saved = 0
        for match in matches:
            try:
                await match_repo.add(match)
                matches_saved += 1
            except Exception as e:
                logger.error(f"   [ERROR] Failed to save match {match.id}: {e}")
        logger.info(f"   [SAVED] {matches_saved} matches")
        
        # Save game results using repository
        logger.info("   [INFO] Saving game results...")
        game_results_saved = 0
        for gr in game_results:
            try:
                await game_result_repo.add(gr)
                game_results_saved += 1
            except Exception as e:
                logger.error(f"   [ERROR] Failed to save game result {gr.id}: {e}")
        logger.info(f"   [SAVED] {game_results_saved} game results")
        
        # Save position comparisons using repository
        logger.info("   [INFO] Saving position comparisons...")
        comparisons_saved = 0
        for pc in position_comparisons:
            try:
                await position_comparison_repo.add(pc)
                comparisons_saved += 1
            except Exception as e:
                logger.error(f"   [ERROR] Failed to save position comparison {pc.id}: {e}")
        logger.info(f"   [SAVED] {comparisons_saved} position comparisons")
        
        # Save match scorings using repository
        logger.info("   [INFO] Saving match scorings...")
        scorings_saved = 0
        for ms in match_scorings:
            try:
                await match_scoring_repo.add(ms)
                scorings_saved += 1
            except Exception as e:
                logger.error(f"   [ERROR] Failed to save match scoring {ms.id}: {e}")
        logger.info(f"   [SAVED] {scorings_saved} match scorings")
        
        games_created = game_results_saved  # For summary
        matches_created = matches_saved
    else:
        logger.warning(f"   [SKIP] Game file not found: {legacy_game_path}")
        games_created = 0
        matches_created = 0
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("Data Migration Complete!")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Summary:")
    logger.info(f"  - Leagues: {len(league_id_map)}")
    logger.info(f"  - Clubs: {len(club_id_map)}")
    logger.info(f"  - Players: {len(player_id_map)}")
    logger.info(f"  - League Seasons: {len(league_season_id_map)}")
    logger.info(f"  - Team Seasons: {len(team_season_id_map)}")
    logger.info(f"  - Events: {len(event_id_map)}")
    logger.info(f"  - Matches: {matches_created}")
    logger.info(f"  - Game Results: {games_created}")
    logger.info("")
    logger.info("Data saved to CSV files in sample_data/relational_csv/")
    logger.info("")


async def run_with_timeout():
    """Run seed script with 10 second timeout."""
    try:
        await asyncio.wait_for(seed_sample_data(), timeout=10.0)
    except asyncio.TimeoutError:
        logger.error("")
        logger.error("=" * 70)
        logger.error("ERROR: Seed script timed out after 10 seconds!")
        logger.error("=" * 70)
        logger.error("")
        logger.error("The seed script appears to be stuck in an infinite loop.")
        logger.error("Please check the code for:")
        logger.error("  - Nested loops that may not terminate")
        logger.error("  - Repository operations that may be blocking")
        logger.error("  - Data processing that may be taking too long")
        logger.error("")
        logger.error("Exiting with error code 1")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    result = asyncio.run(run_with_timeout())
    
    # Validate after seeding if successful
    if result:
        logger.info("\n" + "=" * 70)
        logger.info("Post-Seed Validation")
        logger.info("=" * 70)
        try:
            from scripts.validate_sample_data import validate_data
            data_path = Path("sample_data/relational_csv")
            is_valid, issues = validate_data(data_path)
            
            if not is_valid:
                logger.warning("\n[WARNING] Data validation found issues. Review the output above.")
                logger.warning("Consider running the seed script again or manually fixing issues.")
            else:
                logger.info("\n[SUCCESS] Data validation passed!")
        except ImportError:
            logger.info("[INFO] Validation script not available, skipping validation")
        except Exception as e:
            logger.warning(f"[WARNING] Validation failed with error: {e}")
