"""
League Slug-Based Routes

Human-readable routes for league standings using slugs instead of UUIDs.

Examples:
    /leagues/bayl/standings?season=2025-26
    /leagues/bayl/standings?season=25/26
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional
from infrastructure.logging import get_logger
from application.queries.league.get_league_standings_query import GetLeagueStandingsQuery
from application.query_handlers.league.get_league_standings_handler import GetLeagueStandingsHandler
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
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from presentation.api.v1.queries.slug_utils import (
    resolve_league_by_abbreviation,
    resolve_league_season_by_league_and_season,
    normalize_season_string
)

logger = get_logger(__name__)

router = APIRouter(prefix="/leagues", tags=["leagues-slug"])

# Setup Jinja2 for preliminary templates
_template_dir = Path(__file__).parent.parent.parent.parent / "templates"
env = Environment(loader=FileSystemLoader(str(_template_dir)))

# Initialize repositories - use sample data CSV files
_data_path = Path(__file__).parent.parent.parent.parent.parent / "sample_data" / "relational_csv"
_adapter = PandasDataAdapter(data_path=_data_path)

# Initialize repositories with mappers
_league_repo = PandasLeagueRepository(_adapter, PandasLeagueMapper())
_league_season_repo = PandasLeagueSeasonRepository(_adapter, PandasLeagueSeasonMapper())
_event_repo = PandasEventRepository(_adapter, PandasEventMapper())
_match_repo = PandasMatchRepository(_adapter, PandasMatchMapper())
_game_result_repo = PandasGameResultRepository(_adapter, PandasGameResultMapper())
_position_comparison_repo = PandasPositionComparisonRepository(_adapter, PandasPositionComparisonMapper())
_team_season_repo = PandasTeamSeasonRepository(_adapter, PandasTeamSeasonMapper())
_team_repo = PandasTeamRepository(_adapter, PandasTeamMapper())
_club_repo = PandasClubRepository(_adapter, PandasClubMapper())
_scoring_system_repo = PandasScoringSystemRepository(_adapter, PandasScoringSystemMapper())

# Initialize domain service
_standings_calculator = StandingsCalculator()

# Initialize handler (production-ready application layer)
_handler = GetLeagueStandingsHandler(
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


@router.get("/{league_abbreviation}/standings", response_class=JSONResponse)
async def get_league_standings_json_slug(
    league_abbreviation: str,
    season: Optional[str] = Query(None, description="Season (e.g., '2025-26' or '25/26')"),
    week: Optional[int] = Query(None, description="Week number (optional)")
):
    """
    Get league standings (JSON response) using league abbreviation slug.
    
    Examples:
        /leagues/bayl/standings?season=2025-26
        /leagues/bayl/standings?season=25/26&week=1
    """
    try:
        # Resolve league abbreviation to league_id
        league_id = await resolve_league_by_abbreviation(league_abbreviation, _league_repo)
        if not league_id:
            raise HTTPException(
                status_code=404,
                detail=f"League with abbreviation '{league_abbreviation}' not found"
            )
        
        # Resolve season to league_season_id if provided
        league_season_id = None
        if season:
            league_season_id = await resolve_league_season_by_league_and_season(
                league_id, season, _league_season_repo
            )
            if not league_season_id:
                raise HTTPException(
                    status_code=404,
                    detail=f"League season '{season}' not found for league '{league_abbreviation}'"
                )
        
        # Use existing handler
        query = GetLeagueStandingsQuery(
            league_id=league_id,
            league_season_id=league_season_id,
            week=week
        )
        result = await _handler.handle(query)
        
        # Convert DTO to dict for JSON response
        return {
            "league_id": str(result.league_id),
            "league_name": result.league_name,
            "league_season_id": str(result.league_season_id),
            "season": result.season,
            "week": result.week,
            "status": result.status,
            "calculated_at": result.calculated_at.isoformat(),
            "standings": [
                {
                    "team_id": str(standing.team_id),
                    "team_name": standing.team_name,
                    "position": standing.position,
                    "total_score": standing.total_score,
                    "total_points": standing.total_points,
                    "average_score": standing.average_score,
                    "games_played": standing.games_played,
                    "wins": standing.wins,
                    "losses": standing.losses,
                    "ties": standing.ties,
                    "weekly_performances": [
                        {
                            "week": wp.week,
                            "score": wp.score,
                            "points": wp.points,
                            "number_of_games": wp.number_of_games
                        }
                        for wp in standing.weekly_performances
                    ]
                }
                for standing in result.standings
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting league standings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{league_abbreviation}/standings/view", response_class=HTMLResponse)
async def get_league_standings_view_slug(
    league_abbreviation: str,
    season: Optional[str] = Query(None, description="Season (e.g., '2025-26' or '25/26')"),
    week: Optional[int] = Query(None, description="Week number (optional)")
):
    """
    Get league standings (HTML view) using league abbreviation slug.
    
    Examples:
        /leagues/bayl/standings/view?season=2025-26
        /leagues/bayl/standings/view?season=25/26&week=1
    """
    try:
        # Resolve league abbreviation to league_id
        league_id = await resolve_league_by_abbreviation(league_abbreviation, _league_repo)
        if not league_id:
            raise HTTPException(
                status_code=404,
                detail=f"League with abbreviation '{league_abbreviation}' not found"
            )
        
        # Resolve season to league_season_id if provided
        league_season_id = None
        if season:
            league_season_id = await resolve_league_season_by_league_and_season(
                league_id, season, _league_season_repo
            )
            if not league_season_id:
                raise HTTPException(
                    status_code=404,
                    detail=f"League season '{season}' not found for league '{league_abbreviation}'"
                )
        
        # Use existing handler
        query = GetLeagueStandingsQuery(
            league_id=league_id,
            league_season_id=league_season_id,
            week=week
        )
        result = await _handler.handle(query)
        
        # Render preliminary template
        template = env.get_template("standings_preliminary.html")
        return template.render(
            league_name=result.league_name,
            season=result.season,
            week=result.week,
            standings=result.standings,
            weekly_standings=result.weekly_standings,
            status=result.status
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting league standings: {e}", exc_info=True)
        # Simple error page
        return HTMLResponse(
            content=f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>",
            status_code=500
        )
