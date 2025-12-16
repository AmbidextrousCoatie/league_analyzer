"""
Value Objects

Value objects are immutable objects defined by their attributes.
They have no identity and are compared by value.
"""

from domain.value_objects.score import Score
from domain.value_objects.points import Points
from domain.value_objects.season import Season
from domain.value_objects.game_result import GameResult
from domain.value_objects.handicap import Handicap
from domain.value_objects.handicap_settings import HandicapSettings, HandicapCalculationMethod

__all__ = [
    'Score',
    'Points',
    'Season',
    'GameResult',
    'Handicap',
    'HandicapSettings',
    'HandicapCalculationMethod',
]

