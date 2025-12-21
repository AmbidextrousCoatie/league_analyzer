"""
Tests for PandasPlayerRepository (CSV implementation).

Following TDD: These tests are written BEFORE implementation.
"""

import pytest
import pandas as pd
from uuid import UUID, uuid4
from domain.entities.player import Player
from domain.repositories.player_repository import PlayerRepository
from domain.exceptions.domain_exception import EntityNotFoundError


class TestPandasPlayerRepository:
    """Test cases for PandasPlayerRepository CSV implementation."""
    
    @pytest.fixture
    def club_id(self):
        """Fixture for club ID."""
        return uuid4()
    
    @pytest.fixture
    def sample_player(self, club_id):
        """Fixture for sample player."""
        return Player(
            id=uuid4(),
            name="John Doe",
            club_id=club_id
        )
    
    @pytest.fixture
    def player_csv_path(self, tmp_path):
        """Create a temporary player.csv file for testing."""
        csv_file = tmp_path / "player.csv"
        df = pd.DataFrame(columns=[
            'id', 'given_name', 'family_name', 'full_name', 'club_id'
        ])
        df.to_csv(csv_file, index=False)
        return csv_file
    
    @pytest.fixture
    def mock_data_adapter(self, player_csv_path):
        """Mock DataAdapter for testing with real CSV file."""
        from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
        adapter = PandasDataAdapter(player_csv_path)
        return adapter
    
    @pytest.fixture
    def player_mapper(self):
        """Player mapper for testing."""
        from infrastructure.persistence.mappers.csv.player_mapper import PandasPlayerMapper
        return PandasPlayerMapper()
    
    @pytest.fixture
    def player_repository(self, mock_data_adapter, player_mapper):
        """Fixture for player repository."""
        from infrastructure.persistence.repositories.csv.player_repository import PandasPlayerRepository
        return PandasPlayerRepository(mock_data_adapter, player_mapper)
    
    async def test_get_by_id_returns_player_when_exists(
        self,
        player_repository: PlayerRepository,
        sample_player: Player
    ):
        """Test getting player by ID when it exists."""
        await player_repository.add(sample_player)
        result = await player_repository.get_by_id(sample_player.id)
        assert result is not None
        assert result.id == sample_player.id
        assert result.name == sample_player.name
    
    async def test_get_by_id_returns_none_when_not_exists(
        self,
        player_repository: PlayerRepository
    ):
        """Test getting player by ID when it doesn't exist."""
        result = await player_repository.get_by_id(uuid4())
        assert result is None
    
    async def test_get_all_returns_all_players(
        self,
        player_repository: PlayerRepository,
        club_id: UUID
    ):
        """Test getting all players."""
        p1 = Player(
            id=uuid4(),
            name="John Doe",
            club_id=club_id
        )
        p2 = Player(
            id=uuid4(),
            name="Jane Smith",
            club_id=club_id
        )
        await player_repository.add(p1)
        await player_repository.add(p2)
        results = await player_repository.get_all()
        assert len(results) >= 2
    
    async def test_add_creates_new_player(
        self,
        player_repository: PlayerRepository,
        sample_player: Player
    ):
        """Test adding a new player."""
        result = await player_repository.add(sample_player)
        assert result.id == sample_player.id
        assert await player_repository.exists(sample_player.id)
    
    async def test_update_modifies_existing_player(
        self,
        player_repository: PlayerRepository,
        sample_player: Player
    ):
        """Test updating an existing player."""
        await player_repository.add(sample_player)
        sample_player.name = "Jane Smith"
        result = await player_repository.update(sample_player)
        assert result.name == "Jane Smith"
    
    async def test_update_raises_error_when_not_exists(
        self,
        player_repository: PlayerRepository,
        sample_player: Player
    ):
        """Test updating non-existent player raises error."""
        with pytest.raises(EntityNotFoundError):
            await player_repository.update(sample_player)
    
    async def test_delete_removes_player(
        self,
        player_repository: PlayerRepository,
        sample_player: Player
    ):
        """Test deleting a player."""
        await player_repository.add(sample_player)
        await player_repository.delete(sample_player.id)
        assert not await player_repository.exists(sample_player.id)
    
    async def test_get_by_club_returns_filtered_players(
        self,
        player_repository: PlayerRepository,
        club_id: UUID
    ):
        """Test getting players by club."""
        p1 = Player(
            id=uuid4(),
            name="John Doe",
            club_id=club_id
        )
        other_club_id = uuid4()
        p2 = Player(
            id=uuid4(),
            name="Jane Smith",
            club_id=other_club_id
        )
        await player_repository.add(p1)
        await player_repository.add(p2)
        results = await player_repository.get_by_club(club_id)
        assert len(results) >= 1
        assert all(p.club_id == club_id for p in results)
    
    async def test_get_by_name_returns_filtered_players(
        self,
        player_repository: PlayerRepository,
        club_id: UUID
    ):
        """Test getting players by name."""
        p1 = Player(
            id=uuid4(),
            name="John Doe",
            club_id=club_id
        )
        await player_repository.add(p1)
        results = await player_repository.get_by_name("John", "Doe")
        assert len(results) >= 1
        assert any(p.name == "John Doe" for p in results)

