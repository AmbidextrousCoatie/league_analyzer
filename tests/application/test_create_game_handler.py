"""
Tests for CreateGameHandler.

Tests the handler with various scenarios including edge cases.
"""

import pytest
from unittest.mock import AsyncMock
from uuid import UUID, uuid4
from domain.entities.match import Match, MatchStatus
from domain.entities.event import Event
from domain.entities.team_season import TeamSeason
from domain.value_objects.event_status import EventStatus
from application.commands.league.create_game_command import CreateGameCommand
from application.command_handlers.league.create_game_handler import CreateGameHandler
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
    return CreateGameHandler(
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


class TestCreateGameHandler:
    """Test suite for CreateGameHandler."""
    
    @pytest.mark.asyncio
    async def test_handle_event_not_found(
        self,
        handler,
        mock_event_repo,
        sample_team_season1,
        sample_team_season2
    ):
        """Test that EntityNotFoundError is raised when event is not found."""
        # Arrange
        event_id = uuid4()
        command = CreateGameCommand(
            event_id=event_id,
            team1_team_season_id=sample_team_season1.id,
            team2_team_season_id=sample_team_season2.id
        )
        mock_event_repo.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError, match="Event .* not found"):
            await handler.handle(command)
    
    @pytest.mark.asyncio
    async def test_handle_team1_season_not_found(
        self,
        handler,
        mock_event_repo,
        mock_team_season_repo,
        sample_event,
        sample_team_season2
    ):
        """Test that EntityNotFoundError is raised when team1 season is not found."""
        # Arrange
        team1_id = uuid4()
        command = CreateGameCommand(
            event_id=sample_event.id,
            team1_team_season_id=team1_id,
            team2_team_season_id=sample_team_season2.id
        )
        mock_event_repo.get_by_id.return_value = sample_event
        mock_team_season_repo.get_by_id.side_effect = lambda x: (
            None if x == team1_id else sample_team_season2
        )
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError, match="TeamSeason .* not found"):
            await handler.handle(command)
    
    @pytest.mark.asyncio
    async def test_handle_same_teams_raises_error(
        self,
        handler,
        mock_event_repo,
        mock_team_season_repo,
        sample_event,
        sample_team_season1
    ):
        """Test that ValidationError is raised when both teams are the same."""
        # Arrange
        command = CreateGameCommand(
            event_id=sample_event.id,
            team1_team_season_id=sample_team_season1.id,
            team2_team_season_id=sample_team_season1.id  # Same team
        )
        mock_event_repo.get_by_id.return_value = sample_event
        mock_team_season_repo.get_by_id.return_value = sample_team_season1
        
        # Act & Assert
        with pytest.raises(ValidationError, match="Team1 and Team2 must be different"):
            await handler.handle(command)
    
    @pytest.mark.asyncio
    async def test_handle_invalid_round_number(
        self,
        handler,
        mock_match_repo,
        mock_event_repo,
        mock_team_season_repo,
        sample_event,
        sample_team_season1,
        sample_team_season2
    ):
        """Test that ValidationError is raised when round number is invalid."""
        # Arrange
        command = CreateGameCommand(
            event_id=sample_event.id,
            team1_team_season_id=sample_team_season1.id,
            team2_team_season_id=sample_team_season2.id,
            round_number=0  # Invalid
        )
        mock_event_repo.get_by_id.return_value = sample_event
        mock_team_season_repo.get_by_id.side_effect = lambda x: (
            sample_team_season1 if x == sample_team_season1.id else sample_team_season2
        )
        mock_match_repo.get_by_event.return_value = []
        
        # Act & Assert
        with pytest.raises(ValidationError, match="Round number must be positive"):
            await handler.handle(command)
    
    @pytest.mark.asyncio
    async def test_handle_success(
        self,
        handler,
        mock_match_repo,
        mock_event_repo,
        mock_team_season_repo,
        sample_event,
        sample_team_season1,
        sample_team_season2
    ):
        """Test successful creation of a match."""
        # Arrange
        command = CreateGameCommand(
            event_id=sample_event.id,
            team1_team_season_id=sample_team_season1.id,
            team2_team_season_id=sample_team_season2.id,
            round_number=1,
            match_number=1,
            team1_total_score=800.0,
            team2_total_score=750.0,
            status=MatchStatus.SCHEDULED
        )
        mock_event_repo.get_by_id.return_value = sample_event
        mock_team_season_repo.get_by_id.side_effect = lambda x: (
            sample_team_season1 if x == sample_team_season1.id else sample_team_season2
        )
        mock_match_repo.get_by_event.return_value = []
        
        # Mock the add method to return the created match
        created_match = Match(
            id=uuid4(),
            event_id=sample_event.id,
            round_number=1,
            match_number=1,
            team1_team_season_id=sample_team_season1.id,
            team2_team_season_id=sample_team_season2.id,
            team1_total_score=800.0,
            team2_total_score=750.0,
            status=MatchStatus.SCHEDULED
        )
        mock_match_repo.add.return_value = created_match
        
        # Act
        result = await handler.handle(command)
        
        # Assert
        assert result.success is True
        assert result.match_id == created_match.id
        assert "created successfully" in result.message.lower()
        mock_match_repo.add.assert_called_once()
        created_match_arg = mock_match_repo.add.call_args[0][0]
        assert created_match_arg.event_id == sample_event.id
        assert created_match_arg.team1_team_season_id == sample_team_season1.id
        assert created_match_arg.team2_team_season_id == sample_team_season2.id
