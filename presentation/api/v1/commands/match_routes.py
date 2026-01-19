"""
Match Command Routes.

API routes for match/game commands (CreateGame, UpdateGame, DeleteGame).
"""

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from uuid import UUID
from typing import Optional
from pydantic import BaseModel
from infrastructure.logging import get_logger
from application.commands.league.create_game_command import CreateGameCommand
from application.commands.league.update_game_command import UpdateGameCommand
from application.commands.league.delete_game_command import DeleteGameCommand
from application.command_handlers.league.create_game_handler import CreateGameHandler
from application.command_handlers.league.update_game_handler import UpdateGameHandler
from application.command_handlers.league.delete_game_handler import DeleteGameHandler
from application.exceptions import ValidationError, EntityNotFoundError
from application.validators import validate_uuid
from domain.entities.match import MatchStatus
from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
from infrastructure.persistence.repositories.csv.match_repository import PandasMatchRepository
from infrastructure.persistence.repositories.csv.event_repository import PandasEventRepository
from infrastructure.persistence.repositories.csv.team_season_repository import PandasTeamSeasonRepository
from infrastructure.persistence.mappers.csv.match_mapper import PandasMatchMapper
from infrastructure.persistence.mappers.csv.event_mapper import PandasEventMapper
from infrastructure.persistence.mappers.csv.team_season_mapper import PandasTeamSeasonMapper
from pathlib import Path

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/matches", tags=["Matches (Commands)"])

# Initialize repositories - use sample data CSV files
_data_path = Path(__file__).parent.parent.parent.parent.parent / "sample_data" / "relational_csv"
_adapter = PandasDataAdapter(data_path=_data_path)

# Initialize repositories with mappers
_match_repo = PandasMatchRepository(_adapter, PandasMatchMapper())
_event_repo = PandasEventRepository(_adapter, PandasEventMapper())
_team_season_repo = PandasTeamSeasonRepository(_adapter, PandasTeamSeasonMapper())

# Initialize handlers
_create_handler = CreateGameHandler(
    match_repository=_match_repo,
    event_repository=_event_repo,
    team_season_repository=_team_season_repo
)

_update_handler = UpdateGameHandler(
    match_repository=_match_repo,
    event_repository=_event_repo,
    team_season_repository=_team_season_repo
)

_delete_handler = DeleteGameHandler(
    match_repository=_match_repo
)


# Request models
class CreateGameRequest(BaseModel):
    """Request model for creating a game."""
    event_id: UUID
    team1_team_season_id: UUID
    team2_team_season_id: UUID
    round_number: int = 1
    match_number: int = 0
    team1_total_score: float = 0.0
    team2_total_score: float = 0.0
    status: Optional[str] = "scheduled"


class UpdateGameRequest(BaseModel):
    """Request model for updating a game."""
    event_id: Optional[UUID] = None
    team1_team_season_id: Optional[UUID] = None
    team2_team_season_id: Optional[UUID] = None
    round_number: Optional[int] = None
    match_number: Optional[int] = None
    team1_total_score: Optional[float] = None
    team2_total_score: Optional[float] = None
    status: Optional[str] = None


@router.post("/", response_class=JSONResponse)
async def create_game(request: CreateGameRequest = Body(...)):
    """
    Create a new match/game.
    
    Args:
        request: CreateGameRequest with match data
    
    Returns:
        JSONResponse with created match ID
    """
    try:
        # Validate UUIDs
        validated_event_id = validate_uuid(request.event_id, "event_id")
        validated_team1_id = validate_uuid(request.team1_team_season_id, "team1_team_season_id")
        validated_team2_id = validate_uuid(request.team2_team_season_id, "team2_team_season_id")
        
        # Parse status
        status = MatchStatus.SCHEDULED
        if request.status:
            try:
                status = MatchStatus(request.status.lower())
            except ValueError:
                raise ValidationError(f"Invalid status: {request.status}")
        
        # Create command
        command = CreateGameCommand(
            event_id=validated_event_id,
            team1_team_season_id=validated_team1_id,
            team2_team_season_id=validated_team2_id,
            round_number=request.round_number,
            match_number=request.match_number,
            team1_total_score=request.team1_total_score,
            team2_total_score=request.team2_total_score,
            status=status
        )
        
        # Execute command
        result = await _create_handler.handle(command)
        
        return JSONResponse(
            content={
                "success": result.success,
                "message": result.message,
                "match_id": str(result.match_id),
                "command_id": str(result.command_id),
                "timestamp": result.timestamp.isoformat()
            },
            status_code=201
        )
    except ValidationError as e:
        logger.warning(f"Validation error in create game: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except EntityNotFoundError as e:
        logger.warning(f"Entity not found in create game: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating game: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{match_id}", response_class=JSONResponse)
async def update_game(
    match_id: UUID,
    request: UpdateGameRequest = Body(...)
):
    """
    Update an existing match/game.
    
    Args:
        match_id: UUID of the match to update
        request: UpdateGameRequest with fields to update
    
    Returns:
        JSONResponse with updated match ID
    """
    try:
        # Validate match_id
        validated_match_id = validate_uuid(match_id, "match_id")
        
        # Validate optional UUIDs if provided
        validated_event_id = None
        if request.event_id is not None:
            validated_event_id = validate_uuid(request.event_id, "event_id")
        
        validated_team1_id = None
        if request.team1_team_season_id is not None:
            validated_team1_id = validate_uuid(request.team1_team_season_id, "team1_team_season_id")
        
        validated_team2_id = None
        if request.team2_team_season_id is not None:
            validated_team2_id = validate_uuid(request.team2_team_season_id, "team2_team_season_id")
        
        # Parse status if provided
        status = None
        if request.status:
            try:
                status = MatchStatus(request.status.lower())
            except ValueError:
                raise ValidationError(f"Invalid status: {request.status}")
        
        # Create command
        command = UpdateGameCommand(
            match_id=validated_match_id,
            event_id=validated_event_id,
            team1_team_season_id=validated_team1_id,
            team2_team_season_id=validated_team2_id,
            round_number=request.round_number,
            match_number=request.match_number,
            team1_total_score=request.team1_total_score,
            team2_total_score=request.team2_total_score,
            status=status
        )
        
        # Execute command
        result = await _update_handler.handle(command)
        
        return JSONResponse(
            content={
                "success": result.success,
                "message": result.message,
                "match_id": str(result.match_id),
                "command_id": str(result.command_id),
                "timestamp": result.timestamp.isoformat()
            }
        )
    except ValidationError as e:
        logger.warning(f"Validation error in update game: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except EntityNotFoundError as e:
        logger.warning(f"Entity not found in update game: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating game: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{match_id}", response_class=JSONResponse)
async def delete_game(match_id: UUID):
    """
    Delete a match/game.
    
    Args:
        match_id: UUID of the match to delete
    
    Returns:
        JSONResponse with deleted match ID
    """
    try:
        # Validate match_id
        validated_match_id = validate_uuid(match_id, "match_id")
        
        # Create command
        command = DeleteGameCommand(match_id=validated_match_id)
        
        # Execute command
        result = await _delete_handler.handle(command)
        
        return JSONResponse(
            content={
                "success": result.success,
                "message": result.message,
                "match_id": str(result.match_id),
                "command_id": str(result.command_id),
                "timestamp": result.timestamp.isoformat()
            }
        )
    except ValidationError as e:
        logger.warning(f"Validation error in delete game: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except EntityNotFoundError as e:
        logger.warning(f"Entity not found in delete game: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting game: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
