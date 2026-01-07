"""
Tests for PandasMatchScoringRepository (CSV implementation).

Following TDD: These tests are written BEFORE implementation.
They should fail initially, then pass after implementation.
"""

import pytest
from uuid import UUID, uuid4
from datetime import datetime
from domain.entities.match_scoring import MatchScoring
from domain.repositories.match_scoring_repository import MatchScoringRepository
from domain.exceptions.domain_exception import EntityNotFoundError


class TestPandasMatchScoringRepository:
    """Test cases for PandasMatchScoringRepository CSV implementation."""
    
    @pytest.fixture
    def match_id(self):
        """Fixture for match ID."""
        return uuid4()
    
    @pytest.fixture
    def scoring_system_id(self):
        """Fixture for scoring system ID."""
        return "liga-bayern-3pt"
    
    @pytest.fixture
    def sample_scoring(self, match_id, scoring_system_id):
        """Fixture for sample match scoring."""
        return MatchScoring(
            id=uuid4(),
            match_id=match_id,
            scoring_system_id=scoring_system_id,
            team1_individual_points=3.0,
            team2_individual_points=1.0,
            team1_match_points=3.0,
            team2_match_points=0.0
        )
    
    @pytest.fixture
    def scoring_csv_path(self, tmp_path):
        """Create a temporary match_scoring.csv file for testing."""
        import pandas as pd
        csv_file = tmp_path / "match_scoring.csv"
        # Create empty CSV with headers
        df = pd.DataFrame(columns=[
            'id', 'match_id', 'scoring_system_id',
            'team1_individual_points', 'team2_individual_points',
            'team1_match_points', 'team2_match_points',
            'computed_at', 'created_at', 'updated_at'
        ])
        df.to_csv(csv_file, index=False)
        return csv_file
    
    @pytest.fixture
    def mock_data_adapter(self, scoring_csv_path):
        """Mock DataAdapter for testing with real CSV file."""
        from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
        adapter = PandasDataAdapter(scoring_csv_path)
        return adapter
    
    @pytest.fixture
    def scoring_mapper(self):
        """Match scoring mapper for testing."""
        from infrastructure.persistence.mappers.csv.match_scoring_mapper import PandasMatchScoringMapper
        return PandasMatchScoringMapper()
    
    @pytest.fixture
    def scoring_repository(self, mock_data_adapter, scoring_mapper):
        """Fixture for match scoring repository."""
        from infrastructure.persistence.repositories.csv.match_scoring_repository import PandasMatchScoringRepository
        return PandasMatchScoringRepository(mock_data_adapter, scoring_mapper)
    
    async def test_get_by_id_returns_scoring_when_exists(
        self,
        scoring_repository: MatchScoringRepository,
        sample_scoring: MatchScoring
    ):
        """Test getting match scoring by ID when it exists."""
        # Arrange
        await scoring_repository.add(sample_scoring)
        
        # Act
        result = await scoring_repository.get_by_id(sample_scoring.id)
        
        # Assert
        assert result is not None
        assert result.id == sample_scoring.id
        assert result.match_id == sample_scoring.match_id
        assert result.scoring_system_id == sample_scoring.scoring_system_id
    
    async def test_get_by_id_returns_none_when_not_exists(
        self,
        scoring_repository: MatchScoringRepository
    ):
        """Test getting match scoring by ID when it doesn't exist."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        result = await scoring_repository.get_by_id(non_existent_id)
        
        # Assert
        assert result is None
    
    async def test_get_all_returns_all_scorings(
        self,
        scoring_repository: MatchScoringRepository,
        match_id: UUID,
        scoring_system_id: str
    ):
        """Test getting all match scorings."""
        # Arrange
        scoring1 = MatchScoring(
            id=uuid4(),
            match_id=match_id,
            scoring_system_id=scoring_system_id,
            team1_individual_points=3.0,
            team2_individual_points=1.0,
            team1_match_points=3.0,
            team2_match_points=0.0
        )
        scoring2 = MatchScoring(
            id=uuid4(),
            match_id=match_id,
            scoring_system_id="liga-bayern-2pt",
            team1_individual_points=3.0,
            team2_individual_points=1.0,
            team1_match_points=2.0,
            team2_match_points=0.0
        )
        await scoring_repository.add(scoring1)
        await scoring_repository.add(scoring2)
        
        # Act
        results = await scoring_repository.get_all()
        
        # Assert
        assert len(results) >= 2
        assert any(s.id == scoring1.id for s in results)
        assert any(s.id == scoring2.id for s in results)
    
    async def test_add_creates_new_scoring(
        self,
        scoring_repository: MatchScoringRepository,
        sample_scoring: MatchScoring
    ):
        """Test adding a new match scoring."""
        # Act
        result = await scoring_repository.add(sample_scoring)
        
        # Assert
        assert result.id == sample_scoring.id
        assert await scoring_repository.exists(sample_scoring.id)
    
    async def test_update_modifies_existing_scoring(
        self,
        scoring_repository: MatchScoringRepository,
        sample_scoring: MatchScoring
    ):
        """Test updating an existing match scoring."""
        # Arrange
        await scoring_repository.add(sample_scoring)
        sample_scoring.update_individual_points(4.0, 0.0)
        sample_scoring.update_match_points(3.0, 0.0)
        
        # Act
        result = await scoring_repository.update(sample_scoring)
        
        # Assert
        assert result.team1_individual_points == 4.0
        assert result.team2_individual_points == 0.0
        assert result.team1_match_points == 3.0
        
        # Verify persisted
        retrieved = await scoring_repository.get_by_id(sample_scoring.id)
        assert retrieved.team1_individual_points == 4.0
        assert retrieved.team1_match_points == 3.0
    
    async def test_update_raises_error_when_not_exists(
        self,
        scoring_repository: MatchScoringRepository,
        sample_scoring: MatchScoring
    ):
        """Test updating non-existent match scoring raises error."""
        # Act & Assert
        with pytest.raises(EntityNotFoundError):
            await scoring_repository.update(sample_scoring)
    
    async def test_delete_removes_scoring(
        self,
        scoring_repository: MatchScoringRepository,
        sample_scoring: MatchScoring
    ):
        """Test deleting a match scoring."""
        # Arrange
        await scoring_repository.add(sample_scoring)
        assert await scoring_repository.exists(sample_scoring.id)
        
        # Act
        await scoring_repository.delete(sample_scoring.id)
        
        # Assert
        assert not await scoring_repository.exists(sample_scoring.id)
        assert await scoring_repository.get_by_id(sample_scoring.id) is None
    
    async def test_delete_raises_error_when_not_exists(
        self,
        scoring_repository: MatchScoringRepository
    ):
        """Test deleting non-existent match scoring raises error."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError):
            await scoring_repository.delete(non_existent_id)
    
    async def test_exists_returns_true_when_scoring_exists(
        self,
        scoring_repository: MatchScoringRepository,
        sample_scoring: MatchScoring
    ):
        """Test exists returns True when match scoring exists."""
        # Arrange
        await scoring_repository.add(sample_scoring)
        
        # Act
        result = await scoring_repository.exists(sample_scoring.id)
        
        # Assert
        assert result is True
    
    async def test_exists_returns_false_when_scoring_not_exists(
        self,
        scoring_repository: MatchScoringRepository
    ):
        """Test exists returns False when match scoring doesn't exist."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        result = await scoring_repository.exists(non_existent_id)
        
        # Assert
        assert result is False
    
    async def test_get_by_match_returns_filtered_scorings(
        self,
        scoring_repository: MatchScoringRepository,
        match_id: UUID,
        scoring_system_id: str
    ):
        """Test getting match scorings by match."""
        # Arrange
        other_match_id = uuid4()
        scoring1 = MatchScoring(
            id=uuid4(),
            match_id=match_id,
            scoring_system_id=scoring_system_id,
            team1_individual_points=3.0,
            team2_individual_points=1.0,
            team1_match_points=3.0,
            team2_match_points=0.0
        )
        scoring2 = MatchScoring(
            id=uuid4(),
            match_id=other_match_id,
            scoring_system_id=scoring_system_id,
            team1_individual_points=2.0,
            team2_individual_points=2.0,
            team1_match_points=1.0,
            team2_match_points=1.0
        )
        await scoring_repository.add(scoring1)
        await scoring_repository.add(scoring2)
        
        # Act
        results = await scoring_repository.get_by_match(match_id)
        
        # Assert
        assert len(results) >= 1
        assert all(s.match_id == match_id for s in results)
        assert any(s.id == scoring1.id for s in results)
        assert not any(s.id == scoring2.id for s in results)
    
    async def test_get_by_match_and_system_returns_scoring_when_exists(
        self,
        scoring_repository: MatchScoringRepository,
        match_id: UUID,
        scoring_system_id: str
    ):
        """Test getting match scoring by match and scoring system."""
        # Arrange
        scoring = MatchScoring(
            id=uuid4(),
            match_id=match_id,
            scoring_system_id=scoring_system_id,
            team1_individual_points=3.0,
            team2_individual_points=1.0,
            team1_match_points=3.0,
            team2_match_points=0.0
        )
        await scoring_repository.add(scoring)
        
        # Act
        result = await scoring_repository.get_by_match_and_system(match_id, scoring_system_id)
        
        # Assert
        assert result is not None
        assert result.id == scoring.id
        assert result.scoring_system_id == scoring_system_id
    
    async def test_get_by_match_and_system_returns_none_when_not_exists(
        self,
        scoring_repository: MatchScoringRepository,
        match_id: UUID,
        scoring_system_id: str
    ):
        """Test getting match scoring returns None when not exists."""
        # Act
        result = await scoring_repository.get_by_match_and_system(match_id, scoring_system_id)
        
        # Assert
        assert result is None
    
    async def test_get_by_scoring_system_returns_filtered_scorings(
        self,
        scoring_repository: MatchScoringRepository,
        match_id: UUID,
        scoring_system_id: str
    ):
        """Test getting match scorings by scoring system."""
        # Arrange
        other_system_id = "liga-bayern-2pt"
        scoring1 = MatchScoring(
            id=uuid4(),
            match_id=match_id,
            scoring_system_id=scoring_system_id,
            team1_individual_points=3.0,
            team2_individual_points=1.0,
            team1_match_points=3.0,
            team2_match_points=0.0
        )
        scoring2 = MatchScoring(
            id=uuid4(),
            match_id=match_id,
            scoring_system_id=other_system_id,
            team1_individual_points=3.0,
            team2_individual_points=1.0,
            team1_match_points=2.0,
            team2_match_points=0.0
        )
        await scoring_repository.add(scoring1)
        await scoring_repository.add(scoring2)
        
        # Act
        results = await scoring_repository.get_by_scoring_system(scoring_system_id)
        
        # Assert
        assert len(results) >= 1
        assert all(s.scoring_system_id == scoring_system_id for s in results)
        assert any(s.id == scoring1.id for s in results)
        assert not any(s.id == scoring2.id for s in results)

