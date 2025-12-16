"""
Tests for Season value object.
"""

import pytest
from domain.value_objects.season import Season


class TestSeason:
    """Test cases for Season value object."""
    
    def test_create_valid_season(self):
        """Test creating a valid season."""
        season = Season("2024-25")
        assert season.value == "2024-25"
    
    def test_create_season_with_slash(self):
        """Test creating season with slash separator."""
        season = Season("2024/25")
        assert season.value == "2024/25"
    
    def test_create_special_season_all(self):
        """Test creating special season 'all'."""
        season = Season("all")
        assert season.is_special()
        assert season.get_start_year() is None
    
    def test_create_special_season_latest(self):
        """Test creating special season 'latest'."""
        season = Season("latest")
        assert season.is_special()
    
    def test_create_special_season_current(self):
        """Test creating special season 'current'."""
        season = Season("current")
        assert season.is_special()
    
    def test_create_empty_season_raises_error(self):
        """Test that empty season raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Season("")
    
    def test_create_invalid_format_raises_error(self):
        """Test that invalid format raises error."""
        with pytest.raises(ValueError):
            Season("2024")
        with pytest.raises(ValueError):
            Season("24-25")
        with pytest.raises(ValueError):
            Season("2024-2025")
    
    def test_season_get_start_year(self):
        """Test getting start year from season."""
        season = Season("2024-25")
        assert season.get_start_year() == 2024
    
    def test_season_get_end_year(self):
        """Test getting end year from season."""
        season = Season("2024-25")
        assert season.get_end_year() == 2025
    
    def test_season_equality(self):
        """Test season equality (case insensitive)."""
        season1 = Season("2024-25")
        season2 = Season("2024-25")
        season3 = Season("2024/25")
        season4 = Season("2023-24")
        
        assert season1 == season2
        # Note: Season equality is based on exact value match (case-insensitive)
        # Different separators are treated as different values
        # This is by design - normalization would require additional logic
        assert season1 != season3  # Different separator, so not equal
        assert season1 != season4
    
    def test_season_hash(self):
        """Test season hashing."""
        season1 = Season("2024-25")
        season2 = Season("2024-25")
        assert hash(season1) == hash(season2)
    
    def test_season_in_set(self):
        """Test using season in sets."""
        seasons = {Season("2024-25"), Season("2023-24"), Season("2024-25")}
        assert len(seasons) == 2  # Duplicate removed
    
    @pytest.mark.parametrize("value,start_year,end_year", [
        ("2024-25", 2024, 2025),
        ("2023-24", 2023, 2024),
        ("2020-21", 2020, 2021),
    ])
    def test_valid_season_formats(self, value, start_year, end_year):
        """Test various valid season formats."""
        season = Season(value)
        assert season.get_start_year() == start_year
        assert season.get_end_year() == end_year
    
    def test_season_invalid_year_range(self):
        """Test that invalid year range raises error."""
        with pytest.raises(ValueError, match="end year must be start year \\+ 1"):
            Season("2024-26")  # End year should be 2025

