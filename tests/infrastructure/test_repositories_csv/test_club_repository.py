"""
Tests for PandasClubRepository (CSV implementation).

Following TDD: These tests are written BEFORE implementation.
They should fail initially, then pass after implementation.
"""

import pytest
import pandas as pd
from uuid import UUID, uuid4
from domain.entities.club import Club
from domain.repositories.club_repository import ClubRepository
from domain.exceptions.domain_exception import EntityNotFoundError


class TestPandasClubRepository:
    """Test cases for PandasClubRepository CSV implementation."""

    @pytest.fixture
    def sample_club(self) -> Club:
        """Fixture for a sample club."""
        return Club(
            id=uuid4(),
            name="Bowling Club Alpha",
            short_name="BCA",
            address="123 Bowling Lane"
        )

    @pytest.fixture
    def club_csv_path(self, tmp_path):
        """Create a temporary club.csv file for testing."""
        csv_file = tmp_path / "club.csv"
        df = pd.DataFrame(columns=[
            "id",
            "name",
            "short_name",
            "home_alley_id",
            "address",
        ])
        df.to_csv(csv_file, index=False)
        return csv_file

    @pytest.fixture
    def mock_data_adapter(self, club_csv_path):
        """Mock DataAdapter for testing with real CSV file."""
        from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter

        return PandasDataAdapter(club_csv_path)

    @pytest.fixture
    def club_mapper(self):
        """Club mapper for testing."""
        from infrastructure.persistence.mappers.csv.club_mapper import PandasClubMapper

        return PandasClubMapper()

    @pytest.fixture
    def club_repository(self, mock_data_adapter, club_mapper) -> ClubRepository:
        """Fixture for club repository."""
        from infrastructure.persistence.repositories.csv.club_repository import (
            PandasClubRepository,
        )

        return PandasClubRepository(mock_data_adapter, club_mapper)

    async def test_get_by_id_returns_club_when_exists(
        self,
        club_repository: ClubRepository,
        sample_club: Club,
    ):
        """Test getting club by ID when it exists."""
        await club_repository.add(sample_club)

        result = await club_repository.get_by_id(sample_club.id)

        assert result is not None
        assert result.id == sample_club.id
        assert result.name == sample_club.name

    async def test_get_by_id_returns_none_when_not_exists(
        self,
        club_repository: ClubRepository,
    ):
        """Test getting club by ID when it doesn't exist."""
        result = await club_repository.get_by_id(uuid4())
        assert result is None

    async def test_get_all_returns_all_clubs(
        self,
        club_repository: ClubRepository,
    ):
        """Test getting all clubs."""
        c1 = Club(name="Club One")
        c2 = Club(name="Club Two")
        await club_repository.add(c1)
        await club_repository.add(c2)

        results = await club_repository.get_all()

        assert len(results) >= 2
        assert any(c.name == "Club One" for c in results)
        assert any(c.name == "Club Two" for c in results)

    async def test_find_by_name_returns_partial_matches(
        self,
        club_repository: ClubRepository,
    ):
        """Test finding clubs by partial name."""
        c1 = Club(name="Bowling Club Alpha")
        c2 = Club(name="Bowling Club Beta")
        await club_repository.add(c1)
        await club_repository.add(c2)

        results = await club_repository.find_by_name("Alpha")

        assert len(results) >= 1
        assert any("Alpha" in c.name for c in results)

    async def test_add_creates_new_club(
        self,
        club_repository: ClubRepository,
        sample_club: Club,
    ):
        """Test adding a new club."""
        result = await club_repository.add(sample_club)

        assert result.id == sample_club.id
        # Verify persisted
        stored = await club_repository.get_by_id(sample_club.id)
        assert stored is not None
        assert stored.name == sample_club.name

    async def test_update_modifies_existing_club(
        self,
        club_repository: ClubRepository,
        sample_club: Club,
    ):
        """Test updating an existing club."""
        await club_repository.add(sample_club)
        sample_club.update_name("Updated Club Name")

        result = await club_repository.update(sample_club)

        assert result.name == "Updated Club Name"
        stored = await club_repository.get_by_id(sample_club.id)
        assert stored.name == "Updated Club Name"

    async def test_update_raises_error_when_not_exists(
        self,
        club_repository: ClubRepository,
        sample_club: Club,
    ):
        """Test updating non-existent club raises error."""
        with pytest.raises(EntityNotFoundError):
            await club_repository.update(sample_club)

    async def test_delete_removes_club(
        self,
        club_repository: ClubRepository,
        sample_club: Club,
    ):
        """Test deleting a club."""
        await club_repository.add(sample_club)

        deleted = await club_repository.delete(sample_club.id)

        assert deleted is True
        assert await club_repository.get_by_id(sample_club.id) is None

    async def test_delete_returns_false_when_not_exists(
        self,
        club_repository: ClubRepository,
    ):
        """Test deleting a non-existent club returns False."""
        deleted = await club_repository.delete(uuid4())
        assert deleted is False

