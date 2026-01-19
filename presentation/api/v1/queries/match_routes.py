"""
Match Query Routes (Preliminary Frontend).

⚠️ PRELIMINARY: This is a makeshift frontend for rapid iteration.
The application layer (queries/handlers) is production-ready.
This frontend can be refactored later without affecting the backend.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from uuid import UUID
from infrastructure.logging import get_logger
from application.validators import validate_uuid
from application.exceptions import ValidationError, EntityNotFoundError
from application.queries.league.get_match_overview_query import GetMatchOverviewQuery
from application.query_handlers.league.get_match_overview_handler import GetMatchOverviewHandler
from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
from infrastructure.persistence.repositories.csv.match_repository import PandasMatchRepository
from infrastructure.persistence.repositories.csv.event_repository import PandasEventRepository
from infrastructure.persistence.repositories.csv.league_season_repository import PandasLeagueSeasonRepository
from infrastructure.persistence.repositories.csv.league_repository import PandasLeagueRepository
from infrastructure.persistence.repositories.csv.team_season_repository import PandasTeamSeasonRepository
from infrastructure.persistence.repositories.csv.team_repository import PandasTeamRepository
from infrastructure.persistence.repositories.csv.club_repository import PandasClubRepository
from infrastructure.persistence.repositories.csv.position_comparison_repository import PandasPositionComparisonRepository
from infrastructure.persistence.repositories.csv.match_scoring_repository import PandasMatchScoringRepository
from infrastructure.persistence.repositories.csv.player_repository import PandasPlayerRepository
from infrastructure.persistence.repositories.csv.scoring_system_repository import PandasScoringSystemRepository
from infrastructure.persistence.mappers.csv.match_mapper import PandasMatchMapper
from infrastructure.persistence.mappers.csv.event_mapper import PandasEventMapper
from infrastructure.persistence.mappers.csv.league_season_mapper import PandasLeagueSeasonMapper
from infrastructure.persistence.mappers.csv.league_mapper import PandasLeagueMapper
from infrastructure.persistence.mappers.csv.team_season_mapper import PandasTeamSeasonMapper
from infrastructure.persistence.mappers.csv.team_mapper import PandasTeamMapper
from infrastructure.persistence.mappers.csv.club_mapper import PandasClubMapper
from infrastructure.persistence.mappers.csv.position_comparison_mapper import PandasPositionComparisonMapper
from infrastructure.persistence.mappers.csv.match_scoring_mapper import PandasMatchScoringMapper
from infrastructure.persistence.mappers.csv.player_mapper import PandasPlayerMapper
from infrastructure.persistence.mappers.csv.scoring_system_mapper import PandasScoringSystemMapper
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/matches", tags=["matches"])

# Initialize data adapter
_data_path = Path("sample_data/relational_csv")
_adapter = PandasDataAdapter(_data_path)

# Initialize mappers
_match_mapper = PandasMatchMapper()
_event_mapper = PandasEventMapper()
_league_season_mapper = PandasLeagueSeasonMapper()
_league_mapper = PandasLeagueMapper()
_team_season_mapper = PandasTeamSeasonMapper()
_team_mapper = PandasTeamMapper()
_club_mapper = PandasClubMapper()
_position_comparison_mapper = PandasPositionComparisonMapper()
_match_scoring_mapper = PandasMatchScoringMapper()
_player_mapper = PandasPlayerMapper()
_scoring_system_mapper = PandasScoringSystemMapper()

# Initialize repositories
_match_repo = PandasMatchRepository(_adapter, _match_mapper)
_event_repo = PandasEventRepository(_adapter, _event_mapper)
_league_season_repo = PandasLeagueSeasonRepository(_adapter, _league_season_mapper)
_league_repo = PandasLeagueRepository(_adapter, _league_mapper)
_team_season_repo = PandasTeamSeasonRepository(_adapter, _team_season_mapper)
_team_repo = PandasTeamRepository(_adapter, _team_mapper)
_club_repo = PandasClubRepository(_adapter, _club_mapper)
_position_comparison_repo = PandasPositionComparisonRepository(_adapter, _position_comparison_mapper)
_match_scoring_repo = PandasMatchScoringRepository(_adapter, _match_scoring_mapper)
_player_repo = PandasPlayerRepository(_adapter, _player_mapper)
_scoring_system_repo = PandasScoringSystemRepository(_adapter, _scoring_system_mapper)

# Initialize handler
_handler = GetMatchOverviewHandler(
    match_repository=_match_repo,
    event_repository=_event_repo,
    league_season_repository=_league_season_repo,
    league_repository=_league_repo,
    team_season_repository=_team_season_repo,
    team_repository=_team_repo,
    club_repository=_club_repo,
    position_comparison_repository=_position_comparison_repo,
    match_scoring_repository=_match_scoring_repo,
    player_repository=_player_repo,
    scoring_system_repository=_scoring_system_repo
)

# Initialize Jinja2 environment
_template_path = Path("presentation/templates")
_env = Environment(loader=FileSystemLoader(str(_template_path)))


@router.get("/{match_id}", response_class=JSONResponse)
async def get_match_overview_json(match_id: str):
    """
    Get match overview as JSON.
    
    Args:
        match_id: UUID of the match
    
    Returns:
        JSON response with match overview data
    """
    try:
        # Validate UUID
        validated_match_id = validate_uuid(match_id, "match_id")
        
        # Create query
        query = GetMatchOverviewQuery(match_id=validated_match_id)
        
        # Handle query
        result = await _handler.handle(query)
        
        # Convert DTO to dict for JSON response
        return JSONResponse(content={
            "match_id": str(result.match_id),
            "event_id": str(result.event_id),
            "league_id": str(result.league_id),
            "league_name": result.league_name,
            "league_abbreviation": result.league_abbreviation,
            "league_season_id": str(result.league_season_id),
            "season": result.season,
            "league_week": result.league_week,
            "round_number": result.round_number,
            "match_number": result.match_number,
            "team1": {
                "team_id": str(result.team1.team_id),
                "team_name": result.team1.team_name,
                "total_score": result.team1.total_score,
                "individual_points": result.team1.individual_points,
                "match_points": result.team1.match_points,
                "total_points": result.team1.total_points
            },
            "team2": {
                "team_id": str(result.team2.team_id),
                "team_name": result.team2.team_name,
                "total_score": result.team2.total_score,
                "individual_points": result.team2.individual_points,
                "match_points": result.team2.match_points,
                "total_points": result.team2.total_points
            },
            "position_comparisons": [
                {
                    "position": pc.position,
                    "team1_player_id": str(pc.team1_player_id),
                    "team1_player_name": pc.team1_player_name,
                    "team1_score": pc.team1_score,
                    "team1_points": pc.team1_points,
                    "team2_player_id": str(pc.team2_player_id),
                    "team2_player_name": pc.team2_player_name,
                    "team2_score": pc.team2_score,
                    "team2_points": pc.team2_points,
                    "outcome": pc.outcome
                }
                for pc in result.position_comparisons
            ],
            "calculated_at": result.calculated_at.isoformat()
        })
    
    except ValidationError as e:
        logger.error(f"Validation error getting match overview: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except EntityNotFoundError as e:
        logger.error(f"Entity not found getting match overview: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting match overview: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{match_id}/view", response_class=HTMLResponse)
async def get_match_overview_view(match_id: str):
    """
    Get match overview as HTML.
    
    Args:
        match_id: UUID of the match
    
    Returns:
        HTML response with match overview
    """
    try:
        # Validate UUID
        validated_match_id = validate_uuid(match_id, "match_id")
        
        # Create query
        query = GetMatchOverviewQuery(match_id=validated_match_id)
        
        # Handle query
        result = await _handler.handle(query)
        
        # Render template
        template = _env.get_template("match_overview_preliminary.html")
        return HTMLResponse(content=template.render(
            title="Match Overview",
            match_id=str(result.match_id),
            event_id=str(result.event_id),
            league_id=str(result.league_id),
            league_name=result.league_name,
            league_abbreviation=result.league_abbreviation,
            league_season_id=str(result.league_season_id),
            season=result.season,
            league_week=result.league_week,
            round_number=result.round_number,
            match_number=result.match_number,
            team1=result.team1,
            team2=result.team2,
            position_comparisons=result.position_comparisons,
            calculated_at=result.calculated_at
        ))
    
    except ValidationError as e:
        logger.error(f"Validation error getting match overview: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except EntityNotFoundError as e:
        logger.error(f"Entity not found getting match overview: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting match overview: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
