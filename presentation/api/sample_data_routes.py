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
from domain.entities.team import Team
from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
from infrastructure.persistence.mappers.csv.event_mapper import PandasEventMapper
from infrastructure.persistence.mappers.csv.league_season_mapper import PandasLeagueSeasonMapper
from infrastructure.persistence.mappers.csv.team_season_mapper import PandasTeamSeasonMapper
from infrastructure.persistence.mappers.csv.game_mapper import PandasGameMapper
from infrastructure.persistence.mappers.csv.player_mapper import PandasPlayerMapper
from infrastructure.persistence.mappers.csv.league_mapper import PandasLeagueMapper
from infrastructure.persistence.mappers.csv.team_mapper import PandasTeamMapper
from infrastructure.persistence.mappers.csv.club_mapper import PandasClubMapper
from infrastructure.persistence.repositories.csv.event_repository import PandasEventRepository
from infrastructure.persistence.repositories.csv.league_season_repository import PandasLeagueSeasonRepository
from infrastructure.persistence.repositories.csv.team_season_repository import PandasTeamSeasonRepository
from infrastructure.persistence.repositories.csv.game_repository import PandasGameRepository
from infrastructure.persistence.repositories.csv.player_repository import PandasPlayerRepository
from infrastructure.persistence.repositories.csv.league_repository import PandasLeagueRepository
from infrastructure.persistence.repositories.csv.team_repository import PandasTeamRepository
from infrastructure.persistence.repositories.csv.club_repository import PandasClubRepository
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
        'team': PandasTeamRepository(adapter, PandasTeamMapper()),
        'club': PandasClubRepository(adapter, PandasClubMapper())
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


@router.get("/teams", response_class=HTMLResponse)
async def list_teams():
    """List all teams (club squads)."""
    repos = _get_repositories()
    teams = await repos['team'].get_all()
    clubs = await repos['club'].get_all()
    
    # Create mapping for quick lookup
    club_map = {club.id: club for club in clubs}
    
    # Enrich teams with club information
    enriched_teams = []
    for team in teams:
        club = club_map.get(team.club_id)
        enriched_teams.append({
            'team': team,
            'club_name': club.name if club else 'Unknown',
            'club_short_name': club.short_name if club else None
        })
    
    # Sort by club name, then team number
    enriched_teams.sort(key=lambda x: (
        x['club_name'],
        x['team'].team_number
    ))
    
    template = env.get_template("sample_data_teams.html")
    return HTMLResponse(content=template.render(
        title="Teams",
        enriched_teams=enriched_teams
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
    """List all games."""
    repos = _get_repositories()
    games = await repos['game'].get_all()
    
    template = env.get_template("sample_data_games.html")
    return HTMLResponse(content=template.render(
        title="Games",
        games=games
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


@router.get("/api/teams")
async def api_teams() -> List[Dict[str, Any]]:
    """API endpoint for teams."""
    repos = _get_repositories()
    teams = await repos['team'].get_all()
    return [
        {
            "id": str(team.id),
            "name": team.name,
            "club_id": str(team.club_id) if team.club_id else None,
            "team_number": team.team_number
        }
        for team in teams
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


@router.get("/api/players")
async def api_players() -> List[Dict[str, Any]]:
    """API endpoint for players."""
    repos = _get_repositories()
    players = await repos['player'].get_all()
    return [
        {
            "id": str(player.id),
            "dbu_id": player.dbu_id,
            "name": player.name,
            "club_id": str(player.club_id) if player.club_id else None
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
    """API endpoint for games."""
    repos = _get_repositories()
    games = await repos['game'].get_all()
    return [
        {
            "id": str(game.id),
            "event_id": str(game.event_id) if game.event_id else None,
            "team_id": str(game.team_id) if game.team_id else None,
            "opponent_team_id": str(game.opponent_team_id) if game.opponent_team_id else None,
            "match_number": game.match_number,
            "round_number": game.round_number
        }
        for game in games
    ]

