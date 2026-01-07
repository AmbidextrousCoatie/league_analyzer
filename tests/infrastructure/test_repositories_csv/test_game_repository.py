"""
Tests for PandasGameRepository (CSV implementation).

Following TDD: These tests are written BEFORE implementation.
"""

import pytest
import pandas as pd
from uuid import UUID, uuid4
from datetime import datetime
from domain.entities.game import Game
from domain.repositories.game_repository import GameRepository
from domain.value_objects.game_result import GameResult
from domain.exceptions.domain_exception import EntityNotFoundError


class TestPandasGameRepository:
    """Test cases for PandasGameRepository CSV implementation."""
    
    @pytest.fixture
    def event_id(self):
        """Fixture for event ID."""
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
    def sample_game(self, event_id, player_id, team_season_id):
        """Fixture for sample game."""
        return Game(
            id=uuid4(),
            event_id=event_id,
            player_id=player_id,
            team_season_id=team_season_id,
            position=1,
            match_number=1,
            round_number=1,
            score=200.0,
            points=2.0
        )
    
    @pytest.fixture
    def game_csv_path(self, tmp_path):
        """Create a temporary game.csv file for testing."""
        csv_file = tmp_path / "game.csv"
        df = pd.DataFrame(columns=[
            'id', 'event_id', 'player_id', 'team_season_id', 'position',
            'match_number', 'round_number', 'score', 'points',
            'opponent_id', 'opponent_team_season_id', 'handicap', 'is_disqualified',
            'created_at', 'updated_at'
        ])
        df.to_csv(csv_file, index=False)
        return csv_file
    
    @pytest.fixture
    def mock_data_adapter(self, game_csv_path):
        """Mock DataAdapter for testing with real CSV file."""
        from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
        adapter = PandasDataAdapter(game_csv_path)
        return adapter
    
    @pytest.fixture
    def game_mapper(self):
        """Game mapper for testing."""
        from infrastructure.persistence.mappers.csv.game_mapper import PandasGameMapper
        return PandasGameMapper()
    
    @pytest.fixture
    def game_repository(self, mock_data_adapter, game_mapper):
        """Fixture for game repository."""
        from infrastructure.persistence.repositories.csv.game_repository import PandasGameRepository
        return PandasGameRepository(mock_data_adapter, game_mapper)
    
    async def test_get_by_id_returns_game_when_exists(
        self,
        game_repository: GameRepository,
        sample_game: Game
    ):
        """Test getting game by ID when it exists."""
        await game_repository.add(sample_game)
        result = await game_repository.get_by_id(sample_game.id)
        assert result is not None
        assert result.id == sample_game.id
    
    async def test_get_by_id_returns_none_when_not_exists(
        self,
        game_repository: GameRepository
    ):
        """Test getting game by ID when it doesn't exist."""
        result = await game_repository.get_by_id(uuid4())
        assert result is None
    
    async def test_get_all_returns_all_games(
        self,
        game_repository: GameRepository,
        event_id: UUID,
        player_id: UUID,
        team_season_id: UUID
    ):
        """Test getting all games."""
        g1 = Game(
            id=uuid4(),
            event_id=event_id,
            player_id=player_id,
            team_season_id=team_season_id,
            position=0,
            match_number=1,
            round_number=1,
            score=200.0,
            points=2.0
        )
        g2 = Game(
            id=uuid4(),
            event_id=event_id,
            player_id=player_id,
            team_season_id=team_season_id,
            position=0,
            match_number=2,
            round_number=1,
            score=180.0,
            points=0.0
        )
        await game_repository.add(g1)
        await game_repository.add(g2)
        results = await game_repository.get_all()
        assert len(results) >= 2
    
    async def test_add_creates_new_game(
        self,
        game_repository: GameRepository,
        sample_game: Game
    ):
        """Test adding a new game."""
        result = await game_repository.add(sample_game)
        assert result.id == sample_game.id
        assert await game_repository.exists(sample_game.id)
    
    async def test_update_modifies_existing_game(
        self,
        game_repository: GameRepository,
        sample_game: Game
    ):
        """Test updating an existing game."""
        await game_repository.add(sample_game)
        # Update match_number directly (Game doesn't have update_match_number method)
        sample_game.match_number = 2
        sample_game.updated_at = datetime.utcnow()
        result = await game_repository.update(sample_game)
        assert result.match_number == 2
    
    async def test_update_raises_error_when_not_exists(
        self,
        game_repository: GameRepository,
        sample_game: Game
    ):
        """Test updating non-existent game raises error."""
        with pytest.raises(EntityNotFoundError):
            await game_repository.update(sample_game)
    
    async def test_delete_removes_game(
        self,
        game_repository: GameRepository,
        sample_game: Game
    ):
        """Test deleting a game."""
        await game_repository.add(sample_game)
        await game_repository.delete(sample_game.id)
        assert not await game_repository.exists(sample_game.id)
    
    async def test_get_by_event_returns_filtered_games(
        self,
        game_repository: GameRepository,
        event_id: UUID,
        player_id: UUID,
        team_season_id: UUID
    ):
        """Test getting games by event."""
        g1 = Game(
            id=uuid4(),
            event_id=event_id,
            player_id=player_id,
            team_season_id=team_season_id,
            position=0,
            match_number=1,
            round_number=1,
            score=200.0,
            points=2.0
        )
        other_event_id = uuid4()
        g2 = Game(
            id=uuid4(),
            event_id=other_event_id,
            player_id=player_id,
            team_season_id=team_season_id,
            position=0,
            match_number=1,
            round_number=1,
            score=180.0,
            points=0.0
        )
        await game_repository.add(g1)
        await game_repository.add(g2)
        results = await game_repository.get_by_event(event_id)
        assert len(results) >= 1
        assert all(g.event_id == event_id for g in results)
    
    async def test_get_by_team_season_returns_filtered_games(
        self,
        game_repository: GameRepository,
        event_id: UUID,
        player_id: UUID,
        team_season_id: UUID
    ):
        """Test getting games by team season."""
        g1 = Game(
            id=uuid4(),
            event_id=event_id,
            player_id=player_id,
            team_season_id=team_season_id,
            position=0,
            match_number=1,
            round_number=1,
            score=200.0,
            points=2.0
        )
        other_team_season_id = uuid4()
        g2 = Game(
            id=uuid4(),
            event_id=event_id,
            player_id=player_id,
            team_season_id=other_team_season_id,
            position=0,
            match_number=1,
            round_number=1,
            score=180.0,
            points=0.0
        )
        await game_repository.add(g1)
        await game_repository.add(g2)
        results = await game_repository.get_by_team_season(team_season_id)
        assert len(results) >= 1
        assert any(g.team_season_id == team_season_id for g in results)
    
    async def test_get_by_event_and_match_returns_filtered_games(
        self,
        game_repository: GameRepository,
        event_id: UUID,
        player_id: UUID,
        team_season_id: UUID
    ):
        """Test getting games by event and match number."""
        g1 = Game(
            id=uuid4(),
            event_id=event_id,
            player_id=player_id,
            team_season_id=team_season_id,
            position=0,
            match_number=1,
            round_number=1,
            score=200.0,
            points=2.0
        )
        await game_repository.add(g1)
        results = await game_repository.get_by_event_and_match(event_id, 1)
        assert len(results) >= 1
        assert all(g.match_number == 1 for g in results)

