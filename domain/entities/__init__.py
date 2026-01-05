"""
Domain Entities

Entities represent domain objects with identity and business logic.
They have a lifecycle and can change over time.
"""

from domain.entities.team import Team
from domain.entities.player import Player
from domain.entities.league import League
from domain.entities.game import Game  # Legacy - kept for backward compatibility
from domain.entities.game_result import GameResult  # New: Raw game results
from domain.entities.event import Event
from domain.entities.team_season import TeamSeason
from domain.entities.league_season import LeagueSeason
from domain.entities.club import Club
from domain.entities.scoring_system import ScoringSystem
from domain.entities.club_player import ClubPlayer
from domain.entities.match import Match, MatchStatus  # New: Match entity
from domain.entities.position_comparison import PositionComparison, ComparisonOutcome  # New: Position comparisons
from domain.entities.match_scoring import MatchScoring  # New: Match scoring results

__all__ = [
    'Team',
    'Player',
    'League',
    'Game',  # Legacy
    'GameResult',  # New
    'Event',
    'TeamSeason',
    'LeagueSeason',
    'Club',
    'ScoringSystem',
    'Match',
    'MatchStatus',
    'PositionComparison',
    'ComparisonOutcome',
    'MatchScoring',
]

