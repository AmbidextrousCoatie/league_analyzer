"""
Player Slug-Based Routes

Human-readable routes for player statistics using slugs instead of UUIDs.

Examples:
    /players/max-mustermann/stats?season=25-26
    /players/max-mustermann/stats?league=bayl&season=25-26
    /players/max-mustermann/history
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional
from pathlib import Path
from infrastructure.logging import get_logger
from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
from infrastructure.persistence.repositories.csv.player_repository import PandasPlayerRepository
from infrastructure.persistence.mappers.csv.player_mapper import PandasPlayerMapper
from presentation.api.v1.queries.slug_utils import (
    resolve_player_by_slug,
    slugify
)

logger = get_logger(__name__)

router = APIRouter(prefix="/players", tags=["players-slug"])

# Initialize repositories - use sample data CSV files
_data_path = Path(__file__).parent.parent.parent.parent.parent / "sample_data" / "relational_csv"
_adapter = PandasDataAdapter(data_path=_data_path)

# Initialize repositories with mappers
_player_repo = PandasPlayerRepository(_adapter, PandasPlayerMapper())


@router.get("/{player_slug}/stats", response_class=JSONResponse)
async def get_player_stats_json_slug(
    player_slug: str,
    season: Optional[str] = Query(None, description="Season (e.g., '2025-26' or '25/26')"),
    league: Optional[str] = Query(None, description="League abbreviation (e.g., 'bayl')"),
    team: Optional[str] = Query(None, description="Team (format: 'club-slug/team-number', e.g., 'bk-muenchen/3')"),
    tournament: Optional[str] = Query(None, description="Tournament ID"),
    club: Optional[str] = Query(None, description="Club slug"),
    week: Optional[int] = Query(None, description="Week number (optional)")
):
    """
    Get player statistics (JSON response) using player slug.
    
    Examples:
        /players/max-mustermann/stats?season=25-26
        /players/max-mustermann/stats?league=bayl&season=25-26
        /players/max-mustermann/stats?team=bk-muenchen/3&season=25-26
    """
    try:
        # Resolve player slug to player_id
        player_id = await resolve_player_by_slug(player_slug, _player_repo)
        if not player_id:
            # Get available players for better error message
            all_players = await _player_repo.get_all()
            available_players = []
            for player in all_players[:10]:  # Limit to first 10
                available_players.append(f"'{player.name}' (slug: '{slugify(player.name)}')")
            
            raise HTTPException(
                status_code=404,
                detail=f"Player with slug '{player_slug}' not found. Available players: {', '.join(available_players)}"
            )
        
        # TODO: Implement player stats query handler
        # For now, return not implemented
        raise HTTPException(
            status_code=501,
            detail="Player statistics query handler not yet implemented. This will be available in Phase 3."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting player stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{player_slug}/stats/view", response_class=HTMLResponse)
async def get_player_stats_view_slug(
    player_slug: str,
    season: Optional[str] = Query(None, description="Season (e.g., '2025-26' or '25/26')"),
    league: Optional[str] = Query(None, description="League abbreviation (e.g., 'bayl')"),
    team: Optional[str] = Query(None, description="Team (format: 'club-slug/team-number')"),
    tournament: Optional[str] = Query(None, description="Tournament ID"),
    club: Optional[str] = Query(None, description="Club slug"),
    week: Optional[int] = Query(None, description="Week number (optional)")
):
    """
    Get player statistics (HTML view) using player slug.
    
    Examples:
        /players/max-mustermann/stats/view?season=25-26
        /players/max-mustermann/stats/view?league=bayl&season=25-26
    """
    try:
        # Resolve player slug to player_id
        player_id = await resolve_player_by_slug(player_slug, _player_repo)
        if not player_id:
            raise HTTPException(
                status_code=404,
                detail=f"Player with slug '{player_slug}' not found"
            )
        
        # TODO: Implement player stats query handler
        # For now, return not implemented
        return HTMLResponse(
            content="<html><body><h1>Not Implemented</h1><p>Player statistics query handler not yet implemented. This will be available in Phase 3.</p></body></html>",
            status_code=501
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting player stats: {e}", exc_info=True)
        return HTMLResponse(
            content=f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>",
            status_code=500
        )


@router.get("/{player_slug}/history", response_class=JSONResponse)
async def get_player_history_json_slug(
    player_slug: str
):
    """
    Get player history (all teams, clubs, leagues, tournaments).
    
    Examples:
        /players/max-mustermann/history
    """
    try:
        # Resolve player slug to player_id
        player_id = await resolve_player_by_slug(player_slug, _player_repo)
        if not player_id:
            raise HTTPException(
                status_code=404,
                detail=f"Player with slug '{player_slug}' not found"
            )
        
        # TODO: Implement player history query handler
        raise HTTPException(
            status_code=501,
            detail="Player history query handler not yet implemented. This will be available in Phase 3."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting player history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{player_slug}/teams", response_class=JSONResponse)
async def get_player_teams_json_slug(
    player_slug: str
):
    """
    Get all teams a player has played for.
    
    Examples:
        /players/max-mustermann/teams
    """
    try:
        # Resolve player slug to player_id
        player_id = await resolve_player_by_slug(player_slug, _player_repo)
        if not player_id:
            raise HTTPException(
                status_code=404,
                detail=f"Player with slug '{player_slug}' not found"
            )
        
        # TODO: Implement player teams query handler
        raise HTTPException(
            status_code=501,
            detail="Player teams query handler not yet implemented. This will be available in Phase 3."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting player teams: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{player_slug}/clubs", response_class=JSONResponse)
async def get_player_clubs_json_slug(
    player_slug: str
):
    """
    Get all clubs a player has been member of.
    
    Examples:
        /players/max-mustermann/clubs
    """
    try:
        # Resolve player slug to player_id
        player_id = await resolve_player_by_slug(player_slug, _player_repo)
        if not player_id:
            raise HTTPException(
                status_code=404,
                detail=f"Player with slug '{player_slug}' not found"
            )
        
        # TODO: Implement player clubs query handler
        raise HTTPException(
            status_code=501,
            detail="Player clubs query handler not yet implemented. This will be available in Phase 3."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting player clubs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{player_slug}/leagues", response_class=JSONResponse)
async def get_player_leagues_json_slug(
    player_slug: str
):
    """
    Get all leagues a player has competed in.
    
    Examples:
        /players/max-mustermann/leagues
    """
    try:
        # Resolve player slug to player_id
        player_id = await resolve_player_by_slug(player_slug, _player_repo)
        if not player_id:
            raise HTTPException(
                status_code=404,
                detail=f"Player with slug '{player_slug}' not found"
            )
        
        # TODO: Implement player leagues query handler
        raise HTTPException(
            status_code=501,
            detail="Player leagues query handler not yet implemented. This will be available in Phase 3."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting player leagues: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
