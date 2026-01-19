"""
Tests for GetTeamVsTeamComparisonHandler.

Tests the handler with various scenarios including edge cases.
"""

import pytest
from unittest.mock import AsyncMock
from uuid import UUID, uuid4
from datetime import datetime
from domain.value_objects.season import Season
from domain.entities.league import League
from domain.entities.league_season import LeagueSeason
from domain.entities.team import Team
from domain.entities.team_season import TeamSeason
from domain.entities.event import Event
from domain.entities.match import Match, MatchStatus
from domain.entities.game_result import GameResult
from domain.entities.position_comparison import PositionComparison, ComparisonOutcome
from domain.entities.scoring_system import ScoringSystem
from domain.entities.club import Club
from domain.value_objects.event_status import EventStatus
from application.queries.league.get_team_vs_team_comparison_query import GetTeamVsTeamComparisonQuery
from application.query_handlers.league.get_team_vs_team_comparison_handler import GetTeamVsTeamComparisonHandler
from application.exceptions import EntityNotFoundError


@pytest.fixture
def mock_team_season_repo():
    """Mock TeamSeasonRepository."""
    return AsyncMock()


@pytest.fixture
def mock_league_season_repo():
    """Mock LeagueSeasonRepository."""
    return AsyncMock()


@pytest.fixture
def mock_league_repo():
    """Mock LeagueRepository."""
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
def mock_scoring_system_repo():
    """Mock ScoringSystemRepository."""
    return AsyncMock()


@pytest.fixture
def mock_team_repo():
    """Mock TeamRepository."""
    return AsyncMock()


@pytest.fixture
def mock_match_scoring_repo():
    """Mock MatchScoringRepository."""
    return AsyncMock()


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
def sample_scoring_system():
    """Sample ScoringSystem entity."""
    return ScoringSystem(
        id=uuid4(),
        name="Test Scoring",
        points_per_team_match_win=2.0,
        points_per_team_match_loss=0.0,
        points_per_team_match_tie=1.0,
        points_per_individual_match_win=1.0,
        points_per_individual_match_loss=0.0,
        points_per_individual_match_tie=0.5
    )


@pytest.fixture
def sample_league_season(sample_league, sample_scoring_system):
    """Sample LeagueSeason entity."""
    return LeagueSeason(
        id=uuid4(),
        league_id=sample_league.id,
        season=Season("2024-25"),
        scoring_system_id=str(sample_scoring_system.id)
    )


@pytest.fixture
def sample_club():
    """Sample Club entity."""
    return Club(
        id=uuid4(),
        name="Test Club",
        short_name="TC"
    )


@pytest.fixture
def sample_team1(sample_club):
    """Sample Team entity for team 1."""
    return Team(
        id=uuid4(),
        club_id=sample_club.id,
        team_number=1,
        name="Team 1"
    )


@pytest.fixture
def sample_team2(sample_club):
    """Sample Team entity for team 2."""
    return Team(
        id=uuid4(),
        club_id=sample_club.id,
        team_number=2,
        name="Team 2"
    )


@pytest.fixture
def sample_team_season1(sample_league_season, sample_team1):
    """Sample TeamSeason entity for team 1."""
    return TeamSeason(
        id=uuid4(),
        league_season_id=sample_league_season.id,
        team_id=sample_team1.id,
        vacancy_status="filled"
    )


@pytest.fixture
def sample_team_season2(sample_league_season, sample_team2):
    """Sample TeamSeason entity for team 2."""
    return TeamSeason(
        id=uuid4(),
        league_season_id=sample_league_season.id,
        team_id=sample_team2.id,
        vacancy_status="filled"
    )


@pytest.fixture
def sample_event(sample_league_season):
    """Sample Event entity."""
    return Event(
        id=uuid4(),
        league_season_id=sample_league_season.id,
        league_week=1,
        status=EventStatus.COMPLETED,
        date=datetime(2024, 10, 1)
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


@pytest.fixture
def handler(
    mock_team_season_repo,
    mock_league_season_repo,
    mock_league_repo,
    mock_event_repo,
    mock_match_repo,
    mock_game_result_repo,
    mock_position_comparison_repo,
    mock_scoring_system_repo,
    mock_team_repo,
    mock_match_scoring_repo
):
    """Create handler with mocked repositories."""
    return GetTeamVsTeamComparisonHandler(
        team_season_repository=mock_team_season_repo,
        league_season_repository=mock_league_season_repo,
        league_repository=mock_league_repo,
        event_repository=mock_event_repo,
        match_repository=mock_match_repo,
        game_result_repository=mock_game_result_repo,
        position_comparison_repository=mock_position_comparison_repo,
        scoring_system_repository=mock_scoring_system_repo,
        team_repository=mock_team_repo,
        match_scoring_repository=mock_match_scoring_repo
    )


class TestGetTeamVsTeamComparisonHandler:
    """Test suite for GetTeamVsTeamComparisonHandler."""
    
    @pytest.mark.asyncio
    async def test_handle_team1_not_found(
        self,
        handler,
        mock_team_season_repo,
        sample_team_season2
    ):
        """Test that EntityNotFoundError is raised when team1 season is not found."""
        # Arrange
        team1_id = uuid4()
        query = GetTeamVsTeamComparisonQuery(
            team1_season_id=team1_id,
            team2_season_id=sample_team_season2.id
        )
        mock_team_season_repo.get_by_id.side_effect = lambda x: (
            None if x == team1_id else sample_team_season2
        )
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError, match="TeamSeason .* not found"):
            await handler.handle(query)
    
    @pytest.mark.asyncio
    async def test_handle_team2_not_found(
        self,
        handler,
        mock_team_season_repo,
        sample_team_season1
    ):
        """Test that EntityNotFoundError is raised when team2 season is not found."""
        # Arrange
        team2_id = uuid4()
        query = GetTeamVsTeamComparisonQuery(
            team1_season_id=sample_team_season1.id,
            team2_season_id=team2_id
        )
        mock_team_season_repo.get_by_id.side_effect = lambda x: (
            sample_team_season1 if x == sample_team_season1.id else None
        )
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError, match="TeamSeason .* not found"):
            await handler.handle(query)
    
    @pytest.mark.asyncio
    async def test_handle_different_league_seasons(
        self,
        handler,
        mock_team_season_repo,
        sample_team_season1,
        sample_team_season2
    ):
        """Test that EntityNotFoundError is raised when teams are in different league seasons."""
        # Arrange
        different_league_season = TeamSeason(
            id=uuid4(),
            league_season_id=uuid4(),  # Different league season
            team_id=sample_team_season2.team_id,
            vacancy_status="filled"
        )
        query = GetTeamVsTeamComparisonQuery(
            team1_season_id=sample_team_season1.id,
            team2_season_id=different_league_season.id
        )
        mock_team_season_repo.get_by_id.side_effect = lambda x: (
            sample_team_season1 if x == sample_team_season1.id else different_league_season
        )
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError, match="Teams must be in the same league season"):
            await handler.handle(query)
    
    @pytest.mark.asyncio
    async def test_handle_no_matches(
        self,
        handler,
        mock_team_season_repo,
        mock_league_season_repo,
        mock_league_repo,
        mock_event_repo,
        mock_match_repo,
        mock_team_repo,
        mock_scoring_system_repo,
        sample_league,
        sample_league_season,
        sample_scoring_system,
        sample_team_season1,
        sample_team_season2,
        sample_team1,
        sample_team2,
        sample_club
    ):
        """Test handler returns empty comparison when no matches exist."""
        # Arrange
        query = GetTeamVsTeamComparisonQuery(
            team1_season_id=sample_team_season1.id,
            team2_season_id=sample_team_season2.id
        )
        
        mock_team_season_repo.get_by_id.side_effect = lambda x: (
            sample_team_season1 if x == sample_team_season1.id else sample_team_season2
        )
        mock_league_season_repo.get_by_id.return_value = sample_league_season
        mock_league_repo.get_by_id.return_value = sample_league
        mock_scoring_system_repo.get_by_id.return_value = sample_scoring_system
        mock_team_repo.get_by_id.side_effect = lambda x: (
            sample_team1 if x == sample_team1.id else sample_team2
        )
        mock_event_repo.get_by_league_season.return_value = []
        mock_match_repo.get_by_event.return_value = []
        
        # Act
        result = await handler.handle(query)
        
        # Assert
        assert result.team1_season_id == sample_team_season1.id
        assert result.team2_season_id == sample_team_season2.id
        assert result.matches_played == 0
        assert result.team1_wins == 0
        assert result.team2_wins == 0
        assert result.ties == 0
        assert result.matches == []
    
    @pytest.mark.asyncio
    async def test_handle_single_match_with_position_comparisons(
        self,
        handler,
        mock_team_season_repo,
        mock_league_season_repo,
        mock_league_repo,
        mock_event_repo,
        mock_match_repo,
        mock_game_result_repo,
        mock_position_comparison_repo,
        mock_scoring_system_repo,
        mock_team_repo,
        sample_league,
        sample_league_season,
        sample_scoring_system,
        sample_team_season1,
        sample_team_season2,
        sample_team1,
        sample_team2,
        sample_club,
        sample_event,
        sample_match
    ):
        """Test handler correctly calculates comparison with one match."""
        # Arrange
        query = GetTeamVsTeamComparisonQuery(
            team1_season_id=sample_team_season1.id,
            team2_season_id=sample_team_season2.id
        )
        
        # Mock repositories
        mock_team_season_repo.get_by_id.side_effect = lambda x: (
            sample_team_season1 if x == sample_team_season1.id else sample_team_season2
        )
        mock_league_season_repo.get_by_id.return_value = sample_league_season
        mock_league_repo.get_by_id.return_value = sample_league
        mock_scoring_system_repo.get_by_id.return_value = sample_scoring_system
        mock_team_repo.get_by_id.side_effect = lambda x: (
            sample_team1 if x == sample_team1.id else sample_team2
        )
        mock_event_repo.get_by_league_season.return_value = [sample_event]
        mock_match_repo.get_by_event.return_value = [sample_match]
        
        # Mock game results
        player1_id = uuid4()
        player2_id = uuid4()
        game_results = [
            GameResult(
                id=uuid4(),
                match_id=sample_match.id,
                team_season_id=sample_team_season1.id,
                player_id=player1_id,
                position=0,
                score=200.0
            ),
            GameResult(
                id=uuid4(),
                match_id=sample_match.id,
                team_season_id=sample_team_season2.id,
                player_id=player2_id,
                position=0,
                score=180.0
            )
        ]
        mock_game_result_repo.get_by_match.return_value = game_results
        
        # Mock position comparisons
        position_comparisons = [
            PositionComparison(
                id=uuid4(),
                match_id=sample_match.id,
                position=0,
                team1_player_id=player1_id,
                team2_player_id=player2_id,
                team1_score=200.0,
                team2_score=180.0,
                outcome=ComparisonOutcome.TEAM1_WIN
            )
        ]
        mock_position_comparison_repo.get_by_match.return_value = position_comparisons
        
        # Act
        result = await handler.handle(query)
        
        # Assert
        assert result.matches_played == 1
        assert result.team1_wins == 1
        assert result.team2_wins == 0
        assert result.ties == 0
        # Total scores are aggregated from position comparisons (only position 0 has data: 200 vs 180)
        assert result.team1_total_score == 200  # From position comparison
        assert result.team2_total_score == 180  # From position comparison
        assert len(result.matches) == 1
        assert result.matches[0].result == "team1_win"
        # Check individual points (team1 won position 0, so gets win points)
        assert result.team1_total_individual_points == sample_scoring_system.points_per_individual_match_win
        assert result.team2_total_individual_points == sample_scoring_system.points_per_individual_match_loss
