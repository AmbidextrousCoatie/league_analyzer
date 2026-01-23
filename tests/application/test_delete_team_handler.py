"""
Tests for DeleteTeamHandler.

Tests the handler with various scenarios including edge cases.
"""

import pytest
from unittest.mock import AsyncMock
from uuid import UUID, uuid4
from domain.entities.team import Team
from domain.entities.team_season import TeamSeason
from domain.entities.club import Club
from application.commands.league.delete_team_command import DeleteTeamCommand
from application.command_handlers.league.delete_team_handler import DeleteTeamHandler
from application.exceptions import EntityNotFoundError, ValidationError


@pytest.fixture
def mock_team_repo():
    """Mock TeamRepository."""
    return AsyncMock()


@pytest.fixture
def mock_team_season_repo():
    """Mock TeamSeasonRepository."""
    return AsyncMock()


@pytest.fixture
def handler(mock_team_repo, mock_team_season_repo):
    """Create handler with mocked repositories."""
    return DeleteTeamHandler(
        team_repository=mock_team_repo,
        team_season_repository=mock_team_season_repo
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
        name="Test Team",
        club_id=sample_club.id,
        team_number=1
    )


@pytest.fixture
def sample_team_season(sample_team):
    """Sample TeamSeason entity."""
    return TeamSeason(
        id=uuid4(),
        league_season_id=uuid4(),
        team_id=sample_team.id
    )


class TestDeleteTeamHandler:
    """Test suite for DeleteTeamHandler."""
    
    @pytest.mark.asyncio
    async def test_handle_team_not_found(
        self,
        handler,
        mock_team_repo,
        mock_team_season_repo
    ):
        """Test that EntityNotFoundError is raised when team is not found."""
        # Arrange
        team_id = uuid4()
        command = DeleteTeamCommand(team_id=team_id)
        mock_team_repo.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError) as exc_info:
            await handler.handle(command)
        
        assert f"Team {team_id} not found" in str(exc_info.value)
        mock_team_repo.get_by_id.assert_called_once_with(team_id)
        mock_team_repo.delete.assert_not_called()
        mock_team_season_repo.get_by_team.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_team_with_related_data_no_force(
        self,
        handler,
        mock_team_repo,
        mock_team_season_repo,
        sample_team,
        sample_team_season
    ):
        """Test that ValidationError is raised when team has related data and force=False."""
        # Arrange
        command = DeleteTeamCommand(team_id=sample_team.id, force=False)
        mock_team_repo.get_by_id.return_value = sample_team
        mock_team_season_repo.get_by_team.return_value = [sample_team_season]
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await handler.handle(command)
        
        assert "has related data" in str(exc_info.value).lower()
        assert "team season" in str(exc_info.value).lower()
        mock_team_repo.delete.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_team_with_related_data_force_true(
        self,
        handler,
        mock_team_repo,
        mock_team_season_repo,
        sample_team,
        sample_team_season
    ):
        """Test that team is deleted when force=True even with related data."""
        # Arrange
        command = DeleteTeamCommand(team_id=sample_team.id, force=True)
        mock_team_repo.get_by_id.return_value = sample_team
        mock_team_season_repo.get_by_team.return_value = [sample_team_season]
        
        # Act
        result = await handler.handle(command)
        
        # Assert
        assert result.success is True
        assert result.team_id == sample_team.id
        assert "deleted successfully" in result.message.lower()
        assert result.command_id == command.command_id
        assert result.timestamp == command.timestamp
        
        mock_team_repo.get_by_id.assert_called_once_with(sample_team.id)
        mock_team_season_repo.get_by_team.assert_called_once_with(sample_team.id)
        mock_team_repo.delete.assert_called_once_with(sample_team.id)
    
    @pytest.mark.asyncio
    async def test_handle_team_no_related_data(
        self,
        handler,
        mock_team_repo,
        mock_team_season_repo,
        sample_team
    ):
        """Test successful deletion when team has no related data."""
        # Arrange
        command = DeleteTeamCommand(team_id=sample_team.id, force=False)
        mock_team_repo.get_by_id.return_value = sample_team
        mock_team_season_repo.get_by_team.return_value = []
        
        # Act
        result = await handler.handle(command)
        
        # Assert
        assert result.success is True
        assert result.team_id == sample_team.id
        assert "deleted successfully" in result.message.lower()
        
        mock_team_repo.get_by_id.assert_called_once_with(sample_team.id)
        mock_team_season_repo.get_by_team.assert_called_once_with(sample_team.id)
        mock_team_repo.delete.assert_called_once_with(sample_team.id)
    
    @pytest.mark.asyncio
    async def test_handle_team_multiple_related_data_no_force(
        self,
        handler,
        mock_team_repo,
        mock_team_season_repo,
        sample_team
    ):
        """Test that ValidationError is raised when team has multiple related team seasons and force=False."""
        # Arrange
        team_season1 = TeamSeason(
            id=uuid4(),
            league_season_id=uuid4(),
            team_id=sample_team.id
        )
        team_season2 = TeamSeason(
            id=uuid4(),
            league_season_id=uuid4(),
            team_id=sample_team.id
        )
        command = DeleteTeamCommand(team_id=sample_team.id, force=False)
        mock_team_repo.get_by_id.return_value = sample_team
        mock_team_season_repo.get_by_team.return_value = [team_season1, team_season2]
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await handler.handle(command)
        
        assert "has related data" in str(exc_info.value).lower()
        assert "2 team season" in str(exc_info.value).lower()
        mock_team_repo.delete.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_team_multiple_related_data_force_true(
        self,
        handler,
        mock_team_repo,
        mock_team_season_repo,
        sample_team
    ):
        """Test that team is deleted when force=True even with multiple related team seasons."""
        # Arrange
        team_season1 = TeamSeason(
            id=uuid4(),
            league_season_id=uuid4(),
            team_id=sample_team.id
        )
        team_season2 = TeamSeason(
            id=uuid4(),
            league_season_id=uuid4(),
            team_id=sample_team.id
        )
        command = DeleteTeamCommand(team_id=sample_team.id, force=True)
        mock_team_repo.get_by_id.return_value = sample_team
        mock_team_season_repo.get_by_team.return_value = [team_season1, team_season2]
        
        # Act
        result = await handler.handle(command)
        
        # Assert
        assert result.success is True
        assert result.team_id == sample_team.id
        mock_team_repo.delete.assert_called_once_with(sample_team.id)
