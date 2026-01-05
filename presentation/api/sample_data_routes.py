"""
Sample Data Routes

FastAPI routes for displaying sample data created via CRUD operations.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from infrastructure.logging import get_logger

logger = get_logger(__name__)
from pathlib import Path
from typing import List, Dict, Any
from uuid import UUID
from domain.entities.league import League
from domain.entities.league_season import LeagueSeason
from domain.entities.team_season import TeamSeason
from domain.entities.event import Event
from domain.entities.game import Game
from domain.entities.player import Player
from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
from infrastructure.persistence.mappers.csv.event_mapper import PandasEventMapper
from infrastructure.persistence.mappers.csv.league_season_mapper import PandasLeagueSeasonMapper
from infrastructure.persistence.mappers.csv.team_season_mapper import PandasTeamSeasonMapper
from infrastructure.persistence.mappers.csv.game_mapper import PandasGameMapper
from infrastructure.persistence.mappers.csv.player_mapper import PandasPlayerMapper
from infrastructure.persistence.mappers.csv.league_mapper import PandasLeagueMapper
from infrastructure.persistence.mappers.csv.club_mapper import PandasClubMapper
from infrastructure.persistence.mappers.csv.scoring_system_mapper import PandasScoringSystemMapper
from infrastructure.persistence.repositories.csv.event_repository import PandasEventRepository
from infrastructure.persistence.repositories.csv.league_season_repository import PandasLeagueSeasonRepository
from infrastructure.persistence.repositories.csv.team_season_repository import PandasTeamSeasonRepository
from infrastructure.persistence.repositories.csv.game_repository import PandasGameRepository
from infrastructure.persistence.repositories.csv.player_repository import PandasPlayerRepository
from infrastructure.persistence.repositories.csv.league_repository import PandasLeagueRepository
from infrastructure.persistence.repositories.csv.club_repository import PandasClubRepository
from infrastructure.persistence.repositories.csv.scoring_system_repository import PandasScoringSystemRepository
from infrastructure.persistence.repositories.csv.club_player_repository import PandasClubPlayerRepository
from infrastructure.persistence.mappers.csv.club_player_mapper import PandasClubPlayerMapper
from jinja2 import Environment, FileSystemLoader

router = APIRouter(prefix="/sample-data", tags=["sample-data"])

# Setup Jinja2 - use templates in presentation layer
_template_dir = Path(__file__).parent.parent / "templates"
env = Environment(loader=FileSystemLoader(str(_template_dir)))

# Initialize repositories - use sample data CSV files
_data_path = Path(__file__).parent.parent.parent / "sample_data" / "relational_csv"

# Import seed function
import sys
_seed_script_path = Path(__file__).parent.parent.parent / "scripts" / "seed_sample_data.py"
if _seed_script_path.exists():
    # Add scripts directory to path for imports
    sys.path.insert(0, str(_seed_script_path.parent.parent))
    from scripts.seed_sample_data import seed_sample_data
else:
    seed_sample_data = None

def _get_repositories():
    """Get initialized repositories."""
    # Create a single adapter for all entities
    adapter = PandasDataAdapter(_data_path)
    
    return {
        'event': PandasEventRepository(adapter, PandasEventMapper()),
        'league_season': PandasLeagueSeasonRepository(adapter, PandasLeagueSeasonMapper()),
        'team_season': PandasTeamSeasonRepository(adapter, PandasTeamSeasonMapper()),
        'game': PandasGameRepository(adapter, PandasGameMapper()),
        'player': PandasPlayerRepository(adapter, PandasPlayerMapper()),
        'league': PandasLeagueRepository(adapter, PandasLeagueMapper()),
        'club': PandasClubRepository(adapter, PandasClubMapper()),
        'scoring_system': PandasScoringSystemRepository(adapter, PandasScoringSystemMapper()),
        'club_player': PandasClubPlayerRepository(adapter, PandasClubPlayerMapper())
    }


@router.get("/", response_class=HTMLResponse)
async def sample_data_index():
    """Main page listing all sample data."""
    try:
        template = env.get_template("sample_data_index.html")
        return HTMLResponse(content=template.render(title="Sample Data - CRUD Operations Demo"))
    except Exception as e:
        from infrastructure.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error in sample_data_index: {e}", exc_info=True)
        return HTMLResponse(content=f"<h1>Error</h1><p>{str(e)}</p>", status_code=500)


@router.post("/seed", response_class=JSONResponse)
async def seed_data():
    """
    Trigger seed script to create sample data.
    This endpoint runs the seed_sample_data script and returns the results.
    """
    if seed_sample_data is None:
        raise HTTPException(
            status_code=500,
            detail="Seed script not found. Cannot seed data."
        )
    
    try:
        logger.info("Starting seed data operation...")
        await seed_sample_data()
        logger.info("Seed data operation completed successfully")
        return JSONResponse(content={
            "status": "success",
            "message": "Sample data seeded successfully",
            "data_path": str(_data_path)
        })
    except Exception as e:
        logger.error(f"Error seeding data: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error seeding data: {str(e)}"
        )


@router.post("/validate", response_class=JSONResponse)
async def validate_data_endpoint():
    """
    Validate sample data without fixing issues.
    Returns validation results.
    """
    try:
        from scripts.validate_sample_data import validate_data
        
        logger.info("Starting data validation...")
        is_valid, issues = validate_data(_data_path)
        logger.info(f"Data validation completed. Valid: {is_valid}, Issues: {len(issues)}")
        
        return JSONResponse(content={
            "status": "success",
            "is_valid": is_valid,
            "issues": issues,
            "issue_count": len(issues),
            "message": "Validation completed successfully" if is_valid else f"Found {len(issues)} issues"
        })
    except Exception as e:
        logger.error(f"Error validating data: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error validating data: {str(e)}"
        )


@router.post("/validate-fix", response_class=JSONResponse)
async def validate_and_fix_data_endpoint():
    """
    Validate sample data and fix issues automatically.
    Returns validation results and fixes applied.
    """
    try:
        from scripts.validate_sample_data import validate_data, sanitize_data
        
        logger.info("Starting data validation and fix...")
        
        # First validate
        is_valid, issues = validate_data(_data_path)
        
        # Then fix
        fixes = sanitize_data(_data_path, fix_issues=True)
        
        # Re-validate after fixes
        is_valid_after, issues_after = validate_data(_data_path)
        
        logger.info(f"Data validation and fix completed. Valid before: {is_valid}, Valid after: {is_valid_after}")
        
        return JSONResponse(content={
            "status": "success",
            "is_valid_before": is_valid,
            "is_valid_after": is_valid_after,
            "issues_before": issues,
            "issues_after": issues_after,
            "issue_count_before": len(issues),
            "issue_count_after": len(issues_after),
            "fixes_applied": fixes,
            "message": f"Fixed {sum(fixes.values())} issues. Validation {'passed' if is_valid_after else 'still has issues'}."
        })
    except Exception as e:
        logger.error(f"Error validating/fixing data: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error validating/fixing data: {str(e)}"
        )


@router.get("/leagues", response_class=HTMLResponse)
async def list_leagues():
    """List all leagues."""
    try:
        repos = _get_repositories()
        leagues = await repos['league'].get_all()
        
        # Sort leagues by level (ascending - level 3 is highest in dataset)
        leagues = sorted(leagues, key=lambda l: l.level)
        
        template = env.get_template("sample_data_leagues.html")
        return HTMLResponse(content=template.render(
            title="Leagues",
            leagues=leagues
        ))
    except Exception as e:
        from infrastructure.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error in list_leagues: {e}", exc_info=True)
        return HTMLResponse(content=f"<h1>Error</h1><p>{str(e)}</p>", status_code=500)


@router.get("/league-seasons", response_class=HTMLResponse)
async def list_league_seasons():
    """List all league seasons."""
    repos = _get_repositories()
    league_seasons = await repos['league_season'].get_all()
    leagues = await repos['league'].get_all()
    
    # Create a mapping of league_id to league name/abbreviation
    league_map = {league.id: league for league in leagues}
    
    # Enrich league seasons with league information
    enriched_seasons = []
    for ls in league_seasons:
        league = league_map.get(ls.league_id)
        enriched_seasons.append({
            'league_season': ls,
            'league_name': league.name if league else 'Unknown',
            'league_abbreviation': league.abbreviation if league else str(ls.league_id)[:8]
        })
    
    template = env.get_template("sample_data_league_seasons.html")
    return HTMLResponse(content=template.render(
        title="League Seasons",
        enriched_seasons=enriched_seasons
    ))


@router.get("/scoring-systems", response_class=HTMLResponse)
async def list_scoring_systems():
    """List all scoring systems."""
    repos = _get_repositories()
    scoring_systems = await repos['scoring_system'].get_all()
    
    # Sort by name
    scoring_systems = sorted(scoring_systems, key=lambda ss: ss.name)
    
    template = env.get_template("sample_data_scoring_systems.html")
    return HTMLResponse(content=template.render(
        title="Scoring Systems",
        scoring_systems=scoring_systems
    ))


@router.get("/clubs", response_class=HTMLResponse)
async def list_clubs():
    """List all clubs."""
    repos = _get_repositories()
    clubs = await repos['club'].get_all()
    
    # Sort by name
    clubs = sorted(clubs, key=lambda c: c.name)
    
    template = env.get_template("sample_data_clubs.html")
    return HTMLResponse(content=template.render(
        title="Clubs",
        clubs=clubs
    ))


@router.get("/club-players", response_class=HTMLResponse)
async def list_club_players():
    """List all club-player relationships."""
    repos = _get_repositories()
    club_players = await repos['club_player'].get_all()
    clubs = await repos['club'].get_all()
    players = await repos['player'].get_all()
    
    # Create mappings for quick lookup
    club_map = {club.id: club for club in clubs}
    player_map = {player.id: player for player in players}
    
    # Enrich club players with club and player information
    enriched_relationships = []
    for cp in club_players:
        club = club_map.get(cp.club_id)
        player = player_map.get(cp.player_id)
        
        enriched_relationships.append({
            'club_player': cp,
            'club_name': club.name if club else 'Unknown',
            'club_short_name': club.short_name if club else None,
            'player_name': player.name if player else 'Unknown',
            'player_dbu_id': player.dbu_id if player else None
        })
    
    # Sort by club name, then player name
    enriched_relationships.sort(key=lambda x: (
        x['club_name'],
        x['player_name']
    ))
    
    template = env.get_template("sample_data_club_players.html")
    return HTMLResponse(content=template.render(
        title="Club-Player Relationships",
        relationships=enriched_relationships
    ))


@router.get("/team-seasons", response_class=HTMLResponse)
async def list_team_seasons():
    """List all team seasons (team participation in league seasons)."""
    repos = _get_repositories()
    team_seasons = await repos['team_season'].get_all()
    clubs = await repos['club'].get_all()
    league_seasons = await repos['league_season'].get_all()
    leagues = await repos['league'].get_all()
    
    # Create mappings for quick lookup
    club_map = {club.id: club for club in clubs}
    league_season_map = {ls.id: ls for ls in league_seasons}
    league_map = {league.id: league for league in leagues}
    
    # Enrich team seasons with club, league, and season information
    enriched_seasons = []
    for ts in team_seasons:
        club = club_map.get(ts.club_id)
        league_season = league_season_map.get(ts.league_season_id)
        league = league_map.get(league_season.league_id) if league_season else None
        
        enriched_seasons.append({
            'team_season': ts,
            'club_name': club.name if club else 'Unknown',
            'club_short_name': club.short_name if club else None,
            'league_name': league.name if league else 'Unknown',
            'league_abbreviation': league.abbreviation if league else None,
            'season': str(league_season.season) if league_season else 'Unknown',
            'team_number': ts.team_number,
            'vacancy_status': ts.vacancy_status
        })
    
    # Sort by club name, then team number, then season
    enriched_seasons.sort(key=lambda x: (
        x['club_name'],
        x['team_number'],
        x['season']
    ))
    
    template = env.get_template("sample_data_team_seasons.html")
    return HTMLResponse(content=template.render(
        title="Team Seasons",
        enriched_seasons=enriched_seasons
    ))


@router.get("/players", response_class=HTMLResponse)
async def list_players():
    """List all players."""
    repos = _get_repositories()
    players = await repos['player'].get_all()
    
    template = env.get_template("sample_data_players.html")
    return HTMLResponse(content=template.render(
        title="Players",
        players=players
    ))


@router.get("/events", response_class=HTMLResponse)
async def list_events():
    """List all events."""
    repos = _get_repositories()
    events = await repos['event'].get_all()
    
    template = env.get_template("sample_data_events.html")
    return HTMLResponse(content=template.render(
        title="Events",
        events=events
    ))


@router.get("/games", response_class=HTMLResponse)
async def list_games():
    """List all game results (new data model)."""
    import pandas as pd
    from uuid import UUID
    
    # Read game_result.csv directly (repositories not implemented yet)
    game_result_path = _data_path / "game_result.csv"
    game_results = []
    
    if game_result_path.exists():
        df = pd.read_csv(game_result_path)
        for _, row in df.iterrows():
            game_results.append({
                'id': row['id'],
                'match_id': row['match_id'],
                'player_id': row['player_id'],
                'team_season_id': row['team_season_id'],
                'position': int(row['position']),
                'score': int(row['score']),  # Scores are integers
                'handicap': row['handicap'] if pd.notna(row['handicap']) and str(row['handicap']).strip() else None,
                'is_disqualified': bool(row['is_disqualified']) if pd.notna(row['is_disqualified']) else False
            })
    
    template = env.get_template("sample_data_games.html")
    return HTMLResponse(content=template.render(
        title="Game Results",
        games=game_results
    ))


@router.get("/api/leagues")
async def api_leagues() -> List[Dict[str, Any]]:
    """API endpoint for leagues."""
    repos = _get_repositories()
    leagues = await repos['league'].get_all()
    
    # Sort leagues by level (ascending - level 3 is highest in dataset)
    leagues = sorted(leagues, key=lambda l: l.level)
    
    return [
        {
            "id": str(league.id),
            "name": league.name,
            "abbreviation": league.abbreviation,
            "level": league.level
        }
        for league in leagues
    ]


@router.get("/api/league-seasons")
async def api_league_seasons() -> List[Dict[str, Any]]:
    """API endpoint for league seasons."""
    repos = _get_repositories()
    league_seasons = await repos['league_season'].get_all()
    return [
        {
            "id": str(ls.id),
            "league_id": str(ls.league_id),
            "season": str(ls.season),
            "scoring_system_id": ls.scoring_system_id,
            "number_of_teams": ls.number_of_teams,
            "players_per_team": ls.players_per_team
        }
        for ls in league_seasons
    ]


@router.get("/api/team-seasons")
async def api_team_seasons() -> List[Dict[str, Any]]:
    """API endpoint for team seasons."""
    repos = _get_repositories()
    team_seasons = await repos['team_season'].get_all()
    return [
        {
            "id": str(ts.id),
            "league_season_id": str(ts.league_season_id),
            "club_id": str(ts.club_id),
            "team_number": ts.team_number,
            "vacancy_status": ts.vacancy_status.value
        }
        for ts in team_seasons
    ]


@router.get("/api/clubs")
async def api_clubs() -> List[Dict[str, Any]]:
    """API endpoint for clubs."""
    repos = _get_repositories()
    clubs = await repos['club'].get_all()
    return [
        {
            "id": str(club.id),
            "name": club.name,
            "short_name": club.short_name,
            "home_alley_id": str(club.home_alley_id) if club.home_alley_id else None,
            "address": club.address
        }
        for club in clubs
    ]


@router.get("/api/players")
async def api_players() -> List[Dict[str, Any]]:
    """API endpoint for players."""
    repos = _get_repositories()
    players = await repos['player'].get_all()
    return [
        {
            "id": str(player.id),
            "dbu_id": player.dbu_id,
            "name": player.name
        }
        for player in players
    ]


@router.get("/api/events")
async def api_events() -> List[Dict[str, Any]]:
    """API endpoint for events."""
    repos = _get_repositories()
    events = await repos['event'].get_all()
    return [
        {
            "id": str(event.id),
            "league_season_id": str(event.league_season_id),
            "event_type": event.event_type,
            "league_week": event.league_week,
            "date": event.date.isoformat() if event.date else None,
            "venue_id": event.venue_id,
            "status": event.status.value
        }
        for event in events
    ]


@router.get("/api/games")
async def api_games() -> List[Dict[str, Any]]:
    """API endpoint for game results (new data model)."""
    import pandas as pd
    
    # Read game_result.csv directly (repositories not implemented yet)
    game_result_path = _data_path / "game_result.csv"
    game_results = []
    
    if game_result_path.exists():
        df = pd.read_csv(game_result_path)
        for _, row in df.iterrows():
            game_results.append({
                "id": row['id'],
                "match_id": row['match_id'],
                "player_id": row['player_id'],
                "team_season_id": row['team_season_id'],
                "position": int(row['position']),
                "score": int(row['score']),  # Scores are integers
                "handicap": row['handicap'] if pd.notna(row['handicap']) and str(row['handicap']).strip() else None,
                "is_disqualified": bool(row['is_disqualified']) if pd.notna(row['is_disqualified']) else False
            })
    
    return game_results


@router.get("/match-detail", response_class=HTMLResponse)
async def match_detail():
    """Show detailed information for a randomly selected match."""
    import pandas as pd
    import random
    
    # Load all CSV files
    match_path = _data_path / "match.csv"
    game_result_path = _data_path / "game_result.csv"
    position_comparison_path = _data_path / "position_comparison.csv"
    match_scoring_path = _data_path / "match_scoring.csv"
    event_path = _data_path / "event.csv"
    league_season_path = _data_path / "league_season.csv"
    league_path = _data_path / "league.csv"
    team_season_path = _data_path / "team_season.csv"
    club_path = _data_path / "club.csv"
    player_path = _data_path / "player.csv"
    
    if not match_path.exists():
        return HTMLResponse(content="<h1>No matches found</h1><p>Run seed script first.</p>")
    
    # Load data
    df_matches = pd.read_csv(match_path)
    df_game_results = pd.read_csv(game_result_path) if game_result_path.exists() else pd.DataFrame()
    df_position_comparisons = pd.read_csv(position_comparison_path) if position_comparison_path.exists() else pd.DataFrame()
    df_match_scoring = pd.read_csv(match_scoring_path) if match_scoring_path.exists() else pd.DataFrame()
    df_events = pd.read_csv(event_path) if event_path.exists() else pd.DataFrame()
    df_league_seasons = pd.read_csv(league_season_path) if league_season_path.exists() else pd.DataFrame()
    df_leagues = pd.read_csv(league_path) if league_path.exists() else pd.DataFrame()
    df_team_seasons = pd.read_csv(team_season_path) if team_season_path.exists() else pd.DataFrame()
    df_clubs = pd.read_csv(club_path) if club_path.exists() else pd.DataFrame()
    df_players = pd.read_csv(player_path) if player_path.exists() else pd.DataFrame()
    
    # Select random match
    if df_matches.empty:
        return HTMLResponse(content="<h1>No matches found</h1>")
    
    random_match = df_matches.sample(n=1).iloc[0]
    match_id = random_match['id']
    
    # Get match data
    event_id = random_match['event_id']
    round_number = int(random_match['round_number'])
    match_number = int(random_match['match_number'])
    team1_id = random_match['team1_team_season_id']
    team2_id = random_match['team2_team_season_id']
    team1_total = int(random_match['team1_total_score'])
    team2_total = int(random_match['team2_total_score'])
    
    # Get event info
    event_row = df_events[df_events['id'] == event_id] if not df_events.empty else pd.DataFrame()
    league_season_id = event_row.iloc[0]['league_season_id'] if not event_row.empty and 'league_season_id' in event_row.columns else None
    league_week = int(event_row.iloc[0]['league_week']) if not event_row.empty and 'league_week' in event_row.columns and pd.notna(event_row.iloc[0].get('league_week')) else None
    
    # Get league season info
    league_season_row = df_league_seasons[df_league_seasons['id'] == league_season_id] if league_season_id and not df_league_seasons.empty else pd.DataFrame()
    league_id = league_season_row.iloc[0]['league_id'] if not league_season_row.empty and 'league_id' in league_season_row.columns else None
    season_str = league_season_row.iloc[0]['season'] if not league_season_row.empty and 'season' in league_season_row.columns else None
    
    # Get league info
    league_row = df_leagues[df_leagues['id'] == league_id] if league_id and not df_leagues.empty else pd.DataFrame()
    league_name = league_row.iloc[0]['name'] if not league_row.empty and 'name' in league_row.columns else 'Unknown League'
    league_abbr = league_row.iloc[0]['abbreviation'] if not league_row.empty and 'abbreviation' in league_row.columns else None
    
    # Get team season info
    team1_row = df_team_seasons[df_team_seasons['id'] == team1_id] if not df_team_seasons.empty else pd.DataFrame()
    team2_row = df_team_seasons[df_team_seasons['id'] == team2_id] if not df_team_seasons.empty else pd.DataFrame()
    
    team1_club_id = team1_row.iloc[0]['club_id'] if not team1_row.empty and 'club_id' in team1_row.columns else None
    team1_number = int(team1_row.iloc[0]['team_number']) if not team1_row.empty and 'team_number' in team1_row.columns and pd.notna(team1_row.iloc[0].get('team_number')) else None
    
    team2_club_id = team2_row.iloc[0]['club_id'] if not team2_row.empty and 'club_id' in team2_row.columns else None
    team2_number = int(team2_row.iloc[0]['team_number']) if not team2_row.empty and 'team_number' in team2_row.columns and pd.notna(team2_row.iloc[0].get('team_number')) else None
    
    # Get club names
    club1_row = df_clubs[df_clubs['id'] == team1_club_id] if team1_club_id and not df_clubs.empty else pd.DataFrame()
    club2_row = df_clubs[df_clubs['id'] == team2_club_id] if team2_club_id and not df_clubs.empty else pd.DataFrame()
    
    club1_name = club1_row.iloc[0]['name'] if not club1_row.empty and 'name' in club1_row.columns else 'Unknown Club'
    club2_name = club2_row.iloc[0]['name'] if not club2_row.empty and 'name' in club2_row.columns else 'Unknown Club'
    
    team1_name = f"{club1_name} {team1_number}" if team1_number else club1_name
    team2_name = f"{club2_name} {team2_number}" if team2_number else club2_name
    
    # Get game results for this match
    match_game_results = df_game_results[df_game_results['match_id'] == match_id]
    
    # Get position comparisons
    match_comparisons = df_position_comparisons[df_position_comparisons['match_id'] == match_id] if not df_position_comparisons.empty else pd.DataFrame()
    
    # Get match scoring
    match_scoring_row = df_match_scoring[df_match_scoring['match_id'] == match_id] if not df_match_scoring.empty else pd.DataFrame()
    team1_individual_points = float(match_scoring_row.iloc[0]['team1_individual_points']) if not match_scoring_row.empty and 'team1_individual_points' in match_scoring_row.columns else 0.0
    team2_individual_points = float(match_scoring_row.iloc[0]['team2_individual_points']) if not match_scoring_row.empty and 'team2_individual_points' in match_scoring_row.columns else 0.0
    team1_match_points = float(match_scoring_row.iloc[0]['team1_match_points']) if not match_scoring_row.empty and 'team1_match_points' in match_scoring_row.columns else 0.0
    team2_match_points = float(match_scoring_row.iloc[0]['team2_match_points']) if not match_scoring_row.empty and 'team2_match_points' in match_scoring_row.columns else 0.0
    
    # Build position-by-position data
    position_data = []
    for position in range(4):  # Positions 0-3
        # Get comparison for this position
        comp_row = match_comparisons[match_comparisons['position'] == position] if not match_comparisons.empty else pd.DataFrame()
        
        if not comp_row.empty and 'team1_player_id' in comp_row.columns:
            team1_player_id = comp_row.iloc[0]['team1_player_id']
            team2_player_id = comp_row.iloc[0]['team2_player_id']
            team1_score = int(comp_row.iloc[0]['team1_score']) if 'team1_score' in comp_row.columns else 0
            team2_score = int(comp_row.iloc[0]['team2_score']) if 'team2_score' in comp_row.columns else 0
            outcome = comp_row.iloc[0]['outcome'] if 'outcome' in comp_row.columns else None
            
            # Get player names
            player1_row = df_players[df_players['id'] == team1_player_id] if not df_players.empty else pd.DataFrame()
            player2_row = df_players[df_players['id'] == team2_player_id] if not df_players.empty else pd.DataFrame()
            
            # Player CSV has 'full_name' column, not 'name'
            player1_name = player1_row.iloc[0]['full_name'] if not player1_row.empty and 'full_name' in player1_row.columns else 'Unknown Player'
            player2_name = player2_row.iloc[0]['full_name'] if not player2_row.empty and 'full_name' in player2_row.columns else 'Unknown Player'
            
            # Determine points gained
            if outcome == 'team1_win':
                team1_points = 1.0
                team2_points = 0.0
            elif outcome == 'team2_win':
                team1_points = 0.0
                team2_points = 1.0
            else:  # tie
                team1_points = 0.5
                team2_points = 0.5
            
            position_data.append({
                'position': position,
                'team1_player': player1_name,
                'team2_player': player2_name,
                'team1_score': team1_score,
                'team2_score': team2_score,
                'team1_points': team1_points,
                'team2_points': team2_points,
                'outcome': outcome
            })
        else:
            # No comparison found for this position
            position_data.append({
                'position': position,
                'team1_player': '-',
                'team2_player': '-',
                'team1_score': 0,
                'team2_score': 0,
                'team1_points': 0.0,
                'team2_points': 0.0,
                'outcome': None
            })
    
    template = env.get_template("sample_data_match_detail.html")
    return HTMLResponse(content=template.render(
        title="Match Detail",
        season=season_str or 'Unknown',
        league_name=league_name,
        league_abbr=league_abbr,
        league_week=league_week,
        round_number=round_number,
        match_number=match_number,
        team1_name=team1_name,
        team2_name=team2_name,
        team1_total=team1_total,
        team2_total=team2_total,
        team1_individual_points=team1_individual_points,
        team2_individual_points=team2_individual_points,
        team1_match_points=team1_match_points,
        team2_match_points=team2_match_points,
        position_data=position_data
    ))

