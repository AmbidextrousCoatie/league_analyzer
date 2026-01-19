"""
Tests for GetMatchOverviewHandler.

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
from domain.entities.match_scoring import MatchScoring
from domain.value_objects.event_status import EventStatus
from application.queries.league.get_match_overview_query import GetMatchOverviewQuery
from application.query_handlers.league.get_match_overview_handler import GetMatchOverviewHandler
from application.exceptions import EntityNotFoundError


@pytest.fixture
def mock_match_repo():
    """Mock MatchRepository."""
    return AsyncMock()


@pytest.fixture
def mock_event_repo():
    """Mock EventRepository."""
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
def mock_position_comparison_repo():
    """Mock PositionComparisonRepository."""
    return AsyncMock()


@pytest.fixture
def mock_match_scoring_repo():
    """Mock MatchScoringRepository."""
    return AsyncMock()


@pytest.fixture
def mock_player_repo():
    """Mock PlayerRepository."""
    return AsyncMock()


@pytest.fixture
def mock_scoring_system_repo():
    """Mock ScoringSystemRepository."""
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
    mock_match_repo,
    mock_event_repo,
    mock_league_season_repo,
    mock_league_repo,
    mock_team_season_repo,
    mock_team_repo,
    mock_club_repo,
    mock_position_comparison_repo,
    mock_match_scoring_repo,
    mock_player_repo,
    mock_scoring_system_repo
):
    """Create handler with mocked repositories."""
    return GetMatchOverviewHandler(
        match_repository=mock_match_repo,
        event_repository=mock_event_repo,
        league_season_repository=mock_league_season_repo,
        league_repository=mock_league_repo,
        team_season_repository=mock_team_season_repo,
        team_repository=mock_team_repo,
        club_repository=mock_club_repo,
        position_comparison_repository=mock_position_comparison_repo,
        match_scoring_repository=mock_match_scoring_repo,
        player_repository=mock_player_repo,
        scoring_system_repository=mock_scoring_system_repo
    )


class TestGetMatchOverviewHandler:
    """Test suite for GetMatchOverviewHandler."""
    
    @pytest.mark.asyncio
    async def test_handle_match_not_found(
        self,
        handler,
        mock_match_repo
    ):
        """Test that EntityNotFoundError is raised when match is not found."""
        # Arrange
        match_id = uuid4()
        query = GetMatchOverviewQuery(match_id=match_id)
        mock_match_repo.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError, match="Match .* not found"):
            await handler.handle(query)
    
    @pytest.mark.asyncio
    async def test_handle_event_not_found(
        self,
        handler,
        mock_match_repo,
        mock_event_repo,
        sample_match
    ):
        """Test that EntityNotFoundError is raised when event is not found."""
        # Arrange
        query = GetMatchOverviewQuery(match_id=sample_match.id)
        mock_match_repo.get_by_id.return_value = sample_match
        mock_event_repo.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError, match="Event .* not found"):
            await handler.handle(query)
    
    @pytest.mark.asyncio
    async def test_handle_success(
        self,
        handler,
        mock_match_repo,
        mock_event_repo,
        mock_league_season_repo,
        mock_league_repo,
        mock_team_season_repo,
        mock_team_repo,
        mock_club_repo,
        mock_position_comparison_repo,
        mock_match_scoring_repo,
        mock_player_repo,
        mock_scoring_system_repo,
        sample_match,
        sample_event,
        sample_league_season,
        sample_league,
        sample_team_season1,
        sample_team_season2,
        sample_team1,
        sample_team2,
        sample_club,
        sample_scoring_system
    ):
        """Test successful handling of match overview."""
        # Arrange
        query = GetMatchOverviewQuery(match_id=sample_match.id)
        
        # Mock repositories
        mock_match_repo.get_by_id.return_value = sample_match
        mock_event_repo.get_by_id.return_value = sample_event
        mock_league_season_repo.get_by_id.return_value = sample_league_season
        mock_league_repo.get_by_id.return_value = sample_league
        mock_team_season_repo.get_by_id.side_effect = lambda x: (
            sample_team_season1 if x == sample_team_season1.id else sample_team_season2
        )
        mock_team_repo.get_by_id.side_effect = lambda x: (
            sample_team1 if x == sample_team1.id else sample_team2
        )
        mock_club_repo.get_by_id.return_value = sample_club
        mock_scoring_system_repo.get_by_id.return_value = sample_scoring_system
        
        # Mock position comparisons
        player1_id = uuid4()
        player2_id = uuid4()
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
        
        # Mock match scoring
        match_scoring = MatchScoring(
            id=uuid4(),
            match_id=sample_match.id,
            scoring_system_id=str(sample_scoring_system.id),
            team1_match_points=2.0,
            team2_match_points=0.0,
            team1_individual_points=1.0,
            team2_individual_points=0.0
        )
        mock_match_scoring_repo.get_by_match_and_system.return_value = match_scoring
        
        # Mock players - Player entity only has 'name' attribute, not 'full_name'
        mock_player_repo.get_by_id.side_effect = lambda x: (
            Player(id=x, name="Player 1") if x == player1_id
            else Player(id=x, name="Player 2")
        )
        
        # We need to mock game_result_repo.get_by_match but it's not in the handler fixture
        # Let me check what the handler actually uses...
        # Actually, looking at the handler, it uses game_result_repo which we don't have in the fixture
        # Let me add it
        
        # Actually wait, I see the issue - the handler doesn't use game_result_repo directly
        # It uses position_comparison_repo to get position comparisons
        # But we still need to handle the case where game results are needed
        
        # For now, let's test what we can with the available mocks
        # The handler will fail when trying to get game results, but that's okay for now
        
        # Actually, I realize the handler structure might be different. Let me check if we need game_result_repo
        # Looking at the handler code, it doesn't seem to use game_result_repo directly for match overview
        # It uses position_comparison_repo and match_scoring_repo
        
        # Act
        result = await handler.handle(query)
        
        # Assert
        assert result.match_id == sample_match.id
        assert result.event_id == sample_event.id
        assert result.league_id == sample_league.id
        assert result.league_name == sample_league.name
        assert len(result.position_comparisons) > 0
        assert result.team1.total_score == 800
        assert result.team2.total_score == 750
