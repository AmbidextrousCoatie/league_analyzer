"""
Pytest configuration and shared fixtures.

This file is automatically discovered by pytest and provides
shared fixtures and configuration for all tests.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from uuid import uuid4
from datetime import datetime
from domain.value_objects import (
    Score, Points, Season, Handicap, GameResult,
    HandicapSettings, HandicapCalculationMethod
)
from domain.entities import Team, Player, League, Game
from domain.domain_services import HandicapCalculator


# ============================================================================
# Value Object Fixtures
# ============================================================================

@pytest.fixture
def sample_score():
    """Fixture for a valid Score value object."""
    return Score(200.0)


@pytest.fixture
def sample_points():
    """Fixture for a valid Points value object."""
    return Points(2.5)


@pytest.fixture
def sample_season():
    """Fixture for a valid Season value object."""
    return Season("2024-25")


@pytest.fixture
def sample_handicap():
    """Fixture for a valid Handicap value object."""
    return Handicap(20.0)


@pytest.fixture
def sample_handicap_settings():
    """Fixture for HandicapSettings with cumulative average method."""
    return HandicapSettings(
        enabled=True,
        calculation_method=HandicapCalculationMethod.CUMULATIVE_AVERAGE,
        base_average=200.0,
        percentage=0.9,
        max_handicap=50.0,
        cap_handicap_score=True
    )


@pytest.fixture
def sample_handicap_settings_moving_window():
    """Fixture for HandicapSettings with moving window method."""
    return HandicapSettings(
        enabled=True,
        calculation_method=HandicapCalculationMethod.MOVING_WINDOW,
        base_average=200.0,
        percentage=0.9,
        max_handicap=50.0,
        moving_window_size=5,
        cap_handicap_score=True
    )


@pytest.fixture
def sample_game_result(sample_score, sample_points, sample_handicap):
    """Fixture for a valid GameResult value object."""
    return GameResult(
        player_id=uuid4(),
        position=1,
        scratch_score=sample_score,
        points=sample_points,
        handicap=sample_handicap
    )


# ============================================================================
# Entity Fixtures
# ============================================================================

@pytest.fixture
def sample_team():
    """Fixture for a valid Team entity."""
    return Team(name="Team Alpha", league_id=uuid4())


@pytest.fixture
def sample_player():
    """Fixture for a valid Player entity."""
    return Player(name="John Doe")


@pytest.fixture
def sample_league(sample_season):
    """Fixture for a valid League entity."""
    return League(name="Test League", season=sample_season)


@pytest.fixture
def sample_game(sample_league, sample_season):
    """Fixture for a valid Game entity."""
    team1_id = uuid4()
    team2_id = uuid4()
    return Game(
        league_id=sample_league.id,
        season=sample_season,
        week=1,
        team_id=team1_id,
        opponent_team_id=team2_id
    )


# ============================================================================
# Helper Functions
# ============================================================================

def create_game_results(player_id, scores, positions=None, handicaps=None):
    """
    Helper function to create a list of GameResult objects.
    
    Args:
        player_id: UUID of the player
        scores: List of scratch scores
        positions: Optional list of positions (defaults to 1)
        handicaps: Optional list of handicaps (defaults to None)
    
    Returns:
        List of GameResult objects
    """
    from domain.value_objects.game_result import GameResult
    from domain.value_objects.score import Score
    from domain.value_objects.points import Points
    from domain.value_objects.handicap import Handicap
    
    if positions is None:
        positions = [1] * len(scores)
    if handicaps is None:
        handicaps = [None] * len(scores)
    
    results = []
    for i, (score, position, handicap) in enumerate(zip(scores, positions, handicaps)):
        result = GameResult(
            player_id=player_id,
            position=position,
            scratch_score=Score(score),
            points=Points(2.0),
            handicap=Handicap(handicap) if handicap is not None else None
        )
        results.append(result)
    
    return results

