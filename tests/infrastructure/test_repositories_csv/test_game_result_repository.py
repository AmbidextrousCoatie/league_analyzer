"""
Tests for PandasGameResultRepository (CSV implementation).

Following TDD: These tests are written BEFORE implementation.
They should fail initially, then pass after implementation.
"""

import pytest
from uuid import UUID, uuid4
from datetime import datetime
from domain.entities.game_result import GameResult
from domain.repositories.game_result_repository import GameResultRepository
from domain.exceptions.domain_exception import EntityNotFoundError


class TestPandasGameResultRepository:
    """Test cases for PandasGameResultRepository CSV implementation."""
    
    @pytest.fixture
    def match_id(self):
        """Fixture for match ID."""
        return uuid4()
    
    @pytest.fixture
    def player_id(self):
        """Fixture for player ID."""
        return uuid4()
    
    @pytest.fixture
    def team_season_id(self):
        """Fixture for team season ID."""
        return uuid4()
    
    @pytest.fixture
    def sample_game_result(self, match_id, player_id, team_season_id):
        """Fixture for sample game result."""
        return GameResult(
            id=uuid4(),
            match_id=match_id,
            player_id=player_id,
            team_season_id=team_season_id,
            position=0,
            score=200
        )
    
    @pytest.fixture
    def game_result_csv_path(self, tmp_path):
        """Create a temporary game_result.csv file for testing."""
        import pandas as pd
        csv_file = tmp_path / "game_result.csv"
        # Create empty CSV with headers
        df = pd.DataFrame(columns=[
            'id', 'match_id', 'player_id', 'team_season_id', 'position',
            'score', 'handicap', 'is_disqualified', 'created_at', 'updated_at'
        ])
        df.to_csv(csv_file, index=False)
        return csv_file
    
    @pytest.fixture
    def mock_data_adapter(self, game_result_csv_path):
        """Mock DataAdapter for testing with real CSV file."""
        from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
        adapter = PandasDataAdapter(game_result_csv_path)
        return adapter
    
    @pytest.fixture
    def game_result_mapper(self):
        """Game result mapper for testing."""
        from infrastructure.persistence.mappers.csv.game_result_mapper import PandasGameResultMapper
        return PandasGameResultMapper()
    
    @pytest.fixture
    def game_result_repository(self, mock_data_adapter, game_result_mapper):
        """Fixture for game result repository."""
        from infrastructure.persistence.repositories.csv.game_result_repository import PandasGameResultRepository
        return PandasGameResultRepository(mock_data_adapter, game_result_mapper)
    
    async def test_get_by_id_returns_game_result_when_exists(
        self,
        game_result_repository: GameResultRepository,
        sample_game_result: GameResult
    ):
        """Test getting game result by ID when it exists."""
        # Arrange
        await game_result_repository.add(sample_game_result)
        
        # Act
        result = await game_result_repository.get_by_id(sample_game_result.id)
        
        # Assert
        assert result is not None
        assert result.id == sample_game_result.id
        assert result.match_id == sample_game_result.match_id
        assert result.player_id == sample_game_result.player_id
    
    async def test_get_by_id_returns_none_when_not_exists(
        self,
        game_result_repository: GameResultRepository
    ):
        """Test getting game result by ID when it doesn't exist."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        result = await game_result_repository.get_by_id(non_existent_id)
        
        # Assert
        assert result is None
    
    async def test_get_all_returns_all_game_results(
        self,
        game_result_repository: GameResultRepository,
        match_id: UUID,
        player_id: UUID,
        team_season_id: UUID
    ):
        """Test getting all game results."""
        # Arrange
        gr1 = GameResult(
            id=uuid4(),
            match_id=match_id,
            player_id=player_id,
            team_season_id=team_season_id,
            position=0,
            score=200
        )
        gr2 = GameResult(
            id=uuid4(),
            match_id=match_id,
            player_id=player_id,
            team_season_id=team_season_id,
            position=1,
            score=180
        )
        await game_result_repository.add(gr1)
        await game_result_repository.add(gr2)
        
        # Act
        results = await game_result_repository.get_all()
        
        # Assert
        assert len(results) >= 2
        assert any(gr.id == gr1.id for gr in results)
        assert any(gr.id == gr2.id for gr in results)
    
    async def test_add_creates_new_game_result(
        self,
        game_result_repository: GameResultRepository,
        sample_game_result: GameResult
    ):
        """Test adding a new game result."""
        # Act
        result = await game_result_repository.add(sample_game_result)
        
        # Assert
        assert result.id == sample_game_result.id
        assert await game_result_repository.exists(sample_game_result.id)
    
    async def test_update_modifies_existing_game_result(
        self,
        game_result_repository: GameResultRepository,
        sample_game_result: GameResult
    ):
        """Test updating an existing game result."""
        # Arrange
        await game_result_repository.add(sample_game_result)
        sample_game_result.update_score(220)
        sample_game_result.set_handicap(10.0)
        
        # Act
        result = await game_result_repository.update(sample_game_result)
        
        # Assert
        assert result.score == 220
        assert result.handicap == 10.0
        
        # Verify persisted
        retrieved = await game_result_repository.get_by_id(sample_game_result.id)
        assert retrieved.score == 220
        assert retrieved.handicap == 10.0
    
    async def test_update_raises_error_when_not_exists(
        self,
        game_result_repository: GameResultRepository,
        sample_game_result: GameResult
    ):
        """Test updating non-existent game result raises error."""
        # Act & Assert
        with pytest.raises(EntityNotFoundError):
            await game_result_repository.update(sample_game_result)
    
    async def test_delete_removes_game_result(
        self,
        game_result_repository: GameResultRepository,
        sample_game_result: GameResult
    ):
        """Test deleting a game result."""
        # Arrange
        await game_result_repository.add(sample_game_result)
        assert await game_result_repository.exists(sample_game_result.id)
        
        # Act
        await game_result_repository.delete(sample_game_result.id)
        
        # Assert
        assert not await game_result_repository.exists(sample_game_result.id)
        assert await game_result_repository.get_by_id(sample_game_result.id) is None
    
    async def test_delete_raises_error_when_not_exists(
        self,
        game_result_repository: GameResultRepository
    ):
        """Test deleting non-existent game result raises error."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError):
            await game_result_repository.delete(non_existent_id)
    
    async def test_exists_returns_true_when_game_result_exists(
        self,
        game_result_repository: GameResultRepository,
        sample_game_result: GameResult
    ):
        """Test exists returns True when game result exists."""
        # Arrange
        await game_result_repository.add(sample_game_result)
        
        # Act
        result = await game_result_repository.exists(sample_game_result.id)
        
        # Assert
        assert result is True
    
    async def test_exists_returns_false_when_game_result_not_exists(
        self,
        game_result_repository: GameResultRepository
    ):
        """Test exists returns False when game result doesn't exist."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        result = await game_result_repository.exists(non_existent_id)
        
        # Assert
        assert result is False
    
    async def test_get_by_match_returns_filtered_game_results(
        self,
        game_result_repository: GameResultRepository,
        match_id: UUID,
        player_id: UUID,
        team_season_id: UUID
    ):
        """Test getting game results by match."""
        # Arrange
        other_match_id = uuid4()
        gr1 = GameResult(
            id=uuid4(),
            match_id=match_id,
            player_id=player_id,
            team_season_id=team_season_id,
            position=0,
            score=200
        )
        gr2 = GameResult(
            id=uuid4(),
            match_id=other_match_id,
            player_id=player_id,
            team_season_id=team_season_id,
            position=0,
            score=180
        )
        await game_result_repository.add(gr1)
        await game_result_repository.add(gr2)
        
        # Act
        results = await game_result_repository.get_by_match(match_id)
        
        # Assert
        assert len(results) >= 1
        assert all(gr.match_id == match_id for gr in results)
        assert any(gr.id == gr1.id for gr in results)
        assert not any(gr.id == gr2.id for gr in results)
    
    async def test_get_by_match_and_team_returns_filtered_game_results(
        self,
        game_result_repository: GameResultRepository,
        match_id: UUID,
        player_id: UUID,
        team_season_id: UUID
    ):
        """Test getting game results by match and team."""
        # Arrange
        other_team_id = uuid4()
        gr1 = GameResult(
            id=uuid4(),
            match_id=match_id,
            player_id=player_id,
            team_season_id=team_season_id,
            position=0,
            score=200
        )
        gr2 = GameResult(
            id=uuid4(),
            match_id=match_id,
            player_id=player_id,
            team_season_id=other_team_id,
            position=0,
            score=180
        )
        await game_result_repository.add(gr1)
        await game_result_repository.add(gr2)
        
        # Act
        results = await game_result_repository.get_by_match_and_team(match_id, team_season_id)
        
        # Assert
        assert len(results) >= 1
        assert all(gr.match_id == match_id and gr.team_season_id == team_season_id for gr in results)
        assert any(gr.id == gr1.id for gr in results)
        assert not any(gr.id == gr2.id for gr in results)
    
    async def test_get_by_player_returns_filtered_game_results(
        self,
        game_result_repository: GameResultRepository,
        match_id: UUID,
        player_id: UUID,
        team_season_id: UUID
    ):
        """Test getting game results by player."""
        # Arrange
        other_player_id = uuid4()
        gr1 = GameResult(
            id=uuid4(),
            match_id=match_id,
            player_id=player_id,
            team_season_id=team_season_id,
            position=0,
            score=200
        )
        gr2 = GameResult(
            id=uuid4(),
            match_id=match_id,
            player_id=other_player_id,
            team_season_id=team_season_id,
            position=0,
            score=180
        )
        await game_result_repository.add(gr1)
        await game_result_repository.add(gr2)
        
        # Act
        results = await game_result_repository.get_by_player(player_id)
        
        # Assert
        assert len(results) >= 1
        assert all(gr.player_id == player_id for gr in results)
        assert any(gr.id == gr1.id for gr in results)
        assert not any(gr.id == gr2.id for gr in results)
    
    async def test_get_by_team_returns_filtered_game_results(
        self,
        game_result_repository: GameResultRepository,
        match_id: UUID,
        player_id: UUID,
        team_season_id: UUID
    ):
        """Test getting game results by team."""
        # Arrange
        other_team_id = uuid4()
        gr1 = GameResult(
            id=uuid4(),
            match_id=match_id,
            player_id=player_id,
            team_season_id=team_season_id,
            position=0,
            score=200
        )
        gr2 = GameResult(
            id=uuid4(),
            match_id=match_id,
            player_id=player_id,
            team_season_id=other_team_id,
            position=0,
            score=180
        )
        await game_result_repository.add(gr1)
        await game_result_repository.add(gr2)
        
        # Act
        results = await game_result_repository.get_by_team(team_season_id)
        
        # Assert
        assert len(results) >= 1
        assert all(gr.team_season_id == team_season_id for gr in results)
        assert any(gr.id == gr1.id for gr in results)
        assert not any(gr.id == gr2.id for gr in results)
    
    async def test_find_by_match_and_position_returns_game_result_when_exists(
        self,
        game_result_repository: GameResultRepository,
        match_id: UUID,
        player_id: UUID,
        team_season_id: UUID
    ):
        """Test finding game result by match, team, and position."""
        # Arrange
        gr = GameResult(
            id=uuid4(),
            match_id=match_id,
            player_id=player_id,
            team_season_id=team_season_id,
            position=2,
            score=200
        )
        await game_result_repository.add(gr)
        
        # Act
        result = await game_result_repository.find_by_match_and_position(
            match_id=match_id,
            team_season_id=team_season_id,
            position=2
        )
        
        # Assert
        assert result is not None
        assert result.id == gr.id
    
    async def test_find_by_match_and_position_returns_none_when_not_exists(
        self,
        game_result_repository: GameResultRepository,
        match_id: UUID,
        team_season_id: UUID
    ):
        """Test finding game result returns None when not exists."""
        # Act
        result = await game_result_repository.find_by_match_and_position(
            match_id=match_id,
            team_season_id=team_season_id,
            position=2
        )
        
        # Assert
        assert result is None

