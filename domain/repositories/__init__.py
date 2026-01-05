"""
Repository Interfaces

Abstract interfaces for data access repositories.
These interfaces are storage-agnostic and work for CSV or SQL implementations.
"""

from domain.repositories.base_repository import BaseRepository
from domain.repositories.league_repository import LeagueRepository
from domain.repositories.team_repository import TeamRepository
from domain.repositories.player_repository import PlayerRepository
from domain.repositories.game_repository import GameRepository  # Legacy
from domain.repositories.game_result_repository import GameResultRepository  # New
from domain.repositories.event_repository import EventRepository
from domain.repositories.team_season_repository import TeamSeasonRepository
from domain.repositories.league_season_repository import LeagueSeasonRepository
from domain.repositories.club_repository import ClubRepository
from domain.repositories.scoring_system_repository import ScoringSystemRepository
from domain.repositories.club_player_repository import ClubPlayerRepository
from domain.repositories.match_repository import MatchRepository  # New
from domain.repositories.position_comparison_repository import PositionComparisonRepository  # New
from domain.repositories.match_scoring_repository import MatchScoringRepository  # New

__all__ = [
    'BaseRepository',
    'LeagueRepository',
    'TeamRepository',
    'PlayerRepository',
    'GameRepository',  # Legacy
    'GameResultRepository',  # New
    'EventRepository',
    'TeamSeasonRepository',
    'LeagueSeasonRepository',
    'ClubRepository',
    'ScoringSystemRepository',
    'MatchRepository',  # New
    'PositionComparisonRepository',  # New
    'MatchScoringRepository',  # New
]

