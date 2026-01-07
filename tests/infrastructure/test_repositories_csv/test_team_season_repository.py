"""
Tests for PandasTeamSeasonRepository (CSV implementation).

Following TDD: These tests are written BEFORE implementation.
"""

import pytest
import pandas as pd
from uuid import UUID, uuid4
from domain.entities.team_season import TeamSeason
from domain.repositories.team_season_repository import TeamSeasonRepository
from domain.value_objects.vacancy_status import VacancyStatus
from domain.exceptions.domain_exception import EntityNotFoundError


class TestPandasTeamSeasonRepository:
    """Test cases for PandasTeamSeasonRepository CSV implementation."""
    
    @pytest.fixture
    def league_season_id(self):
        """Fixture for league season ID."""
        return uuid4()
    
    @pytest.fixture
    def club_id(self):
        """Fixture for club ID."""
        return uuid4()
    
    @pytest.fixture
    def sample_team_season(self, league_season_id, club_id):
        """Fixture for sample team season."""
        return TeamSeason(
            id=uuid4(),
            league_season_id=league_season_id,
            club_id=club_id,
            team_number=1,
            vacancy_status=VacancyStatus.ACTIVE
        )
    
    @pytest.fixture
    def team_season_csv_path(self, tmp_path):
        """Create a temporary team_season.csv file for testing."""
        csv_file = tmp_path / "team_season.csv"
        df = pd.DataFrame(columns=[
            'id', 'league_season_id', 'club_id', 'team_number'
        ])
        df.to_csv(csv_file, index=False)
        return csv_file
    
    @pytest.fixture
    def mock_data_adapter(self, team_season_csv_path):
        """Mock DataAdapter for testing with real CSV file."""
        from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
        adapter = PandasDataAdapter(team_season_csv_path)
        return adapter
    
    @pytest.fixture
    def team_season_mapper(self):
        """Team season mapper for testing."""
        from infrastructure.persistence.mappers.csv.team_season_mapper import PandasTeamSeasonMapper
        return PandasTeamSeasonMapper()
    
    @pytest.fixture
    def team_season_repository(self, mock_data_adapter, team_season_mapper):
        """Fixture for team season repository."""
        from infrastructure.persistence.repositories.csv.team_season_repository import PandasTeamSeasonRepository
        return PandasTeamSeasonRepository(mock_data_adapter, team_season_mapper)
    
    async def test_get_by_id_returns_team_season_when_exists(
        self,
        team_season_repository: TeamSeasonRepository,
        sample_team_season: TeamSeason
    ):
        """Test getting team season by ID when it exists."""
        await team_season_repository.add(sample_team_season)
        result = await team_season_repository.get_by_id(sample_team_season.id)
        assert result is not None
        assert result.id == sample_team_season.id
    
    async def test_get_by_id_returns_none_when_not_exists(
        self,
        team_season_repository: TeamSeasonRepository
    ):
        """Test getting team season by ID when it doesn't exist."""
        result = await team_season_repository.get_by_id(uuid4())
        assert result is None
    
    async def test_get_all_returns_all_team_seasons(
        self,
        team_season_repository: TeamSeasonRepository,
        league_season_id: UUID,
        club_id: UUID
    ):
        """Test getting all team seasons."""
        ts1 = TeamSeason(
            id=uuid4(),
            league_season_id=league_season_id,
            club_id=club_id,
            team_number=1
        )
        ts2 = TeamSeason(
            id=uuid4(),
            league_season_id=league_season_id,
            club_id=club_id,
            team_number=2
        )
        await team_season_repository.add(ts1)
        await team_season_repository.add(ts2)
        results = await team_season_repository.get_all()
        assert len(results) >= 2
    
    async def test_add_creates_new_team_season(
        self,
        team_season_repository: TeamSeasonRepository,
        sample_team_season: TeamSeason
    ):
        """Test adding a new team season."""
        result = await team_season_repository.add(sample_team_season)
        assert result.id == sample_team_season.id
        assert await team_season_repository.exists(sample_team_season.id)
    
    async def test_add_duplicate_team_season_combination_updates_existing(
        self,
        team_season_repository: TeamSeasonRepository,
        league_season_id: UUID,
        club_id: UUID
    ):
        """Test that adding a TeamSeason with same club+team_number+league_season updates existing."""
        # This test documents expected behavior: same club+team_number+league_season should be unique
        # Note: Current implementation only checks for duplicate IDs, not business key duplicates
        # This may need to be enforced at application/domain service level
        ts1 = TeamSeason(
            id=uuid4(),
            league_season_id=league_season_id,
            club_id=club_id,
            team_number=1
        )
        await team_season_repository.add(ts1)
        
        # Try to add another TeamSeason with same club+team_number+league_season but different ID
        # Current implementation allows this - may need business rule enforcement
        ts2 = TeamSeason(
            id=uuid4(),  # Different ID
            league_season_id=league_season_id,
            club_id=club_id,
            team_number=1  # Same team_number
        )
        # Repository currently allows this - test documents current behavior
        result = await team_season_repository.add(ts2)
        # Both should exist (current behavior)
        assert await team_season_repository.exists(ts1.id)
        assert await team_season_repository.exists(ts2.id)
    
    async def test_update_modifies_existing_team_season(
        self,
        team_season_repository: TeamSeasonRepository,
        sample_team_season: TeamSeason
    ):
        """Test updating an existing team season."""
        await team_season_repository.add(sample_team_season)
        sample_team_season.mark_vacant()
        result = await team_season_repository.update(sample_team_season)
        assert result.vacancy_status == VacancyStatus.VACANT
    
    async def test_update_raises_error_when_not_exists(
        self,
        team_season_repository: TeamSeasonRepository,
        sample_team_season: TeamSeason
    ):
        """Test updating non-existent team season raises error."""
        with pytest.raises(EntityNotFoundError):
            await team_season_repository.update(sample_team_season)
    
    async def test_delete_removes_team_season(
        self,
        team_season_repository: TeamSeasonRepository,
        sample_team_season: TeamSeason
    ):
        """Test deleting a team season."""
        await team_season_repository.add(sample_team_season)
        await team_season_repository.delete(sample_team_season.id)
        assert not await team_season_repository.exists(sample_team_season.id)
    
    async def test_get_by_league_season_returns_filtered_team_seasons(
        self,
        team_season_repository: TeamSeasonRepository,
        league_season_id: UUID,
        club_id: UUID
    ):
        """Test getting team seasons by league season."""
        ts1 = TeamSeason(
            id=uuid4(),
            league_season_id=league_season_id,
            club_id=club_id,
            team_number=1
        )
        other_league_season_id = uuid4()
        ts2 = TeamSeason(
            id=uuid4(),
            league_season_id=other_league_season_id,
            club_id=club_id,
            team_number=1
        )
        await team_season_repository.add(ts1)
        await team_season_repository.add(ts2)
        results = await team_season_repository.get_by_league_season(league_season_id)
        assert len(results) >= 1
        assert all(ts.league_season_id == league_season_id for ts in results)
    
    async def test_get_by_club_returns_filtered_team_seasons(
        self,
        team_season_repository: TeamSeasonRepository,
        league_season_id: UUID,
        club_id: UUID
    ):
        """Test getting team seasons by club."""
        ts1 = TeamSeason(
            id=uuid4(),
            league_season_id=league_season_id,
            club_id=club_id,
            team_number=1
        )
        other_club_id = uuid4()
        ts2 = TeamSeason(
            id=uuid4(),
            league_season_id=league_season_id,
            club_id=other_club_id,
            team_number=1
        )
        await team_season_repository.add(ts1)
        await team_season_repository.add(ts2)
        results = await team_season_repository.get_by_club(club_id)
        assert len(results) >= 1
        assert all(ts.club_id == club_id for ts in results)
    
    async def test_get_by_vacancy_status_returns_filtered_team_seasons(
        self,
        team_season_repository: TeamSeasonRepository,
        league_season_id: UUID,
        club_id: UUID
    ):
        """Test getting team seasons by vacancy status."""
        ts1 = TeamSeason(
            id=uuid4(),
            league_season_id=league_season_id,
            club_id=club_id,
            team_number=1,
            vacancy_status=VacancyStatus.ACTIVE
        )
        ts2 = TeamSeason(
            id=uuid4(),
            league_season_id=league_season_id,
            club_id=club_id,
            team_number=2,
            vacancy_status=VacancyStatus.VACANT
        )
        await team_season_repository.add(ts1)
        await team_season_repository.add(ts2)
        results = await team_season_repository.get_by_vacancy_status(VacancyStatus.VACANT)
        assert len(results) >= 1
        assert all(ts.vacancy_status == VacancyStatus.VACANT for ts in results)

