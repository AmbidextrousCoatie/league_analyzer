"""
Tests for Team entity.

Team entity represents a specific squad (team number) within a club.
Teams participate in league seasons via TeamSeason entity.
"""

import pytest
from uuid import uuid4
from domain.entities.team import Team, InvalidTeamData
from domain.exceptions.domain_exception import InvalidTeamOperation


class TestTeam:
    """Test cases for Team entity."""
    
    def test_create_valid_team(self):
        """Test creating a valid team."""
        club_id = uuid4()
        team = Team(name="Team Alpha", club_id=club_id)
        assert team.name == "Team Alpha"
        assert team.club_id == club_id
        assert team.team_number == 1  # Default
        assert team.id is not None
    
    def test_create_team_with_team_number(self):
        """Test creating team with specific team number."""
        club_id = uuid4()
        team = Team(name="Team Alpha", club_id=club_id, team_number=2)
        assert team.team_number == 2
    
    def test_create_team_empty_name_raises_error(self):
        """Test that empty team name raises error."""
        club_id = uuid4()
        with pytest.raises(InvalidTeamData, match="cannot be empty"):
            Team(name="", club_id=club_id)
        with pytest.raises(InvalidTeamData, match="cannot be empty"):
            Team(name="   ", club_id=club_id)
    
    def test_create_team_missing_club_id_raises_error(self):
        """Test that team without club_id raises error."""
        with pytest.raises(InvalidTeamData, match="must belong to a club"):
            Team(name="Team Alpha", club_id=None)
    
    def test_create_team_invalid_team_number_raises_error(self):
        """Test that invalid team number raises error."""
        club_id = uuid4()
        with pytest.raises(InvalidTeamData, match="Team number must be positive"):
            Team(name="Team Alpha", club_id=club_id, team_number=0)
        with pytest.raises(InvalidTeamData, match="Team number must be positive"):
            Team(name="Team Alpha", club_id=club_id, team_number=-1)
    
    def test_assign_to_club(self):
        """Test assigning team to a club."""
        club_id1 = uuid4()
        team = Team(name="Team Alpha", club_id=club_id1, team_number=1)
        
        club_id2 = uuid4()
        team.assign_to_club(club_id2, team_number=2)
        assert team.club_id == club_id2
        assert team.team_number == 2
    
    def test_assign_to_club_invalid_team_number_raises_error(self):
        """Test that assigning with invalid team number raises error."""
        club_id = uuid4()
        team = Team(name="Team Alpha", club_id=club_id)
        
        with pytest.raises(InvalidTeamOperation, match="Team number must be positive"):
            team.assign_to_club(uuid4(), team_number=0)
    
    def test_update_team_number(self):
        """Test updating team number."""
        club_id = uuid4()
        team = Team(name="Team Alpha", club_id=club_id, team_number=1)
        
        team.update_team_number(3)
        assert team.team_number == 3
    
    def test_update_team_number_invalid_raises_error(self):
        """Test that updating to invalid team number raises error."""
        club_id = uuid4()
        team = Team(name="Team Alpha", club_id=club_id)
        
        with pytest.raises(InvalidTeamOperation, match="Team number must be positive"):
            team.update_team_number(0)
    
    def test_update_name(self):
        """Test updating team name."""
        club_id = uuid4()
        team = Team(name="Team Alpha", club_id=club_id)
        team.update_name("Team Beta")
        assert team.name == "Team Beta"
    
    def test_update_name_empty_raises_error(self):
        """Test that updating to empty name raises error."""
        club_id = uuid4()
        team = Team(name="Team Alpha", club_id=club_id)
        with pytest.raises(ValueError, match="cannot be empty"):
            team.update_name("")
        with pytest.raises(ValueError, match="cannot be empty"):
            team.update_name("   ")
    
    def test_team_equality(self):
        """Test team equality based on ID."""
        club_id = uuid4()
        team1 = Team(name="Team Alpha", club_id=club_id)
        team2 = Team(name="Team Beta", club_id=club_id)
        team3 = Team(name="Team Alpha", club_id=club_id)
        team3.id = team1.id  # Same ID
        
        assert team1 == team3
        assert team1 != team2
        assert team1 != "not a team"
    
    def test_team_hash(self):
        """Test team hashing."""
        club_id = uuid4()
        team1 = Team(name="Team Alpha", club_id=club_id)
        team2 = Team(name="Team Alpha", club_id=club_id)
        team2.id = team1.id
        
        assert hash(team1) == hash(team2)
    
    def test_team_repr(self):
        """Test team string representation."""
        club_id = uuid4()
        team = Team(name="Team Alpha", club_id=club_id)
        repr_str = repr(team)
        assert "Team Alpha" in repr_str
        assert str(team.id) in repr_str
        assert str(club_id) in repr_str
