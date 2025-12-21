"""
Tests for PandasLeagueSeasonRepository (CSV implementation).

Following TDD: These tests are written BEFORE implementation.
They should fail initially, then pass after implementation.
"""

import pytest
import pandas as pd
from uuid import UUID, uuid4
from domain.entities.league_season import LeagueSeason
from domain.repositories.league_season_repository import LeagueSeasonRepository
from domain.value_objects.season import Season
from domain.exceptions.domain_exception import EntityNotFoundError


class TestPandasLeagueSeasonRepository:
    """Test cases for PandasLeagueSeasonRepository CSV implementation."""
    
    @pytest.fixture
    def league_id(self):
        """Fixture for league ID."""
        return uuid4()
    
    @pytest.fixture
    def season(self):
        """Fixture for season."""
        return Season("2024-25")
    
    @pytest.fixture
    def sample_league_season(self, league_id, season):
        """Fixture for sample league season."""
        return LeagueSeason(
            id=uuid4(),
            league_id=league_id,
            season=season,
            scoring_system_id="system-1",
            number_of_teams=8,
            players_per_team=4
        )
    
    @pytest.fixture
    def league_season_csv_path(self, tmp_path):
        """Create a temporary league_season.csv file for testing."""
        csv_file = tmp_path / "league_season.csv"
        df = pd.DataFrame(columns=[
            'id', 'league_id', 'season', 'scoring_system_id', 
            'number_of_teams', 'players_per_team'
        ])
        df.to_csv(csv_file, index=False)
        return csv_file
    
    @pytest.fixture
    def mock_data_adapter(self, league_season_csv_path):
        """Mock DataAdapter for testing with real CSV file."""
        from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
        adapter = PandasDataAdapter(league_season_csv_path)
        return adapter
    
    @pytest.fixture
    def league_season_mapper(self):
        """League season mapper for testing."""
        from infrastructure.persistence.mappers.csv.league_season_mapper import PandasLeagueSeasonMapper
        return PandasLeagueSeasonMapper()
    
    @pytest.fixture
    def league_season_repository(self, mock_data_adapter, league_season_mapper):
        """Fixture for league season repository."""
        from infrastructure.persistence.repositories.csv.league_season_repository import PandasLeagueSeasonRepository
        return PandasLeagueSeasonRepository(mock_data_adapter, league_season_mapper)
    
    async def test_get_by_id_returns_league_season_when_exists(
        self,
        league_season_repository: LeagueSeasonRepository,
        sample_league_season: LeagueSeason
    ):
        """Test getting league season by ID when it exists."""
        # Arrange
        await league_season_repository.add(sample_league_season)
        
        # Act
        result = await league_season_repository.get_by_id(sample_league_season.id)
        
        # Assert
        assert result is not None
        assert result.id == sample_league_season.id
        assert result.league_id == sample_league_season.league_id
        assert result.season == sample_league_season.season
    
    async def test_get_by_id_returns_none_when_not_exists(
        self,
        league_season_repository: LeagueSeasonRepository
    ):
        """Test getting league season by ID when it doesn't exist."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        result = await league_season_repository.get_by_id(non_existent_id)
        
        # Assert
        assert result is None
    
    async def test_get_all_returns_all_league_seasons(
        self,
        league_season_repository: LeagueSeasonRepository,
        league_id: UUID,
        season: Season
    ):
        """Test getting all league seasons."""
        # Arrange
        ls1 = LeagueSeason(
            id=uuid4(),
            league_id=league_id,
            season=season,
            scoring_system_id="system-1"
        )
        ls2 = LeagueSeason(
            id=uuid4(),
            league_id=league_id,
            season=Season("2025-26"),
            scoring_system_id="system-1"
        )
        await league_season_repository.add(ls1)
        await league_season_repository.add(ls2)
        
        # Act
        results = await league_season_repository.get_all()
        
        # Assert
        assert len(results) >= 2
        assert any(ls.id == ls1.id for ls in results)
        assert any(ls.id == ls2.id for ls in results)
    
    async def test_add_creates_new_league_season(
        self,
        league_season_repository: LeagueSeasonRepository,
        sample_league_season: LeagueSeason
    ):
        """Test adding a new league season."""
        # Act
        result = await league_season_repository.add(sample_league_season)
        
        # Assert
        assert result.id == sample_league_season.id
        assert await league_season_repository.exists(sample_league_season.id)
    
    async def test_update_modifies_existing_league_season(
        self,
        league_season_repository: LeagueSeasonRepository,
        sample_league_season: LeagueSeason
    ):
        """Test updating an existing league season."""
        # Arrange
        await league_season_repository.add(sample_league_season)
        sample_league_season.update_scoring_system("system-2")
        sample_league_season.update_team_config(10, 5)
        
        # Act
        result = await league_season_repository.update(sample_league_season)
        
        # Assert
        assert result.scoring_system_id == "system-2"
        assert result.number_of_teams == 10
        assert result.players_per_team == 5
        
        # Verify persisted
        retrieved = await league_season_repository.get_by_id(sample_league_season.id)
        assert retrieved.scoring_system_id == "system-2"
    
    async def test_update_raises_error_when_not_exists(
        self,
        league_season_repository: LeagueSeasonRepository,
        sample_league_season: LeagueSeason
    ):
        """Test updating non-existent league season raises error."""
        # Act & Assert
        with pytest.raises(EntityNotFoundError):
            await league_season_repository.update(sample_league_season)
    
    async def test_delete_removes_league_season(
        self,
        league_season_repository: LeagueSeasonRepository,
        sample_league_season: LeagueSeason
    ):
        """Test deleting a league season."""
        # Arrange
        await league_season_repository.add(sample_league_season)
        assert await league_season_repository.exists(sample_league_season.id)
        
        # Act
        await league_season_repository.delete(sample_league_season.id)
        
        # Assert
        assert not await league_season_repository.exists(sample_league_season.id)
        assert await league_season_repository.get_by_id(sample_league_season.id) is None
    
    async def test_delete_raises_error_when_not_exists(
        self,
        league_season_repository: LeagueSeasonRepository
    ):
        """Test deleting non-existent league season raises error."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError):
            await league_season_repository.delete(non_existent_id)
    
    async def test_exists_returns_true_when_league_season_exists(
        self,
        league_season_repository: LeagueSeasonRepository,
        sample_league_season: LeagueSeason
    ):
        """Test exists returns True when league season exists."""
        # Arrange
        await league_season_repository.add(sample_league_season)
        
        # Act
        result = await league_season_repository.exists(sample_league_season.id)
        
        # Assert
        assert result is True
    
    async def test_exists_returns_false_when_league_season_not_exists(
        self,
        league_season_repository: LeagueSeasonRepository
    ):
        """Test exists returns False when league season doesn't exist."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        result = await league_season_repository.exists(non_existent_id)
        
        # Assert
        assert result is False
    
    async def test_get_by_league_returns_filtered_league_seasons(
        self,
        league_season_repository: LeagueSeasonRepository,
        league_id: UUID
    ):
        """Test getting league seasons by league."""
        # Arrange
        ls1 = LeagueSeason(
            id=uuid4(),
            league_id=league_id,
            season=Season("2024-25"),
            scoring_system_id="system-1"
        )
        other_league_id = uuid4()
        ls2 = LeagueSeason(
            id=uuid4(),
            league_id=other_league_id,
            season=Season("2024-25"),
            scoring_system_id="system-1"
        )
        await league_season_repository.add(ls1)
        await league_season_repository.add(ls2)
        
        # Act
        results = await league_season_repository.get_by_league(league_id)
        
        # Assert
        assert len(results) >= 1
        assert all(ls.league_id == league_id for ls in results)
        assert any(ls.id == ls1.id for ls in results)
        assert not any(ls.id == ls2.id for ls in results)
    
    async def test_get_by_season_returns_filtered_league_seasons(
        self,
        league_season_repository: LeagueSeasonRepository,
        league_id: UUID,
        season: Season
    ):
        """Test getting league seasons by season."""
        # Arrange
        ls1 = LeagueSeason(
            id=uuid4(),
            league_id=league_id,
            season=season,
            scoring_system_id="system-1"
        )
        ls2 = LeagueSeason(
            id=uuid4(),
            league_id=league_id,
            season=Season("2025-26"),
            scoring_system_id="system-1"
        )
        await league_season_repository.add(ls1)
        await league_season_repository.add(ls2)
        
        # Act
        results = await league_season_repository.get_by_season(season)
        
        # Assert
        assert len(results) >= 1
        assert all(ls.season == season for ls in results)
        assert any(ls.id == ls1.id for ls in results)
        assert not any(ls.id == ls2.id for ls in results)
    
    async def test_get_by_league_and_season_returns_single_league_season(
        self,
        league_season_repository: LeagueSeasonRepository,
        league_id: UUID,
        season: Season
    ):
        """Test getting league season by league and season."""
        # Arrange
        ls1 = LeagueSeason(
            id=uuid4(),
            league_id=league_id,
            season=season,
            scoring_system_id="system-1"
        )
        await league_season_repository.add(ls1)
        
        # Act
        result = await league_season_repository.get_by_league_and_season(league_id, season)
        
        # Assert
        assert result is not None
        assert result.id == ls1.id
        assert result.league_id == league_id
        assert result.season == season

