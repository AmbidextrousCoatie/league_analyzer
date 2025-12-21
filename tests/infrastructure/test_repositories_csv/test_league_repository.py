"""
Tests for PandasLeagueRepository (CSV implementation).

Following TDD: These tests are written BEFORE implementation.
"""

import pytest
import pandas as pd
from uuid import UUID, uuid4
from domain.entities.league import League
from domain.repositories.league_repository import LeagueRepository
from domain.exceptions.domain_exception import EntityNotFoundError


class TestPandasLeagueRepository:
    """Test cases for PandasLeagueRepository CSV implementation."""
    
    @pytest.fixture
    def sample_league(self):
        """Fixture for sample league."""
        from domain.value_objects.season import Season
        return League(
            id=uuid4(),
            name="Test League",
            season=Season("2024-25")
        )
    
    @pytest.fixture
    def league_csv_path(self, tmp_path):
        """Create a temporary league.csv file for testing."""
        csv_file = tmp_path / "league.csv"
        df = pd.DataFrame(columns=[
            'id', 'name', 'short_name'
        ])
        df.to_csv(csv_file, index=False)
        return csv_file
    
    @pytest.fixture
    def mock_data_adapter(self, league_csv_path):
        """Mock DataAdapter for testing with real CSV file."""
        from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
        adapter = PandasDataAdapter(league_csv_path)
        return adapter
    
    @pytest.fixture
    def league_mapper(self):
        """League mapper for testing."""
        from infrastructure.persistence.mappers.csv.league_mapper import PandasLeagueMapper
        return PandasLeagueMapper()
    
    @pytest.fixture
    def league_repository(self, mock_data_adapter, league_mapper):
        """Fixture for league repository."""
        from infrastructure.persistence.repositories.csv.league_repository import PandasLeagueRepository
        return PandasLeagueRepository(mock_data_adapter, league_mapper)
    
    async def test_get_by_id_returns_league_when_exists(
        self,
        league_repository: LeagueRepository,
        sample_league: League
    ):
        """Test getting league by ID when it exists."""
        await league_repository.add(sample_league)
        result = await league_repository.get_by_id(sample_league.id)
        assert result is not None
        assert result.id == sample_league.id
        assert result.name == sample_league.name
    
    async def test_get_by_id_returns_none_when_not_exists(
        self,
        league_repository: LeagueRepository
    ):
        """Test getting league by ID when it doesn't exist."""
        result = await league_repository.get_by_id(uuid4())
        assert result is None
    
    async def test_get_all_returns_all_leagues(
        self,
        league_repository: LeagueRepository
    ):
        """Test getting all leagues."""
        from domain.value_objects.season import Season
        l1 = League(
            id=uuid4(),
            name="League 1",
            season=Season("2024-25")
        )
        l2 = League(
            id=uuid4(),
            name="League 2",
            season=Season("2024-25")
        )
        await league_repository.add(l1)
        await league_repository.add(l2)
        results = await league_repository.get_all()
        assert len(results) >= 2
    
    async def test_add_creates_new_league(
        self,
        league_repository: LeagueRepository,
        sample_league: League
    ):
        """Test adding a new league."""
        result = await league_repository.add(sample_league)
        assert result.id == sample_league.id
        assert await league_repository.exists(sample_league.id)
    
    async def test_update_modifies_existing_league(
        self,
        league_repository: LeagueRepository,
        sample_league: League
    ):
        """Test updating an existing league."""
        await league_repository.add(sample_league)
        sample_league.update_name("Updated League")
        result = await league_repository.update(sample_league)
        assert result.name == "Updated League"
    
    async def test_update_raises_error_when_not_exists(
        self,
        league_repository: LeagueRepository,
        sample_league: League
    ):
        """Test updating non-existent league raises error."""
        with pytest.raises(EntityNotFoundError):
            await league_repository.update(sample_league)
    
    async def test_delete_removes_league(
        self,
        league_repository: LeagueRepository,
        sample_league: League
    ):
        """Test deleting a league."""
        await league_repository.add(sample_league)
        await league_repository.delete(sample_league.id)
        assert not await league_repository.exists(sample_league.id)
    
    async def test_get_by_name_returns_filtered_leagues(
        self,
        league_repository: LeagueRepository
    ):
        """Test getting leagues by name."""
        from domain.value_objects.season import Season
        l1 = League(
            id=uuid4(),
            name="Test League",
            season=Season("2024-25")
        )
        await league_repository.add(l1)
        results = await league_repository.get_by_name("Test League")
        assert len(results) >= 1
        assert any(l.name == "Test League" for l in results)

