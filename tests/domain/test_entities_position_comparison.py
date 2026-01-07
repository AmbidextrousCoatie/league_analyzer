"""
Tests for PositionComparison entity.

Covers:
- Constructor invariants (required IDs, position range, non-negative scores)
- Behavior method update_scores and outcome helpers.
"""

import pytest
from uuid import uuid4

from domain.entities.position_comparison import (
    PositionComparison,
    ComparisonOutcome,
    InvalidPositionComparisonData,
)


class TestPositionComparison:
    """Test cases for PositionComparison entity."""

    def _valid_kwargs(self) -> dict:
        return {
            "match_id": uuid4(),
            "position": 0,
            "team1_player_id": uuid4(),
            "team2_player_id": uuid4(),
            "team1_score": 200.0,
            "team2_score": 190.0,
        }

    def test_create_valid_position_comparison(self):
        pc = PositionComparison(**self._valid_kwargs())
        assert pc.match_id is not None
        assert 0 <= pc.position <= 3
        assert pc.team1_score >= 0
        assert pc.team2_score >= 0
        assert pc.outcome in {
            ComparisonOutcome.TEAM1_WIN,
            ComparisonOutcome.TEAM2_WIN,
            ComparisonOutcome.TIE,
        }

    @pytest.mark.parametrize(
        "field",
        ["match_id", "team1_player_id", "team2_player_id"],
    )
    def test_missing_required_ids_raise_error(self, field: str):
        kwargs = self._valid_kwargs()
        kwargs[field] = None
        with pytest.raises(InvalidPositionComparisonData):
            PositionComparison(**kwargs)

    @pytest.mark.parametrize("position", [-1, 4])
    def test_invalid_position_raises_error(self, position: int):
        kwargs = self._valid_kwargs()
        kwargs["position"] = position
        with pytest.raises(InvalidPositionComparisonData):
            PositionComparison(**kwargs)

    @pytest.mark.parametrize(
        "fields",
        [
            {"team1_score": -1.0},
            {"team2_score": -1.0},
        ],
    )
    def test_negative_scores_in_constructor_raise_error(self, fields: dict):
        kwargs = self._valid_kwargs()
        kwargs.update(fields)
        with pytest.raises(InvalidPositionComparisonData):
            PositionComparison(**kwargs)

    def test_outcome_determined_correctly_from_scores(self):
        kwargs = self._valid_kwargs()
        kwargs["team1_score"] = 210
        kwargs["team2_score"] = 190
        pc = PositionComparison(**kwargs)
        assert pc.is_team1_win()
        assert not pc.is_team2_win()
        assert not pc.is_tie()

        pc.update_scores(180, 200)
        assert pc.is_team2_win()
        assert not pc.is_team1_win()
        assert not pc.is_tie()

        pc.update_scores(190, 190)
        assert pc.is_tie()
        assert not pc.is_team1_win()
        assert not pc.is_team2_win()

    def test_update_scores_negative_raises(self):
        pc = PositionComparison(**self._valid_kwargs())
        with pytest.raises(InvalidPositionComparisonData):
            pc.update_scores(-1.0, 200.0)
        with pytest.raises(InvalidPositionComparisonData):
            pc.update_scores(200.0, -1.0)

