"""
Tests for UpdateTeamHandler.

Tests the handler with various scenarios including edge cases.
"""

import pytest
from unittest.mock import AsyncMock
from uuid import UUID, uuid4
from domain.entities.team import Team
from domain.entities.club import Club
from application.commands.league.update_team_command import UpdateTeamCommand
from application.command_handlers.league.update_team_handler import UpdateTeamHandler
from application.exceptions import EntityNotFoundError, ValidationError


@pytest.fixture
def mock_team_repo():
    """Mock TeamRepository."""
    return AsyncMock()


@pytest.fixture
def mock_club_repo():
    """Mock ClubRepository."""
    return AsyncMock()


@pytest.fixture
def handler(mock_team_repo, mock_club_repo):
    """Create handler with mocked repositories."""
    return UpdateTeamHandler(
        team_repository=mock_team_repo,
        club_repository=mock_club_repo
    )


@pytest.fixture
def sample_club():
    """Sample Club entity."""
    return Club(
        id=uuid4(),
        name="Test Club"
    )


@pytest.fixture
def sample_team(sample_club):
    """Sample Team entity."""
    return Team(
        id=uuid4(),
        name="Original Team",
        club_id=sample_club.id,
        team_number=1
    )


@pytest.fixture
def another_club():
    """Another Club entity."""
    return Club(
        id=uuid4(),
        name="Another Club"
    )


class TestUpdateTeamHandler:
    """Test suite for UpdateTeamHandler."""
    
    @pytest.mark.asyncio
    async def test_handle_team_not_found(
        self,
        handler,
        mock_team_repo
    ):
        """Test that EntityNotFoundError is raised when team is not found."""
        # Arrange
        team_id = uuid4()
        command = UpdateTeamCommand(team_id=team_id, name="New Name")
        mock_team_repo.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError) as exc_info:
            await handler.handle(command)
        
        assert f"Team {team_id} not found" in str(exc_info.value)
        mock_team_repo.get_by_id.assert_called_once_with(team_id)
        mock_team_repo.update.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_club_not_found(
        self,
        handler,
        mock_team_repo,
        mock_club_repo,
        sample_team
    ):
        """Test that EntityNotFoundError is raised when new club is not found."""
        # Arrange
        new_club_id = uuid4()
        command = UpdateTeamCommand(
            team_id=sample_team.id,
            club_id=new_club_id
        )
        mock_team_repo.get_by_id.return_value = sample_team
        mock_club_repo.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError) as exc_info:
            await handler.handle(command)
        
        assert f"Club {new_club_id} not found" in str(exc_info.value)
        mock_club_repo.get_by_id.assert_called_once_with(new_club_id)
        mock_team_repo.update.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_empty_name(
        self,
        handler,
        mock_team_repo,
        sample_team
    ):
        """Test that ValidationError is raised when team name is empty."""
        # Arrange
        command = UpdateTeamCommand(
            team_id=sample_team.id,
            name=""
        )
        mock_team_repo.get_by_id.return_value = sample_team
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await handler.handle(command)
        
        assert "Team name cannot be empty" in str(exc_info.value)
        mock_team_repo.update.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_whitespace_name(
        self,
        handler,
        mock_team_repo,
        sample_team
    ):
        """Test that ValidationError is raised when team name is only whitespace."""
        # Arrange
        command = UpdateTeamCommand(
            team_id=sample_team.id,
            name="   "
        )
        mock_team_repo.get_by_id.return_value = sample_team
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await handler.handle(command)
        
        assert "Team name cannot be empty" in str(exc_info.value)
        mock_team_repo.update.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_invalid_team_number_zero(
        self,
        handler,
        mock_team_repo,
        sample_team
    ):
        """Test that ValidationError is raised when team number is zero."""
        # Arrange
        command = UpdateTeamCommand(
            team_id=sample_team.id,
            team_number=0
        )
        mock_team_repo.get_by_id.return_value = sample_team
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await handler.handle(command)
        
        assert "Team number must be positive" in str(exc_info.value)
        mock_team_repo.update.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_invalid_team_number_negative(
        self,
        handler,
        mock_team_repo,
        sample_team
    ):
        """Test that ValidationError is raised when team number is negative."""
        # Arrange
        command = UpdateTeamCommand(
            team_id=sample_team.id,
            team_number=-1
        )
        mock_team_repo.get_by_id.return_value = sample_team
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await handler.handle(command)
        
        assert "Team number must be positive" in str(exc_info.value)
        mock_team_repo.update.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_duplicate_team_number(
        self,
        handler,
        mock_team_repo,
        mock_club_repo,
        sample_club,
        sample_team
    ):
        """Test that ValidationError is raised when duplicate team number exists."""
        # Arrange
        existing_team = Team(
            id=uuid4(),
            name="Existing Team",
            club_id=sample_club.id,
            team_number=2
        )
        command = UpdateTeamCommand(
            team_id=sample_team.id,
            team_number=2
        )
        mock_team_repo.get_by_id.return_value = sample_team
        mock_team_repo.get_by_club.return_value = [sample_team, existing_team]
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await handler.handle(command)
        
        assert "already exists" in str(exc_info.value).lower()
        mock_team_repo.update.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_update_name_only(
        self,
        handler,
        mock_team_repo,
        sample_team
    ):
        """Test successful update of team name only."""
        # Arrange
        command = UpdateTeamCommand(
            team_id=sample_team.id,
            name="Updated Team Name"
        )
        mock_team_repo.get_by_id.return_value = sample_team
        
        # Mock updated team
        updated_team = Team(
            id=sample_team.id,
            name="Updated Team Name",
            club_id=sample_team.club_id,
            team_number=sample_team.team_number
        )
        mock_team_repo.update.return_value = updated_team
        
        # Act
        result = await handler.handle(command)
        
        # Assert
        assert result.success is True
        assert result.team_id == sample_team.id
        assert "updated successfully" in result.message.lower()
        assert result.command_id == command.command_id
        assert result.timestamp == command.timestamp
        
        mock_team_repo.get_by_id.assert_called_once_with(sample_team.id)
        mock_team_repo.update.assert_called_once()
        
        # Verify the team entity passed to update()
        updated_team_arg = mock_team_repo.update.call_args[0][0]
        assert updated_team_arg.name == "Updated Team Name"
        assert updated_team_arg.club_id == sample_team.club_id
        assert updated_team_arg.team_number == sample_team.team_number
    
    @pytest.mark.asyncio
    async def test_handle_update_club_and_team_number(
        self,
        handler,
        mock_team_repo,
        mock_club_repo,
        sample_team,
        another_club
    ):
        """Test successful update of club and team number."""
        # Arrange
        command = UpdateTeamCommand(
            team_id=sample_team.id,
            club_id=another_club.id,
            team_number=3
        )
        mock_team_repo.get_by_id.return_value = sample_team
        mock_club_repo.get_by_id.return_value = another_club
        mock_team_repo.get_by_club.return_value = []  # No existing teams in new club
        
        # Mock updated team
        updated_team = Team(
            id=sample_team.id,
            name=sample_team.name,
            club_id=another_club.id,
            team_number=3
        )
        mock_team_repo.update.return_value = updated_team
        
        # Act
        result = await handler.handle(command)
        
        # Assert
        assert result.success is True
        assert result.team_id == sample_team.id
        
        updated_team_arg = mock_team_repo.update.call_args[0][0]
        assert updated_team_arg.club_id == another_club.id
        assert updated_team_arg.team_number == 3
    
    @pytest.mark.asyncio
    async def test_handle_update_all_fields(
        self,
        handler,
        mock_team_repo,
        mock_club_repo,
        sample_team,
        another_club
    ):
        """Test successful update of all fields."""
        # Arrange
        command = UpdateTeamCommand(
            team_id=sample_team.id,
            name="Fully Updated Team",
            club_id=another_club.id,
            team_number=5
        )
        mock_team_repo.get_by_id.return_value = sample_team
        mock_club_repo.get_by_id.return_value = another_club
        mock_team_repo.get_by_club.return_value = []
        
        updated_team = Team(
            id=sample_team.id,
            name="Fully Updated Team",
            club_id=another_club.id,
            team_number=5
        )
        mock_team_repo.update.return_value = updated_team
        
        # Act
        result = await handler.handle(command)
        
        # Assert
        assert result.success is True
        
        updated_team_arg = mock_team_repo.update.call_args[0][0]
        assert updated_team_arg.name == "Fully Updated Team"
        assert updated_team_arg.club_id == another_club.id
        assert updated_team_arg.team_number == 5
    
    @pytest.mark.asyncio
    async def test_handle_no_changes(
        self,
        handler,
        mock_team_repo,
        sample_team
    ):
        """Test that update succeeds even when no fields are provided (no-op)."""
        # Arrange
        command = UpdateTeamCommand(team_id=sample_team.id)
        mock_team_repo.get_by_id.return_value = sample_team
        mock_team_repo.update.return_value = sample_team
        
        # Act
        result = await handler.handle(command)
        
        # Assert
        assert result.success is True
        assert result.team_id == sample_team.id
        mock_team_repo.update.assert_called_once()
