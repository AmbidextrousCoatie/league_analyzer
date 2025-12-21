# Storage Scalability Analysis & Migration Strategy

**Date:** 2025-12-21  
**Context:** CSV files → Future relational database migration  
**Data Growth:** ~200x current volume expected

---

## Executive Summary

### Current Situation
- **Current data:** ~5-10% of expected per-season data
- **Legacy seasons:** 5-10 seasons to add
- **Future growth:** 10+ years of data
- **Expected total:** ~200x current volume

### Recommendation
✅ **CSV files are feasible for Phase 2** (current + legacy seasons)  
⚠️ **Plan migration to relational DB** before reaching full 10-year dataset  
✅ **Design abstraction layer** for easy migration

---

## Current Data Volume Analysis

### Data Size Estimates (Actual)

| Table | Current Rows | Current Size | 200x Size |
|-------|-------------|--------------|-----------|
| `event.csv` | 10 | 0.58 KB | ~116 KB |
| `game_result.csv` | 3,120 | 99.48 KB | ~19.9 MB |
| `player.csv` | 139 | 5.93 KB | ~1.2 MB |
| `team_season.csv` | 32 | 0.36 KB | ~72 KB |
| `league_season.csv` | 4 | 0.21 KB | ~42 KB |
| `club.csv` | 18 | 0.63 KB | ~126 KB |
| `venue.csv` | 5 | 0.45 KB | ~90 KB |
| **Total** | **3,328** | **~108 KB (0.11 MB)** | **~21 MB** |

**Key Finding:** Current data is ~108 KB. At 200x scale, we're looking at ~21 MB total, which is **very manageable** for CSV files.

### CSV File Limitations

#### ✅ Advantages (Current Phase)
- Simple, human-readable
- Easy to version control
- No database server needed
- Fast for small datasets (< 1 MB)
- Easy backup (just copy files)

#### ⚠️ Limitations (200x Scale)
- **No indexing:** Full table scans for queries
- **No transactions:** Risk of data corruption
- **No concurrent writes:** File locking issues
- **Memory intensive:** Load entire file into memory
- **Slow queries:** O(n) complexity for filtering
- **No relationships:** Manual joins in code
- **File size limits:** Large files become unwieldy

### Performance Estimates (200x Scale)

| Operation | Current (CSV) | 200x Scale (CSV) | 200x Scale (SQL) |
|-----------|---------------|-------------------|------------------|
| Load all events | < 1 ms | ~50-100 ms | ~5-10 ms |
| Filter by season | < 1 ms | ~50-100 ms | ~1-2 ms (indexed) |
| Join events + results | < 5 ms | ~200-500 ms | ~10-20 ms |
| Write new event | < 1 ms | ~50-100 ms | ~1-2 ms |
| Complex query | < 10 ms | ~500-1000 ms | ~20-50 ms |

**Conclusion:** CSV performance degrades significantly at 200x scale, especially for complex queries.

---

## Migration Strategy

### Phase 1: CSV Storage (Current - Phase 2)
**Timeline:** Now through Phase 2 completion  
**Data Volume:** Current + 5-10 legacy seasons (~10-20x current)

**Why CSV is OK:**
- ✅ Data volume manageable (~2-4 MB total)
- ✅ Simple implementation
- ✅ No database setup required
- ✅ Fast enough for current needs

**Design Requirements:**
- ✅ Repository pattern abstraction
- ✅ Interface-based design
- ✅ No direct CSV access in domain/application layers
- ✅ Easy to swap implementation

### Phase 2: Migration Planning (Phase 3)
**Timeline:** During Phase 3 (Application Layer)  
**Preparation:** Design database schema, migration scripts

**Migration Triggers:**
- Data volume exceeds ~10 MB
- Performance issues observed
- Need for concurrent writes
- Complex query requirements

### Phase 3: Database Migration (Phase 4+)
**Timeline:** Before reaching full 10-year dataset  
**Target:** PostgreSQL or SQLite (recommendation: PostgreSQL)

**Migration Steps:**
1. Create database schema
2. Implement SQL repositories
3. Data migration script (CSV → DB)
4. Parallel running (CSV + DB)
5. Switch over
6. Remove CSV repositories

---

## Architecture Design: Storage Abstraction

### Repository Pattern for Easy Migration

```
┌─────────────────────────────────────────┐
│         Application Layer                │
│  (Uses Repository Interfaces Only)      │
└─────────────────┬───────────────────────┘
                   │
                   │ Uses Interface
                   │
┌─────────────────▼───────────────────────┐
│      Repository Interfaces              │
│  (Abstract, Storage-Agnostic)           │
│  - LeagueRepository                     │
│  - EventRepository                      │
│  - GameRepository                       │
└─────────────────┬───────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
┌───────▼────────┐  ┌─────────▼──────────┐
│ CSV Repos      │  │ SQL Repos          │
│ (Current)      │  │ (Future)           │
│                │  │                    │
│ PandasLeague   │  │ PostgresLeague     │
│ PandasEvent    │  │ PostgresEvent      │
│ PandasGame     │  │ PostgresGame       │
└────────────────┘  └────────────────────┘
```

### Key Design Principles

1. **Interface Segregation**
   - Repository interfaces in `domain` or `application` layer
   - No storage-specific details in interfaces
   - Storage-agnostic method signatures

2. **Dependency Inversion**
   - Application depends on interfaces, not implementations
   - DI container provides implementations
   - Easy to swap implementations

3. **Single Responsibility**
   - CSV repositories handle CSV-specific logic
   - SQL repositories handle SQL-specific logic
   - Mapping logic separated from storage logic

4. **Open/Closed Principle**
   - Add new storage backends without changing interfaces
   - Extend functionality without modifying existing code

---

## Repository Interface Design

### Example: EventRepository Interface

```python
# domain/repositories/event_repository.py (or application/repositories/)
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from domain.entities.event import Event
from domain.value_objects.season import Season

class EventRepository(ABC):
    """Abstract repository interface - storage agnostic"""
    
    @abstractmethod
    async def get_by_id(self, event_id: UUID) -> Optional[Event]:
        """Get event by ID - works for CSV or SQL"""
        pass
    
    @abstractmethod
    async def get_by_league_season(
        self, 
        league_season_id: UUID
    ) -> List[Event]:
        """Get all events for a league season"""
        pass
    
    @abstractmethod
    async def get_by_week(
        self,
        league_season_id: UUID,
        week: int
    ) -> List[Event]:
        """Get events for a specific week"""
        pass
    
    @abstractmethod
    async def add(self, event: Event) -> Event:
        """Add new event - implementation handles CSV or SQL"""
        pass
    
    @abstractmethod
    async def update(self, event: Event) -> Event:
        """Update existing event"""
        pass
    
    @abstractmethod
    async def delete(self, event_id: UUID) -> None:
        """Delete event"""
        pass
```

### CSV Implementation

```python
# infrastructure/persistence/repositories/csv/event_repository.py
from domain.repositories.event_repository import EventRepository
from infrastructure.persistence.adapters.data_adapter import DataAdapter
from infrastructure.persistence.mappers.event_mapper import EventMapper

class PandasEventRepository(EventRepository):
    """CSV-based implementation using Pandas"""
    
    def __init__(self, data_adapter: DataAdapter, mapper: EventMapper):
        self._adapter = data_adapter
        self._mapper = mapper
    
    async def get_by_id(self, event_id: UUID) -> Optional[Event]:
        # Load CSV, filter, map to domain
        df = self._adapter.get_event_data()
        row = df[df['id'] == str(event_id)]
        if row.empty:
            return None
        return self._mapper.to_domain(row.iloc[0])
    
    async def add(self, event: Event) -> Event:
        # Append to CSV file
        df = self._adapter.get_event_data()
        new_row = self._mapper.to_dataframe(event)
        df = pd.concat([df, new_row], ignore_index=True)
        self._adapter.save_event_data(df)
        return event
```

### SQL Implementation (Future)

```python
# infrastructure/persistence/repositories/sql/event_repository.py
from domain.repositories.event_repository import EventRepository
from sqlalchemy.orm import Session
from infrastructure.persistence.mappers.event_mapper import EventMapper

class PostgresEventRepository(EventRepository):
    """PostgreSQL-based implementation"""
    
    def __init__(self, session: Session, mapper: EventMapper):
        self._session = session
        self._mapper = mapper
    
    async def get_by_id(self, event_id: UUID) -> Optional[Event]:
        # Query database, map to domain
        db_event = self._session.query(EventModel).filter_by(id=event_id).first()
        if not db_event:
            return None
        return self._mapper.to_domain(db_event)
    
    async def add(self, event: Event) -> Event:
        # Insert into database
        db_event = self._mapper.to_db(event)
        self._session.add(db_event)
        self._session.commit()
        return event
```

---

## Migration Checklist

### Pre-Migration (Phase 2)
- [x] Design repository interfaces (storage-agnostic)
- [ ] Implement CSV repositories
- [ ] Create data mapper interfaces
- [ ] Document CSV schema
- [ ] Test CSV repositories thoroughly

### Migration Preparation (Phase 3)
- [ ] Design database schema (SQL)
- [ ] Create migration scripts (CSV → SQL)
- [ ] Implement SQL repositories
- [ ] Create parallel running capability
- [ ] Test data migration script

### Migration Execution (Phase 4)
- [ ] Run data migration (CSV → SQL)
- [ ] Verify data integrity
- [ ] Switch DI container to SQL repositories
- [ ] Monitor performance
- [ ] Remove CSV repositories (optional)

---

## Recommendations

### Immediate (Phase 2)
1. ✅ **Use CSV files** - Feasible for current + legacy seasons
2. ✅ **Design repository interfaces** - Storage-agnostic
3. ✅ **Implement CSV repositories** - With proper abstraction
4. ✅ **Create mapper layer** - Domain ↔ CSV conversion

### Short-term (Phase 3)
1. ⚠️ **Monitor performance** - Watch for degradation
2. ⚠️ **Plan database schema** - Design SQL tables
3. ⚠️ **Create migration scripts** - CSV → SQL conversion

### Long-term (Phase 4+)
1. 🎯 **Migrate to PostgreSQL** - Before reaching full 10-year dataset
2. 🎯 **Implement SQL repositories** - Using same interfaces
3. 🎯 **Switch via DI container** - Minimal code changes

---

## Database Choice Recommendation

### Option 1: PostgreSQL (Recommended)
**Pros:**
- ✅ Production-grade relational database
- ✅ Excellent performance at scale
- ✅ ACID transactions
- ✅ Complex queries and indexing
- ✅ Concurrent access support
- ✅ Industry standard

**Cons:**
- ⚠️ Requires database server
- ⚠️ More setup complexity

**Best for:** Production, long-term scalability

### Option 2: SQLite
**Pros:**
- ✅ No server required (file-based)
- ✅ Easy setup
- ✅ ACID transactions
- ✅ Good performance for moderate data

**Cons:**
- ⚠️ Limited concurrent writes
- ⚠️ File-based (similar to CSV in some ways)

**Best for:** Development, small deployments

### Recommendation: **PostgreSQL**
- Better long-term scalability
- Industry standard
- Better concurrent access
- More features (JSON, full-text search, etc.)

---

## Performance Benchmarks (Estimated)

### CSV Performance (200x Scale)
- **Simple query:** 50-100 ms
- **Complex query:** 500-1000 ms
- **Write operation:** 50-100 ms
- **Concurrent writes:** ❌ Not supported

### SQL Performance (200x Scale)
- **Simple query:** 1-2 ms (indexed)
- **Complex query:** 20-50 ms (indexed)
- **Write operation:** 1-2 ms
- **Concurrent writes:** ✅ Supported

**Conclusion:** SQL provides 10-50x performance improvement at scale.

---

## Implementation Plan

### Week 4: Repository Interfaces
- Design storage-agnostic interfaces
- Document interface contracts
- Create mapper interfaces

### Week 5: CSV Repositories
- Implement CSV repositories
- Create CSV mappers
- Test with current data

### Week 6: Unit of Work
- Add transaction support (for future SQL)
- Document migration path

### Future: SQL Migration
- Design database schema
- Implement SQL repositories
- Create migration scripts
- Switch via DI container

---

## Conclusion

✅ **CSV files are feasible for Phase 2** (current + legacy seasons)  
✅ **Repository pattern enables easy migration**  
⚠️ **Plan migration before reaching full 10-year dataset**  
🎯 **PostgreSQL recommended for long-term scalability**

**Key Success Factor:** Proper abstraction layer (Repository pattern) makes migration seamless.

---

**Next Steps:**
1. Design repository interfaces (storage-agnostic)
2. Implement CSV repositories
3. Create mapper layer
4. Document migration path

