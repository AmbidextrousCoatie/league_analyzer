"""
Tests for GetLeagueStandingsHandler.

Tests the handler with various scenarios including edge cases.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4
from datetime import datetime
from domain.value_objects.season import Season
from domain.value_objects.standings_status import StandingsStatus
from domain.entities.league import League
from domain.entities.league_season import LeagueSeason
from domain.entities.team import Team
from domain.entities.team_season import TeamSeason
from domain.entities.event import Event
from domain.value_objects.event_status import EventStatus
from domain.entities.scoring_system import ScoringSystem
from domain.domain_services.standings_calculator import StandingsCalculator
from domain.domain_services.standings_calculator import Standings, TeamStanding
from domain.value_objects.score import Score
from domain.value_objects.points import Points
from application.queries.league.get_league_standings_query import GetLeagueStandingsQuery
from application.query_handlers.league.get_league_standings_handler import GetLeagueStandingsHandler
from application.exceptions import EntityNotFoundError


@pytest.fixture
def mock_league_repo():
    """Mock LeagueRepository."""
    return AsyncMock()


@pytest.fixture
def mock_league_season_repo():
    """Mock LeagueSeasonRepository."""
    return AsyncMock()


@pytest.fixture
def mock_event_repo():
    """Mock EventRepository."""
    return AsyncMock()


@pytest.fixture
def mock_match_repo():
    """Mock MatchRepository."""
    return AsyncMock()


@pytest.fixture
def mock_game_result_repo():
    """Mock GameResultRepository."""
    return AsyncMock()


@pytest.fixture
def mock_position_comparison_repo():
    """Mock PositionComparisonRepository."""
    return AsyncMock()


@pytest.fixture
def mock_team_season_repo():
    """Mock TeamSeasonRepository."""
    return AsyncMock()


@pytest.fixture
def mock_team_repo():
    """Mock TeamRepository."""
    return AsyncMock()


@pytest.fixture
def mock_club_repo():
    """Mock ClubRepository."""
    return AsyncMock()


@pytest.fixture
def mock_scoring_system_repo():
    """Mock ScoringSystemRepository."""
    return AsyncMock()


@pytest.fixture
def mock_standings_calculator():
    """Mock StandingsCalculator."""
    return MagicMock(spec=StandingsCalculator)


@pytest.fixture
def sample_league():
    """Sample League entity."""
    return League(
        id=uuid4(),
        name="Test League",
        abbreviation="TEST",
        level=3
    )


@pytest.fixture
def sample_league_season(sample_league):
    """Sample LeagueSeason entity."""
    scoring_system_id = str(uuid4())
    return LeagueSeason(
        id=uuid4(),
        league_id=sample_league.id,
        season=Season("2024-25"),
        scoring_system_id=scoring_system_id
    )


@pytest.fixture
def sample_scoring_system():
    """Sample ScoringSystem entity."""
    return ScoringSystem(
        id=uuid4(),
        name="Standard Scoring",
        points_per_team_match_win=2.0,
        points_per_team_match_loss=0.0,
        points_per_team_match_tie=1.0,
        points_per_individual_match_win=1.0,
        points_per_individual_match_loss=0.0,
        points_per_individual_match_tie=0.5
    )


@pytest.fixture
def sample_team():
    """Sample Team entity."""
    return Team(
        id=uuid4(),
        name="Team Alpha",
        club_id=uuid4(),
        team_number=1
    )


@pytest.fixture
def sample_team_season(sample_league_season, sample_team):
    """Sample TeamSeason entity."""
    return TeamSeason(
        id=uuid4(),
        league_season_id=sample_league_season.id,
        team_id=sample_team.id
    )


@pytest.fixture
def sample_event(sample_league_season):
    """Sample Event entity."""
    return Event(
        id=uuid4(),
        league_season_id=sample_league_season.id,
        event_type="league",
        league_week=1,
        status=EventStatus.COMPLETED,
        date=datetime(2024, 9, 1)
    )


@pytest.fixture
def handler(
    mock_league_repo,
    mock_league_season_repo,
    mock_event_repo,
    mock_match_repo,
    mock_game_result_repo,
    mock_position_comparison_repo,
    mock_team_season_repo,
    mock_team_repo,
    mock_club_repo,
    mock_scoring_system_repo,
    mock_standings_calculator
):
    """Create GetLeagueStandingsHandler with mocked dependencies."""
    return GetLeagueStandingsHandler(
        league_repository=mock_league_repo,
        league_season_repository=mock_league_season_repo,
        event_repository=mock_event_repo,
        match_repository=mock_match_repo,
        game_result_repository=mock_game_result_repo,
        position_comparison_repository=mock_position_comparison_repo,
        team_season_repository=mock_team_season_repo,
        team_repository=mock_team_repo,
        club_repository=mock_club_repo,
        scoring_system_repository=mock_scoring_system_repo,
        standings_calculator=mock_standings_calculator
    )


class TestGetLeagueStandingsHandler:
    """Test suite for GetLeagueStandingsHandler."""
    
    @pytest.mark.asyncio
    async def test_handle_league_not_found(self, handler, mock_league_repo):
        """Test that EntityNotFoundError is raised when league is not found."""
        # Arrange
        query = GetLeagueStandingsQuery(league_id=uuid4())
        mock_league_repo.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError, match="League .* not found"):
            await handler.handle(query)
        
        mock_league_repo.get_by_id.assert_called_once_with(query.league_id)
    
    @pytest.mark.asyncio
    async def test_handle_league_season_not_found_with_explicit_id(
        self,
        handler,
        mock_league_repo,
        mock_league_season_repo,
        sample_league
    ):
        """Test that EntityNotFoundError is raised when explicit league_season_id is not found."""
        # Arrange
        league_season_id = uuid4()
        query = GetLeagueStandingsQuery(
            league_id=sample_league.id,
            league_season_id=league_season_id
        )
        mock_league_repo.get_by_id.return_value = sample_league
        mock_league_season_repo.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError, match="LeagueSeason .* not found"):
            await handler.handle(query)
        
        mock_league_season_repo.get_by_id.assert_called_once_with(league_season_id)
    
    @pytest.mark.asyncio
    async def test_handle_no_league_seasons_found(
        self,
        handler,
        mock_league_repo,
        mock_league_season_repo,
        sample_league
    ):
        """Test that EntityNotFoundError is raised when no league seasons exist."""
        # Arrange
        query = GetLeagueStandingsQuery(league_id=sample_league.id)
        mock_league_repo.get_by_id.return_value = sample_league
        mock_league_season_repo.get_by_league.return_value = []
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError, match="No league seasons found"):
            await handler.handle(query)
    
    @pytest.mark.asyncio
    async def test_handle_scoring_system_not_found(
        self,
        handler,
        mock_league_repo,
        mock_league_season_repo,
        mock_scoring_system_repo,
        sample_league,
        sample_league_season
    ):
        """Test that EntityNotFoundError is raised when scoring system is not found."""
        # Arrange
        query = GetLeagueStandingsQuery(league_id=sample_league.id)
        mock_league_repo.get_by_id.return_value = sample_league
        mock_league_season_repo.get_by_league.return_value = [sample_league_season]
        mock_scoring_system_repo.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError, match="ScoringSystem .* not found"):
            await handler.handle(query)
    
    @pytest.mark.asyncio
    async def test_handle_no_events_returns_empty_standings(
        self,
        handler,
        mock_league_repo,
        mock_league_season_repo,
        mock_event_repo,
        mock_scoring_system_repo,
        sample_league,
        sample_league_season,
        sample_scoring_system
    ):
        """Test that empty standings are returned when no events exist."""
        # Arrange
        query = GetLeagueStandingsQuery(league_id=sample_league.id)
        mock_league_repo.get_by_id.return_value = sample_league
        mock_league_season_repo.get_by_league.return_value = [sample_league_season]
        mock_scoring_system_repo.get_by_id.return_value = sample_scoring_system
        mock_event_repo.get_by_league_season.return_value = []
        
        # Act
        result = await handler.handle(query)
        
        # Assert
        assert result.league_id == sample_league.id
        assert result.league_name == sample_league.name
        assert result.league_season_id == sample_league_season.id
        assert result.season == sample_league_season.season.value
        assert result.standings == []
        assert result.weekly_standings == []
        assert result.status == "provisional"
    
    @pytest.mark.asyncio
    async def test_handle_no_team_seasons_returns_empty_standings(
        self,
        handler,
        mock_league_repo,
        mock_league_season_repo,
        mock_event_repo,
        mock_team_season_repo,
        mock_scoring_system_repo,
        sample_league,
        sample_league_season,
        sample_scoring_system,
        sample_event
    ):
        """Test that empty standings are returned when no team seasons exist."""
        # Arrange
        query = GetLeagueStandingsQuery(league_id=sample_league.id)
        mock_league_repo.get_by_id.return_value = sample_league
        mock_league_season_repo.get_by_league.return_value = [sample_league_season]
        mock_scoring_system_repo.get_by_id.return_value = sample_scoring_system
        mock_event_repo.get_by_league_season.return_value = [sample_event]
        mock_team_season_repo.get_by_league_season.return_value = []
        
        # Act
        result = await handler.handle(query)
        
        # Assert
        assert result.standings == []
        assert result.weekly_standings == []
    
    @pytest.mark.asyncio
    async def test_handle_success_with_standings(
        self,
        handler,
        mock_league_repo,
        mock_league_season_repo,
        mock_event_repo,
        mock_match_repo,
        mock_game_result_repo,
        mock_position_comparison_repo,
        mock_team_season_repo,
        mock_team_repo,
        mock_club_repo,
        mock_scoring_system_repo,
        mock_standings_calculator,
        sample_league,
        sample_league_season,
        sample_scoring_system,
        sample_event,
        sample_team,
        sample_team_season
    ):
        """Test successful handling with calculated standings."""
        # Arrange
        query = GetLeagueStandingsQuery(league_id=sample_league.id)
        mock_league_repo.get_by_id.return_value = sample_league
        mock_league_season_repo.get_by_league.return_value = [sample_league_season]
        mock_scoring_system_repo.get_by_id.return_value = sample_scoring_system
        mock_event_repo.get_by_league_season.return_value = [sample_event]
        mock_team_season_repo.get_by_league_season.return_value = [sample_team_season]
        mock_team_repo.get_by_id.return_value = sample_team
        
        # Mock empty matches and game results (simplified test)
        mock_match_repo.get_by_event.return_value = []
        mock_game_result_repo.get_by_match.return_value = []
        mock_position_comparison_repo.get_by_match.return_value = []
        
        # Mock standings calculator to return empty standings
        mock_standings_calculator.calculate_standings.return_value = Standings(
            league_season_id=sample_league_season.id,
            teams=[],
            status=StandingsStatus.PROVISIONAL,
            calculated_at=datetime.utcnow()
        )
        
        # Act
        result = await handler.handle(query)
        
        # Assert
        assert result.league_id == sample_league.id
        assert result.league_name == sample_league.name
        assert result.league_season_id == sample_league_season.id
        assert result.season == sample_league_season.season.value
        assert result.standings == []
        assert result.status == "provisional"
    
    @pytest.mark.asyncio
    async def test_handle_with_explicit_league_season_id(
        self,
        handler,
        mock_league_repo,
        mock_league_season_repo,
        mock_event_repo,
        mock_scoring_system_repo,
        sample_league,
        sample_league_season,
        sample_scoring_system
    ):
        """Test handling with explicit league_season_id."""
        # Arrange
        query = GetLeagueStandingsQuery(
            league_id=sample_league.id,
            league_season_id=sample_league_season.id
        )
        mock_league_repo.get_by_id.return_value = sample_league
        mock_league_season_repo.get_by_id.return_value = sample_league_season
        mock_scoring_system_repo.get_by_id.return_value = sample_scoring_system
        mock_event_repo.get_by_league_season.return_value = []
        
        # Act
        result = await handler.handle(query)
        
        # Assert
        assert result.league_season_id == sample_league_season.id
        # Should not call get_by_league when explicit ID is provided
        mock_league_season_repo.get_by_league.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_with_week_filter(
        self,
        handler,
        mock_league_repo,
        mock_league_season_repo,
        mock_event_repo,
        mock_scoring_system_repo,
        sample_league,
        sample_league_season,
        sample_scoring_system,
        sample_event
    ):
        """Test handling with week filter."""
        # Arrange
        query = GetLeagueStandingsQuery(
            league_id=sample_league.id,
            week=1
        )
        mock_league_repo.get_by_id.return_value = sample_league
        mock_league_season_repo.get_by_league.return_value = [sample_league_season]
        mock_scoring_system_repo.get_by_id.return_value = sample_scoring_system
        mock_event_repo.get_by_league_season.return_value = [sample_event]
        
        # Act
        result = await handler.handle(query)
        
        # Assert
        assert result.week == 1
