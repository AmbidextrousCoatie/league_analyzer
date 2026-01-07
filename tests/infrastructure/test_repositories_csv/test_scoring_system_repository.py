"""
Tests for PandasScoringSystemRepository (CSV implementation).

Following TDD: These tests are written BEFORE implementation.
They should fail initially, then pass after implementation.
"""

import pytest
import pandas as pd
from uuid import UUID, uuid4
from domain.entities.scoring_system import ScoringSystem
from domain.repositories.scoring_system_repository import ScoringSystemRepository


class TestPandasScoringSystemRepository:
    """Test cases for PandasScoringSystemRepository CSV implementation."""

    @pytest.fixture
    def sample_scoring_system(self) -> ScoringSystem:
        """Fixture for a sample scoring system."""
        return ScoringSystem(
            id=uuid4(),
            name="Standard 2-Point System",
            points_per_individual_match_win=1.0,
            points_per_individual_match_tie=0.5,
            points_per_individual_match_loss=0.0,
            points_per_team_match_win=2.0,
            points_per_team_match_tie=1.0,
            points_per_team_match_loss=0.0,
            allow_ties=True,
        )

    @pytest.fixture
    def scoring_system_csv_path(self, tmp_path):
        """Create a temporary scoring_system.csv file for testing."""
        csv_file = tmp_path / "scoring_system.csv"
        df = pd.DataFrame(
            columns=[
                "id",
                "name",
                "points_per_individual_match_win",
                "points_per_individual_match_tie",
                "points_per_individual_match_loss",
                "points_per_team_match_win",
                "points_per_team_match_tie",
                "points_per_team_match_loss",
                "allow_ties",
            ]
        )
        df.to_csv(csv_file, index=False)
        return csv_file

    @pytest.fixture
    def mock_data_adapter(self, scoring_system_csv_path):
        """Mock PandasDataAdapter for testing with real CSV file."""
        from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter

        return PandasDataAdapter(scoring_system_csv_path)

    @pytest.fixture
    def scoring_system_mapper(self):
        """ScoringSystem mapper for testing."""
        from infrastructure.persistence.mappers.csv.scoring_system_mapper import (
            PandasScoringSystemMapper,
        )

        return PandasScoringSystemMapper()

    @pytest.fixture
    def scoring_system_repository(
        self, mock_data_adapter, scoring_system_mapper
    ) -> ScoringSystemRepository:
        """Fixture for scoring system repository."""
        from infrastructure.persistence.repositories.csv.scoring_system_repository import (
            PandasScoringSystemRepository,
        )

        return PandasScoringSystemRepository(mock_data_adapter, scoring_system_mapper)

    async def test_get_by_id_returns_scoring_system_when_exists(
        self,
        scoring_system_repository: ScoringSystemRepository,
        sample_scoring_system: ScoringSystem,
    ):
        """Test getting scoring system by ID when it exists."""
        await scoring_system_repository.add(sample_scoring_system)

        result = await scoring_system_repository.get_by_id(sample_scoring_system.id)

        assert result is not None
        assert result.id == sample_scoring_system.id
        assert result.name == sample_scoring_system.name

    async def test_get_by_id_returns_none_when_not_exists(
        self,
        scoring_system_repository: ScoringSystemRepository,
    ):
        """Test getting scoring system by ID when it doesn't exist."""
        result = await scoring_system_repository.get_by_id(uuid4())
        assert result is None

    async def test_get_all_returns_all_scoring_systems(
        self,
        scoring_system_repository: ScoringSystemRepository,
    ):
        """Test getting all scoring systems."""
        s1 = ScoringSystem(name="System A")
        s2 = ScoringSystem(name="System B")
        await scoring_system_repository.add(s1)
        await scoring_system_repository.add(s2)

        results = await scoring_system_repository.get_all()

        assert len(results) >= 2
        assert any(s.name == "System A" for s in results)
        assert any(s.name == "System B" for s in results)

    async def test_find_by_name_returns_matching_system(
        self,
        scoring_system_repository: ScoringSystemRepository,
        sample_scoring_system: ScoringSystem,
    ):
        """Test finding scoring system by name (case-insensitive)."""
        await scoring_system_repository.add(sample_scoring_system)

        result = await scoring_system_repository.find_by_name(
            "standard 2-point system"
        )

        assert result is not None
        assert result.id == sample_scoring_system.id

    async def test_add_creates_new_scoring_system(
        self,
        scoring_system_repository: ScoringSystemRepository,
        sample_scoring_system: ScoringSystem,
    ):
        """Test adding a new scoring system."""
        result = await scoring_system_repository.add(sample_scoring_system)

        assert result.id == sample_scoring_system.id
        assert await scoring_system_repository.exists(sample_scoring_system.id)

    async def test_update_modifies_existing_scoring_system(
        self,
        scoring_system_repository: ScoringSystemRepository,
        sample_scoring_system: ScoringSystem,
    ):
        """Test updating an existing scoring system."""
        await scoring_system_repository.add(sample_scoring_system)
        sample_scoring_system.update_team_points(win=3.0, tie=1.5, loss=0.0)

        result = await scoring_system_repository.update(sample_scoring_system)

        assert result.points_per_team_match_win == 3.0
        assert result.points_per_team_match_tie == 1.5

    async def test_delete_removes_scoring_system(
        self,
        scoring_system_repository: ScoringSystemRepository,
        sample_scoring_system: ScoringSystem,
    ):
        """Test deleting a scoring system."""
        await scoring_system_repository.add(sample_scoring_system)

        deleted = await scoring_system_repository.delete(sample_scoring_system.id)

        assert deleted is True
        assert not await scoring_system_repository.exists(sample_scoring_system.id)

    async def test_delete_returns_false_when_not_exists(
        self,
        scoring_system_repository: ScoringSystemRepository,
    ):
        """Test deleting a non-existent scoring system returns False."""
        deleted = await scoring_system_repository.delete(uuid4())
        assert deleted is False

