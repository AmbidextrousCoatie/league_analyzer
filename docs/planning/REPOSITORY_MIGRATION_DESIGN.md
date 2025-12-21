# Repository Pattern Design for Easy Migration

**Date:** 2025-12-21  
**Purpose:** Design repository interfaces that enable seamless migration from CSV to SQL

---

## Design Principles

### 1. Storage-Agnostic Interfaces
- Repository interfaces contain **no storage-specific details**
- Methods work identically for CSV and SQL implementations
- Application layer depends on interfaces, not implementations

### 2. Dependency Injection
- DI container provides repository implementations
- Switch implementations by changing DI configuration
- No code changes needed in application layer

### 3. Mapper Layer Separation
- Separate mapping logic from storage logic
- Mappers handle Domain ↔ Storage conversion
- Same mapper interface works for CSV and SQL

### 4. Interface Location Strategy

**Option A: Domain Layer** (Recommended)
```
domain/
  repositories/
    event_repository.py      # Interface
    game_repository.py       # Interface
    ...
```

**Option B: Application Layer**
```
application/
  repositories/
    event_repository.py      # Interface
    game_repository.py       # Interface
    ...
```

**Recommendation:** **Domain Layer** - Repositories are part of domain infrastructure needs.

---

## Repository Interface Structure

### Base Repository Interface

```python
# domain/repositories/base_repository.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
from uuid import UUID

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """
    Base repository interface - storage agnostic.
    
    All repositories implement these basic CRUD operations.
    Storage-specific implementations handle the details.
    """
    
    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """
        Get entity by ID.
        
        Args:
            entity_id: UUID of the entity
        
        Returns:
            Entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(self) -> List[T]:
        """
        Get all entities.
        
        Returns:
            List of all entities
        """
        pass
    
    @abstractmethod
    async def add(self, entity: T) -> T:
        """
        Add a new entity.
        
        Args:
            entity: Entity to add
        
        Returns:
            Added entity (with generated ID if applicable)
        """
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """
        Update an existing entity.
        
        Args:
            entity: Entity to update
        
        Returns:
            Updated entity
        
        Raises:
            EntityNotFoundError: If entity doesn't exist
        """
        pass
    
    @abstractmethod
    async def delete(self, entity_id: UUID) -> None:
        """
        Delete an entity by ID.
        
        Args:
            entity_id: UUID of entity to delete
        
        Raises:
            EntityNotFoundError: If entity doesn't exist
        """
        pass
    
    @abstractmethod
    async def exists(self, entity_id: UUID) -> bool:
        """
        Check if entity exists.
        
        Args:
            entity_id: UUID to check
        
        Returns:
            True if exists, False otherwise
        """
        pass
```

### Entity-Specific Repository Interface Example

```python
# domain/repositories/event_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from domain.entities.event import Event
from domain.value_objects.event_status import EventStatus

class EventRepository(ABC):
    """
    Repository interface for Event entities.
    
    Storage-agnostic interface - works for CSV or SQL implementations.
    """
    
    @abstractmethod
    async def get_by_id(self, event_id: UUID) -> Optional[Event]:
        """Get event by ID."""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Event]:
        """Get all events."""
        pass
    
    @abstractmethod
    async def get_by_league_season(
        self, 
        league_season_id: UUID
    ) -> List[Event]:
        """
        Get all events for a league season.
        
        Args:
            league_season_id: UUID of the league season
        
        Returns:
            List of events for the season
        """
        pass
    
    @abstractmethod
    async def get_by_week(
        self,
        league_season_id: UUID,
        week: int
    ) -> List[Event]:
        """
        Get events for a specific week.
        
        Args:
            league_season_id: UUID of the league season
            week: Week number
        
        Returns:
            List of events for the week
        """
        pass
    
    @abstractmethod
    async def get_by_status(
        self,
        status: EventStatus
    ) -> List[Event]:
        """
        Get events by status.
        
        Args:
            status: EventStatus to filter by
        
        Returns:
            List of events with the status
        """
        pass
    
    @abstractmethod
    async def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Event]:
        """
        Get events within a date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
        
        Returns:
            List of events in the date range
        """
        pass
    
    @abstractmethod
    async def add(self, event: Event) -> Event:
        """Add a new event."""
        pass
    
    @abstractmethod
    async def update(self, event: Event) -> Event:
        """Update an existing event."""
        pass
    
    @abstractmethod
    async def delete(self, event_id: UUID) -> None:
        """Delete an event."""
        pass
    
    @abstractmethod
    async def exists(self, event_id: UUID) -> bool:
        """Check if event exists."""
        pass
```

---

## Implementation Structure

### CSV Implementation

```python
# infrastructure/persistence/repositories/csv/event_repository.py
from domain.repositories.event_repository import EventRepository
from infrastructure.persistence.adapters.data_adapter import DataAdapter
from infrastructure.persistence.mappers.event_mapper import EventMapper
from domain.entities.event import Event
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from domain.value_objects.event_status import EventStatus

class PandasEventRepository(EventRepository):
    """
    CSV-based Event repository using Pandas.
    
    This implementation reads/writes CSV files using Pandas DataFrames.
    """
    
    def __init__(
        self,
        data_adapter: DataAdapter,
        mapper: EventMapper
    ):
        self._adapter = data_adapter
        self._mapper = mapper
    
    async def get_by_id(self, event_id: UUID) -> Optional[Event]:
        """Get event by ID from CSV."""
        df = await self._adapter.get_event_data()
        row = df[df['id'] == str(event_id)]
        if row.empty:
            return None
        return self._mapper.to_domain(row.iloc[0])
    
    async def get_by_league_season(
        self, 
        league_season_id: UUID
    ) -> List[Event]:
        """Get events for league season from CSV."""
        df = await self._adapter.get_event_data()
        filtered = df[df['league_season_id'] == str(league_season_id)]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def add(self, event: Event) -> Event:
        """Add event to CSV file."""
        df = await self._adapter.get_event_data()
        new_row = self._mapper.to_dataframe(event)
        df = pd.concat([df, new_row], ignore_index=True)
        await self._adapter.save_event_data(df)
        return event
    
    # ... other methods ...
```

### SQL Implementation (Future)

```python
# infrastructure/persistence/repositories/sql/event_repository.py
from domain.repositories.event_repository import EventRepository
from sqlalchemy.orm import Session
from infrastructure.persistence.mappers.event_mapper import EventMapper
from infrastructure.persistence.models.event_model import EventModel
from domain.entities.event import Event
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from domain.value_objects.event_status import EventStatus

class PostgresEventRepository(EventRepository):
    """
    PostgreSQL-based Event repository.
    
    This implementation uses SQLAlchemy to interact with PostgreSQL.
    """
    
    def __init__(
        self,
        session: Session,
        mapper: EventMapper
    ):
        self._session = session
        self._mapper = mapper
    
    async def get_by_id(self, event_id: UUID) -> Optional[Event]:
        """Get event by ID from database."""
        db_event = (
            self._session
            .query(EventModel)
            .filter_by(id=event_id)
            .first()
        )
        if not db_event:
            return None
        return self._mapper.to_domain(db_event)
    
    async def get_by_league_season(
        self, 
        league_season_id: UUID
    ) -> List[Event]:
        """Get events for league season from database."""
        db_events = (
            self._session
            .query(EventModel)
            .filter_by(league_season_id=league_season_id)
            .all()
        )
        return [self._mapper.to_domain(db_event) for db_event in db_events]
    
    async def add(self, event: Event) -> Event:
        """Add event to database."""
        db_event = self._mapper.to_db(event)
        self._session.add(db_event)
        self._session.commit()
        return event
    
    # ... other methods ...
```

---

## Mapper Layer

### Mapper Interface

```python
# infrastructure/persistence/mappers/base_mapper.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

DomainEntity = TypeVar('DomainEntity')
StorageModel = TypeVar('StorageModel')  # DataFrame row or SQL model

class BaseMapper(ABC, Generic[DomainEntity, StorageModel]):
    """
    Base mapper interface for converting between domain and storage models.
    """
    
    @abstractmethod
    def to_domain(self, storage_model: StorageModel) -> DomainEntity:
        """
        Convert storage model to domain entity.
        
        Args:
            storage_model: Storage representation (DataFrame row or SQL model)
        
        Returns:
            Domain entity
        """
        pass
    
    @abstractmethod
    def to_storage(self, domain_entity: DomainEntity) -> StorageModel:
        """
        Convert domain entity to storage model.
        
        Args:
            domain_entity: Domain entity
        
        Returns:
            Storage representation (DataFrame row or SQL model)
        """
        pass
```

### CSV Mapper Implementation

```python
# infrastructure/persistence/mappers/csv/event_mapper.py
from infrastructure.persistence.mappers.base_mapper import BaseMapper
from domain.entities.event import Event
from domain.value_objects.event_status import EventStatus
import pandas as pd
from uuid import UUID
from datetime import datetime

class PandasEventMapper(BaseMapper[Event, pd.Series]):
    """Mapper for Event entity ↔ Pandas DataFrame."""
    
    def to_domain(self, row: pd.Series) -> Event:
        """Convert DataFrame row to Event entity."""
        return Event(
            id=UUID(row['id']),
            league_season_id=UUID(row['league_season_id']),
            event_type=row['event_type'],
            league_week=int(row['league_week']) if pd.notna(row['league_week']) else None,
            date=pd.to_datetime(row['date']).to_pydatetime(),
            venue_id=row['venue_id'] if pd.notna(row['venue_id']) else None,
            status=EventStatus(row['status']),
            disqualification_reason=row.get('disqualification_reason'),
            notes=row.get('notes')
        )
    
    def to_storage(self, event: Event) -> pd.Series:
        """Convert Event entity to DataFrame row."""
        return pd.Series({
            'id': str(event.id),
            'league_season_id': str(event.league_season_id),
            'event_type': event.event_type,
            'league_week': event.league_week,
            'date': event.date.isoformat(),
            'venue_id': event.venue_id,
            'status': event.status.value,
            'disqualification_reason': event.disqualification_reason,
            'notes': event.notes
        })
```

### SQL Mapper Implementation (Future)

```python
# infrastructure/persistence/mappers/sql/event_mapper.py
from infrastructure.persistence.mappers.base_mapper import BaseMapper
from domain.entities.event import Event
from infrastructure.persistence.models.event_model import EventModel
from domain.value_objects.event_status import EventStatus

class PostgresEventMapper(BaseMapper[Event, EventModel]):
    """Mapper for Event entity ↔ SQLAlchemy model."""
    
    def to_domain(self, db_event: EventModel) -> Event:
        """Convert SQL model to Event entity."""
        return Event(
            id=db_event.id,
            league_season_id=db_event.league_season_id,
            event_type=db_event.event_type,
            league_week=db_event.league_week,
            date=db_event.date,
            venue_id=db_event.venue_id,
            status=EventStatus(db_event.status),
            disqualification_reason=db_event.disqualification_reason,
            notes=db_event.notes
        )
    
    def to_storage(self, event: Event) -> EventModel:
        """Convert Event entity to SQL model."""
        return EventModel(
            id=event.id,
            league_season_id=event.league_season_id,
            event_type=event.event_type,
            league_week=event.league_week,
            date=event.date,
            venue_id=event.venue_id,
            status=event.status.value,
            disqualification_reason=event.disqualification_reason,
            notes=event.notes
        )
```

---

## Dependency Injection Configuration

### CSV Configuration (Current)

```python
# infrastructure/config/container.py
from dependency_injector import containers, providers
from infrastructure.persistence.repositories.csv.event_repository import PandasEventRepository
from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
from infrastructure.persistence.mappers.csv.event_mapper import PandasEventMapper

class Container(containers.DeclarativeContainer):
    """DI Container configuration."""
    
    # Data adapter
    data_adapter = providers.Singleton(PandasDataAdapter)
    
    # Mappers
    event_mapper = providers.Singleton(PandasEventMapper)
    
    # Repositories (CSV)
    event_repository = providers.Factory(
        PandasEventRepository,
        data_adapter=data_adapter,
        mapper=event_mapper
    )
```

### SQL Configuration (Future)

```python
# infrastructure/config/container.py (updated)
from dependency_injector import containers, providers
from infrastructure.persistence.repositories.sql.event_repository import PostgresEventRepository
from infrastructure.persistence.mappers.sql.event_mapper import PostgresEventMapper
from sqlalchemy.orm import Session

class Container(containers.DeclarativeContainer):
    """DI Container configuration."""
    
    # Database session
    db_session = providers.Singleton(Session)
    
    # Mappers
    event_mapper = providers.Singleton(PostgresEventMapper)
    
    # Repositories (SQL)
    event_repository = providers.Factory(
        PostgresEventRepository,
        session=db_session,
        mapper=event_mapper
    )
```

**Migration:** Just change the DI container configuration - no application code changes!

---

## Migration Checklist

### Phase 2: CSV Implementation
- [ ] Create repository interfaces in `domain/repositories/`
- [ ] Implement CSV repositories in `infrastructure/persistence/repositories/csv/`
- [ ] Create CSV mappers in `infrastructure/persistence/mappers/csv/`
- [ ] Configure DI container for CSV repositories
- [ ] Test CSV repositories thoroughly

### Phase 3: SQL Preparation
- [ ] Design database schema
- [ ] Create SQLAlchemy models
- [ ] Create SQL mappers
- [ ] Implement SQL repositories
- [ ] Create data migration script (CSV → SQL)

### Phase 4: Migration
- [ ] Run data migration
- [ ] Update DI container to use SQL repositories
- [ ] Test SQL repositories
- [ ] Monitor performance
- [ ] Remove CSV repositories (optional)

---

## Key Benefits

✅ **Zero Application Code Changes** - Switch via DI container  
✅ **Same Interface** - CSV and SQL use identical interfaces  
✅ **Testable** - Easy to mock repositories for testing  
✅ **Flexible** - Can run CSV and SQL in parallel during migration  
✅ **Maintainable** - Clear separation of concerns  

---

**This design ensures seamless migration from CSV to SQL!** 🎳

