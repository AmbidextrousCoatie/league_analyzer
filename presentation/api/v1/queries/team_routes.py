"""
Team Query Routes (Preliminary Frontend).

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
from application.queries.league.get_team_score_sheet_query import GetTeamScoreSheetQuery
from application.query_handlers.league.get_team_score_sheet_handler import GetTeamScoreSheetHandler
from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
from infrastructure.persistence.repositories.csv.league_repository import PandasLeagueRepository
from infrastructure.persistence.repositories.csv.league_season_repository import PandasLeagueSeasonRepository
from infrastructure.persistence.repositories.csv.team_season_repository import PandasTeamSeasonRepository
from infrastructure.persistence.repositories.csv.event_repository import PandasEventRepository
from infrastructure.persistence.repositories.csv.match_repository import PandasMatchRepository
from infrastructure.persistence.repositories.csv.game_result_repository import PandasGameResultRepository
from infrastructure.persistence.repositories.csv.position_comparison_repository import PandasPositionComparisonRepository
from infrastructure.persistence.repositories.csv.scoring_system_repository import PandasScoringSystemRepository
from infrastructure.persistence.repositories.csv.player_repository import PandasPlayerRepository
from infrastructure.persistence.repositories.csv.club_repository import PandasClubRepository
from infrastructure.persistence.repositories.csv.team_repository import PandasTeamRepository
from infrastructure.persistence.mappers.csv.league_mapper import PandasLeagueMapper
from infrastructure.persistence.mappers.csv.league_season_mapper import PandasLeagueSeasonMapper
from infrastructure.persistence.mappers.csv.team_season_mapper import PandasTeamSeasonMapper
from infrastructure.persistence.mappers.csv.event_mapper import PandasEventMapper
from infrastructure.persistence.mappers.csv.match_mapper import PandasMatchMapper
from infrastructure.persistence.mappers.csv.game_result_mapper import PandasGameResultMapper
from infrastructure.persistence.mappers.csv.position_comparison_mapper import PandasPositionComparisonMapper
from infrastructure.persistence.mappers.csv.scoring_system_mapper import PandasScoringSystemMapper
from infrastructure.persistence.mappers.csv.player_mapper import PandasPlayerMapper
from infrastructure.persistence.mappers.csv.club_mapper import PandasClubMapper
from infrastructure.persistence.mappers.csv.team_mapper import PandasTeamMapper
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/teams", tags=["teams"])

# Setup Jinja2 for preliminary templates
_template_dir = Path(__file__).parent.parent.parent.parent / "templates"
env = Environment(loader=FileSystemLoader(str(_template_dir)))

# Initialize repositories - use sample data CSV files
_data_path = Path(__file__).parent.parent.parent.parent.parent / "sample_data" / "relational_csv"
_adapter = PandasDataAdapter(data_path=_data_path)

# Initialize repositories with mappers
_league_repo = PandasLeagueRepository(_adapter, PandasLeagueMapper())
_league_season_repo = PandasLeagueSeasonRepository(_adapter, PandasLeagueSeasonMapper())
_team_season_repo = PandasTeamSeasonRepository(_adapter, PandasTeamSeasonMapper())
_event_repo = PandasEventRepository(_adapter, PandasEventMapper())
_match_repo = PandasMatchRepository(_adapter, PandasMatchMapper())
_game_result_repo = PandasGameResultRepository(_adapter, PandasGameResultMapper())
_position_comparison_repo = PandasPositionComparisonRepository(_adapter, PandasPositionComparisonMapper())
_scoring_system_repo = PandasScoringSystemRepository(_adapter, PandasScoringSystemMapper())
_player_repo = PandasPlayerRepository(_adapter, PandasPlayerMapper())
_club_repo = PandasClubRepository(_adapter, PandasClubMapper())
_team_repo = PandasTeamRepository(_adapter, PandasTeamMapper())

# Initialize handler (production-ready application layer)
_handler = GetTeamScoreSheetHandler(
    league_repository=_league_repo,
    league_season_repository=_league_season_repo,
    team_season_repository=_team_season_repo,
    event_repository=_event_repo,
    match_repository=_match_repo,
    game_result_repository=_game_result_repo,
    position_comparison_repository=_position_comparison_repo,
    scoring_system_repository=_scoring_system_repo,
    player_repository=_player_repo,
    club_repository=_club_repo,
    team_repository=_team_repo
)


@router.get("/{team_season_id}/score-sheet", response_class=JSONResponse)
async def get_team_score_sheet_json(
    team_season_id: UUID,
    league_season_id: Optional[UUID] = None,
    week: Optional[int] = None
):
    """
    Get team score sheet (JSON response).
    
    ⚠️ PRELIMINARY: Simple JSON endpoint for rapid iteration.
    
    Args:
        team_season_id: UUID of the team season (required)
        league_season_id: Optional UUID of the league season (if None, derived from team_season)
        week: Optional week number to filter by (None = all weeks)
    """
    try:
        # If league_season_id not provided, derive it from team_season
        if league_season_id is None:
            team_season = await _team_season_repo.get_by_id(team_season_id)
            if not team_season:
                raise HTTPException(status_code=404, detail=f"TeamSeason {team_season_id} not found")
            league_season_id = team_season.league_season_id
        
        query = GetTeamScoreSheetQuery(
            league_season_id=league_season_id,
            team_season_id=team_season_id,
            week=week
        )
        result = await _handler.handle(query)
        
        # Convert DTO to dict for JSON response
        return {
            "league_season_id": str(result.league_season_id),
            "league_name": result.league_name,
            "season": result.season,
            "team_season_id": str(result.team_season_id),
            "team_name": result.team_name,
            "week": result.week,
            "matches": [
                {
                    "match_id": str(m.match_id),
                    "event_id": str(m.event_id),
                    "week": m.week,
                    "round_number": m.round_number,
                    "match_number": m.match_number,
                    "opponent_team_season_id": str(m.opponent_team_season_id),
                    "opponent_team_name": m.opponent_team_name,
                    "team_total_score": m.team_total_score,
                    "opponent_total_score": m.opponent_total_score,
                    "team_match_points": m.team_match_points,
                    "opponent_match_points": m.opponent_match_points,
                    "position_scores": [
                        {
                            "position": ps.position,
                            "player_id": str(ps.player_id),
                            "player_name": ps.player_name,
                            "score": ps.score,
                            "opponent_player_id": str(ps.opponent_player_id),
                            "opponent_player_name": ps.opponent_player_name,
                            "opponent_score": ps.opponent_score,
                            "points": ps.points
                        }
                        for ps in m.position_scores
                    ]
                }
                for m in result.matches
            ],
            "position_summaries": [
                {
                    "position": ps.position,
                    "total_points": ps.total_points,
                    "matches_played": ps.matches_played
                }
                for ps in result.position_summaries
            ],
            "total_team_match_points": result.total_team_match_points,
            "total_individual_points": result.total_individual_points,
            "total_points": result.total_points,
            "wins": result.wins,
            "losses": result.losses,
            "ties": result.ties
        }
    except Exception as e:
        logger.error(f"Error getting team score sheet: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{team_season_id}/score-sheet/view", response_class=HTMLResponse)
async def get_team_score_sheet_view(
    team_season_id: UUID,
    league_season_id: Optional[UUID] = None,
    week: Optional[int] = None
):
    """
    Get team score sheet (HTML view).
    
    ⚠️ PRELIMINARY: Simple HTML template for rapid iteration.
    Will be replaced with proper Vue.js frontend in Phase 5.
    
    Args:
        team_season_id: UUID of the team season (required)
        league_season_id: Optional UUID of the league season (if None, derived from team_season)
        week: Optional week number to filter by (None = all weeks)
    """
    try:
        # If league_season_id not provided, derive it from team_season
        if league_season_id is None:
            team_season = await _team_season_repo.get_by_id(team_season_id)
            if not team_season:
                raise HTTPException(status_code=404, detail=f"TeamSeason {team_season_id} not found")
            league_season_id = team_season.league_season_id
        
        query = GetTeamScoreSheetQuery(
            league_season_id=league_season_id,
            team_season_id=team_season_id,
            week=week
        )
        result = await _handler.handle(query)
        
        # Render preliminary template
        template = env.get_template("team_score_sheet.html")
        return template.render(
            league_name=result.league_name,
            season=result.season,
            team_name=result.team_name,
            week=result.week,
            matches=result.matches,
            position_summaries=result.position_summaries,
            total_team_match_points=result.total_team_match_points,
            total_individual_points=result.total_individual_points,
            total_points=result.total_points,
            wins=result.wins,
            losses=result.losses,
            ties=result.ties
        )
    except Exception as e:
        logger.error(f"Error getting team score sheet: {e}", exc_info=True)
        return HTMLResponse(
            content=f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>",
            status_code=500
        )
