"""
Tests for League entity.
"""

import pytest
from uuid import uuid4
from domain.entities.league import League
from domain.entities.team import Team
from domain.value_objects.handicap_settings import HandicapSettings, HandicapCalculationMethod
from domain.exceptions.domain_exception import InvalidTeamOperation


class TestLeague:
    """Test cases for League entity."""
    
    def test_create_valid_league(self):
        """Test creating a valid league."""
        league = League(name="Test League", abbreviation="TEST", level=3)
        assert league.name == "Test League"
        assert league.abbreviation == "TEST"
        assert league.level == 3
        assert league.get_team_count() == 0
    
    def test_create_league_empty_name_raises_error(self):
        """Test that empty league name raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            League(name="", level=3)
    
    def test_create_league_invalid_level_raises_error(self):
        """Test that league with invalid level raises error."""
        with pytest.raises(ValueError, match="level must be between"):
            League(name="Test League", level=0)
        with pytest.raises(ValueError, match="level must be between"):
            League(name="Test League", level=8)
    
    def test_create_league_auto_level_from_abbreviation(self):
        """Test that league level is auto-set from abbreviation if abbreviation matches known league."""
        league = League(name="Bayernliga", abbreviation="BayL", level=7)  # Default level, should auto-set to 3
        assert league.level == 3  # BayL maps to level 3
    
    def test_create_league_auto_name_from_abbreviation(self):
        """Test that league name is auto-set from abbreviation if name not provided."""
        league = League(name="", abbreviation="BayL", level=3)
        assert league.name == "Bayernliga"  # BayL maps to Bayernliga
    
    def test_add_team(self):
        """Test adding a team to league."""
        league = League(name="Test League", abbreviation="TEST", level=3)
        team = Team(name="Team Alpha")
        
        league.add_team(team)
        assert league.has_team(team.id)
        assert league.get_team_count() == 1
        assert team.league_id == league.id
    
    def test_add_duplicate_team_raises_error(self):
        """Test that adding duplicate team raises error."""
        league = League(name="Test League", abbreviation="TEST", level=3)
        team = Team(name="Team Alpha")
        
        league.add_team(team)
        with pytest.raises(InvalidTeamOperation):
            league.add_team(team)
    
    def test_remove_team(self):
        """Test removing team from league."""
        league = League(name="Test League", abbreviation="TEST", level=3)
        team = Team(name="Team Alpha")
        
        league.add_team(team)
        league.remove_team(team)
        
        assert not league.has_team(team.id)
        assert league.get_team_count() == 0
        assert team.league_id is None
    
    def test_remove_nonexistent_team_raises_error(self):
        """Test that removing nonexistent team raises error."""
        league = League(name="Test League", abbreviation="TEST", level=3)
        team = Team(name="Team Alpha")
        
        with pytest.raises(InvalidTeamOperation):
            league.remove_team(team)
    
    def test_set_handicap_settings(self):
        """Test setting handicap settings."""
        league = League(name="Test League", abbreviation="TEST", level=3)
        settings = HandicapSettings(enabled=True)
        
        league.set_handicap_settings(settings)
        assert league.handicap_settings == settings
    
    def test_has_handicap_enabled(self):
        """Test checking if handicap is enabled."""
        league = League(name="Test League", abbreviation="TEST", level=3)
        assert league.has_handicap_enabled() is False
        
        league.set_handicap_settings(HandicapSettings(enabled=True))
        assert league.has_handicap_enabled() is True
        
        league.set_handicap_settings(HandicapSettings(enabled=False))
        assert league.has_handicap_enabled() is False
    
    def test_update_name(self):
        """Test updating league name."""
        league = League(name="Test League", abbreviation="TEST", level=3)
        league.update_name("Updated League")
        assert league.name == "Updated League"
    
    def test_update_name_empty_raises_error(self):
        """Test that updating to empty name raises error."""
        league = League(name="Test League", abbreviation="TEST", level=3)
        with pytest.raises(ValueError, match="cannot be empty"):
            league.update_name("")
        with pytest.raises(ValueError, match="cannot be empty"):
            league.update_name("   ")
    
    def test_set_level(self):
        """Test setting level for league."""
        league = League(name="Test League", abbreviation="TEST", level=3)
        league.set_level(4)
        assert league.level == 4
        
        with pytest.raises(ValueError, match="level must be between"):
            league.set_level(0)
        with pytest.raises(ValueError, match="level must be between"):
            league.set_level(8)
    
    def test_league_equality(self):
        """Test league equality based on ID."""
        league1 = League(name="Test League", level=3)
        league2 = League(name="Other League", level=3)
        league3 = League(name="Test League", level=3)
        league3.id = league1.id  # Same ID
        
        assert league1 == league3
        assert league1 != league2
        assert league1 != "not a league"
    
    def test_league_hash(self):
        """Test league hashing."""
        league1 = League(name="Test League", level=3)
        league2 = League(name="Test League", level=3)
        league2.id = league1.id
        
        assert hash(league1) == hash(league2)
    
    def test_league_repr(self):
        """Test league string representation."""
        league = League(name="Test League", abbreviation="TEST", level=3)
        repr_str = repr(league)
        assert "Test League" in repr_str
        assert "level=3" in repr_str

