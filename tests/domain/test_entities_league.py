"""
Tests for League entity.
"""

import pytest
from uuid import uuid4
from domain.entities.league import League
from domain.entities.team import Team
from domain.value_objects.season import Season
from domain.value_objects.handicap_settings import HandicapSettings, HandicapCalculationMethod
from domain.exceptions.domain_exception import InvalidTeamOperation


class TestLeague:
    """Test cases for League entity."""
    
    def test_create_valid_league(self):
        """Test creating a valid league."""
        season = Season("2024-25")
        league = League(name="Test League", season=season)
        assert league.name == "Test League"
        assert league.season == season
        assert league.get_team_count() == 0
    
    def test_create_league_empty_name_raises_error(self):
        """Test that empty league name raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            League(name="", season=Season("2024-25"))
    
    def test_create_league_no_season_raises_error(self):
        """Test that league without season raises error."""
        with pytest.raises(ValueError, match="must have a season"):
            League(name="Test League", season=None)
    
    def test_add_team(self):
        """Test adding a team to league."""
        league = League(name="Test League", season=Season("2024-25"))
        team = Team(name="Team Alpha")
        
        league.add_team(team)
        assert league.has_team(team.id)
        assert league.get_team_count() == 1
        assert team.league_id == league.id
    
    def test_add_duplicate_team_raises_error(self):
        """Test that adding duplicate team raises error."""
        league = League(name="Test League", season=Season("2024-25"))
        team = Team(name="Team Alpha")
        
        league.add_team(team)
        with pytest.raises(InvalidTeamOperation):
            league.add_team(team)
    
    def test_remove_team(self):
        """Test removing team from league."""
        league = League(name="Test League", season=Season("2024-25"))
        team = Team(name="Team Alpha")
        
        league.add_team(team)
        league.remove_team(team)
        
        assert not league.has_team(team.id)
        assert league.get_team_count() == 0
        assert team.league_id is None
    
    def test_remove_nonexistent_team_raises_error(self):
        """Test that removing nonexistent team raises error."""
        league = League(name="Test League", season=Season("2024-25"))
        team = Team(name="Team Alpha")
        
        with pytest.raises(InvalidTeamOperation):
            league.remove_team(team)
    
    def test_set_handicap_settings(self):
        """Test setting handicap settings."""
        league = League(name="Test League", season=Season("2024-25"))
        settings = HandicapSettings(enabled=True)
        
        league.set_handicap_settings(settings)
        assert league.handicap_settings == settings
    
    def test_has_handicap_enabled(self):
        """Test checking if handicap is enabled."""
        league = League(name="Test League", season=Season("2024-25"))
        assert league.has_handicap_enabled() is False
        
        league.set_handicap_settings(HandicapSettings(enabled=True))
        assert league.has_handicap_enabled() is True
        
        league.set_handicap_settings(HandicapSettings(enabled=False))
        assert league.has_handicap_enabled() is False
    
    def test_update_name(self):
        """Test updating league name."""
        league = League(name="Test League", season=Season("2024-25"))
        league.update_name("Updated League")
        assert league.name == "Updated League"
    
    def test_update_name_empty_raises_error(self):
        """Test that updating to empty name raises error."""
        league = League(name="Test League", season=Season("2024-25"))
        with pytest.raises(ValueError, match="cannot be empty"):
            league.update_name("")
        with pytest.raises(ValueError, match="cannot be empty"):
            league.update_name("   ")
    
    def test_set_season(self):
        """Test setting season for league."""
        league = League(name="Test League", season=Season("2024-25"))
        new_season = Season("2025-26")
        league.set_season(new_season)
        assert league.season == new_season
    
    def test_league_equality(self):
        """Test league equality based on ID."""
        league1 = League(name="Test League", season=Season("2024-25"))
        league2 = League(name="Other League", season=Season("2024-25"))
        league3 = League(name="Test League", season=Season("2024-25"))
        league3.id = league1.id  # Same ID
        
        assert league1 == league3
        assert league1 != league2
        assert league1 != "not a league"
    
    def test_league_hash(self):
        """Test league hashing."""
        league1 = League(name="Test League", season=Season("2024-25"))
        league2 = League(name="Test League", season=Season("2024-25"))
        league2.id = league1.id
        
        assert hash(league1) == hash(league2)
    
    def test_league_repr(self):
        """Test league string representation."""
        league = League(name="Test League", season=Season("2024-25"))
        repr_str = repr(league)
        assert "Test League" in repr_str
        assert "2024-25" in repr_str

