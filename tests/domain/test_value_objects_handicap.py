"""
Tests for Handicap value object.
"""

import pytest
from domain.value_objects.handicap import Handicap, InvalidHandicap
from domain.value_objects.score import Score


class TestHandicap:
    """Test cases for Handicap value object."""
    
    def test_create_valid_handicap(self):
        """Test creating a valid handicap."""
        handicap = Handicap(20.0)
        assert handicap.value == 20.0
    
    def test_create_zero_handicap(self):
        """Test creating zero handicap."""
        handicap = Handicap(0.0)
        assert handicap.value == 0.0
    
    def test_create_negative_handicap_raises_error(self):
        """Test that negative handicap raises error."""
        with pytest.raises(InvalidHandicap, match="cannot be negative"):
            Handicap(-10.0)
    
    def test_create_handicap_with_max(self):
        """Test creating handicap with maximum limit."""
        handicap = Handicap(30.0, max_handicap=50.0)
        assert handicap.value == 30.0
        assert handicap.max_handicap == 50.0
    
    def test_create_handicap_exceeding_max_raises_error(self):
        """Test that handicap exceeding max raises error."""
        with pytest.raises(InvalidHandicap, match="exceeds maximum"):
            Handicap(60.0, max_handicap=50.0)
    
    def test_apply_handicap_to_score(self):
        """Test applying handicap to a score."""
        handicap = Handicap(20.0)
        scratch = Score(180.0)
        result = handicap.apply_to_score(scratch)
        assert result.value == 200.0
    
    def test_apply_handicap_with_capping(self):
        """Test applying handicap with capping at 300."""
        handicap = Handicap(30.0)
        scratch = Score(280.0)
        result = handicap.apply_to_score(scratch, cap_at_300=True)
        assert result.value == 300.0  # Capped at 300
    
    def test_apply_handicap_without_capping(self):
        """Test applying handicap without capping."""
        handicap = Handicap(30.0)
        scratch = Score(280.0)
        result = handicap.apply_to_score(scratch, cap_at_300=False)
        assert result.value == 310.0  # Not capped
    
    def test_apply_handicap_to_high_scratch_raises_error(self):
        """Test that applying to score > 300 raises error."""
        handicap = Handicap(20.0)
        with pytest.raises(InvalidHandicap, match="exceeds maximum 300"):
            # Score validation happens in apply_to_score
            scratch = Score(301.0)  # This should fail at Score creation
            handicap.apply_to_score(scratch)
    
    def test_handicap_addition(self):
        """Test adding two handicaps."""
        h1 = Handicap(20.0)
        h2 = Handicap(10.0)
        result = h1 + h2
        assert result.value == 30.0
    
    def test_handicap_subtraction(self):
        """Test subtracting handicaps."""
        h1 = Handicap(30.0)
        h2 = Handicap(10.0)
        result = h1 - h2
        assert result.value == 20.0
    
    def test_handicap_comparison(self):
        """Test handicap comparisons."""
        h1 = Handicap(20.0)
        h2 = Handicap(30.0)
        h3 = Handicap(20.0)
        
        assert h1 < h2
        assert h2 > h1
        assert h1 == h3
        assert h1 != h2
    
    @pytest.mark.parametrize("value,max_handicap,expected_valid", [
        (20.0, None, True),
        (50.0, 50.0, True),
        (50.0, 60.0, True),
        (60.0, 50.0, False),  # Exceeds max
    ])
    def test_handicap_max_validation(self, value, max_handicap, expected_valid):
        """Test handicap max validation."""
        if expected_valid:
            handicap = Handicap(value, max_handicap=max_handicap if max_handicap else 0.0)
            assert handicap.value == value
        else:
            with pytest.raises(InvalidHandicap):
                Handicap(value, max_handicap=max_handicap)

