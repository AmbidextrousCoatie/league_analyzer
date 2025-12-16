"""
Tests for Points value object.
"""

import pytest
from domain.value_objects.points import Points, InvalidPoints


class TestPoints:
    """Test cases for Points value object."""
    
    def test_create_valid_points(self):
        """Test creating valid points."""
        points = Points(2.5)
        assert points.value == 2.5
    
    def test_create_zero_points(self):
        """Test creating zero points."""
        points = Points(0.0)
        assert points.value == 0.0
    
    def test_create_negative_points_raises_error(self):
        """Test that negative points raise InvalidPoints."""
        with pytest.raises(InvalidPoints, match="cannot be negative"):
            Points(-1.0)
    
    def test_points_is_immutable(self):
        """Test that Points is immutable."""
        points = Points(2.5)
        with pytest.raises(Exception):
            points.value = 3.0
    
    def test_points_addition(self):
        """Test adding two points values."""
        p1 = Points(2.0)
        p2 = Points(1.5)
        result = p1 + p2
        assert result.value == 3.5
        assert isinstance(result, Points)
    
    def test_points_subtraction(self):
        """Test subtracting points."""
        p1 = Points(5.0)
        p2 = Points(2.0)
        result = p1 - p2
        assert result.value == 3.0
    
    def test_points_subtraction_negative_raises_error(self):
        """Test that subtraction resulting in negative raises error."""
        p1 = Points(1.0)
        p2 = Points(2.0)
        with pytest.raises(InvalidPoints, match="cannot be negative"):
            _ = p1 - p2
    
    def test_points_division(self):
        """Test dividing points."""
        points = Points(10.0)
        result = points / 2
        assert result.value == 5.0
    
    def test_points_multiplication(self):
        """Test multiplying points."""
        points = Points(2.0)
        result = points * 3
        assert result.value == 6.0
    
    def test_points_comparison(self):
        """Test points comparisons."""
        p1 = Points(2.0)
        p2 = Points(3.0)
        p3 = Points(2.0)
        
        assert p1 < p2
        assert p2 > p1
        assert p1 == p3
        assert p1 != p2
    
    @pytest.mark.parametrize("value", [0.0, 0.5, 1.0, 2.5, 10.0, 100.0])
    def test_valid_points_values(self, value):
        """Test various valid points values."""
        points = Points(value)
        assert points.value == value

