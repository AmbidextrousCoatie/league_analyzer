"""
Team Slug-Based Routes

Human-readable routes for team score sheets using slugs instead of UUIDs.

Examples:
    /clubs/bc-munchen/teams/1/seasons/2025-26/score-sheet
    /clubs/bc-munchen/teams/1/seasons/25/26/score-sheet?week=1
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
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
from presentation.api.v1.queries.slug_utils import (
    slugify,
    resolve_club_by_slug,
    resolve_team_by_club_and_number,
    resolve_league_season_by_league_and_season,
    resolve_team_season_by_team_and_league_season,
    normalize_season_string
)

logger = get_logger(__name__)

router = APIRouter(prefix="/clubs", tags=["teams-slug"])

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


@router.get("/{club_slug}/teams/{team_number}/seasons/{season}/score-sheet", response_class=JSONResponse)
async def get_team_score_sheet_json_slug(
    club_slug: str,
    team_number: int,
    season: str,
    week: Optional[int] = Query(None, description="Week number (optional)")
):
    """
    Get team score sheet (JSON response) using club slug, team number, and season.
    
    Examples:
        /clubs/bc-munchen/teams/1/seasons/2025-26/score-sheet
        /clubs/bc-munchen/teams/1/seasons/25/26/score-sheet?week=1
    """
    try:
        # Resolve club slug to club_id
        club_id = await resolve_club_by_slug(club_slug, _club_repo)
        if not club_id:
            # Get available clubs for better error message
            all_clubs = await _club_repo.get_all()
            available_clubs = []
            for club in all_clubs:
                from presentation.api.v1.queries.slug_utils import slugify
                available_clubs.append(f"'{club.name}' (slug: '{slugify(club.name)}')")
            
            raise HTTPException(
                status_code=404,
                detail=f"Club with slug '{club_slug}' not found. Available clubs: {', '.join(available_clubs[:10])}"  # Limit to first 10
            )
        
        # Resolve team by club_id and team_number
        team_id = await resolve_team_by_club_and_number(club_id, team_number, _team_repo)
        if not team_id:
            # Get available teams for better error message
            all_teams = await _team_repo.get_by_club(club_id)
            available_teams = sorted([team.team_number for team in all_teams])
            
            if available_teams:
                available_teams_str = ', '.join([f"{tn}" for tn in available_teams])
                raise HTTPException(
                    status_code=404,
                    detail=f"Team {team_number} not found for club '{club_slug}'. Available teams: {available_teams_str}"
                )
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Team {team_number} not found for club '{club_slug}'. No teams found for this club."
                )
        
        # Get all league seasons to find the one matching the season string
        # We need to find which league this team participates in for the given season
        all_league_seasons = await _league_season_repo.get_all()
        team_seasons = await _team_season_repo.get_by_team(team_id)
        
        # Find team_season_id for the given season
        league_season_id = None
        for ts in team_seasons:
            ls = next((ls for ls in all_league_seasons if ls.id == ts.league_season_id), None)
            if ls:
                # Normalize season strings for comparison
                ls_season_str = str(ls.season).replace('-', '/').strip()
                normalized_season = normalize_season_string(season)
                normalized_ls_season = normalize_season_string(ls_season_str)
                
                if normalized_ls_season == normalized_season:
                    league_season_id = ls.id
                    break
        
        if not league_season_id:
            raise HTTPException(
                status_code=404,
                detail=f"Team {team_number} from club '{club_slug}' not found in season '{season}'"
            )
        
        # Resolve team_season_id
        team_season_id = await resolve_team_season_by_team_and_league_season(
            team_id, league_season_id, _team_season_repo
        )
        if not team_season_id:
            raise HTTPException(
                status_code=404,
                detail=f"Team season not found for team {team_number} from club '{club_slug}' in season '{season}'"
            )
        
        # Use existing handler
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting team score sheet: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{club_slug}/teams/{team_number}/seasons/{season}/score-sheet/view", response_class=HTMLResponse)
async def get_team_score_sheet_view_slug(
    club_slug: str,
    team_number: int,
    season: str,
    week: Optional[int] = Query(None, description="Week number (optional)")
):
    """
    Get team score sheet (HTML view) using club slug, team number, and season.
    
    Examples:
        /clubs/bc-munchen/teams/1/seasons/2025-26/score-sheet/view
        /clubs/bc-munchen/teams/1/seasons/25/26/score-sheet/view?week=1
    """
    try:
        # Resolve club slug to club_id
        club_id = await resolve_club_by_slug(club_slug, _club_repo)
        if not club_id:
            # Get available clubs for better error message
            all_clubs = await _club_repo.get_all()
            available_clubs = []
            for club in all_clubs:
                from presentation.api.v1.queries.slug_utils import slugify
                available_clubs.append(f"'{club.name}' (slug: '{slugify(club.name)}')")
            
            raise HTTPException(
                status_code=404,
                detail=f"Club with slug '{club_slug}' not found. Available clubs: {', '.join(available_clubs[:10])}"  # Limit to first 10
            )
        
        # Resolve team by club_id and team_number
        team_id = await resolve_team_by_club_and_number(club_id, team_number, _team_repo)
        if not team_id:
            # Get available teams for better error message
            all_teams = await _team_repo.get_by_club(club_id)
            available_teams = sorted([team.team_number for team in all_teams])
            
            if available_teams:
                available_teams_str = ', '.join([f"{tn}" for tn in available_teams])
                raise HTTPException(
                    status_code=404,
                    detail=f"Team {team_number} not found for club '{club_slug}'. Available teams: {available_teams_str}"
                )
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Team {team_number} not found for club '{club_slug}'. No teams found for this club."
                )
        
        # Get all league seasons to find the one matching the season string
        all_league_seasons = await _league_season_repo.get_all()
        team_seasons = await _team_season_repo.get_by_team(team_id)
        
        # Find team_season_id for the given season
        league_season_id = None
        for ts in team_seasons:
            ls = next((ls for ls in all_league_seasons if ls.id == ts.league_season_id), None)
            if ls:
                # Normalize season strings for comparison
                ls_season_str = str(ls.season).replace('-', '/').strip()
                normalized_season = normalize_season_string(season)
                normalized_ls_season = normalize_season_string(ls_season_str)
                
                if normalized_ls_season == normalized_season:
                    league_season_id = ls.id
                    break
        
        if not league_season_id:
            raise HTTPException(
                status_code=404,
                detail=f"Team {team_number} from club '{club_slug}' not found in season '{season}'"
            )
        
        # Resolve team_season_id
        team_season_id = await resolve_team_season_by_team_and_league_season(
            team_id, league_season_id, _team_season_repo
        )
        if not team_season_id:
            raise HTTPException(
                status_code=404,
                detail=f"Team season not found for team {team_number} from club '{club_slug}' in season '{season}'"
            )
        
        # Use existing handler
        query = GetTeamScoreSheetQuery(
            league_season_id=league_season_id,
            team_season_id=team_season_id,
            week=week
        )
        result = await _handler.handle(query)
        
        # Render template
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting team score sheet: {e}", exc_info=True)
        return HTMLResponse(
            content=f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>",
            status_code=500
        )


