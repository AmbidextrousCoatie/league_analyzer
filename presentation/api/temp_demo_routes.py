"""
TEMPORARY DEMO ROUTES - Uses Real Handlers

These routes demonstrate the application layer handlers using real seed data.
They provide quick access to standings, statistics, and match data.

TODO: These can be removed once proper frontend is implemented, or kept as quick demo endpoints.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Dict, List, Optional
from uuid import UUID
from infrastructure.logging import get_logger
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from application.queries.league.get_league_standings_query import GetLeagueStandingsQuery
from application.query_handlers.league.get_league_standings_handler import GetLeagueStandingsHandler
from application.exceptions import ValidationError, EntityNotFoundError
from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
from infrastructure.persistence.repositories.csv.league_repository import PandasLeagueRepository
from infrastructure.persistence.repositories.csv.league_season_repository import PandasLeagueSeasonRepository
from infrastructure.persistence.repositories.csv.event_repository import PandasEventRepository
from infrastructure.persistence.repositories.csv.match_repository import PandasMatchRepository
from infrastructure.persistence.repositories.csv.game_result_repository import PandasGameResultRepository
from infrastructure.persistence.repositories.csv.position_comparison_repository import PandasPositionComparisonRepository
from infrastructure.persistence.repositories.csv.team_season_repository import PandasTeamSeasonRepository
from infrastructure.persistence.repositories.csv.team_repository import PandasTeamRepository
from infrastructure.persistence.repositories.csv.club_repository import PandasClubRepository
from infrastructure.persistence.repositories.csv.scoring_system_repository import PandasScoringSystemRepository
from infrastructure.persistence.mappers.csv.league_mapper import PandasLeagueMapper
from infrastructure.persistence.mappers.csv.league_season_mapper import PandasLeagueSeasonMapper
from infrastructure.persistence.mappers.csv.event_mapper import PandasEventMapper
from infrastructure.persistence.mappers.csv.match_mapper import PandasMatchMapper
from infrastructure.persistence.mappers.csv.game_result_mapper import PandasGameResultMapper
from infrastructure.persistence.mappers.csv.position_comparison_mapper import PandasPositionComparisonMapper
from infrastructure.persistence.mappers.csv.team_season_mapper import PandasTeamSeasonMapper
from infrastructure.persistence.mappers.csv.team_mapper import PandasTeamMapper
from infrastructure.persistence.mappers.csv.club_mapper import PandasClubMapper
from infrastructure.persistence.mappers.csv.scoring_system_mapper import PandasScoringSystemMapper
from domain.domain_services.standings_calculator import StandingsCalculator

logger = get_logger(__name__)

router = APIRouter(prefix="/api/temp/demo", tags=["TEMPORARY - Demo"])

# Setup Jinja2 for preliminary templates
# File is at: presentation/api/temp_demo_routes.py
# Templates are at: presentation/templates/
_template_dir = Path(__file__).parent.parent / "templates"
_jinja_env = Environment(loader=FileSystemLoader(str(_template_dir)))

# Initialize data adapter and repositories (same as in league_routes.py)
_data_path = Path("sample_data/relational_csv")
_adapter = PandasDataAdapter(_data_path)

# Initialize mappers
_league_mapper = PandasLeagueMapper()
_league_season_mapper = PandasLeagueSeasonMapper()
_event_mapper = PandasEventMapper()
_match_mapper = PandasMatchMapper()
_game_result_mapper = PandasGameResultMapper()
_position_comparison_mapper = PandasPositionComparisonMapper()
_team_season_mapper = PandasTeamSeasonMapper()
_team_mapper = PandasTeamMapper()
_club_mapper = PandasClubMapper()
_scoring_system_mapper = PandasScoringSystemMapper()

# Initialize repositories
_league_repo = PandasLeagueRepository(_adapter, _league_mapper)
_league_season_repo = PandasLeagueSeasonRepository(_adapter, _league_season_mapper)
_event_repo = PandasEventRepository(_adapter, _event_mapper)
_match_repo = PandasMatchRepository(_adapter, _match_mapper)
_game_result_repo = PandasGameResultRepository(_adapter, _game_result_mapper)
_position_comparison_repo = PandasPositionComparisonRepository(_adapter, _position_comparison_mapper)
_team_season_repo = PandasTeamSeasonRepository(_adapter, _team_season_mapper)
_team_repo = PandasTeamRepository(_adapter, _team_mapper)
_club_repo = PandasClubRepository(_adapter, _club_mapper)
_scoring_system_repo = PandasScoringSystemRepository(_adapter, _scoring_system_mapper)

# Initialize domain service
_standings_calculator = StandingsCalculator()

# Initialize handler
_standings_handler = GetLeagueStandingsHandler(
    league_repository=_league_repo,
    league_season_repository=_league_season_repo,
    event_repository=_event_repo,
    match_repository=_match_repo,
    game_result_repository=_game_result_repo,
    position_comparison_repository=_position_comparison_repo,
    team_season_repository=_team_season_repo,
    team_repository=_team_repo,
    club_repository=_club_repo,
    scoring_system_repository=_scoring_system_repo,
    standings_calculator=_standings_calculator
)


# Removed create_demo_data() - now using real handlers and seed data


@router.get("/standings/view", response_class=HTMLResponse)
async def get_standings_view(
    request: Request,
    league_abbreviation: Optional[str] = "bayl",
    season: Optional[str] = None
):
    """
    TEMPORARY: Get league standings HTML view using real handlers and seed data.
    
    This endpoint uses GetLeagueStandingsHandler to access real seed data.
    Defaults to "bayl" league if not specified.
    """
    logger.info(f"Demo endpoint: /api/temp/demo/standings/view accessed (league={league_abbreviation}, season={season})")
    
    try:
        # Resolve league abbreviation to league_id
        from presentation.api.v1.queries.slug_utils import resolve_league_by_abbreviation
        league_id = await resolve_league_by_abbreviation(league_abbreviation, _league_repo)
        if not league_id:
            raise HTTPException(
                status_code=404,
                detail=f"League with abbreviation '{league_abbreviation}' not found"
            )
        
        # Resolve season to league_season_id if provided
        league_season_id = None
        if season:
            from presentation.api.v1.queries.slug_utils import resolve_league_season_by_league_and_season
            from application.validators import validate_season_string
            validated_season = validate_season_string(season, "season")
            league_season_id = await resolve_league_season_by_league_and_season(
                league_id, validated_season, _league_season_repo
            )
            if not league_season_id:
                raise HTTPException(
                    status_code=404,
                    detail=f"League season '{season}' not found for league '{league_abbreviation}'"
                )
        
        # Use real handler
        query = GetLeagueStandingsQuery(
            league_id=league_id,
            league_season_id=league_season_id,
            week=None
        )
        result = await _standings_handler.handle(query)
        
        # Render template
        template = _jinja_env.get_template("demo_standings_preliminary.html")
        return HTMLResponse(content=template.render(
            request=request,
            title=f"Demo Standings - {result.league_name}",
            league_name=result.league_name,
            season=result.season,
            week=result.week,
            status=result.status,
            standings=result.standings,
            weekly_standings=result.weekly_standings
        ))
    
    except ValidationError as e:
        logger.error(f"Validation error in demo standings view: {e}")
        return HTMLResponse(
            content=f"<html><body><h1>Validation Error</h1><p>{str(e)}</p></body></html>",
            status_code=400
        )
    except EntityNotFoundError as e:
        logger.error(f"Entity not found in demo standings view: {e}")
        return HTMLResponse(
            content=f"<html><body><h1>Not Found</h1><p>{str(e)}</p></body></html>",
            status_code=404
        )
    except Exception as e:
        logger.error(f"Error in demo standings view: {e}", exc_info=True)
        return HTMLResponse(
            content=f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>",
            status_code=500
        )


@router.get("/standings", response_class=JSONResponse)
async def get_standings(league_abbreviation: Optional[str] = "bayl", season: Optional[str] = None):
    """
    TEMPORARY: Get league standings using real handlers and seed data.
    
    This endpoint uses GetLeagueStandingsHandler to access real seed data.
    Defaults to "bayl" league if not specified.
    
    Args:
        league_abbreviation: League abbreviation (default: "bayl")
        season: Optional season string (e.g., "25/26" or "2025-26")
    
    Returns:
        League standings from real seed data
    """
    logger.info(f"Demo endpoint: /api/temp/demo/standings accessed (league={league_abbreviation}, season={season})")
    
    try:
        # Resolve league abbreviation to league_id
        from presentation.api.v1.queries.slug_utils import resolve_league_by_abbreviation
        league_id = await resolve_league_by_abbreviation(league_abbreviation, _league_repo)
        if not league_id:
            raise HTTPException(
                status_code=404,
                detail=f"League with abbreviation '{league_abbreviation}' not found"
            )
        
        # Resolve season to league_season_id if provided
        league_season_id = None
        if season:
            from presentation.api.v1.queries.slug_utils import resolve_league_season_by_league_and_season
            from application.validators import validate_season_string
            validated_season = validate_season_string(season, "season")
            league_season_id = await resolve_league_season_by_league_and_season(
                league_id, validated_season, _league_season_repo
            )
            if not league_season_id:
                raise HTTPException(
                    status_code=404,
                    detail=f"League season '{season}' not found for league '{league_abbreviation}'"
                )
        
        # Use real handler
        query = GetLeagueStandingsQuery(
            league_id=league_id,
            league_season_id=league_season_id,
            week=None
        )
        result = await _standings_handler.handle(query)
        
        # Convert to JSON-serializable format
        standings_list = []
        for standing in result.standings:
            weekly_perfs = []
            for wp in standing.weekly_performances:
                weekly_perfs.append({
                    'week': wp.week,
                    'score': wp.score,
                    'points': wp.points,
                    'games': wp.number_of_games
                })
            
            standings_list.append({
                'team_id': str(standing.team_id),
                'team_name': standing.team_name,
                'position': standing.position,
                'total_score': standing.total_score,
                'total_points': standing.total_points,
                'average_score': standing.average_score,
                'games_played': standing.games_played,
                'wins': standing.wins,
                'losses': standing.losses,
                'ties': standing.ties,
                'weekly_performances': weekly_perfs
            })
        
        return {
            'league_id': str(result.league_id),
            'league_name': result.league_name,
            'league_season_id': str(result.league_season_id),
            'season': result.season,
            'week': result.week,
            'status': result.status,
            'calculated_at': result.calculated_at.isoformat(),
            'standings': standings_list,
            'note': 'Uses real seed data via GetLeagueStandingsHandler'
        }
    
    except ValidationError as e:
        logger.error(f"Validation error in demo standings: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except EntityNotFoundError as e:
        logger.error(f"Entity not found in demo standings: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in demo standings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/team-statistics/{team_name}")
async def get_team_statistics(team_name: str):
    """
    TEMPORARY: Get team statistics - placeholder for future implementation.
    
    TODO: Implement GetTeamStatisticsHandler and use it here.
    For now, this endpoint is disabled as it requires team statistics handler.
    """
    logger.info(f"Demo endpoint: /api/temp/demo/team-statistics/{team_name} accessed")
    
    return {
        'error': 'Team statistics endpoint not yet implemented',
        'note': 'Will use GetTeamStatisticsHandler when implemented',
        'suggestion': 'Use /api/v1/teams/{team_season_id}/score-sheet for team data'
    }


@router.get("/player-statistics/{player_name}")
async def get_player_statistics(player_name: str):
    """
    TEMPORARY: Get player statistics - placeholder for future implementation.
    
    TODO: Implement GetPlayerStatisticsHandler and use it here.
    For now, this endpoint is disabled as it requires player statistics handler.
    """
    logger.info(f"Demo endpoint: /api/temp/demo/player-statistics/{player_name} accessed")
    
    return {
        'error': 'Player statistics endpoint not yet implemented',
        'note': 'Will use GetPlayerStatisticsHandler when implemented',
        'suggestion': 'Use /api/v1/players/{player_slug}/stats for player data'
    }


@router.get("/demo-data/view", response_class=HTMLResponse)
async def get_demo_data_view(request: Request):
    """
    TEMPORARY: Get list of available leagues from seed data (HTML view).
    
    Useful for debugging and understanding what data is available.
    """
    logger.info("Demo endpoint: /api/temp/demo/demo-data/view accessed")
    
    try:
        # Get all leagues from seed data
        leagues = await _league_repo.get_all()
        
        league_list = []
        for league in leagues:
            # Get league seasons for this league
            league_seasons = await _league_season_repo.get_by_league(league.id)
            
            league_list.append({
                'id': str(league.id),
                'name': league.name,
                'abbreviation': league.abbreviation,
                'level': league.level,
                'seasons': [str(ls.season) for ls in league_seasons]
            })
        
        # Render template
        template = _jinja_env.get_template("demo_data_preliminary.html")
        return HTMLResponse(content=template.render(
            request=request,
            title="Demo Data - Available Leagues",
            leagues=league_list
        ))
    
    except Exception as e:
        logger.error(f"Error getting demo data view: {e}", exc_info=True)
        return HTMLResponse(
            content=f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>",
            status_code=500
        )


@router.get("/demo-data", response_class=JSONResponse)
async def get_demo_data():
    """
    TEMPORARY: Get list of available leagues from seed data.
    
    Useful for debugging and understanding what data is available.
    """
    logger.info("Demo endpoint: /api/temp/demo/demo-data accessed")
    
    try:
        # Get all leagues from seed data
        leagues = await _league_repo.get_all()
        
        league_list = []
        for league in leagues:
            # Get league seasons for this league
            league_seasons = await _league_season_repo.get_by_league(league.id)
            
            league_list.append({
                'id': str(league.id),
                'name': league.name,
                'abbreviation': league.abbreviation,
                'level': league.level,
                'seasons': [str(ls.season) for ls in league_seasons]
            })
        
        return {
            'leagues': league_list,
            'note': 'Uses real seed data via repositories',
            'suggestion': 'Use /api/temp/demo/standings?league_abbreviation=bayl to see standings'
        }
    
    except Exception as e:
        logger.error(f"Error getting demo data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

