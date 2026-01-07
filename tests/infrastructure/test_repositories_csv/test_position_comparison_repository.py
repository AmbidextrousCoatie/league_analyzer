"""
Tests for PandasPositionComparisonRepository (CSV implementation).

Following TDD: These tests are written BEFORE implementation.
They should fail initially, then pass after implementation.
"""

import pytest
from uuid import UUID, uuid4
from datetime import datetime
from domain.entities.position_comparison import PositionComparison, ComparisonOutcome
from domain.repositories.position_comparison_repository import PositionComparisonRepository
from domain.exceptions.domain_exception import EntityNotFoundError


class TestPandasPositionComparisonRepository:
    """Test cases for PandasPositionComparisonRepository CSV implementation."""
    
    @pytest.fixture
    def match_id(self):
        """Fixture for match ID."""
        return uuid4()
    
    @pytest.fixture
    def team1_player_id(self):
        """Fixture for team1 player ID."""
        return uuid4()
    
    @pytest.fixture
    def team2_player_id(self):
        """Fixture for team2 player ID."""
        return uuid4()
    
    @pytest.fixture
    def sample_comparison(self, match_id, team1_player_id, team2_player_id):
        """Fixture for sample position comparison."""
        return PositionComparison(
            id=uuid4(),
            match_id=match_id,
            position=0,
            team1_player_id=team1_player_id,
            team2_player_id=team2_player_id,
            team1_score=200,
            team2_score=180
        )
    
    @pytest.fixture
    def comparison_csv_path(self, tmp_path):
        """Create a temporary position_comparison.csv file for testing."""
        import pandas as pd
        csv_file = tmp_path / "position_comparison.csv"
        # Create empty CSV with headers
        df = pd.DataFrame(columns=[
            'id', 'match_id', 'position', 'team1_player_id', 'team2_player_id',
            'team1_score', 'team2_score', 'outcome', 'created_at', 'updated_at'
        ])
        df.to_csv(csv_file, index=False)
        return csv_file
    
    @pytest.fixture
    def mock_data_adapter(self, comparison_csv_path):
        """Mock DataAdapter for testing with real CSV file."""
        from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
        adapter = PandasDataAdapter(comparison_csv_path)
        return adapter
    
    @pytest.fixture
    def comparison_mapper(self):
        """Position comparison mapper for testing."""
        from infrastructure.persistence.mappers.csv.position_comparison_mapper import PandasPositionComparisonMapper
        return PandasPositionComparisonMapper()
    
    @pytest.fixture
    def comparison_repository(self, mock_data_adapter, comparison_mapper):
        """Fixture for position comparison repository."""
        from infrastructure.persistence.repositories.csv.position_comparison_repository import PandasPositionComparisonRepository
        return PandasPositionComparisonRepository(mock_data_adapter, comparison_mapper)
    
    async def test_get_by_id_returns_comparison_when_exists(
        self,
        comparison_repository: PositionComparisonRepository,
        sample_comparison: PositionComparison
    ):
        """Test getting position comparison by ID when it exists."""
        # Arrange
        await comparison_repository.add(sample_comparison)
        
        # Act
        result = await comparison_repository.get_by_id(sample_comparison.id)
        
        # Assert
        assert result is not None
        assert result.id == sample_comparison.id
        assert result.match_id == sample_comparison.match_id
        assert result.position == sample_comparison.position
    
    async def test_get_by_id_returns_none_when_not_exists(
        self,
        comparison_repository: PositionComparisonRepository
    ):
        """Test getting position comparison by ID when it doesn't exist."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        result = await comparison_repository.get_by_id(non_existent_id)
        
        # Assert
        assert result is None
    
    async def test_get_all_returns_all_comparisons(
        self,
        comparison_repository: PositionComparisonRepository,
        match_id: UUID,
        team1_player_id: UUID,
        team2_player_id: UUID
    ):
        """Test getting all position comparisons."""
        # Arrange
        comp1 = PositionComparison(
            id=uuid4(),
            match_id=match_id,
            position=0,
            team1_player_id=team1_player_id,
            team2_player_id=team2_player_id,
            team1_score=200,
            team2_score=180
        )
        comp2 = PositionComparison(
            id=uuid4(),
            match_id=match_id,
            position=1,
            team1_player_id=team1_player_id,
            team2_player_id=team2_player_id,
            team1_score=190,
            team2_score=195
        )
        await comparison_repository.add(comp1)
        await comparison_repository.add(comp2)
        
        # Act
        results = await comparison_repository.get_all()
        
        # Assert
        assert len(results) >= 2
        assert any(c.id == comp1.id for c in results)
        assert any(c.id == comp2.id for c in results)
    
    async def test_add_creates_new_comparison(
        self,
        comparison_repository: PositionComparisonRepository,
        sample_comparison: PositionComparison
    ):
        """Test adding a new position comparison."""
        # Act
        result = await comparison_repository.add(sample_comparison)
        
        # Assert
        assert result.id == sample_comparison.id
        assert await comparison_repository.exists(sample_comparison.id)
    
    async def test_update_modifies_existing_comparison(
        self,
        comparison_repository: PositionComparisonRepository,
        sample_comparison: PositionComparison
    ):
        """Test updating an existing position comparison."""
        # Arrange
        await comparison_repository.add(sample_comparison)
        sample_comparison.update_scores(220, 200)
        
        # Act
        result = await comparison_repository.update(sample_comparison)
        
        # Assert
        assert result.team1_score == 220
        assert result.team2_score == 200
        assert result.outcome == ComparisonOutcome.TEAM1_WIN
        
        # Verify persisted
        retrieved = await comparison_repository.get_by_id(sample_comparison.id)
        assert retrieved.team1_score == 220
        assert retrieved.outcome == ComparisonOutcome.TEAM1_WIN
    
    async def test_update_raises_error_when_not_exists(
        self,
        comparison_repository: PositionComparisonRepository,
        sample_comparison: PositionComparison
    ):
        """Test updating non-existent position comparison raises error."""
        # Act & Assert
        with pytest.raises(EntityNotFoundError):
            await comparison_repository.update(sample_comparison)
    
    async def test_delete_removes_comparison(
        self,
        comparison_repository: PositionComparisonRepository,
        sample_comparison: PositionComparison
    ):
        """Test deleting a position comparison."""
        # Arrange
        await comparison_repository.add(sample_comparison)
        assert await comparison_repository.exists(sample_comparison.id)
        
        # Act
        await comparison_repository.delete(sample_comparison.id)
        
        # Assert
        assert not await comparison_repository.exists(sample_comparison.id)
        assert await comparison_repository.get_by_id(sample_comparison.id) is None
    
    async def test_delete_raises_error_when_not_exists(
        self,
        comparison_repository: PositionComparisonRepository
    ):
        """Test deleting non-existent position comparison raises error."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError):
            await comparison_repository.delete(non_existent_id)
    
    async def test_exists_returns_true_when_comparison_exists(
        self,
        comparison_repository: PositionComparisonRepository,
        sample_comparison: PositionComparison
    ):
        """Test exists returns True when position comparison exists."""
        # Arrange
        await comparison_repository.add(sample_comparison)
        
        # Act
        result = await comparison_repository.exists(sample_comparison.id)
        
        # Assert
        assert result is True
    
    async def test_exists_returns_false_when_comparison_not_exists(
        self,
        comparison_repository: PositionComparisonRepository
    ):
        """Test exists returns False when position comparison doesn't exist."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        result = await comparison_repository.exists(non_existent_id)
        
        # Assert
        assert result is False
    
    async def test_get_by_match_returns_filtered_comparisons(
        self,
        comparison_repository: PositionComparisonRepository,
        match_id: UUID,
        team1_player_id: UUID,
        team2_player_id: UUID
    ):
        """Test getting position comparisons by match."""
        # Arrange
        other_match_id = uuid4()
        comp1 = PositionComparison(
            id=uuid4(),
            match_id=match_id,
            position=0,
            team1_player_id=team1_player_id,
            team2_player_id=team2_player_id,
            team1_score=200,
            team2_score=180
        )
        comp2 = PositionComparison(
            id=uuid4(),
            match_id=other_match_id,
            position=0,
            team1_player_id=team1_player_id,
            team2_player_id=team2_player_id,
            team1_score=190,
            team2_score=195
        )
        await comparison_repository.add(comp1)
        await comparison_repository.add(comp2)
        
        # Act
        results = await comparison_repository.get_by_match(match_id)
        
        # Assert
        assert len(results) >= 1
        assert all(c.match_id == match_id for c in results)
        assert any(c.id == comp1.id for c in results)
        assert not any(c.id == comp2.id for c in results)
    
    async def test_get_by_match_and_position_returns_comparison_when_exists(
        self,
        comparison_repository: PositionComparisonRepository,
        match_id: UUID,
        team1_player_id: UUID,
        team2_player_id: UUID
    ):
        """Test getting position comparison by match and position."""
        # Arrange
        comp = PositionComparison(
            id=uuid4(),
            match_id=match_id,
            position=2,
            team1_player_id=team1_player_id,
            team2_player_id=team2_player_id,
            team1_score=200,
            team2_score=180
        )
        await comparison_repository.add(comp)
        
        # Act
        result = await comparison_repository.get_by_match_and_position(match_id, position=2)
        
        # Assert
        assert result is not None
        assert result.id == comp.id
        assert result.position == 2
    
    async def test_get_by_match_and_position_returns_none_when_not_exists(
        self,
        comparison_repository: PositionComparisonRepository,
        match_id: UUID
    ):
        """Test getting position comparison returns None when not exists."""
        # Act
        result = await comparison_repository.get_by_match_and_position(match_id, position=2)
        
        # Assert
        assert result is None
    
    async def test_get_by_player_returns_filtered_comparisons(
        self,
        comparison_repository: PositionComparisonRepository,
        match_id: UUID,
        team1_player_id: UUID,
        team2_player_id: UUID
    ):
        """Test getting position comparisons by player."""
        # Arrange
        other_player_id = uuid4()
        comp1 = PositionComparison(
            id=uuid4(),
            match_id=match_id,
            position=0,
            team1_player_id=team1_player_id,
            team2_player_id=team2_player_id,
            team1_score=200,
            team2_score=180
        )
        comp2 = PositionComparison(
            id=uuid4(),
            match_id=match_id,
            position=1,
            team1_player_id=other_player_id,
            team2_player_id=team2_player_id,
            team1_score=190,
            team2_score=195
        )
        await comparison_repository.add(comp1)
        await comparison_repository.add(comp2)
        
        # Act
        results = await comparison_repository.get_by_player(team1_player_id)
        
        # Assert
        assert len(results) >= 1
        assert any(c.id == comp1.id for c in results)
        assert not any(c.id == comp2.id for c in results)
        # Player should appear as team1 or team2
        assert all(
            c.team1_player_id == team1_player_id or c.team2_player_id == team1_player_id
            for c in results
        )

