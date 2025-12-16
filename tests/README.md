# Test Suite - League Analyzer v2

## Overview

Comprehensive test suite for the League Analyzer v2 domain models using pytest.

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── domain/
│   ├── test_value_objects_*.py   # Value object tests
│   ├── test_entities_*.py         # Entity tests
│   └── test_domain_services_*.py  # Domain service tests
└── README.md                      # This file
```

## Running Tests

### Run All Tests
```bash
pytest
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

### Run with Coverage Report
```bash
pytest --cov=domain --cov-report=term-missing
```

## Test Coverage

Current coverage targets:
- **Value Objects**: 100% coverage
- **Entities**: 100% coverage
- **Domain Services**: 100% coverage
- **Overall**: Minimum 80% (enforced by pytest.ini)

## Test Categories

### Unit Tests (`@pytest.mark.unit`)
Fast, isolated tests for individual components.

### Integration Tests (`@pytest.mark.integration`)
Tests that verify components work together.

### Domain Tests (`@pytest.mark.domain`)
Tests specific to the domain layer.

## Writing New Tests

### Test Naming Convention
- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<description>`

### Example Test Structure
```python
import pytest
from domain.value_objects.score import Score

class TestScore:
    """Test cases for Score value object."""
    
    def test_create_valid_score(self):
        """Test creating a valid score."""
        score = Score(200.0)
        assert score.value == 200.0
    
    @pytest.mark.parametrize("value,expected", [
        (100.0, 100.0),
        (200.0, 200.0),
        (300.0, 300.0),
    ])
    def test_valid_score_values(self, value, expected):
        """Test various valid score values."""
        score = Score(value)
        assert score.value == expected
```

### Using Fixtures
```python
def test_with_fixture(sample_score):
    """Test using a fixture."""
    assert sample_score.value == 200.0
```

### Parametrized Tests
```python
@pytest.mark.parametrize("input,expected", [
    (100, 100),
    (200, 200),
])
def test_multiple_values(input, expected):
    assert input == expected
```

## Continuous Integration

Tests should be run:
- Before committing code
- In CI/CD pipeline
- Before merging pull requests

## Coverage Reports

Coverage reports are generated in:
- **Terminal**: `--cov-report=term-missing`
- **HTML**: `htmlcov/index.html`
- **XML**: `coverage.xml` (for CI tools)

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Clear Names**: Test names should describe what they test
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Test Edge Cases**: Include boundary conditions
5. **Test Error Cases**: Verify exceptions are raised correctly
6. **Use Fixtures**: Share common setup code
7. **Parametrize**: Test multiple similar cases efficiently

## Regression Testing

All tests serve as regression tests. When a bug is found:
1. Write a test that reproduces the bug
2. Fix the bug
3. Verify the test passes
4. Ensure all other tests still pass

