# Testing Framework Setup - League Analyzer v2

## Overview

Comprehensive test suite for League Analyzer v2 using **pytest** with coverage reporting. The test framework is designed to be an integral part of the development cycle, ensuring code quality and preventing regressions.

## Test Framework: pytest

**pytest** was chosen as the testing framework because it:
- Provides excellent test discovery and execution
- Supports fixtures for test setup/teardown
- Enables parametrized tests for testing multiple scenarios
- Integrates seamlessly with coverage tools
- Has a large ecosystem of plugins
- Produces clear, readable test output

## Installation

```bash
pip install pytest pytest-cov pytest-asyncio pytest-mock
```

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── domain/
│   ├── test_value_objects_*.py   # Value object tests
│   ├── test_entities_*.py         # Entity tests
│   └── test_domain_services_*.py  # Domain service tests
└── README.md                      # Test documentation
```

## Running Tests

### Run All Tests
```bash
pytest
# or
python -m pytest
```

### Run with Coverage
```bash
pytest --cov=domain --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/domain/test_value_objects_score.py
```

### Run Specific Test Class
```bash
pytest tests/domain/test_value_objects_score.py::TestScore
```

### Run Specific Test Method
```bash
pytest tests/domain/test_value_objects_score.py::TestScore::test_create_valid_score
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Without Coverage (Faster)
```bash
pytest --no-cov
```

## Test Coverage

### Current Status
- **138 tests** covering domain models
- **All tests passing** ✅
- Coverage includes:
  - Value Objects (Score, Points, Season, Handicap, GameResult, HandicapSettings)
  - Entities (Team, Player, League, Game)
  - Domain Services (HandicapCalculator)

### Coverage Reports

Coverage reports are generated in multiple formats:
- **Terminal**: `--cov-report=term-missing` (shows missing lines)
- **HTML**: `htmlcov/index.html` (interactive HTML report)
- **XML**: `coverage.xml` (for CI/CD integration)

### Viewing HTML Coverage Report
```bash
# Generate report
pytest --cov=domain --cov-report=html

# Open in browser (Windows)
start htmlcov/index.html

# Open in browser (Linux/Mac)
open htmlcov/index.html
```

## Test Categories

Tests are organized by domain layer:

### Value Objects (`test_value_objects_*.py`)
- **Score**: Validation, arithmetic operations, comparisons
- **Points**: Validation, arithmetic operations
- **Season**: Format validation, year extraction, equality
- **Handicap**: Validation, max capping, application to scores
- **GameResult**: Position validation, handicap integration
- **HandicapSettings**: Configuration validation

### Entities (`test_entities_*.py`)
- **Team**: Creation, league assignment, name updates
- **Player**: Team assignment, handicap tracking per season
- **League**: Team management, handicap settings
- **Game**: Result management, validation

### Domain Services (`test_domain_services_*.py`)
- **HandicapCalculator**: 
  - Cumulative average calculation
  - Moving window calculation
  - Handicap capping
  - Recalculation logic

## Test Patterns

### Using Fixtures

Fixtures are defined in `conftest.py` and can be used in any test:

```python
def test_with_fixture(sample_score, sample_handicap_settings):
    """Test using fixtures."""
    assert sample_score.value == 200.0
    assert sample_handicap_settings.enabled is True
```

### Parametrized Tests

Test multiple scenarios efficiently:

```python
@pytest.mark.parametrize("value,expected", [
    (100.0, 100.0),
    (200.0, 200.0),
    (300.0, 300.0),
])
def test_valid_score_values(value, expected):
    """Test various valid score values."""
    score = Score(value)
    assert score.value == expected
```

### Testing Exceptions

Verify that exceptions are raised correctly:

```python
def test_create_negative_score_raises_error(self):
    """Test that negative scores raise InvalidScore."""
    with pytest.raises(InvalidScore, match="cannot be negative"):
        Score(-10.0)
```

## Continuous Integration

### Pre-commit Checklist
- [ ] Run all tests: `pytest`
- [ ] Check coverage: `pytest --cov=domain --cov-report=term-missing`
- [ ] Ensure no linter errors
- [ ] Verify all tests pass

### CI/CD Integration

The test suite is designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install pytest pytest-cov
    pytest --cov=domain --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Regression Testing

All tests serve as regression tests. When a bug is found:

1. **Write a failing test** that reproduces the bug
2. **Fix the bug** in the implementation
3. **Verify the test passes**
4. **Run all tests** to ensure no regressions

## Best Practices

### Test Organization
- One test file per module/class
- Group related tests in test classes
- Use descriptive test names: `test_<what>_<expected_behavior>`

### Test Isolation
- Each test should be independent
- Use fixtures for shared setup
- Avoid test interdependencies

### Test Coverage Goals
- **Value Objects**: 100% coverage (immutable, critical logic)
- **Entities**: 100% coverage (business logic)
- **Domain Services**: 100% coverage (calculation logic)
- **Overall**: Minimum 80% coverage (enforced in CI)

### Test Quality
- Test both happy paths and error cases
- Test edge cases and boundary conditions
- Use parametrized tests for similar scenarios
- Keep tests readable and maintainable

## Common Commands

```bash
# Quick test run
pytest

# Full test run with coverage
pytest --cov=domain --cov-report=html

# Run only failing tests
pytest --lf

# Run last failed tests first
pytest --ff

# Run tests matching pattern
pytest -k "test_score"

# Run tests with markers
pytest -m unit

# Run tests in parallel (requires pytest-xdist)
pytest -n auto
```

## Troubleshooting

### Import Errors
If you see `ModuleNotFoundError`, ensure:
- Project root is in Python path (handled by `conftest.py`)
- All dependencies are installed
- Virtual environment is activated

### Coverage Issues
- Coverage may be low initially as we build out tests
- Focus on domain layer first (highest priority)
- Use `--cov-fail-under=0` during development

### Test Discovery
- Ensure test files start with `test_` or end with `_test.py`
- Test classes should start with `Test`
- Test methods should start with `test_`

## Next Steps

1. **Add integration tests** for application layer
2. **Add infrastructure tests** for persistence layer
3. **Add API tests** for presentation layer
4. **Set up CI/CD** with automated test runs
5. **Increase coverage** to 80%+ across all layers

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Test-Driven Development (TDD)](https://en.wikipedia.org/wiki/Test-driven_development)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

