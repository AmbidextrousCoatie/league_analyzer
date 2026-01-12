"""
Slug Resolution Utilities

Utilities for converting between human-readable slugs and entity IDs.
"""

import re
from typing import Optional
from uuid import UUID
from infrastructure.logging import get_logger
from domain.repositories.league_repository import LeagueRepository
from domain.repositories.league_season_repository import LeagueSeasonRepository
from domain.repositories.club_repository import ClubRepository
from domain.repositories.team_repository import TeamRepository
from domain.repositories.team_season_repository import TeamSeasonRepository
from domain.repositories.player_repository import PlayerRepository
from domain.value_objects.season import Season

logger = get_logger(__name__)


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.
    
    Handles German umlauts:
        ä -> ae, ö -> oe, ü -> ue, ß -> ss
    
    Examples:
        "BK München" -> "bk-muenchen"
        "BC Comet Nürnberg" -> "bc-comet-nurnberg"
        "BayL" -> "bayl"
        "2025-26" -> "2025-26"
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Replace German umlauts and special characters
    replacements = {
        'ä': 'ae',
        'ö': 'oe',
        'ü': 'ue',
        'ß': 'ss',
        'à': 'a',
        'á': 'a',
        'â': 'a',
        'ã': 'a',
        'è': 'e',
        'é': 'e',
        'ê': 'e',
        'ì': 'i',
        'í': 'i',
        'î': 'i',
        'ò': 'o',
        'ó': 'o',
        'ô': 'o',
        'õ': 'o',
        'ù': 'u',
        'ú': 'u',
        'û': 'u',
        'ý': 'y',
        'ÿ': 'y',
        'ç': 'c',
        'ñ': 'n'
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    # Replace spaces and remaining special characters with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    
    # Remove leading/trailing hyphens
    text = text.strip('-')
    
    return text


async def resolve_league_by_abbreviation(
    abbreviation: str,
    league_repo: LeagueRepository
) -> Optional[UUID]:
    """
    Resolve league abbreviation to league_id.
    
    Args:
        abbreviation: League abbreviation (e.g., "BayL", "LL N1")
        league_repo: League repository
        
    Returns:
        League UUID if found, None otherwise
    """
    try:
        leagues = await league_repo.get_all()
        for league in leagues:
            if league.abbreviation.lower() == abbreviation.lower():
                return league.id
        return None
    except Exception as e:
        logger.error(f"Error resolving league by abbreviation '{abbreviation}': {e}")
        return None


async def resolve_league_season_by_league_and_season(
    league_id: UUID,
    season_str: str,
    league_season_repo: LeagueSeasonRepository
) -> Optional[UUID]:
    """
    Resolve league_id + season string to league_season_id.
    
    Args:
        league_id: League UUID
        season_str: Season string (e.g., "2025-26", "25/26")
        league_season_repo: LeagueSeason repository
        
    Returns:
        LeagueSeason UUID if found, None otherwise
    """
    try:
        # Normalize season string
        normalized_season = normalize_season_string(season_str)
        
        league_seasons = await league_season_repo.get_all()
        for ls in league_seasons:
            if ls.league_id == league_id:
                # Compare normalized season strings
                ls_season_str = str(ls.season).replace('-', '/').strip()
                normalized_ls_season = normalize_season_string(ls_season_str)
                
                if normalized_ls_season == normalized_season:
                    return ls.id
        
        return None
    except Exception as e:
        logger.error(f"Error resolving league season for league {league_id}, season {season_str}: {e}")
        return None


async def resolve_club_by_slug(
    club_slug: str,
    club_repo: ClubRepository
) -> Optional[UUID]:
    """
    Resolve club slug to club_id.
    
    Args:
        club_slug: Club slug (e.g., "bk-muenchen")
        club_repo: Club repository
        
    Returns:
        Club UUID if found, None otherwise
    """
    try:
        clubs = await club_repo.get_all()
        available_slugs = []
        for club in clubs:
            club_slug_normalized = slugify(club.name)
            available_slugs.append((club.name, club_slug_normalized))
            if club_slug_normalized == club_slug:
                return club.id
        
        # Log available clubs for debugging
        logger.debug(f"Club slug '{club_slug}' not found. Available clubs:")
        for name, slug in available_slugs:
            logger.debug(f"  '{name}' -> '{slug}'")
        
        return None
    except Exception as e:
        logger.error(f"Error resolving club by slug '{club_slug}': {e}")
        return None


async def resolve_team_by_club_and_number(
    club_id: UUID,
    team_number: int,
    team_repo: TeamRepository
) -> Optional[UUID]:
    """
    Resolve club_id + team_number to team_id.
    
    Args:
        club_id: Club UUID
        team_number: Team number (1, 2, 3, ...)
        team_repo: Team repository
        
    Returns:
        Team UUID if found, None otherwise
    """
    try:
        teams = await team_repo.get_by_club(club_id)
        for team in teams:
            if team.team_number == team_number:
                return team.id
        return None
    except Exception as e:
        logger.error(f"Error resolving team for club {club_id}, team {team_number}: {e}")
        return None


async def resolve_team_season_by_team_and_league_season(
    team_id: UUID,
    league_season_id: UUID,
    team_season_repo: TeamSeasonRepository
) -> Optional[UUID]:
    """
    Resolve team_id + league_season_id to team_season_id.
    
    Args:
        team_id: Team UUID
        league_season_id: LeagueSeason UUID
        team_season_repo: TeamSeason repository
        
    Returns:
        TeamSeason UUID if found, None otherwise
    """
    try:
        team_seasons = await team_season_repo.get_by_league_season(league_season_id)
        for ts in team_seasons:
            if ts.team_id == team_id:
                return ts.id
        return None
    except Exception as e:
        logger.error(f"Error resolving team season for team {team_id}, league_season {league_season_id}: {e}")
        return None


async def resolve_player_by_slug(
    player_slug: str,
    player_repo: PlayerRepository
) -> Optional[UUID]:
    """
    Resolve player slug to player_id.
    
    Args:
        player_slug: Player slug (e.g., "max-mustermann")
        player_repo: Player repository
        
    Returns:
        Player UUID if found, None otherwise
    """
    try:
        players = await player_repo.get_all()
        available_slugs = []
        for player in players:
            player_slug_normalized = slugify(player.name)
            available_slugs.append((player.name, player_slug_normalized))
            if player_slug_normalized == player_slug:
                return player.id
        
        # Log available players for debugging
        logger.debug(f"Player slug '{player_slug}' not found. Available players:")
        for name, slug in available_slugs[:10]:  # Limit to first 10
            logger.debug(f"  '{name}' -> '{slug}'")
        
        return None
    except Exception as e:
        logger.error(f"Error resolving player by slug '{player_slug}': {e}")
        return None


def normalize_season_string(season_str: str) -> str:
    """
    Normalize season string for comparison.
    
    Handles formats like "25/26", "2025-26", "2025/26", etc.
    Normalizes to "YYYY-YY" format.
    """
    if not season_str:
        return ""
    
    season_str = str(season_str).strip()
    
    # Handle formats like "25/26" or "25-26"
    if re.match(r'^\d{2}[-/]\d{2}$', season_str):
        parts = season_str.split('/') if '/' in season_str else season_str.split('-')
        if len(parts) == 2:
            start_short = int(parts[0])
            end_short = int(parts[1])
            # For recent data (2020s), assume 2000s
            if start_short >= 50:
                start_year = 1900 + start_short
            else:
                start_year = 2000 + start_short
            return f"{start_year}-{end_short:02d}"
    
    # Handle formats like "2025-26" or "2025/26"
    if re.match(r'^\d{4}[-/]\d{2}$', season_str):
        return season_str.replace('/', '-')
    
    return season_str
