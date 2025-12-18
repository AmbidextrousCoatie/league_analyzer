"""
Tests for Team entity.
"""

import pytest
from uuid import uuid4
from domain.entities.team import Team
from domain.exceptions.domain_exception import InvalidTeamOperation


class TestTeam:
    """Test cases for Team entity."""
    
    def test_create_valid_team(self):
        """Test creating a valid team."""
        team = Team(name="Team Alpha")
        assert team.name == "Team Alpha"
        assert team.id is not None
        assert team.league_id is None
    
    def test_create_team_with_league(self):
        """Test creating team with league assignment."""
        league_id = uuid4()
        team = Team(name="Team Alpha", league_id=league_id)
        assert team.league_id == league_id
    
    def test_create_team_empty_name_raises_error(self):
        """Test that empty team name raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Team(name="")
        with pytest.raises(ValueError, match="cannot be empty"):
            Team(name="   ")
    
    def test_assign_to_league(self):
        """Test assigning team to a league."""
        team = Team(name="Team Alpha")
        league_id = uuid4()
        team.assign_to_league(league_id)
        assert team.league_id == league_id
    
    def test_assign_to_different_league_raises_error(self):
        """Test that assigning to different league raises error."""
        team = Team(name="Team Alpha", league_id=uuid4())
        different_league_id = uuid4()
        with pytest.raises(InvalidTeamOperation):
            team.assign_to_league(different_league_id)
    
    def test_remove_from_league(self):
        """Test removing team from league."""
        league_id = uuid4()
        team = Team(name="Team Alpha", league_id=league_id)
        team.remove_from_league()
        assert team.league_id is None
    
    def test_update_name(self):
        """Test updating team name."""
        team = Team(name="Team Alpha")
        team.update_name("Team Beta")
        assert team.name == "Team Beta"
    
    def test_update_name_empty_raises_error(self):
        """Test that updating to empty name raises error."""
        team = Team(name="Team Alpha")
        with pytest.raises(ValueError):
            team.update_name("")
    
    def test_team_equality(self):
        """Test team equality based on ID."""
        team1 = Team(name="Team Alpha")
        team2 = Team(name="Team Beta")
        team3 = Team(name="Team Alpha")
        team3.id = team1.id  # Same ID
        
        assert team1 == team3
        assert team1 != team2
        assert team1 != "not a team"
    
    def test_team_hash(self):
        """Test team hashing."""
        team1 = Team(name="Team Alpha")
        team2 = Team(name="Team Alpha")
        team2.id = team1.id
        
        assert hash(team1) == hash(team2)
    
    def test_team_repr(self):
        """Test team string representation."""
        team = Team(name="Team Alpha")
        repr_str = repr(team)
        assert "Team Alpha" in repr_str
        assert str(team.id) in repr_str

