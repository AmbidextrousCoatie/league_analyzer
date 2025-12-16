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

