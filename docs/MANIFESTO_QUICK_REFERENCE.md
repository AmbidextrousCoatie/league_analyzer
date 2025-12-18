# Manifesto Quick Reference

## The Absolute Rules

1. ❌ **NO `print()`** → ✅ Use `logger.info()`
2. ✅ **Write tests first** → TDD: Red → Green → Refactor
3. ✅ **Domain logic in domain** → Not in services/controllers
4. ✅ **Dependencies inward** → Domain has no external dependencies
5. ✅ **Type hints always** → Every function has types
6. ✅ **Validate input** → Never trust user input
7. ✅ **Log exceptions** → Use `logger.exception()`
8. ✅ **Tests before commit** → `pytest` must pass

## Quick Checklist

- [ ] Tests pass
- [ ] Coverage met
- [ ] No `print()`
- [ ] Logging in place
- [ ] Type hints added
- [ ] Domain logic in domain
- [ ] Dependencies injected
- [ ] Input validated

## Common Patterns

### Logging
```python
from infrastructure.logging import get_logger
logger = get_logger(__name__)
logger.info(f"Message: {context}")
```

### Testing
```python
def test_feature():
    # Arrange
    # Act
    # Assert
    assert result == expected
```

### Domain Logic
```python
# ✅ Good: Logic in domain
class Game:
    def add_result(self, result):
        self._validate_result(result)
        self.results.append(result)

# ❌ Bad: Logic in service
class GameService:
    def add_result(self, game, result):
        if len(game.results) > 4:  # Domain logic!
            raise Error()
```

See `docs/DEVELOPMENT_MANIFESTO.md` for complete details.

