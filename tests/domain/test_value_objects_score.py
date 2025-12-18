"""
Tests for Score value object.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from domain.value_objects.score import Score
from domain.exceptions.domain_exception import InvalidScore


class TestScore:
    """Test cases for Score value object."""
    
    def test_create_valid_score(self):
        """Test creating a valid score."""
        score = Score(200.0)
        assert score.value == 200.0
    
    def test_create_perfect_game(self):
        """Test creating a perfect game score (300)."""
        score = Score(300.0)
        assert score.value == 300.0
    
    def test_create_zero_score(self):
        """Test creating a zero score."""
        score = Score(0.0)
        assert score.value == 0.0
    
    def test_create_negative_score_raises_error(self):
        """Test that negative scores raise InvalidScore."""
        with pytest.raises(InvalidScore, match="cannot be negative"):
            Score(-10.0)
    
    def test_score_is_immutable(self):
        """Test that Score is immutable (frozen dataclass)."""
        score = Score(200.0)
        with pytest.raises(Exception):  # Frozen dataclass raises exception
            score.value = 250.0
    
    def test_score_addition(self):
        """Test adding two scores."""
        score1 = Score(150.0)
        score2 = Score(100.0)
        result = score1 + score2
        assert result.value == 250.0
        assert isinstance(result, Score)
    
    def test_score_subtraction(self):
        """Test subtracting two scores."""
        score1 = Score(200.0)
        score2 = Score(50.0)
        result = score1 - score2
        assert result.value == 150.0
    
    def test_score_subtraction_negative_result_raises_error(self):
        """Test that subtraction resulting in negative raises error."""
        score1 = Score(50.0)
        score2 = Score(100.0)
        with pytest.raises(InvalidScore, match="cannot be negative"):
            _ = score1 - score2
    
    def test_score_division(self):
        """Test dividing score by a number."""
        score = Score(200.0)
        result = score / 2
        assert result.value == 100.0
        assert isinstance(result, Score)
    
    def test_score_division_by_zero_raises_error(self):
        """Test that division by zero raises error."""
        score = Score(200.0)
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            _ = score / 0
    
    def test_score_multiplication(self):
        """Test multiplying score by a number."""
        score = Score(100.0)
        result = score * 2
        assert result.value == 200.0
    
    def test_score_comparison(self):
        """Test score comparisons."""
        score1 = Score(150.0)
        score2 = Score(200.0)
        score3 = Score(150.0)
        
        assert score1 < score2
        assert score2 > score1
        assert score1 <= score2
        assert score2 >= score1
        assert score1 == score3
        assert score1 != score2
    
    def test_score_equality_with_non_score(self):
        """Test that Score equality returns False for non-Score objects."""
        score = Score(200.0)
        assert score != "200.0"
        assert score != 200.0
        assert score != None
        assert score != []
    
    def test_score_to_float(self):
        """Test converting score to float."""
        score = Score(200.5)
        assert float(score) == 200.5
        assert isinstance(float(score), float)
    
    def test_score_to_int(self):
        """Test converting score to int."""
        score = Score(200.5)
        assert int(score) == 200
    
    def test_score_repr(self):
        """Test string representation."""
        score = Score(200.0)
        assert repr(score) == "Score(200.0)"
    
    @pytest.mark.parametrize("value,expected", [
        (0.0, 0.0),
        (100.0, 100.0),
        (200.0, 200.0),
        (300.0, 300.0),
        (150.5, 150.5),
    ])
    def test_valid_score_values(self, value, expected):
        """Test various valid score values."""
        score = Score(value)
        assert score.value == expected
    
    @pytest.mark.parametrize("invalid_value", [
        -1.0,
        -100.0,
        -0.1,
    ])
    def test_invalid_score_values(self, invalid_value):
        """Test that invalid score values raise errors."""
        with pytest.raises(InvalidScore):
            Score(invalid_value)

