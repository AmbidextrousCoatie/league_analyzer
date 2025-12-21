"""
Tests for PandasTeamRepository (CSV implementation).

Following TDD: These tests are written BEFORE implementation.
"""

import pytest
import pandas as pd
from uuid import UUID, uuid4
from domain.entities.team import Team
from domain.repositories.team_repository import TeamRepository
from domain.exceptions.domain_exception import EntityNotFoundError


class TestPandasTeamRepository:
    """Test cases for PandasTeamRepository CSV implementation."""
    
    @pytest.fixture
    def club_id(self):
        """Fixture for club ID."""
        return uuid4()
    
    @pytest.fixture
    def sample_team(self):
        """Fixture for sample team."""
        return Team(
            id=uuid4(),
            name="Team 1"
        )
    
    @pytest.fixture
    def team_csv_path(self, tmp_path):
        """Create a temporary team.csv file for testing."""
        csv_file = tmp_path / "team.csv"
        df = pd.DataFrame(columns=[
            'id', 'club_id', 'team_number', 'name', 'league_id'
        ])
        df.to_csv(csv_file, index=False)
        return csv_file
    
    @pytest.fixture
    def mock_data_adapter(self, team_csv_path):
        """Mock DataAdapter for testing with real CSV file."""
        from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
        adapter = PandasDataAdapter(team_csv_path)
        return adapter
    
    @pytest.fixture
    def team_mapper(self):
        """Team mapper for testing."""
        from infrastructure.persistence.mappers.csv.team_mapper import PandasTeamMapper
        return PandasTeamMapper()
    
    @pytest.fixture
    def team_repository(self, mock_data_adapter, team_mapper):
        """Fixture for team repository."""
        from infrastructure.persistence.repositories.csv.team_repository import PandasTeamRepository
        return PandasTeamRepository(mock_data_adapter, team_mapper)
    
    async def test_get_by_id_returns_team_when_exists(
        self,
        team_repository: TeamRepository,
        sample_team: Team
    ):
        """Test getting team by ID when it exists."""
        await team_repository.add(sample_team)
        result = await team_repository.get_by_id(sample_team.id)
        assert result is not None
        assert result.id == sample_team.id
        assert result.name == sample_team.name
    
    async def test_get_by_id_returns_none_when_not_exists(
        self,
        team_repository: TeamRepository
    ):
        """Test getting team by ID when it doesn't exist."""
        result = await team_repository.get_by_id(uuid4())
        assert result is None
    
    async def test_get_all_returns_all_teams(
        self,
        team_repository: TeamRepository,
        club_id: UUID
    ):
        """Test getting all teams."""
        t1 = Team(
            id=uuid4(),
            name="Team 1"
        )
        t2 = Team(
            id=uuid4(),
            name="Team 2"
        )
        await team_repository.add(t1)
        await team_repository.add(t2)
        results = await team_repository.get_all()
        assert len(results) >= 2
    
    async def test_add_creates_new_team(
        self,
        team_repository: TeamRepository,
        sample_team: Team
    ):
        """Test adding a new team."""
        result = await team_repository.add(sample_team)
        assert result.id == sample_team.id
        assert await team_repository.exists(sample_team.id)
    
    async def test_update_modifies_existing_team(
        self,
        team_repository: TeamRepository,
        sample_team: Team
    ):
        """Test updating an existing team."""
        await team_repository.add(sample_team)
        sample_team.update_name("Updated Team")
        result = await team_repository.update(sample_team)
        assert result.name == "Updated Team"
    
    async def test_update_raises_error_when_not_exists(
        self,
        team_repository: TeamRepository,
        sample_team: Team
    ):
        """Test updating non-existent team raises error."""
        with pytest.raises(EntityNotFoundError):
            await team_repository.update(sample_team)
    
    async def test_delete_removes_team(
        self,
        team_repository: TeamRepository,
        sample_team: Team
    ):
        """Test deleting a team."""
        await team_repository.add(sample_team)
        await team_repository.delete(sample_team.id)
        assert not await team_repository.exists(sample_team.id)
    
    async def test_get_by_club_returns_filtered_teams(
        self,
        team_repository: TeamRepository,
        club_id: UUID
    ):
        """Test getting teams by club."""
        league_id = uuid4()
        t1 = Team(
            id=uuid4(),
            name="Team 1"
        )
        t1.assign_to_league(league_id)
        t2 = Team(
            id=uuid4(),
            name="Team 2"
        )
        await team_repository.add(t1)
        await team_repository.add(t2)
        results = await team_repository.get_by_league(league_id)
        assert len(results) >= 1
        assert any(t.league_id == league_id for t in results)

