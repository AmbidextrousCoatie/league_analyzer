# Week 4: Repository Interfaces - Complete

**Date:** 2025-12-21  
**Status:** ✅ Complete

---

## Summary

All repository interfaces have been created in the domain layer. These interfaces are storage-agnostic and will work for both CSV (current) and SQL (future) implementations.

---

## ✅ Completed

### Repository Interfaces Created

1. **BaseRepository** (`domain/repositories/base_repository.py`)
   - Common CRUD operations
   - Generic type support
   - Storage-agnostic interface

2. **EventRepository** (`domain/repositories/event_repository.py`)
   - Query methods: `get_by_league_season`, `get_by_week`, `get_by_status`, `get_by_date_range`
   - CRUD operations

3. **LeagueSeasonRepository** (`domain/repositories/league_season_repository.py`)
   - Query methods: `get_by_league`, `get_by_season`, `get_by_league_and_season`
   - CRUD operations

4. **TeamSeasonRepository** (`domain/repositories/team_season_repository.py`)
   - Query methods: `get_by_league_season`, `get_by_club`, `get_by_vacancy_status`
   - CRUD operations

5. **GameRepository** (`domain/repositories/game_repository.py`)
   - Query methods: `get_by_event`, `get_by_league`, `get_by_week`, `get_by_team`, `get_by_date_range`
   - CRUD operations

6. **PlayerRepository** (`domain/repositories/player_repository.py`)
   - Query methods: `get_by_club`, `get_by_team`, `find_by_name`
   - CRUD operations

7. **LeagueRepository** (`domain/repositories/league_repository.py`)
   - Query methods: `get_by_season`, `find_by_name`
   - CRUD operations

8. **TeamRepository** (`domain/repositories/team_repository.py`)
   - Query methods: `get_by_league`, `find_by_name`
   - CRUD operations

---

## Design Decisions

### Interface Location
- **Location:** `domain/repositories/`
- **Rationale:** Repositories define what the domain needs from persistence, so interfaces belong in the domain layer

### Storage-Agnostic Design
- All interfaces contain **no storage-specific details**
- Methods work identically for CSV and SQL implementations
- Application layer depends on interfaces, not implementations

### Query Methods
- Each repository includes domain-specific query methods
- Methods are designed based on actual use cases
- Filtering, sorting, and complex queries supported

---

## Files Created

```
domain/repositories/
├── __init__.py                    # Exports all interfaces
├── base_repository.py             # Base CRUD interface
├── event_repository.py            # Event queries
├── league_season_repository.py    # LeagueSeason queries
├── team_season_repository.py     # TeamSeason queries
├── game_repository.py             # Game queries
├── player_repository.py           # Player queries
├── league_repository.py           # League queries
└── team_repository.py             # Team queries
```

---

## Interface Structure

### Common Pattern

All repositories follow this pattern:

```python
class EntityRepository(ABC):
    # Basic CRUD
    async def get_by_id(id: UUID) -> Optional[Entity]
    async def get_all() -> List[Entity]
    async def add(entity: Entity) -> Entity
    async def update(entity: Entity) -> Entity
    async def delete(id: UUID) -> None
    async def exists(id: UUID) -> bool
    
    # Domain-specific queries
    async def get_by_xxx(...) -> List[Entity]
    async def find_by_xxx(...) -> List[Entity]
```

---

## Next Steps: Week 5

### CSV Repository Implementations

1. **Create CSV Repositories**
   - Implement all interfaces using Pandas DataFrames
   - Location: `infrastructure/persistence/repositories/csv/`

2. **Create Mapper Layer**
   - Domain ↔ DataFrame conversion
   - Location: `infrastructure/persistence/mappers/csv/`

3. **Update Data Adapter**
   - Extend DataAdapter interface for write operations
   - Add methods for saving DataFrames

4. **DI Container Configuration**
   - Configure repositories in DI container
   - Wire up dependencies

---

## Migration Path (Future)

### SQL Migration (Post-Launch)

When ready to migrate to SQL:

1. **Create SQL Repositories**
   - Implement same interfaces using SQLAlchemy
   - Location: `infrastructure/persistence/repositories/sql/`

2. **Create SQL Mappers**
   - Domain ↔ SQL model conversion
   - Location: `infrastructure/persistence/mappers/sql/`

3. **Update DI Container**
   - Change repository providers from CSV to SQL
   - No application code changes needed!

---

## Testing Strategy

### Interface Tests (Contract Tests)
- Test that interfaces are properly defined
- Verify method signatures
- Check type hints

### Implementation Tests (Week 5)
- Test CSV repository implementations
- Test mapper conversions
- Test CRUD operations
- Test query methods

---

## Key Benefits

✅ **Storage-Agnostic** - Same interface for CSV and SQL  
✅ **Testable** - Easy to mock repositories  
✅ **Maintainable** - Clear separation of concerns  
✅ **Flexible** - Easy to add new query methods  
✅ **Future-Proof** - Ready for SQL migration  

---

## References

- Repository Migration Design: `docs/planning/REPOSITORY_MIGRATION_DESIGN.md`
- Storage Scalability: `docs/planning/STORAGE_SCALABILITY_ANALYSIS.md`
- Current Status: `docs/pm/CURRENT_STATUS.md`

---

**Week 4 Complete! Ready for Week 5: CSV Repository Implementations** 🎳

