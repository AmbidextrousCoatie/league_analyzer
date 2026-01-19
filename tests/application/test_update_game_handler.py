"""
Tests for UpdateGameHandler.

Tests the handler with various scenarios including edge cases.
"""

import pytest
from unittest.mock import AsyncMock
from uuid import UUID, uuid4
from domain.entities.match import Match, MatchStatus
from domain.entities.event import Event
from domain.entities.team_season import TeamSeason
from domain.value_objects.event_status import EventStatus
from application.commands.league.update_game_command import UpdateGameCommand
from application.command_handlers.league.update_game_handler import UpdateGameHandler
from application.exceptions import EntityNotFoundError, ValidationError


@pytest.fixture
def mock_match_repo():
    """Mock MatchRepository."""
    return AsyncMock()


@pytest.fixture
def mock_event_repo():
    """Mock EventRepository."""
    return AsyncMock()


@pytest.fixture
def mock_team_season_repo():
    """Mock TeamSeasonRepository."""
    return AsyncMock()


@pytest.fixture
def handler(mock_match_repo, mock_event_repo, mock_team_season_repo):
    """Create handler with mocked repositories."""
    return UpdateGameHandler(
        match_repository=mock_match_repo,
        event_repository=mock_event_repo,
        team_season_repository=mock_team_season_repo
    )


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
def sample_team_season1():
    """Sample TeamSeason entity for team 1."""
    return TeamSeason(
        id=uuid4(),
        league_season_id=uuid4(),
        team_id=uuid4(),
        vacancy_status="filled"
    )


@pytest.fixture
def sample_team_season2():
    """Sample TeamSeason entity for team 2."""
    return TeamSeason(
        id=uuid4(),
        league_season_id=uuid4(),
        team_id=uuid4(),
        vacancy_status="filled"
    )


@pytest.fixture
def sample_match(sample_event, sample_team_season1, sample_team_season2):
    """Sample Match entity."""
    return Match(
        id=uuid4(),
        event_id=sample_event.id,
        round_number=1,
        match_number=1,
        team1_team_season_id=sample_team_season1.id,
        team2_team_season_id=sample_team_season2.id,
        team1_total_score=800.0,
        team2_total_score=750.0,
        status=MatchStatus.COMPLETED
    )


class TestUpdateGameHandler:
    """Test suite for UpdateGameHandler."""
    
    @pytest.mark.asyncio
    async def test_handle_match_not_found(
        self,
        handler,
        mock_match_repo
    ):
        """Test that EntityNotFoundError is raised when match is not found."""
        # Arrange
        match_id = uuid4()
        command = UpdateGameCommand(match_id=match_id)
        mock_match_repo.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError, match="Match .* not found"):
            await handler.handle(command)
    
    @pytest.mark.asyncio
    async def test_handle_update_scores(
        self,
        handler,
        mock_match_repo,
        sample_match
    ):
        """Test successful update of match scores."""
        # Arrange
        command = UpdateGameCommand(
            match_id=sample_match.id,
            team1_total_score=850.0,
            team2_total_score=800.0
        )
        mock_match_repo.get_by_id.return_value = sample_match
        
        # Mock updated match
        updated_match = Match(
            id=sample_match.id,
            event_id=sample_match.event_id,
            round_number=sample_match.round_number,
            match_number=sample_match.match_number,
            team1_team_season_id=sample_match.team1_team_season_id,
            team2_team_season_id=sample_match.team2_team_season_id,
            team1_total_score=850.0,
            team2_total_score=800.0,
            status=sample_match.status,
            created_at=sample_match.created_at,
            updated_at=sample_match.updated_at
        )
        mock_match_repo.update.return_value = updated_match
        
        # Act
        result = await handler.handle(command)
        
        # Assert
        assert result.success is True
        assert result.match_id == sample_match.id
        mock_match_repo.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_update_status(
        self,
        handler,
        mock_match_repo,
        sample_match
    ):
        """Test successful update of match status."""
        # Arrange
        command = UpdateGameCommand(
            match_id=sample_match.id,
            status=MatchStatus.CANCELLED
        )
        mock_match_repo.get_by_id.return_value = sample_match
        
        # Mock updated match
        updated_match = Match(
            id=sample_match.id,
            event_id=sample_match.event_id,
            round_number=sample_match.round_number,
            match_number=sample_match.match_number,
            team1_team_season_id=sample_match.team1_team_season_id,
            team2_team_season_id=sample_match.team2_team_season_id,
            team1_total_score=sample_match.team1_total_score,
            team2_total_score=sample_match.team2_total_score,
            status=MatchStatus.CANCELLED,
            created_at=sample_match.created_at,
            updated_at=sample_match.updated_at
        )
        mock_match_repo.update.return_value = updated_match
        
        # Act
        result = await handler.handle(command)
        
        # Assert
        assert result.success is True
        assert result.match_id == sample_match.id
