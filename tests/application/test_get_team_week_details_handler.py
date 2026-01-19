"""
Tests for GetTeamWeekDetailsHandler.

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
from domain.entities.player import Player
from domain.value_objects.event_status import EventStatus
from application.queries.league.get_team_week_details_query import GetTeamWeekDetailsQuery
from application.query_handlers.league.get_team_week_details_handler import GetTeamWeekDetailsHandler
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
def mock_player_repo():
    """Mock PlayerRepository."""
    return AsyncMock()


@pytest.fixture
def mock_team_repo():
    """Mock TeamRepository."""
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
def sample_team(sample_club):
    """Sample Team entity."""
    return Team(
        id=uuid4(),
        club_id=sample_club.id,
        team_number=1,
        name="Team 1"
    )


@pytest.fixture
def sample_team_season(sample_league_season, sample_team):
    """Sample TeamSeason entity."""
    return TeamSeason(
        id=uuid4(),
        league_season_id=sample_league_season.id,
        team_id=sample_team.id,
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
def sample_opponent_team_season(sample_league_season):
    """Sample opponent TeamSeason entity."""
    return TeamSeason(
        id=uuid4(),
        league_season_id=sample_league_season.id,
        team_id=uuid4(),
        vacancy_status="filled"
    )


@pytest.fixture
def sample_match(sample_event, sample_team_season, sample_opponent_team_season):
    """Sample Match entity."""
    return Match(
        id=uuid4(),
        event_id=sample_event.id,
        round_number=1,
        match_number=1,
        team1_team_season_id=sample_team_season.id,
        team2_team_season_id=sample_opponent_team_season.id,
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
    mock_player_repo,
    mock_team_repo
):
    """Create handler with mocked repositories."""
    return GetTeamWeekDetailsHandler(
        team_season_repository=mock_team_season_repo,
        league_season_repository=mock_league_season_repo,
        league_repository=mock_league_repo,
        event_repository=mock_event_repo,
        match_repository=mock_match_repo,
        game_result_repository=mock_game_result_repo,
        position_comparison_repository=mock_position_comparison_repo,
        scoring_system_repository=mock_scoring_system_repo,
        player_repository=mock_player_repo,
        team_repository=mock_team_repo
    )


class TestGetTeamWeekDetailsHandler:
    """Test suite for GetTeamWeekDetailsHandler."""
    
    @pytest.mark.asyncio
    async def test_handle_team_season_not_found(
        self,
        handler,
        mock_team_season_repo
    ):
        """Test that EntityNotFoundError is raised when team season is not found."""
        # Arrange
        team_season_id = uuid4()
        query = GetTeamWeekDetailsQuery(
            team_season_id=team_season_id,
            week=1
        )
        mock_team_season_repo.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError, match="TeamSeason .* not found"):
            await handler.handle(query)
    
    @pytest.mark.asyncio
    async def test_handle_no_events_for_week(
        self,
        handler,
        mock_team_season_repo,
        mock_league_season_repo,
        mock_league_repo,
        mock_event_repo,
        mock_team_repo,
        sample_team_season,
        sample_league_season,
        sample_league,
        sample_team
    ):
        """Test that empty result is returned when no events exist for the week."""
        # Arrange
        query = GetTeamWeekDetailsQuery(
            team_season_id=sample_team_season.id,
            week=1
        )
        mock_team_season_repo.get_by_id.return_value = sample_team_season
        mock_league_season_repo.get_by_id.return_value = sample_league_season
        mock_league_repo.get_by_id.return_value = sample_league
        mock_team_repo.get_by_id.return_value = sample_team
        mock_event_repo.get_by_league_season.return_value = []
        
        # Act
        result = await handler.handle(query)
        
        # Assert
        assert result.team_season_id == sample_team_season.id
        assert result.week == 1
        assert result.matches == []
        assert result.player_performances == []
        assert result.total_team_score == 0
        assert result.wins == 0
        assert result.losses == 0
        assert result.ties == 0
    
    @pytest.mark.asyncio
    async def test_handle_success_with_match(
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
        mock_player_repo,
        mock_team_repo,
        sample_team_season,
        sample_league_season,
        sample_scoring_system,
        sample_league,
        sample_team,
        sample_event,
        sample_match,
        sample_opponent_team_season
    ):
        """Test successful handling with a match."""
        # Arrange
        query = GetTeamWeekDetailsQuery(
            team_season_id=sample_team_season.id,
            week=1
        )
        
        # Mock repositories
        mock_team_season_repo.get_by_id.return_value = sample_team_season
        mock_league_season_repo.get_by_id.return_value = sample_league_season
        mock_league_repo.get_by_id.return_value = sample_league
        mock_team_repo.get_by_id.side_effect = lambda x: (
            sample_team if x == sample_team.id else Team(
                id=x,
                club_id=uuid4(),
                team_number=1,
                name="Opponent Team"
            )
        )
        mock_scoring_system_repo.get_by_id.return_value = sample_scoring_system
        mock_event_repo.get_by_league_season.return_value = [sample_event]
        mock_match_repo.get_by_event.return_value = [sample_match]
        
        # Mock game results - need all 4 positions for both teams to get total score of 800
        player_id = uuid4()
        opponent_player_id = uuid4()
        game_results = [
            # Team 1 players (positions 0-3)
            GameResult(
                id=uuid4(),
                match_id=sample_match.id,
                team_season_id=sample_team_season.id,
                player_id=player_id,
                position=0,
                score=200.0
            ),
            GameResult(
                id=uuid4(),
                match_id=sample_match.id,
                team_season_id=sample_team_season.id,
                player_id=uuid4(),
                position=1,
                score=200.0
            ),
            GameResult(
                id=uuid4(),
                match_id=sample_match.id,
                team_season_id=sample_team_season.id,
                player_id=uuid4(),
                position=2,
                score=200.0
            ),
            GameResult(
                id=uuid4(),
                match_id=sample_match.id,
                team_season_id=sample_team_season.id,
                player_id=uuid4(),
                position=3,
                score=200.0
            ),
            # Opponent players (positions 0-3)
            GameResult(
                id=uuid4(),
                match_id=sample_match.id,
                team_season_id=sample_opponent_team_season.id,
                player_id=opponent_player_id,
                position=0,
                score=180.0
            ),
            GameResult(
                id=uuid4(),
                match_id=sample_match.id,
                team_season_id=sample_opponent_team_season.id,
                player_id=uuid4(),
                position=1,
                score=190.0
            ),
            GameResult(
                id=uuid4(),
                match_id=sample_match.id,
                team_season_id=sample_opponent_team_season.id,
                player_id=uuid4(),
                position=2,
                score=190.0
            ),
            GameResult(
                id=uuid4(),
                match_id=sample_match.id,
                team_season_id=sample_opponent_team_season.id,
                player_id=uuid4(),
                position=3,
                score=190.0
            )
        ]
        mock_game_result_repo.get_by_match.return_value = game_results
        
        # Mock position comparisons
        position_comparisons = [
            PositionComparison(
                id=uuid4(),
                match_id=sample_match.id,
                position=0,
                team1_player_id=player_id,
                team2_player_id=opponent_player_id,
                team1_score=200.0,
                team2_score=180.0,
                outcome=ComparisonOutcome.TEAM1_WIN
            )
        ]
        mock_position_comparison_repo.get_by_match.return_value = position_comparisons
        
        # Mock players
        mock_player_repo.get_by_id.side_effect = lambda x: (
            Player(id=x, name="Player 1") if x == player_id
            else Player(id=x, name="Opponent Player")
        )
        
        # Mock opponent team season
        mock_team_season_repo.get_by_id.side_effect = lambda x: (
            sample_team_season if x == sample_team_season.id
            else sample_opponent_team_season if x == sample_opponent_team_season.id
            else None
        )
        
        # Act
        result = await handler.handle(query)
        
        # Assert
        assert result.team_season_id == sample_team_season.id
        assert result.week == 1
        assert len(result.matches) == 1
        assert result.matches[0].result == "win"
        assert result.wins == 1
        assert result.losses == 0
        assert result.ties == 0
        assert result.total_team_score == 800  # Sum of 4 positions: 200+200+200+200
        assert len(result.player_performances) == 4  # One for each position
