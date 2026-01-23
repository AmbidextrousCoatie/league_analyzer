"""
Tests for CreateTeamHandler.

Tests the handler with various scenarios including edge cases.
"""

import pytest
from unittest.mock import AsyncMock
from uuid import UUID, uuid4
from domain.entities.team import Team
from domain.entities.club import Club
from application.commands.league.create_team_command import CreateTeamCommand
from application.command_handlers.league.create_team_handler import CreateTeamHandler
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
    return CreateTeamHandler(
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


class TestCreateTeamHandler:
    """Test suite for CreateTeamHandler."""
    
    @pytest.mark.asyncio
    async def test_handle_club_not_found(
        self,
        handler,
        mock_club_repo
    ):
        """Test that EntityNotFoundError is raised when club is not found."""
        # Arrange
        club_id = uuid4()
        command = CreateTeamCommand(
            name="Test Team",
            club_id=club_id,
            team_number=1
        )
        mock_club_repo.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError) as exc_info:
            await handler.handle(command)
        
        assert f"Club {club_id} not found" in str(exc_info.value)
        mock_club_repo.get_by_id.assert_called_once_with(club_id)
        mock_club_repo.add.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_empty_name(
        self,
        handler,
        mock_club_repo,
        sample_club
    ):
        """Test that ValidationError is raised when team name is empty."""
        # Arrange
        command = CreateTeamCommand(
            name="",
            club_id=sample_club.id,
            team_number=1
        )
        mock_club_repo.get_by_id.return_value = sample_club
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await handler.handle(command)
        
        assert "Team name cannot be empty" in str(exc_info.value)
        mock_club_repo.get_by_id.assert_called_once_with(sample_club.id)
        mock_club_repo.add.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_whitespace_name(
        self,
        handler,
        mock_club_repo,
        sample_club
    ):
        """Test that ValidationError is raised when team name is only whitespace."""
        # Arrange
        command = CreateTeamCommand(
            name="   ",
            club_id=sample_club.id,
            team_number=1
        )
        mock_club_repo.get_by_id.return_value = sample_club
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await handler.handle(command)
        
        assert "Team name cannot be empty" in str(exc_info.value)
        mock_club_repo.add.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_invalid_team_number_zero(
        self,
        handler,
        mock_club_repo,
        sample_club
    ):
        """Test that ValidationError is raised when team number is zero."""
        # Arrange
        command = CreateTeamCommand(
            name="Test Team",
            club_id=sample_club.id,
            team_number=0
        )
        mock_club_repo.get_by_id.return_value = sample_club
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await handler.handle(command)
        
        assert "Team number must be positive" in str(exc_info.value)
        mock_club_repo.add.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_invalid_team_number_negative(
        self,
        handler,
        mock_club_repo,
        sample_club
    ):
        """Test that ValidationError is raised when team number is negative."""
        # Arrange
        command = CreateTeamCommand(
            name="Test Team",
            club_id=sample_club.id,
            team_number=-1
        )
        mock_club_repo.get_by_id.return_value = sample_club
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await handler.handle(command)
        
        assert "Team number must be positive" in str(exc_info.value)
        mock_club_repo.add.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_duplicate_team(
        self,
        handler,
        mock_club_repo,
        mock_team_repo,
        sample_club
    ):
        """Test that ValidationError is raised when duplicate team exists."""
        # Arrange
        existing_team = Team(
            id=uuid4(),
            name="Existing Team",
            club_id=sample_club.id,
            team_number=1
        )
        command = CreateTeamCommand(
            name="New Team",
            club_id=sample_club.id,
            team_number=1
        )
        mock_club_repo.get_by_id.return_value = sample_club
        mock_team_repo.get_by_club.return_value = [existing_team]
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await handler.handle(command)
        
        assert "already exists" in str(exc_info.value).lower()
        mock_club_repo.get_by_id.assert_called_once_with(sample_club.id)
        mock_team_repo.get_by_club.assert_called_once_with(sample_club.id)
        mock_team_repo.add.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_success(
        self,
        handler,
        mock_club_repo,
        mock_team_repo,
        sample_club
    ):
        """Test successful team creation."""
        # Arrange
        command = CreateTeamCommand(
            name="Test Team",
            club_id=sample_club.id,
            team_number=1
        )
        mock_club_repo.get_by_id.return_value = sample_club
        mock_team_repo.get_by_club.return_value = []  # No existing teams
        
        # Mock the created team
        created_team = Team(
            id=uuid4(),
            name="Test Team",
            club_id=sample_club.id,
            team_number=1
        )
        mock_team_repo.add.return_value = created_team
        
        # Act
        result = await handler.handle(command)
        
        # Assert
        assert result.success is True
        assert result.team_id == created_team.id
        assert "created successfully" in result.message.lower()
        assert result.command_id == command.command_id
        assert result.timestamp == command.timestamp
        
        mock_club_repo.get_by_id.assert_called_once_with(sample_club.id)
        mock_team_repo.get_by_club.assert_called_once_with(sample_club.id)
        mock_team_repo.add.assert_called_once()
        
        # Verify the team entity passed to add()
        added_team = mock_team_repo.add.call_args[0][0]
        assert added_team.name == "Test Team"
        assert added_team.club_id == sample_club.id
        assert added_team.team_number == 1
    
    @pytest.mark.asyncio
    async def test_handle_success_with_default_team_number(
        self,
        handler,
        mock_club_repo,
        mock_team_repo,
        sample_club
    ):
        """Test successful team creation with default team number."""
        # Arrange
        command = CreateTeamCommand(
            name="Test Team",
            club_id=sample_club.id
            # team_number defaults to 1
        )
        mock_club_repo.get_by_id.return_value = sample_club
        mock_team_repo.get_by_club.return_value = []
        
        created_team = Team(
            id=uuid4(),
            name="Test Team",
            club_id=sample_club.id,
            team_number=1
        )
        mock_team_repo.add.return_value = created_team
        
        # Act
        result = await handler.handle(command)
        
        # Assert
        assert result.success is True
        assert result.team_id == created_team.id
        
        added_team = mock_team_repo.add.call_args[0][0]
        assert added_team.team_number == 1
    
    @pytest.mark.asyncio
    async def test_handle_success_different_team_number(
        self,
        handler,
        mock_club_repo,
        mock_team_repo,
        sample_club
    ):
        """Test successful team creation with different team number when team 1 exists."""
        # Arrange
        existing_team = Team(
            id=uuid4(),
            name="Team 1",
            club_id=sample_club.id,
            team_number=1
        )
        command = CreateTeamCommand(
            name="Team 2",
            club_id=sample_club.id,
            team_number=2
        )
        mock_club_repo.get_by_id.return_value = sample_club
        mock_team_repo.get_by_club.return_value = [existing_team]
        
        created_team = Team(
            id=uuid4(),
            name="Team 2",
            club_id=sample_club.id,
            team_number=2
        )
        mock_team_repo.add.return_value = created_team
        
        # Act
        result = await handler.handle(command)
        
        # Assert
        assert result.success is True
        assert result.team_id == created_team.id
        
        added_team = mock_team_repo.add.call_args[0][0]
        assert added_team.team_number == 2
