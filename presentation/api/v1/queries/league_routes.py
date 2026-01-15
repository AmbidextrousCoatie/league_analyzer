"""
League Query Routes (Preliminary Frontend).

⚠️ PRELIMINARY: This is a makeshift frontend for rapid iteration.
The application layer (queries/handlers) is production-ready.
This frontend can be refactored later without affecting the backend.

See: docs/planning/PHASE3_FRONTEND_STRATEGY.md
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from uuid import UUID
from typing import Optional
from infrastructure.logging import get_logger
from application.validators import validate_uuid, validate_optional_uuid, validate_week_number
from application.exceptions import ValidationError, EntityNotFoundError
from application.queries.league.get_league_standings_query import GetLeagueStandingsQuery
from application.queries.league.get_league_history_query import GetLeagueHistoryQuery
from application.query_handlers.league.get_league_standings_handler import GetLeagueStandingsHandler
from application.query_handlers.league.get_league_history_handler import GetLeagueHistoryHandler
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
from infrastructure.persistence.repositories.csv.player_repository import PandasPlayerRepository
from infrastructure.persistence.mappers.csv.player_mapper import PandasPlayerMapper
from domain.domain_services.standings_calculator import StandingsCalculator
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/leagues", tags=["leagues"])

# Setup Jinja2 for preliminary templates
# Go up from: presentation/api/v1/queries/league_routes.py
# To: presentation/templates
_template_dir = Path(__file__).parent.parent.parent.parent / "templates"
env = Environment(loader=FileSystemLoader(str(_template_dir)))

# Initialize repositories - use sample data CSV files
# Go up from: presentation/api/v1/queries/league_routes.py
# To: league_analyzer root, then sample_data/relational_csv
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
_player_repo = PandasPlayerRepository(_adapter, PandasPlayerMapper())

# Initialize domain service
_standings_calculator = StandingsCalculator()

# Initialize handlers (production-ready application layer)
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

_history_handler = GetLeagueHistoryHandler(
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
    player_repository=_player_repo,
    standings_handler=_standings_handler
)


@router.get("/{league_id}/standings", response_class=JSONResponse)
async def get_league_standings_json(
    league_id: UUID,
    league_season_id: Optional[UUID] = None,
    week: Optional[int] = None
):
    """
    Get league standings (JSON response).
    
    ⚠️ PRELIMINARY: Simple JSON endpoint for rapid iteration.
    """
    try:
        # Validate inputs
        validated_league_id = validate_uuid(league_id, "league_id")
        validated_league_season_id = validate_optional_uuid(league_season_id, "league_season_id")
        validated_week = validate_week_number(week, "week")
        
        query = GetLeagueStandingsQuery(
            league_id=validated_league_id,
            league_season_id=validated_league_season_id,
            week=validated_week
        )
        result = await _standings_handler.handle(query)
        
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
    except ValidationError as e:
        logger.warning(f"Validation error in league standings: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except EntityNotFoundError as e:
        logger.warning(f"Entity not found in league standings: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting league standings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{league_id}/standings/view", response_class=HTMLResponse)
async def get_league_standings_view(
    league_id: UUID,
    league_season_id: Optional[UUID] = None,
    week: Optional[int] = None
):
    """
    Get league standings (HTML view).
    
    ⚠️ PRELIMINARY: Simple HTML template for rapid iteration.
    Will be replaced with proper Vue.js frontend in Phase 5.
    """
    try:
        query = GetLeagueStandingsQuery(
            league_id=league_id,
            league_season_id=league_season_id,
            week=week
        )
        result = await _standings_handler.handle(query)
        
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
    except ValidationError as e:
        logger.warning(f"Validation error in league standings view: {e}")
        return HTMLResponse(
            content=f"<html><body><h1>Validation Error</h1><p>{str(e)}</p></body></html>",
            status_code=400
        )
    except EntityNotFoundError as e:
        logger.warning(f"Entity not found in league standings view: {e}")
        return HTMLResponse(
            content=f"<html><body><h1>Not Found</h1><p>{str(e)}</p></body></html>",
            status_code=404
        )
    except Exception as e:
        logger.error(f"Error getting league standings: {e}", exc_info=True)
        # Simple error page
        return HTMLResponse(
            content=f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>",
            status_code=500
        )


@router.get("/{league_id}/history", response_class=JSONResponse)
async def get_league_history_json(league_id: UUID):
    """
    Get league history (JSON response).
    
    ⚠️ PRELIMINARY: Simple JSON endpoint for rapid iteration.
    """
    try:
        query = GetLeagueHistoryQuery(league_id=league_id)
        result = await _history_handler.handle(query)
        
        # Convert DTO to dict for JSON response
        return {
            "league_id": str(result.league_id),
            "league_name": result.league_name,
            "first_season": result.first_season,
            "most_recent_season": result.most_recent_season,
            "total_seasons": result.total_seasons,
            "calculated_at": result.calculated_at.isoformat(),
            "season_summaries": [
                {
                    "season": summary.season,
                    "year": summary.year,
                    "league_season_id": str(summary.league_season_id),
                    "league_average": summary.league_average,
                    "number_of_teams": summary.number_of_teams,
                    "number_of_weeks": summary.number_of_weeks,
                    "number_of_games": summary.number_of_games,
                    "top_three": {
                        "first_place": {
                            "team_id": str(top_three.first_place.team_id),
                            "team_name": top_three.first_place.team_name,
                            "total_points": top_three.first_place.total_points,
                            "average_score": top_three.first_place.average_score
                        } if top_three.first_place else None,
                        "second_place": {
                            "team_id": str(top_three.second_place.team_id),
                            "team_name": top_three.second_place.team_name,
                            "total_points": top_three.second_place.total_points,
                            "average_score": top_three.second_place.average_score
                        } if top_three.second_place else None,
                        "third_place": {
                            "team_id": str(top_three.third_place.team_id),
                            "team_name": top_three.third_place.team_name,
                            "total_points": top_three.third_place.total_points,
                            "average_score": top_three.third_place.average_score
                        } if top_three.third_place else None
                    }
                }
                for summary in result.season_summaries
                for top_three in [summary.top_three]
            ],
            "league_average_trend": result.league_average_trend,
            "all_time_records": [
                {
                    "record_type": record.record_type,
                    "value": record.value,
                    "holder_id": str(record.holder_id),
                    "holder_name": record.holder_name,
                    "season": record.season,
                    "league_season_id": str(record.league_season_id),
                    "date": record.date.isoformat() if record.date else None,
                    "week": record.week
                }
                for record in result.all_time_records
            ]
        }
    except ValidationError as e:
        logger.warning(f"Validation error in league history: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except EntityNotFoundError as e:
        logger.warning(f"Entity not found in league history: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting league history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{league_id}/history/view", response_class=HTMLResponse)
async def get_league_history_view(league_id: UUID):
    """
    Get league history (HTML view).
    
    ⚠️ PRELIMINARY: Simple HTML template for rapid iteration.
    Will be replaced with proper Vue.js frontend in Phase 5.
    """
    try:
        query = GetLeagueHistoryQuery(league_id=league_id)
        result = await _history_handler.handle(query)
        
        # Render preliminary template
        template = env.get_template("league_history_preliminary.html")
        return template.render(
            league_name=result.league_name,
            first_season=result.first_season,
            most_recent_season=result.most_recent_season,
            total_seasons=result.total_seasons,
            season_summaries=result.season_summaries,
            league_average_trend=result.league_average_trend,
            all_time_records=result.all_time_records
        )
    except ValidationError as e:
        logger.warning(f"Validation error in league history view: {e}")
        return HTMLResponse(
            content=f"<html><body><h1>Validation Error</h1><p>{str(e)}</p></body></html>",
            status_code=400
        )
    except EntityNotFoundError as e:
        logger.warning(f"Entity not found in league history view: {e}")
        return HTMLResponse(
            content=f"<html><body><h1>Not Found</h1><p>{str(e)}</p></body></html>",
            status_code=404
        )
    except Exception as e:
        logger.error(f"Error getting league history: {e}", exc_info=True)
        # Simple error page
        return HTMLResponse(
            content=f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>",
            status_code=500
        )
