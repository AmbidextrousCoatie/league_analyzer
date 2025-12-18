"""
Tests for Player entity.
"""

import pytest
from uuid import uuid4
from domain.entities.player import Player
from domain.value_objects.season import Season
from domain.value_objects.handicap import Handicap
from domain.exceptions.domain_exception import InvalidTeamOperation


class TestPlayer:
    """Test cases for Player entity."""
    
    def test_create_valid_player(self):
        """Test creating a valid player."""
        player = Player(name="John Doe")
        assert player.name == "John Doe"
        assert player.id is not None
        assert player.team_id is None
    
    def test_create_player_empty_name_raises_error(self):
        """Test that empty player name raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Player(name="")
    
    def test_assign_to_team(self):
        """Test assigning player to a team."""
        player = Player(name="John Doe")
        team_id = uuid4()
        player.assign_to_team(team_id)
        assert player.team_id == team_id
    
    def test_assign_to_different_team_raises_error(self):
        """Test that assigning to different team raises error."""
        player = Player(name="John Doe", team_id=uuid4())
        different_team_id = uuid4()
        with pytest.raises(InvalidTeamOperation):
            player.assign_to_team(different_team_id)
    
    def test_remove_from_team(self):
        """Test removing player from team."""
        player = Player(name="John Doe", team_id=uuid4())
        player.remove_from_team()
        assert player.team_id is None
    
    def test_is_on_team(self):
        """Test checking if player is on a team."""
        player = Player(name="John Doe")
        assert player.is_on_team() is False
        
        player.assign_to_team(uuid4())
        assert player.is_on_team() is True
    
    def test_set_handicap(self):
        """Test setting handicap for a season."""
        player = Player(name="John Doe")
        season = Season("2024-25")
        handicap = Handicap(20.0)
        
        player.set_handicap(season, handicap)
        assert player.get_handicap(season) == handicap
    
    def test_get_handicap_none(self):
        """Test getting handicap when not set."""
        player = Player(name="John Doe")
        season = Season("2024-25")
        assert player.get_handicap(season) is None
    
    def test_has_handicap(self):
        """Test checking if player has handicap."""
        player = Player(name="John Doe")
        season = Season("2024-25")
        
        assert player.has_handicap(season) is False
        
        player.set_handicap(season, Handicap(20.0))
        assert player.has_handicap(season) is True
    
    def test_remove_handicap(self):
        """Test removing handicap."""
        player = Player(name="John Doe")
        season = Season("2024-25")
        player.set_handicap(season, Handicap(20.0))
        
        player.remove_handicap(season)
        assert player.get_handicap(season) is None
    
    def test_handicap_different_seasons(self):
        """Test that handicap is tracked per season."""
        player = Player(name="John Doe")
        season1 = Season("2024-25")
        season2 = Season("2023-24")
        
        player.set_handicap(season1, Handicap(20.0))
        player.set_handicap(season2, Handicap(25.0))
        
        assert player.get_handicap(season1).value == 20.0
        assert player.get_handicap(season2).value == 25.0
    
    def test_update_handicap_during_season(self):
        """Test updating handicap during season."""
        player = Player(name="John Doe")
        season = Season("2024-25")
        
        player.set_handicap(season, Handicap(20.0))
        assert player.get_handicap(season).value == 20.0
        
        # Update handicap mid-season
        player.set_handicap(season, Handicap(25.0))
        assert player.get_handicap(season).value == 25.0
    
    def test_update_name(self):
        """Test updating player name."""
        player = Player(name="John Doe")
        player.update_name("Jane Doe")
        assert player.name == "Jane Doe"
    
    def test_update_name_empty_raises_error(self):
        """Test that updating to empty name raises error."""
        player = Player(name="John Doe")
        with pytest.raises(ValueError, match="cannot be empty"):
            player.update_name("")
        with pytest.raises(ValueError, match="cannot be empty"):
            player.update_name("   ")
    
    def test_player_equality(self):
        """Test player equality based on ID."""
        player1 = Player(name="John Doe")
        player2 = Player(name="Jane Doe")
        player3 = Player(name="John Doe")
        player3.id = player1.id  # Same ID
        
        assert player1 == player3
        assert player1 != player2
        assert player1 != "not a player"
    
    def test_player_hash(self):
        """Test player hashing."""
        player1 = Player(name="John Doe")
        player2 = Player(name="John Doe")
        player2.id = player1.id
        
        assert hash(player1) == hash(player2)
    
    def test_player_repr(self):
        """Test player string representation."""
        player = Player(name="John Doe")
        repr_str = repr(player)
        assert "John Doe" in repr_str
        assert str(player.id) in repr_str

