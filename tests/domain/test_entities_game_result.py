"""
Tests for GameResult entity.

Covers:
- Constructor invariants (required IDs, position range, non-negative score)
- Behavior methods for updating score, handicap, and disqualification flag.
"""

import pytest
from uuid import uuid4

from domain.entities.game_result import GameResult, InvalidGameResultData


class TestGameResult:
    """Test cases for GameResult entity."""

    def _valid_kwargs(self) -> dict:
        return {
            "match_id": uuid4(),
            "player_id": uuid4(),
            "team_season_id": uuid4(),
            "position": 0,
            "score": 200.0,
            "handicap": None,
            "is_disqualified": False,
        }

    def test_create_valid_game_result(self):
        gr = GameResult(**self._valid_kwargs())
        assert gr.match_id is not None
        assert gr.player_id is not None
        assert gr.team_season_id is not None
        assert 0 <= gr.position <= 3
        assert gr.score >= 0

    @pytest.mark.parametrize("field", ["match_id", "player_id", "team_season_id"])
    def test_missing_required_ids_raise_error(self, field: str):
        kwargs = self._valid_kwargs()
        kwargs[field] = None
        with pytest.raises(InvalidGameResultData):
            GameResult(**kwargs)

    @pytest.mark.parametrize("position", [-1, 4])
    def test_invalid_position_raises_error(self, position: int):
        kwargs = self._valid_kwargs()
        kwargs["position"] = position
        with pytest.raises(InvalidGameResultData):
            GameResult(**kwargs)

    def test_negative_score_raises_error(self):
        kwargs = self._valid_kwargs()
        kwargs["score"] = -1.0
        with pytest.raises(InvalidGameResultData):
            GameResult(**kwargs)

    def test_update_score_positive_path(self):
        gr = GameResult(**self._valid_kwargs())
        before = gr.updated_at
        gr.update_score(250.0)
        assert gr.score == 250.0
        assert gr.updated_at >= before

    def test_update_score_negative_raises(self):
        gr = GameResult(**self._valid_kwargs())
        with pytest.raises(InvalidGameResultData):
            gr.update_score(-10.0)

    def test_set_handicap_updates_value(self):
        gr = GameResult(**self._valid_kwargs())
        gr.set_handicap(15.0)
        assert gr.handicap == 15.0
        gr.set_handicap(None)
        assert gr.handicap is None

    def test_disqualify_and_clear(self):
        gr = GameResult(**self._valid_kwargs())
        assert not gr.is_disqualified
        gr.disqualify()
        assert gr.is_disqualified
        gr.clear_disqualification()
        assert not gr.is_disqualified

