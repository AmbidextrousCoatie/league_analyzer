"""
Tests for PandasEventRepository (CSV implementation).

Following TDD: These tests are written BEFORE implementation.
They should fail initially, then pass after implementation.
"""

import pytest
from uuid import UUID, uuid4
from datetime import datetime
from domain.entities.event import Event
from domain.repositories.event_repository import EventRepository
from domain.value_objects.event_status import EventStatus
from domain.exceptions.domain_exception import EntityNotFoundError


class TestPandasEventRepository:
    """Test cases for PandasEventRepository CSV implementation."""
    
    @pytest.fixture
    def league_season_id(self):
        """Fixture for league season ID."""
        return uuid4()
    
    @pytest.fixture
    def sample_event(self, league_season_id):
        """Fixture for sample event."""
        return Event(
            id=uuid4(),
            league_season_id=league_season_id,
            event_type="league",
            league_week=1,
            date=datetime(2024, 1, 15),
            venue_id="venue-1",
            status=EventStatus.SCHEDULED
        )
    
    @pytest.fixture
    def event_repository(self, mock_data_adapter, event_mapper):
        """Fixture for event repository."""
        from infrastructure.persistence.repositories.csv.event_repository import PandasEventRepository
        return PandasEventRepository(mock_data_adapter, event_mapper)
    
    async def test_get_by_id_returns_event_when_exists(
        self,
        event_repository: EventRepository,
        sample_event: Event
    ):
        """Test getting event by ID when it exists."""
        # Arrange
        await event_repository.add(sample_event)
        
        # Act
        result = await event_repository.get_by_id(sample_event.id)
        
        # Assert
        assert result is not None
        assert result.id == sample_event.id
        assert result.league_season_id == sample_event.league_season_id
        assert result.event_type == sample_event.event_type
    
    async def test_get_by_id_returns_none_when_not_exists(
        self,
        event_repository: EventRepository
    ):
        """Test getting event by ID when it doesn't exist."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        result = await event_repository.get_by_id(non_existent_id)
        
        # Assert
        assert result is None
    
    async def test_get_all_returns_all_events(
        self,
        event_repository: EventRepository,
        league_season_id: UUID
    ):
        """Test getting all events."""
        # Arrange
        event1 = Event(
            id=uuid4(),
            league_season_id=league_season_id,
            event_type="league",
            league_week=1,
            date=datetime(2024, 1, 15)
        )
        event2 = Event(
            id=uuid4(),
            league_season_id=league_season_id,
            event_type="league",
            league_week=2,
            date=datetime(2024, 1, 22)
        )
        await event_repository.add(event1)
        await event_repository.add(event2)
        
        # Act
        results = await event_repository.get_all()
        
        # Assert
        assert len(results) >= 2
        assert any(e.id == event1.id for e in results)
        assert any(e.id == event2.id for e in results)
    
    async def test_add_creates_new_event(
        self,
        event_repository: EventRepository,
        sample_event: Event
    ):
        """Test adding a new event."""
        # Act
        result = await event_repository.add(sample_event)
        
        # Assert
        assert result.id == sample_event.id
        assert await event_repository.exists(sample_event.id)
    
    async def test_update_modifies_existing_event(
        self,
        event_repository: EventRepository,
        sample_event: Event
    ):
        """Test updating an existing event."""
        # Arrange
        await event_repository.add(sample_event)
        sample_event.update_status(EventStatus.IN_PROGRESS)
        sample_event.update_notes("Updated notes")
        
        # Act
        result = await event_repository.update(sample_event)
        
        # Assert
        assert result.status == EventStatus.IN_PROGRESS
        assert result.notes == "Updated notes"
        
        # Verify persisted
        retrieved = await event_repository.get_by_id(sample_event.id)
        assert retrieved.status == EventStatus.IN_PROGRESS
    
    async def test_update_raises_error_when_not_exists(
        self,
        event_repository: EventRepository,
        sample_event: Event
    ):
        """Test updating non-existent event raises error."""
        # Act & Assert
        with pytest.raises(EntityNotFoundError):
            await event_repository.update(sample_event)
    
    async def test_delete_removes_event(
        self,
        event_repository: EventRepository,
        sample_event: Event
    ):
        """Test deleting an event."""
        # Arrange
        await event_repository.add(sample_event)
        assert await event_repository.exists(sample_event.id)
        
        # Act
        await event_repository.delete(sample_event.id)
        
        # Assert
        assert not await event_repository.exists(sample_event.id)
        assert await event_repository.get_by_id(sample_event.id) is None
    
    async def test_delete_raises_error_when_not_exists(
        self,
        event_repository: EventRepository
    ):
        """Test deleting non-existent event raises error."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act & Assert
        with pytest.raises(EntityNotFoundError):
            await event_repository.delete(non_existent_id)
    
    async def test_exists_returns_true_when_event_exists(
        self,
        event_repository: EventRepository,
        sample_event: Event
    ):
        """Test exists returns True when event exists."""
        # Arrange
        await event_repository.add(sample_event)
        
        # Act
        result = await event_repository.exists(sample_event.id)
        
        # Assert
        assert result is True
    
    async def test_exists_returns_false_when_event_not_exists(
        self,
        event_repository: EventRepository
    ):
        """Test exists returns False when event doesn't exist."""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        result = await event_repository.exists(non_existent_id)
        
        # Assert
        assert result is False
    
    async def test_get_by_league_season_returns_filtered_events(
        self,
        event_repository: EventRepository,
        league_season_id: UUID
    ):
        """Test getting events by league season."""
        # Arrange
        event1 = Event(
            id=uuid4(),
            league_season_id=league_season_id,
            event_type="league",
            league_week=1,
            date=datetime(2024, 1, 15)
        )
        other_league_season_id = uuid4()
        event2 = Event(
            id=uuid4(),
            league_season_id=other_league_season_id,
            event_type="league",
            league_week=1,
            date=datetime(2024, 1, 15)
        )
        await event_repository.add(event1)
        await event_repository.add(event2)
        
        # Act
        results = await event_repository.get_by_league_season(league_season_id)
        
        # Assert
        assert len(results) >= 1
        assert all(e.league_season_id == league_season_id for e in results)
        assert any(e.id == event1.id for e in results)
        assert not any(e.id == event2.id for e in results)
    
    async def test_get_by_week_returns_filtered_events(
        self,
        event_repository: EventRepository,
        league_season_id: UUID
    ):
        """Test getting events by week."""
        # Arrange
        event1 = Event(
            id=uuid4(),
            league_season_id=league_season_id,
            event_type="league",
            league_week=1,
            date=datetime(2024, 1, 15)
        )
        event2 = Event(
            id=uuid4(),
            league_season_id=league_season_id,
            event_type="league",
            league_week=2,
            date=datetime(2024, 1, 22)
        )
        await event_repository.add(event1)
        await event_repository.add(event2)
        
        # Act
        results = await event_repository.get_by_week(league_season_id, week=1)
        
        # Assert
        assert len(results) >= 1
        assert all(e.league_week == 1 for e in results)
        assert any(e.id == event1.id for e in results)
        assert not any(e.id == event2.id for e in results)
    
    async def test_get_by_status_returns_filtered_events(
        self,
        event_repository: EventRepository,
        sample_event: Event
    ):
        """Test getting events by status."""
        # Arrange
        await event_repository.add(sample_event)
        sample_event.update_status(EventStatus.IN_PROGRESS)
        await event_repository.update(sample_event)
        
        # Act
        results = await event_repository.get_by_status(EventStatus.IN_PROGRESS)
        
        # Assert
        assert len(results) >= 1
        assert all(e.status == EventStatus.IN_PROGRESS for e in results)
        assert any(e.id == sample_event.id for e in results)
    
    async def test_get_by_date_range_returns_filtered_events(
        self,
        event_repository: EventRepository,
        league_season_id: UUID
    ):
        """Test getting events by date range."""
        # Arrange
        event1 = Event(
            id=uuid4(),
            league_season_id=league_season_id,
            event_type="league",
            league_week=1,
            date=datetime(2024, 1, 15)
        )
        event2 = Event(
            id=uuid4(),
            league_season_id=league_season_id,
            event_type="league",
            league_week=2,
            date=datetime(2024, 2, 15)
        )
        event3 = Event(
            id=uuid4(),
            league_season_id=league_season_id,
            event_type="league",
            league_week=3,
            date=datetime(2024, 3, 15)
        )
        await event_repository.add(event1)
        await event_repository.add(event2)
        await event_repository.add(event3)
        
        # Act
        results = await event_repository.get_by_date_range(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 2, 28)
        )
        
        # Assert
        assert len(results) >= 2
        assert any(e.id == event1.id for e in results)
        assert any(e.id == event2.id for e in results)
        assert not any(e.id == event3.id for e in results)

