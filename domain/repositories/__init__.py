"""
Repository Interfaces

Abstract interfaces for data access repositories.
These interfaces are storage-agnostic and work for CSV or SQL implementations.
"""

from domain.repositories.base_repository import BaseRepository
from domain.repositories.league_repository import LeagueRepository
from domain.repositories.team_repository import TeamRepository
from domain.repositories.player_repository import PlayerRepository
from domain.repositories.game_repository import GameRepository
from domain.repositories.event_repository import EventRepository
from domain.repositories.team_season_repository import TeamSeasonRepository
from domain.repositories.league_season_repository import LeagueSeasonRepository

__all__ = [
    'BaseRepository',
    'LeagueRepository',
    'TeamRepository',
    'PlayerRepository',
    'GameRepository',
    'EventRepository',
    'TeamSeasonRepository',
    'LeagueSeasonRepository',
]

