# Development Manifesto - Summary

## The Core Principles

### 1. Architecture
- **Clean Architecture**: Domain → Application → Infrastructure → Presentation
- **Domain-Driven Design**: Rich domain models with business logic
- **CQRS**: Separate commands and queries
- **Dependency Injection**: No globals, no singletons
- **Event-Driven**: Use domain events for side effects

### 2. Testing
- **TDD**: Write tests first (Red → Green → Refactor)
- **Coverage**: Domain 100%, Application 90%+, Infrastructure 80%+
- **All tests are regression tests**

### 3. Logging
- **NO `print()` statements** - Use logging only
- **Multiple levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Multiple channels**: Console and file

### 4. Code Quality
- **Type hints**: Always use type annotations
- **Single Responsibility**: One reason to change
- **DRY**: Don't repeat yourself
- **KISS**: Keep it simple

### 5. Development Workflow
- **Think before coding**: Understand the problem
- **Write tests first**: TDD approach
- **Run tests frequently**: After each change
- **Check before commit**: Tests pass, coverage met, no print()

## The Absolute Rules

1. ❌ **NO `print()`** → ✅ Use `logger.info()`
2. ✅ **Write tests first** → TDD
3. ✅ **Domain logic in domain** → Not in services
4. ✅ **Dependencies inward** → Clean Architecture
5. ✅ **Type hints always** → Every function
6. ✅ **Validate input** → Never trust user input
7. ✅ **Log exceptions** → Use `logger.exception()`
8. ✅ **Tests before commit** → `pytest` must pass

## Quick Checklist

Before committing:
- [ ] Tests pass (`pytest`)
- [ ] Coverage met (`pytest --cov`)
- [ ] No `print()` statements
- [ ] Logging in place
- [ ] Type hints added
- [ ] Domain logic in domain
- [ ] Dependencies injected
- [ ] Input validated

## Resources

- **Full Manifesto**: [DEVELOPMENT_MANIFESTO.md](DEVELOPMENT_MANIFESTO.md)
- **Quick Reference**: [MANIFESTO_QUICK_REFERENCE.md](MANIFESTO_QUICK_REFERENCE.md)
- **Architecture**: [ARCHITECTURE_DESIGN.md](ARCHITECTURE_DESIGN.md)
- **Testing**: [TESTING_SETUP.md](TESTING_SETUP.md)
- **Logging**: [LOGGING_STRATEGY.md](LOGGING_STRATEGY.md)

