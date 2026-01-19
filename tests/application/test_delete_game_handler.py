"""
Tests for DeleteGameHandler.

Tests the handler with various scenarios including edge cases.
"""

import pytest
from unittest.mock import AsyncMock
from uuid import UUID, uuid4
from domain.entities.match import Match, MatchStatus
from domain.entities.event import Event
from domain.entities.team_season import TeamSeason
from domain.value_objects.event_status import EventStatus
from application.commands.league.delete_game_command import DeleteGameCommand
from application.command_handlers.league.delete_game_handler import DeleteGameHandler
from application.exceptions import EntityNotFoundError


@pytest.fixture
def mock_match_repo():
    """Mock MatchRepository."""
    return AsyncMock()


@pytest.fixture
def handler(mock_match_repo):
    """Create handler with mocked repositories."""
    return DeleteGameHandler(match_repository=mock_match_repo)


@pytest.fixture
def sample_event():
    """Sample Event entity."""
    return Event(
        id=uuid4(),
        league_season_id=uuid4(),
        league_week=1,
        status=EventStatus.COMPLETED
    )


@pytest.fixture
def sample_match(sample_event):
    """Sample Match entity."""
    return Match(
        id=uuid4(),
        event_id=sample_event.id,
        round_number=1,
        match_number=1,
        team1_team_season_id=uuid4(),
        team2_team_season_id=uuid4(),
        team1_total_score=800.0,
        team2_total_score=750.0,
        status=MatchStatus.COMPLETED
    )


class TestDeleteGameHandler:
    """Test suite for DeleteGameHandler."""
    
    @pytest.mark.asyncio
    async def test_handle_match_not_found(
        self,
        handler,
        mock_match_repo
    ):
        """Test that EntityNotFoundError is raised when match is not found."""
        # Arrange
        match_id = uuid4()
        command = DeleteGameCommand(match_id=match_id)
        mock_match_repo.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError, match="Match .* not found"):
            await handler.handle(command)
    
    @pytest.mark.asyncio
    async def test_handle_success(
        self,
        handler,
        mock_match_repo,
        sample_match
    ):
        """Test successful deletion of a match."""
        # Arrange
        command = DeleteGameCommand(match_id=sample_match.id)
        mock_match_repo.get_by_id.return_value = sample_match
        mock_match_repo.delete.return_value = None
        
        # Act
        result = await handler.handle(command)
        
        # Assert
        assert result.success is True
        assert result.match_id == sample_match.id
        assert "deleted successfully" in result.message.lower()
        mock_match_repo.delete.assert_called_once_with(sample_match.id)
