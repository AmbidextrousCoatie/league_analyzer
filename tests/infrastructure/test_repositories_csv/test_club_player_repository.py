"""
Tests for PandasClubPlayerRepository (CSV implementation).

Following TDD: These tests are written BEFORE implementation.
They should fail initially, then pass after implementation.
"""

import pytest
import pandas as pd
from uuid import UUID, uuid4
from datetime import date
from domain.entities.club_player import ClubPlayer
from domain.repositories.club_player_repository import ClubPlayerRepository


class TestPandasClubPlayerRepository:
    """Test cases for PandasClubPlayerRepository CSV implementation."""

    @pytest.fixture
    def club_id(self) -> UUID:
        """Fixture for club ID."""
        return uuid4()

    @pytest.fixture
    def player_id(self) -> UUID:
        """Fixture for player ID."""
        return uuid4()

    @pytest.fixture
    def sample_club_player(self, club_id: UUID, player_id: UUID) -> ClubPlayer:
        """Fixture for a sample club-player relationship."""
        return ClubPlayer(
            id=uuid4(),
            club_id=club_id,
            player_id=player_id,
            date_entry=date(2024, 1, 1),
            date_exit=None,
        )

    @pytest.fixture
    def club_player_csv_path(self, tmp_path):
        """Create a temporary club_player.csv file for testing."""
        csv_file = tmp_path / "club_player.csv"
        df = pd.DataFrame(
            columns=[
                "id",
                "club_id",
                "player_id",
                "date_entry",
                "date_exit",
            ]
        )
        df.to_csv(csv_file, index=False)
        return csv_file

    @pytest.fixture
    def mock_data_adapter(self, club_player_csv_path):
        """Mock PandasDataAdapter for testing with real CSV file."""
        from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter

        return PandasDataAdapter(club_player_csv_path)

    @pytest.fixture
    def club_player_mapper(self):
        """ClubPlayer mapper for testing."""
        from infrastructure.persistence.mappers.csv.club_player_mapper import (
            PandasClubPlayerMapper,
        )

        return PandasClubPlayerMapper()

    @pytest.fixture
    def club_player_repository(
        self, mock_data_adapter, club_player_mapper
    ) -> ClubPlayerRepository:
        """Fixture for club-player repository."""
        from infrastructure.persistence.repositories.csv.club_player_repository import (
            PandasClubPlayerRepository,
        )

        return PandasClubPlayerRepository(mock_data_adapter, club_player_mapper)

    async def test_get_by_id_returns_relationship_when_exists(
        self,
        club_player_repository: ClubPlayerRepository,
        sample_club_player: ClubPlayer,
    ):
        """Test getting club-player relationship by ID when it exists."""
        await club_player_repository.add(sample_club_player)

        result = await club_player_repository.get_by_id(sample_club_player.id)

        assert result is not None
        assert result.id == sample_club_player.id
        assert result.club_id == sample_club_player.club_id
        assert result.player_id == sample_club_player.player_id

    async def test_get_by_id_returns_none_when_not_exists(
        self,
        club_player_repository: ClubPlayerRepository,
    ):
        """Test getting club-player relationship by ID when it doesn't exist."""
        result = await club_player_repository.get_by_id(uuid4())
        assert result is None

    async def test_get_all_returns_all_relationships(
        self,
        club_player_repository: ClubPlayerRepository,
        club_id: UUID,
        player_id: UUID,
    ):
        """Test getting all club-player relationships."""
        cp1 = ClubPlayer(
            id=uuid4(),
            club_id=club_id,
            player_id=player_id,
            date_entry=date(2024, 1, 1),
        )
        cp2 = ClubPlayer(
            id=uuid4(),
            club_id=club_id,
            player_id=uuid4(),
            date_entry=date(2024, 2, 1),
        )
        await club_player_repository.add(cp1)
        await club_player_repository.add(cp2)

        results = await club_player_repository.get_all()

        assert len(results) >= 2
        assert any(r.id == cp1.id for r in results)
        assert any(r.id == cp2.id for r in results)

    async def test_get_by_player_returns_filtered_relationships(
        self,
        club_player_repository: ClubPlayerRepository,
        club_id: UUID,
        player_id: UUID,
    ):
        """Test getting relationships by player."""
        cp1 = ClubPlayer(
            id=uuid4(),
            club_id=club_id,
            player_id=player_id,
            date_entry=date(2024, 1, 1),
        )
        other_player = uuid4()
        cp2 = ClubPlayer(
            id=uuid4(),
            club_id=club_id,
            player_id=other_player,
            date_entry=date(2024, 2, 1),
        )
        await club_player_repository.add(cp1)
        await club_player_repository.add(cp2)

        results = await club_player_repository.get_by_player(player_id)

        assert len(results) >= 1
        assert all(r.player_id == player_id for r in results)

    async def test_get_by_club_returns_filtered_relationships(
        self,
        club_player_repository: ClubPlayerRepository,
        club_id: UUID,
        player_id: UUID,
    ):
        """Test getting relationships by club."""
        cp1 = ClubPlayer(
            id=uuid4(),
            club_id=club_id,
            player_id=player_id,
            date_entry=date(2024, 1, 1),
        )
        other_club = uuid4()
        cp2 = ClubPlayer(
            id=uuid4(),
            club_id=other_club,
            player_id=player_id,
            date_entry=date(2024, 2, 1),
        )
        await club_player_repository.add(cp1)
        await club_player_repository.add(cp2)

        results = await club_player_repository.get_by_club(club_id)

        assert len(results) >= 1
        assert all(r.club_id == club_id for r in results)

    async def test_add_creates_new_relationship(
        self,
        club_player_repository: ClubPlayerRepository,
        sample_club_player: ClubPlayer,
    ):
        """Test adding a new club-player relationship."""
        result = await club_player_repository.add(sample_club_player)

        assert result.id == sample_club_player.id
        assert await club_player_repository.exists(sample_club_player.id)

    async def test_add_duplicate_updates_existing(
        self,
        club_player_repository: ClubPlayerRepository,
        club_id: UUID,
        player_id: UUID,
    ):
        """Test that adding same club+player updates existing record."""
        cp1 = ClubPlayer(
            id=uuid4(),
            club_id=club_id,
            player_id=player_id,
            date_entry=date(2024, 1, 1),
        )
        await club_player_repository.add(cp1)

        # Same club+player, different dates
        cp2 = ClubPlayer(
            id=cp1.id,
            club_id=club_id,
            player_id=player_id,
            date_entry=date(2024, 2, 1),
        )
        result = await club_player_repository.add(cp2)

        assert result.date_entry == date(2024, 2, 1)

    async def test_update_modifies_existing_relationship(
        self,
        club_player_repository: ClubPlayerRepository,
        sample_club_player: ClubPlayer,
    ):
        """Test updating an existing club-player relationship."""
        await club_player_repository.add(sample_club_player)
        sample_club_player.date_exit = date(2024, 12, 31)

        result = await club_player_repository.update(sample_club_player)

        assert result.date_exit == date(2024, 12, 31)

    async def test_delete_removes_relationship(
        self,
        club_player_repository: ClubPlayerRepository,
        sample_club_player: ClubPlayer,
    ):
        """Test deleting a club-player relationship."""
        await club_player_repository.add(sample_club_player)

        deleted = await club_player_repository.delete(sample_club_player.id)

        assert deleted is True
        assert not await club_player_repository.exists(sample_club_player.id)

    async def test_delete_returns_false_when_not_exists(
        self,
        club_player_repository: ClubPlayerRepository,
    ):
        """Test deleting a non-existent relationship returns False."""
        deleted = await club_player_repository.delete(uuid4())
        assert deleted is False

