"""
Tests for PandasMatchRepository (CSV implementation).

Following TDD: These tests are written BEFORE implementation.
They should fail initially, then pass after implementation.
"""

import pytest
from uuid import UUID, uuid4
from datetime import datetime
from domain.entities.match import Match, MatchStatus
from domain.repositories.match_repository import MatchRepository
from domain.exceptions.domain_exception import EntityNotFoundError


class TestPandasMatchRepository:
    """Test cases for PandasMatchRepository CSV implementation."""
    
    @pytest.fixture
    def event_id(self):
        """Fixture for event ID."""
        return uuid4()
    
    @pytest.fixture
    def team1_id(self):
        """Fixture for team1 ID."""
        return uuid4()
    
    @pytest.fixture
    def team2_id(self):
        """Fixture for team2 ID."""
        return uuid4()
    
    @pytest.fixture
    def sample_match(self, event_id, team1_id, team2_id):
        """Fixture for sample match."""
        return Match(
            id=uuid4(),
            event_id=event_id,
            round_number=1,
            match_number=0,
            team1_team_season_id=team1_id,
            team2_team_season_id=team2_id,
            team1_total_score=800,
            team2_total_score=750,
            status=MatchStatus.SCHEDULED
        )
    
    @pytest.fixture
    def match_csv_path(self, tmp_path):
        """Create a temporary match.csv file for testing."""
        import pandas as pd
        csv_file = tmp_path / "match.csv"
        # Create empty CSV with headers
        df = pd.DataFrame(columns=[
            'id', 'event_id', 'round_number', 'match_number',
            'team1_team_season_id', 'team2_team_season_id',
            'team1_total_score', 'team2_total_score',
            'status', 'created_at', 'updated_at'
        ])
        df.to_csv(csv_file, index=False)
        return csv_file
    
    @pytest.fixture
    def mock_data_adapter(self, match_csv_path):
        """Mock DataAdapter for testing with real CSV file."""
        from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
        adapter = PandasDataAdapter(match_csv_path)
        return adapter
    
    @pytest.fixture
    def match_mapper(self):
        """Match mapper for testing."""
        from infrastructure.persistence.mappers.csv.match_mapper import PandasMatchMapper
        return PandasMatchMapper()
    
    @pytest.fixture
    def match_repository(self, mock_data_adapter, match_mapper):
        """Fixture for match repository."""
        from infrastructure.persistence.repositories.csv.match_repository import PandasMatchRepository
        return PandasMatchRepository(mock_data_adapter, match_mapper)
    
    async def test_get_by_id_returns_match_when_exists(
        self,
        match_repository: MatchRepository,
        sample_match: Match
    ):
        """Test getting match by ID when it exists."""
        # Arrange
        await match_repository.add(sample_match)
        
        # Act
        result = await match_repository.get_by_id(sample_match.id)
        
        # Assert
        assert result is not None
        assert result.id == sample_match.id
        assert result.event_id == sample_match.event_id
        assert result.round_number == sample_match.round_number
    
    async def test_get_by_id_returns_none_when_not_exists(
        self,
        match_repository: MatchRepository
    ):
        """Test getting match by ID when it doesn't exist."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        result = await match_repository.get_by_id(non_existent_id)
        
        # Assert
        assert result is None
    
    async def test_get_all_returns_all_matches(
        self,
        match_repository: MatchRepository,
        event_id: UUID,
        team1_id: UUID,
        team2_id: UUID
    ):
        """Test getting all matches."""
        # Arrange
        match1 = Match(
            id=uuid4(),
            event_id=event_id,
            round_number=1,
            match_number=0,
            team1_team_season_id=team1_id,
            team2_team_season_id=team2_id
        )
        match2 = Match(
            id=uuid4(),
            event_id=event_id,
            round_number=1,
            match_number=1,
            team1_team_season_id=team1_id,
            team2_team_season_id=team2_id
        )
        await match_repository.add(match1)
        await match_repository.add(match2)
        
        # Act
        results = await match_repository.get_all()
        
        # Assert
        assert len(results) >= 2
        assert any(m.id == match1.id for m in results)
        assert any(m.id == match2.id for m in results)
    
    async def test_add_creates_new_match(
        self,
        match_repository: MatchRepository,
        sample_match: Match
    ):
        """Test adding a new match."""
        # Act
        result = await match_repository.add(sample_match)
        
        # Assert
        assert result.id == sample_match.id
        assert await match_repository.exists(sample_match.id)
    
    async def test_update_modifies_existing_match(
        self,
        match_repository: MatchRepository,
        sample_match: Match
    ):
        """Test updating an existing match."""
        # Arrange
        await match_repository.add(sample_match)
        sample_match.team1_total_score = 900
        sample_match.team2_total_score = 850
        sample_match.status = MatchStatus.COMPLETED
        
        # Act
        result = await match_repository.update(sample_match)
        
        # Assert
        assert result.team1_total_score == 900
        assert result.team2_total_score == 850
        assert result.status == MatchStatus.COMPLETED
        
        # Verify persisted
        retrieved = await match_repository.get_by_id(sample_match.id)
        assert retrieved.team1_total_score == 900
        assert retrieved.status == MatchStatus.COMPLETED
    
    async def test_update_raises_error_when_not_exists(
        self,
        match_repository: MatchRepository,
        sample_match: Match
    ):
        """Test updating non-existent match raises error."""
        # Act & Assert
        with pytest.raises(EntityNotFoundError):
            await match_repository.update(sample_match)
    
    async def test_delete_removes_match(
        self,
        match_repository: MatchRepository,
        sample_match: Match
    ):
        """Test deleting a match."""
        # Arrange
        await match_repository.add(sample_match)
        assert await match_repository.exists(sample_match.id)
        
        # Act
        await match_repository.delete(sample_match.id)
        
        # Assert
        assert not await match_repository.exists(sample_match.id)
        assert await match_repository.get_by_id(sample_match.id) is None
    
    async def test_delete_raises_error_when_not_exists(
        self,
        match_repository: MatchRepository
    ):
        """Test deleting non-existent match raises error."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError):
            await match_repository.delete(non_existent_id)
    
    async def test_exists_returns_true_when_match_exists(
        self,
        match_repository: MatchRepository,
        sample_match: Match
    ):
        """Test exists returns True when match exists."""
        # Arrange
        await match_repository.add(sample_match)
        
        # Act
        result = await match_repository.exists(sample_match.id)
        
        # Assert
        assert result is True
    
    async def test_exists_returns_false_when_match_not_exists(
        self,
        match_repository: MatchRepository
    ):
        """Test exists returns False when match doesn't exist."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        result = await match_repository.exists(non_existent_id)
        
        # Assert
        assert result is False
    
    async def test_get_by_event_returns_filtered_matches(
        self,
        match_repository: MatchRepository,
        event_id: UUID,
        team1_id: UUID,
        team2_id: UUID
    ):
        """Test getting matches by event."""
        # Arrange
        other_event_id = uuid4()
        match1 = Match(
            id=uuid4(),
            event_id=event_id,
            round_number=1,
            match_number=0,
            team1_team_season_id=team1_id,
            team2_team_season_id=team2_id
        )
        match2 = Match(
            id=uuid4(),
            event_id=other_event_id,
            round_number=1,
            match_number=0,
            team1_team_season_id=team1_id,
            team2_team_season_id=team2_id
        )
        await match_repository.add(match1)
        await match_repository.add(match2)
        
        # Act
        results = await match_repository.get_by_event(event_id)
        
        # Assert
        assert len(results) >= 1
        assert all(m.event_id == event_id for m in results)
        assert any(m.id == match1.id for m in results)
        assert not any(m.id == match2.id for m in results)
    
    async def test_get_by_event_and_round_returns_filtered_matches(
        self,
        match_repository: MatchRepository,
        event_id: UUID,
        team1_id: UUID,
        team2_id: UUID
    ):
        """Test getting matches by event and round."""
        # Arrange
        match1 = Match(
            id=uuid4(),
            event_id=event_id,
            round_number=1,
            match_number=0,
            team1_team_season_id=team1_id,
            team2_team_season_id=team2_id
        )
        match2 = Match(
            id=uuid4(),
            event_id=event_id,
            round_number=2,
            match_number=0,
            team1_team_season_id=team1_id,
            team2_team_season_id=team2_id
        )
        await match_repository.add(match1)
        await match_repository.add(match2)
        
        # Act
        results = await match_repository.get_by_event_and_round(event_id, round_number=1)
        
        # Assert
        assert len(results) >= 1
        assert all(m.event_id == event_id and m.round_number == 1 for m in results)
        assert any(m.id == match1.id for m in results)
        assert not any(m.id == match2.id for m in results)
    
    async def test_get_by_team_returns_filtered_matches(
        self,
        match_repository: MatchRepository,
        event_id: UUID,
        team1_id: UUID,
        team2_id: UUID
    ):
        """Test getting matches by team."""
        # Arrange
        other_team_id = uuid4()
        match1 = Match(
            id=uuid4(),
            event_id=event_id,
            round_number=1,
            match_number=0,
            team1_team_season_id=team1_id,
            team2_team_season_id=team2_id
        )
        match2 = Match(
            id=uuid4(),
            event_id=event_id,
            round_number=1,
            match_number=1,
            team1_team_season_id=other_team_id,
            team2_team_season_id=team2_id
        )
        await match_repository.add(match1)
        await match_repository.add(match2)
        
        # Act
        results = await match_repository.get_by_team(team1_id)
        
        # Assert
        assert len(results) >= 1
        assert any(m.id == match1.id for m in results)
        assert not any(m.id == match2.id for m in results)
        # Match should appear if team is team1 or team2
        assert all(
            m.team1_team_season_id == team1_id or m.team2_team_season_id == team1_id
            for m in results
        )
    
    async def test_find_match_returns_match_when_exists(
        self,
        match_repository: MatchRepository,
        event_id: UUID,
        team1_id: UUID,
        team2_id: UUID
    ):
        """Test finding match by event, round, and teams."""
        # Arrange
        match = Match(
            id=uuid4(),
            event_id=event_id,
            round_number=1,
            match_number=0,
            team1_team_season_id=team1_id,
            team2_team_season_id=team2_id
        )
        await match_repository.add(match)
        
        # Act
        result = await match_repository.find_match(
            event_id=event_id,
            round_number=1,
            team1_team_season_id=team1_id,
            team2_team_season_id=team2_id
        )
        
        # Assert
        assert result is not None
        assert result.id == match.id
    
    async def test_find_match_returns_none_when_not_exists(
        self,
        match_repository: MatchRepository,
        event_id: UUID,
        team1_id: UUID,
        team2_id: UUID
    ):
        """Test finding match returns None when not exists."""
        # Act
        result = await match_repository.find_match(
            event_id=event_id,
            round_number=1,
            team1_team_season_id=team1_id,
            team2_team_season_id=team2_id
        )
        
        # Assert
        assert result is None
    
    async def test_get_by_status_returns_filtered_matches(
        self,
        match_repository: MatchRepository,
        sample_match: Match
    ):
        """Test getting matches by status."""
        # Arrange
        await match_repository.add(sample_match)
        sample_match.status = MatchStatus.COMPLETED
        await match_repository.update(sample_match)
        
        # Act
        results = await match_repository.get_by_status(MatchStatus.COMPLETED)
        
        # Assert
        assert len(results) >= 1
        assert all(m.status == MatchStatus.COMPLETED for m in results)
        assert any(m.id == sample_match.id for m in results)

