# TDD Approach for Repository Implementations

**Date:** 2025-12-21  
**Approach:** Test-Driven Development (Red → Green → Refactor)

---

## TDD Process

### Step 1: Red - Write Failing Tests
1. Write tests for repository interface contracts
2. Write tests for CSV repository implementations
3. Run tests - they should fail (no implementation yet)

### Step 2: Green - Implement to Pass Tests
1. Create CSV mapper layer
2. Implement CSV repositories
3. Run tests - they should pass

### Step 3: Refactor - Improve Code
1. Refactor while keeping tests green
2. Optimize performance
3. Improve code quality

---

## Test Structure

### 1. Repository Interface Contract Tests
**Location:** `tests/domain/test_repositories/`

Test that interfaces are properly defined:
- Interface methods exist
- Method signatures are correct
- Type hints are present

### 2. CSV Repository Implementation Tests
**Location:** `tests/infrastructure/test_repositories_csv/`

Test CSV repository implementations:
- CRUD operations
- Query methods
- Error handling
- Data mapping

---

## Test Plan

### For Each Repository:

1. **Contract Tests** (test_repositories_contracts.py)
   - Verify interface exists
   - Verify all methods are abstract
   - Verify method signatures

2. **Implementation Tests** (test_repositories_csv_*.py)
   - `test_get_by_id` - Get entity by ID
   - `test_get_by_id_not_found` - Return None when not found
   - `test_get_all` - Get all entities
   - `test_add` - Add new entity
   - `test_update` - Update existing entity
   - `test_update_not_found` - Raise error when updating non-existent
   - `test_delete` - Delete entity
   - `test_delete_not_found` - Raise error when deleting non-existent
   - `test_exists` - Check if entity exists
   - `test_query_methods` - Test domain-specific queries

---

## Implementation Order (TDD)

1. **EventRepository** (most complex, many relationships)
   - Write tests first
   - Implement CSV repository
   - Implement mapper

2. **LeagueSeasonRepository**
   - Write tests first
   - Implement CSV repository
   - Implement mapper

3. **TeamSeasonRepository**
   - Write tests first
   - Implement CSV repository
   - Implement mapper

4. **GameRepository**
   - Write tests first
   - Implement CSV repository
   - Implement mapper

5. **PlayerRepository**
   - Write tests first
   - Implement CSV repository
   - Implement mapper

6. **LeagueRepository**
   - Write tests first
   - Implement CSV repository
   - Implement mapper

7. **TeamRepository**
   - Write tests first
   - Implement CSV repository
   - Implement mapper

---

## Test Data Strategy

### Use Fixtures
- Create test data fixtures
- Use existing CSV files for reference
- Create minimal test datasets

### Mock DataAdapter
- Mock DataAdapter for unit tests
- Use real DataAdapter for integration tests

---

## Coverage Goals

- **Repository Interfaces:** 100% (all methods tested)
- **CSV Repositories:** 90%+ coverage
- **Mappers:** 100% coverage (critical conversion logic)

---

**Let's follow TDD and write tests first!** 🎳

