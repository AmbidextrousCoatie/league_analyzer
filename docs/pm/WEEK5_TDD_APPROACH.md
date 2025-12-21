# Week 5: TDD Approach for Repository Implementations

**Date:** 2025-12-21  
**Approach:** Test-Driven Development (Red → Green → Refactor)  
**Status:** 🔴 RED Phase - Tests Written, Implementation Pending

---

## TDD Process

### ✅ Step 1: RED - Write Failing Tests (COMPLETE)

We've written comprehensive tests **before** implementing the repositories:

1. **Test Structure Created**
   - `tests/infrastructure/test_repositories_csv/` - Test directory
   - `tests/infrastructure/conftest.py` - Test fixtures
   - `test_event_repository.py` - Complete test suite for EventRepository

2. **Tests Written for EventRepository**
   - ✅ `test_get_by_id_returns_event_when_exists`
   - ✅ `test_get_by_id_returns_none_when_not_exists`
   - ✅ `test_get_all_returns_all_events`
   - ✅ `test_add_creates_new_event`
   - ✅ `test_update_modifies_existing_event`
   - ✅ `test_update_raises_error_when_not_exists`
   - ✅ `test_delete_removes_event`
   - ✅ `test_delete_raises_error_when_not_exists`
   - ✅ `test_exists_returns_true_when_event_exists`
   - ✅ `test_exists_returns_false_when_event_not_exists`
   - ✅ `test_get_by_league_season_returns_filtered_events`
   - ✅ `test_get_by_week_returns_filtered_events`
   - ✅ `test_get_by_status_returns_filtered_events`
   - ✅ `test_get_by_date_range_returns_filtered_events`

3. **Test Results**
   - All 14 tests are **SKIPPED** (expected - no implementation yet)
   - Tests are ready to run once implementation is complete

---

## Next Steps: GREEN Phase

### Step 2: GREEN - Implement to Pass Tests

Now we implement the repositories to make tests pass:

1. **Create CSV Mapper Layer**
   - `infrastructure/persistence/mappers/csv/event_mapper.py`
   - Domain ↔ DataFrame conversion

2. **Implement CSV Repository**
   - `infrastructure/persistence/repositories/csv/event_repository.py`
   - Implement all methods to pass tests

3. **Extend DataAdapter**
   - Add write methods to DataAdapter interface
   - Implement in PandasDataAdapter

4. **Run Tests**
   - Tests should pass (GREEN)
   - Fix any issues until all tests pass

### Step 3: REFACTOR - Improve Code

After tests pass:
- Refactor for clarity
- Optimize performance
- Improve code quality
- Keep tests green

---

## Test Coverage Goals

- **EventRepository Tests:** 14 tests covering all methods
- **Coverage Target:** 90%+ for CSV repositories
- **Mapper Coverage:** 100% (critical conversion logic)

---

## TDD Benefits Demonstrated

✅ **Tests Drive Design** - Tests define the interface contract  
✅ **Documentation** - Tests serve as usage examples  
✅ **Confidence** - Know exactly what to implement  
✅ **Regression Prevention** - Tests catch future bugs  
✅ **Refactoring Safety** - Tests ensure refactoring doesn't break functionality  

---

## Implementation Order (TDD)

Following TDD, we'll implement repositories one at a time:

1. **EventRepository** (Most complex - started)
   - ✅ Tests written
   - ⏳ Implementation next

2. **LeagueSeasonRepository**
   - ⏳ Write tests first
   - ⏳ Then implement

3. **TeamSeasonRepository**
   - ⏳ Write tests first
   - ⏳ Then implement

4. **GameRepository**
   - ⏳ Write tests first
   - ⏳ Then implement

5. **PlayerRepository**
   - ⏳ Write tests first
   - ⏳ Then implement

6. **LeagueRepository**
   - ⏳ Write tests first
   - ⏳ Then implement

7. **TeamRepository**
   - ⏳ Write tests first
   - ⏳ Then implement

---

## Current Status

**Phase:** 🔴 RED  
**Tests Written:** ✅ EventRepository (14 tests)  
**Implementation:** ⏳ Pending  
**Next:** Implement EventRepository to make tests pass  

---

## References

- TDD Plan: `docs/pm/TDD_REPOSITORY_IMPLEMENTATION.md`
- Development Manifesto: `docs/standards/DEVELOPMENT_MANIFESTO.md`
- Test File: `tests/infrastructure/test_repositories_csv/test_event_repository.py`

---

**Following TDD: Tests First, Implementation Next!** 🎳

