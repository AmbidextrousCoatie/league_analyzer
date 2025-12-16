"""
Tests for GameResult value object.
"""

import pytest
from uuid import uuid4
from domain.value_objects.game_result import GameResult, InvalidGameResult
from domain.value_objects.score import Score
from domain.value_objects.points import Points
from domain.value_objects.handicap import Handicap


class TestGameResult:
    """Test cases for GameResult value object."""
    
    def test_create_valid_game_result(self):
        """Test creating a valid game result."""
        player_id = uuid4()
        result = GameResult(
            player_id=player_id,
            position=1,
            scratch_score=Score(200.0),
            points=Points(2.0)
        )
        assert result.player_id == player_id
        assert result.position == 1
        assert result.scratch_score.value == 200.0
    
    def test_create_game_result_with_handicap(self):
        """Test creating game result with handicap."""
        result = GameResult(
            player_id=uuid4(),
            position=1,
            scratch_score=Score(180.0),
            points=Points(2.0),
            handicap=Handicap(20.0)
        )
        assert result.handicap is not None
        assert result.handicap_score.value == 200.0
    
    def test_create_game_result_invalid_position_low(self):
        """Test that position < 1 raises error."""
        with pytest.raises(InvalidGameResult, match="must be between 1 and 4"):
            GameResult(
                player_id=uuid4(),
                position=0,
                scratch_score=Score(200.0),
                points=Points(2.0)
            )
    
    def test_create_game_result_invalid_position_high(self):
        """Test that position > 4 raises error."""
        with pytest.raises(InvalidGameResult, match="must be between 1 and 4"):
            GameResult(
                player_id=uuid4(),
                position=5,
                scratch_score=Score(200.0),
                points=Points(2.0)
            )
    
    def test_game_result_handicap_score_without_handicap(self):
        """Test handicap_score when no handicap is applied."""
        result = GameResult(
            player_id=uuid4(),
            position=1,
            scratch_score=Score(200.0),
            points=Points(2.0)
        )
        assert result.handicap_score == result.scratch_score
        assert result.handicap_score.value == 200.0
    
    def test_game_result_handicap_score_with_handicap(self):
        """Test handicap_score when handicap is applied."""
        result = GameResult(
            player_id=uuid4(),
            position=1,
            scratch_score=Score(180.0),
            points=Points(2.0),
            handicap=Handicap(20.0)
        )
        assert result.handicap_score.value == 200.0
        assert result.scratch_score.value == 180.0
    
    def test_game_result_has_handicap(self):
        """Test has_handicap method."""
        result_with = GameResult(
            player_id=uuid4(),
            position=1,
            scratch_score=Score(200.0),
            points=Points(2.0),
            handicap=Handicap(20.0)
        )
        result_without = GameResult(
            player_id=uuid4(),
            position=1,
            scratch_score=Score(200.0),
            points=Points(2.0)
        )
        assert result_with.has_handicap() is True
        assert result_without.has_handicap() is False
    
    def test_game_result_get_handicap_score_capped(self):
        """Test getting capped handicap score."""
        result = GameResult(
            player_id=uuid4(),
            position=1,
            scratch_score=Score(280.0),
            points=Points(2.0),
            handicap=Handicap(30.0)
        )
        capped = result.get_handicap_score_capped(cap_at_300=True)
        assert capped.value == 300.0
        
        uncapped = result.get_handicap_score_capped(cap_at_300=False)
        assert uncapped.value == 310.0
    
    def test_game_result_equality(self):
        """Test game result equality."""
        player_id = uuid4()
        result1 = GameResult(
            player_id=player_id,
            position=1,
            scratch_score=Score(200.0),
            points=Points(2.0)
        )
        result2 = GameResult(
            player_id=player_id,
            position=1,
            scratch_score=Score(200.0),
            points=Points(2.0)
        )
        assert result1 == result2
    
    @pytest.mark.parametrize("position", [1, 2, 3, 4])
    def test_valid_positions(self, position):
        """Test all valid positions."""
        result = GameResult(
            player_id=uuid4(),
            position=position,
            scratch_score=Score(200.0),
            points=Points(2.0)
        )
        assert result.position == position

