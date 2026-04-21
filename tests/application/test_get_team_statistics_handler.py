"""
Tests for GetTeamStatisticsHandler.

Tests the handler with various scenarios including edge cases.
"""

import pytest
from unittest.mock import AsyncMock
from uuid import UUID, uuid4
from datetime import datetime
from domain.entities.team import Team
from domain.entities.club import Club
from domain.entities.team_season import TeamSeason
from domain.entities.league_season import LeagueSeason
from domain.entities.league import League
from application.queries.league.get_team_statistics_query import GetTeamStatisticsQuery
from application.query_handlers.league.get_team_statistics_handler import GetTeamStatisticsHandler
from application.exceptions import EntityNotFoundError


@pytest.fixture
def mock_team_repo():
    """Mock TeamRepository."""
    return AsyncMock()


@pytest.fixture
def mock_club_repo():
    """Mock ClubRepository."""
    return AsyncMock()


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
def mock_event_repo():
    """Mock EventRepository."""
    return AsyncMock()


@pytest.fixture
def handler(
    mock_team_repo,
    mock_club_repo,
    mock_team_season_repo,
    mock_league_season_repo,
    mock_league_repo,
    mock_event_repo,
    mock_match_repo,
    mock_game_result_repo,
    mock_position_comparison_repo,
    mock_scoring_system_repo
):
    """Create handler with mocked repositories."""
    return GetTeamStatisticsHandler(
        team_repository=mock_team_repo,
        club_repository=mock_club_repo,
        team_season_repository=mock_team_season_repo,
        league_season_repository=mock_league_season_repo,
        league_repository=mock_league_repo,
        event_repository=mock_event_repo,
        match_repository=mock_match_repo,
        game_result_repository=mock_game_result_repo,
        position_comparison_repository=mock_position_comparison_repo,
        scoring_system_repository=mock_scoring_system_repo
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
def sample_league():
    """Sample League entity."""
    return League(
        id=uuid4(),
        name="Test League",
        level=1,
        abbreviation="TL"
    )


@pytest.fixture
def sample_league_season(sample_league):
    """Sample LeagueSeason entity."""
    from domain.value_objects.season import Season
    return LeagueSeason(
        id=uuid4(),
        league_id=sample_league.id,
        season=Season("2024-25"),
        scoring_system_id=str(uuid4())
    )


@pytest.fixture
def sample_team_season(sample_team, sample_league_season):
    """Sample TeamSeason entity."""
    return TeamSeason(
        id=uuid4(),
        league_season_id=sample_league_season.id,
        team_id=sample_team.id
    )


class TestGetTeamStatisticsHandler:
    """Test suite for GetTeamStatisticsHandler."""
    
    @pytest.mark.asyncio
    async def test_handle_team_not_found(
        self,
        handler,
        mock_team_repo
    ):
        """Test that EntityNotFoundError is raised when team is not found."""
        # Arrange
        team_id = uuid4()
        query = GetTeamStatisticsQuery(team_id=team_id)
        mock_team_repo.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError) as exc_info:
            await handler.handle(query)
        
        assert f"Team {team_id} not found" in str(exc_info.value)
        mock_team_repo.get_by_id.assert_called_once_with(team_id)
    
    @pytest.mark.asyncio
    async def test_handle_basic_statistics_all_time(
        self,
        handler,
        mock_team_repo,
        mock_club_repo,
        mock_team_season_repo,
        sample_team,
        sample_club,
        sample_team_season
    ):
        """Test basic statistics calculation for all_time filter."""
        # Arrange
        query = GetTeamStatisticsQuery(team_id=sample_team.id, filter_type="all_time")
        mock_team_repo.get_by_id.return_value = sample_team
        mock_club_repo.get_by_id.return_value = sample_club
        mock_team_season_repo.get_by_team.return_value = []
        
        # Act
        result = await handler.handle(query)
        
        # Assert
        assert result is not None
        assert result.team_id == sample_team.id
        assert result.team_name == sample_team.name
        assert result.club_id == sample_club.id
        assert result.club_name == sample_club.name
        assert result.filter_type == "all_time"
        assert result.total_games_played == 0
        assert result.total_score == 0
        assert result.average_score == 0.0
        assert result.total_points == 0.0
        assert result.average_points == 0.0
        assert result.total_wins == 0
        assert result.total_losses == 0
        assert result.total_ties == 0
        assert len(result.season_progression) == 0
        assert len(result.season_statistics) == 0
        assert len(result.weekly_performances) == 0
        assert len(result.best_games) == 0
        assert len(result.worst_games) == 0
        assert len(result.biggest_wins) == 0
        assert len(result.biggest_losses) == 0
        assert result.clutch_performance.total_close_matches == 0
        assert len(result.position_performance) == 0
        assert result.recent_form.last_n_matches == 0
    
    @pytest.mark.asyncio
    async def test_handle_basic_statistics_with_matches(
        self,
        handler,
        mock_team_repo,
        mock_club_repo,
        mock_team_season_repo,
        mock_league_season_repo,
        mock_league_repo,
        mock_event_repo,
        mock_match_repo,
        mock_game_result_repo,
        mock_position_comparison_repo,
        mock_scoring_system_repo,
        sample_team,
        sample_club,
        sample_team_season,
        sample_league_season,
        sample_league
    ):
        """Test basic statistics calculation with actual matches."""
        from domain.entities.match import Match, MatchStatus
        from domain.entities.game_result import GameResult
        from domain.entities.position_comparison import PositionComparison, ComparisonOutcome
        from domain.entities.scoring_system import ScoringSystem
        from domain.value_objects.season import Season
        
        # Arrange
        query = GetTeamStatisticsQuery(team_id=sample_team.id, filter_type="all_time")
        mock_team_repo.get_by_id.return_value = sample_team
        mock_club_repo.get_by_id.return_value = sample_club
        mock_team_season_repo.get_by_team.return_value = [sample_team_season]
        mock_league_season_repo.get_by_id.return_value = sample_league_season
        mock_league_repo.get_by_id.return_value = sample_league
        
        # Create a match
        match_id = uuid4()
        opponent_team_season_id = uuid4()
        event_id = uuid4()
        match = Match(
            id=match_id,
            event_id=event_id,
            team1_team_season_id=sample_team_season.id,
            team2_team_season_id=opponent_team_season_id,
            team1_total_score=200.0,
            team2_total_score=180.0,
            status=MatchStatus.COMPLETED
        )
        mock_match_repo.get_by_team.return_value = [match]
        
        # Create game results (4 players per team = 8 total)
        game_results = []
        for i in range(4):
            game_results.append(GameResult(
                id=uuid4(),
                match_id=match_id,
                player_id=uuid4(),
                team_season_id=sample_team_season.id,
                position=i,
                score=50.0 + i * 10.0  # 50, 60, 70, 80 = 260 total
            ))
        mock_game_result_repo.get_by_match.return_value = game_results
        
        # Create position comparisons (team wins all 4 positions)
        position_comparisons = []
        for i in range(4):
            position_comparisons.append(PositionComparison(
                id=uuid4(),
                match_id=match_id,
                position=i,
                team1_player_id=uuid4(),
                team2_player_id=uuid4(),
                team1_score=50.0 + i * 10.0,
                team2_score=40.0 + i * 10.0,
                outcome=ComparisonOutcome.TEAM1_WIN
            ))
        mock_position_comparison_repo.get_by_match.return_value = position_comparisons
        
        # Create scoring system
        scoring_system = ScoringSystem(
            id=UUID(sample_league_season.scoring_system_id),
            name="Test System",
            points_per_team_match_win=2.0,
            points_per_team_match_tie=1.0,
            points_per_team_match_loss=0.0,
            points_per_individual_match_win=1.0,
            points_per_individual_match_tie=0.5,
            points_per_individual_match_loss=0.0
        )
        mock_scoring_system_repo.get_by_id.return_value = scoring_system
        
        # Act
        result = await handler.handle(query)
        
        # Assert
        assert result.total_games_played == 1
        assert result.total_score == 260  # Sum of game results (50+60+70+80)
        assert result.average_score == 260.0
        assert result.total_wins == 1
        assert result.total_losses == 0
        assert result.total_ties == 0
        # Total points = team match win (2.0) + individual wins (4 * 1.0 = 4.0) = 6.0
        assert result.total_points == 6.0
        assert result.average_points == 6.0
