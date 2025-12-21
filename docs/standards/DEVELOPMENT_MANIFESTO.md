# Development Manifesto

## Our Principles

This manifesto defines the core principles, practices, and standards for developing League Analyzer v2. All contributors should follow these guidelines to ensure code quality, maintainability, and consistency.

---

## 1. Architecture Principles

### 1.1 Clean Architecture

We follow **Clean Architecture** principles:

- **Domain Layer** (innermost): Pure business logic, no dependencies on external frameworks
- **Application Layer**: Use cases, orchestration, application-specific logic
- **Infrastructure Layer**: External concerns (database, file system, APIs)
- **Presentation Layer**: API endpoints, UI, external interfaces

**Rule**: Dependencies point inward. Domain has no dependencies on other layers.

### 1.2 Domain-Driven Design (DDD)

- **Rich Domain Models**: Entities contain business logic, not just data
- **Value Objects**: Immutable objects representing domain concepts (Score, Points, Season)
- **Domain Services**: Stateless services for complex domain logic (HandicapCalculator)
- **Domain Events**: Use events for side effects and cross-cutting concerns
- **Domain Exceptions**: Domain-specific exceptions, not generic ones

**Rule**: Business logic belongs in the domain layer, not in services or controllers.

### 1.3 CQRS (Command Query Responsibility Segregation)

- **Commands**: Operations that change state (CreateGame, UpdatePlayer)
- **Queries**: Operations that read data (GetLeagueStandings, GetPlayerStats)
- **Separate Handlers**: Command handlers vs query handlers
- **Different Models**: Read models can differ from write models

**Rule**: Separate read and write operations at the application layer.

### 1.4 Dependency Injection (DI)

- **Constructor Injection**: Dependencies injected via constructors
- **DI Container**: Use `dependency-injector` for managing dependencies
- **Interface-Based**: Depend on abstractions, not concrete implementations
- **Testability**: Easy to mock dependencies in tests

**Rule**: No global state or singletons. Use DI for all dependencies.

### 1.5 Event-Driven Architecture

- **Domain Events**: Use events for side effects (GameCreated, PlayerUpdated)
- **Event Bus**: Centralized event publishing and handling
- **Loose Coupling**: Components communicate via events, not direct calls

**Rule**: Use domain events for cross-cutting concerns and side effects.

---

## 2. Testing Principles

### 2.1 Test-Driven Development (TDD)

**We follow TDD:**

1. **Red**: Write a failing test first
2. **Green**: Write minimal code to make it pass
3. **Refactor**: Improve code while keeping tests green

**Rule**: Write tests before implementation. Tests drive design.

### 2.2 Test Coverage

- **Domain Layer**: Target **100% coverage** (critical business logic)
- **Application Layer**: Target **90%+ coverage**
- **Infrastructure Layer**: Target **80%+ coverage**
- **Overall**: Minimum **80% coverage**

**Rule**: No code goes to production without tests.

### 2.3 Test Organization

- **Unit Tests**: Fast, isolated tests for individual components
- **Integration Tests**: Tests that verify components work together
- **Test Structure**: Mirror source structure (`tests/domain/`, `tests/application/`)
- **Test Naming**: `test_<what>_<expected_behavior>`

**Rule**: Tests should be fast, isolated, and readable.

### 2.4 Regression Testing

- **All Tests Are Regression Tests**: Every test prevents future bugs
- **Bug Fixes**: When a bug is found, write a test first, then fix
- **Continuous Testing**: Run tests before committing

**Rule**: If a bug is found, write a test that reproduces it, then fix it.

---

## 3. Logging Principles

### 3.1 No Print Statements

**Absolute Rule**: **NO `print()` statements anywhere in the codebase.**

All output must go through the logging system.

### 3.2 Logging Usage

```python
from infrastructure.logging import get_logger

logger = get_logger(__name__)
logger.info("Application started")
logger.debug("Detailed debug info")
logger.error("Error occurred")
logger.exception("Exception with traceback")
```

**Rule**: Use `get_logger(__name__)` in every module that needs logging.

### 3.3 Log Levels

- **DEBUG**: Detailed information for diagnosing problems (development only)
- **INFO**: General informational messages about application flow
- **WARNING**: Something unexpected happened, but application continues
- **ERROR**: Error occurred, but application can continue
- **CRITICAL**: Serious error that may cause application to stop

**Rule**: Use appropriate log levels. Include context in messages.

### 3.4 Logging Best Practices

- ✅ Include context: `logger.info(f"Creating game: id={game_id}")`
- ✅ Use `logger.exception()` for exceptions (includes traceback)
- ✅ Don't log sensitive information (passwords, tokens)
- ❌ Never use `print()`
- ❌ Don't use wrong log levels

**Rule**: Logging should help diagnose issues, not create noise.

---

## 4. Code Quality Principles

### 4.1 Code Organization

- **Layered Structure**: Domain → Application → Infrastructure → Presentation
- **Single Responsibility**: Each class/function has one reason to change
- **DRY (Don't Repeat Yourself)**: Extract common logic into reusable components
- **KISS (Keep It Simple, Stupid)**: Prefer simple solutions over complex ones

**Rule**: Code should be easy to understand and maintain.

### 4.2 Naming Conventions

- **Classes**: PascalCase (`HandicapCalculator`, `GameResult`)
- **Functions/Methods**: snake_case (`calculate_handicap`, `get_player_stats`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_HANDICAP`, `DEFAULT_SEASON`)
- **Private Methods**: Leading underscore (`_calculate_average`, `_validate_input`)

**Rule**: Names should be descriptive and self-documenting.

### 4.3 Type Hints

- **Always Use Type Hints**: All functions should have type annotations
- **Return Types**: Always specify return types
- **Optional Types**: Use `Optional[T]` for nullable values
- **Generic Types**: Use generics for reusable code

**Rule**: Type hints improve code readability and catch errors early.

### 4.4 Documentation

- **Docstrings**: All public functions/classes should have docstrings
- **Google Style**: Use Google-style docstrings
- **Examples**: Include usage examples in complex functions
- **README Files**: Each major component should have a README

**Rule**: Code should be self-documenting, but documentation helps.

---

## 5. Development Workflow

### 5.1 Before Starting Work

1. **Understand Requirements**: Read and understand the task
2. **Write Tests First**: Follow TDD - write failing tests first
3. **Check Existing Code**: Look for similar patterns or code to reuse
4. **Plan Architecture**: Consider where code belongs (domain/application/infrastructure)

**Rule**: Think before coding. Understand the problem first.

### 5.2 During Development

1. **Write Tests**: Write tests as you develop
2. **Run Tests Frequently**: Run tests after each change
3. **Check Logging**: Ensure proper logging is in place
4. **Follow Patterns**: Use established patterns and conventions
5. **Keep It Simple**: Don't over-engineer

**Rule**: Develop incrementally. Small, tested changes.

### 5.3 Before Committing

1. **Run All Tests**: `pytest` must pass
2. **Check Coverage**: Ensure coverage targets are met
3. **Check Logging**: No `print()` statements
4. **Review Code**: Self-review for quality
5. **Update Documentation**: Update docs if needed

**Rule**: Never commit broken code or code without tests.

---

## 6. Domain Modeling Principles

### 6.1 Entities vs Value Objects

- **Entities**: Have identity, mutable, tracked by ID (Team, Player, League, Game)
- **Value Objects**: Immutable, compared by value (Score, Points, Season, Handicap)

**Rule**: Use value objects for concepts without identity. Use entities for things with identity.

### 6.2 Rich Domain Models

- **Business Logic in Domain**: Domain objects contain behavior, not just data
- **Anemic Models Are Bad**: Avoid data-only classes
- **Domain Invariants**: Enforce business rules in domain objects

**Rule**: Domain models should express business concepts, not just data structures.

### 6.3 Validation

- **Input Validation**: Validate at application layer (commands/queries)
- **Domain Validation**: Validate business rules in domain layer
- **Data Validation**: Validate data integrity at infrastructure layer

**Rule**: Validate early, validate often, but validate at the right layer.

---

## 7. Error Handling Principles

### 7.1 Exception Types

- **Domain Exceptions**: Domain-specific errors (`InvalidGameData`, `DuplicateGame`)
- **Application Exceptions**: Application-level errors (validation, authorization)
- **Infrastructure Exceptions**: Technical errors (database, network)

**Rule**: Use appropriate exception types for each layer.

### 7.2 Exception Handling

- **Fail Fast**: Validate early and fail fast
- **Don't Swallow Exceptions**: Log and re-raise or handle appropriately
- **Use Specific Exceptions**: Don't catch generic `Exception` unless necessary
- **Log Exceptions**: Always log exceptions with context

**Rule**: Exceptions should be meaningful and help diagnose issues.

---

## 8. Performance Principles

### 8.1 Optimization

- **Measure First**: Don't optimize prematurely
- **Profile Before Optimizing**: Identify bottlenecks first
- **Optimize Critical Paths**: Focus on code that runs frequently
- **Cache Wisely**: Use caching for expensive operations

**Rule**: Make it work, make it right, then make it fast.

### 8.2 Database Access

- **Repository Pattern**: Abstract database access
- **Query Optimization**: Optimize queries, not just code
- **Lazy Loading**: Load data when needed
- **Batch Operations**: Batch database operations when possible

**Rule**: Database access should be efficient and abstracted.

---

## 9. Security Principles

### 9.1 Input Validation

- **Validate All Input**: Never trust user input
- **Sanitize Input**: Clean input before processing
- **Type Validation**: Validate types and formats
- **Business Rule Validation**: Validate business rules

**Rule**: All input is untrusted until validated.

### 9.2 Sensitive Data

- **Don't Log Sensitive Data**: Never log passwords, tokens, or personal data
- **Encrypt Sensitive Data**: Encrypt data at rest and in transit
- **Secure Defaults**: Use secure defaults for configuration

**Rule**: Security is not optional. Handle sensitive data carefully.

---

## 10. Documentation Principles

### 10.1 Code Documentation

- **Docstrings**: All public APIs should have docstrings
- **Comments**: Explain "why", not "what"
- **README Files**: Major components should have READMEs
- **Architecture Docs**: Document architectural decisions

**Rule**: Documentation should help developers understand and use the code.

### 10.2 Decision Records

- **Document Decisions**: Record important architectural decisions
- **Explain Rationale**: Explain why decisions were made
- **Update Docs**: Keep documentation up to date

**Rule**: Future developers should understand why code is structured as it is.

---

## 11. Continuous Improvement

### 11.1 Code Reviews

- **Review All Code**: All code should be reviewed
- **Constructive Feedback**: Provide helpful, constructive feedback
- **Learn from Reviews**: Use reviews as learning opportunities

**Rule**: Code reviews improve code quality and share knowledge.

### 11.2 Refactoring

- **Refactor Regularly**: Don't let technical debt accumulate
- **Small Refactorings**: Prefer small, frequent refactorings
- **Tests First**: Refactor with tests to ensure correctness

**Rule**: Refactoring is part of development, not a separate activity.

---

## 12. Summary: The Rules

### The Absolute Rules

1. ✅ **NO `print()` statements** - Use logging
2. ✅ **Write tests first** - Follow TDD
3. ✅ **Domain logic in domain layer** - Not in services
4. ✅ **Dependencies point inward** - Clean Architecture
5. ✅ **Use type hints** - Always
6. ✅ **Validate input** - Always
7. ✅ **Log exceptions** - Always
8. ✅ **Run tests before commit** - Always
9. ✅ **DO NOT touch legacy code** - Never modify `league_analyzer_v1/` directory

### The Guidelines

- Prefer simple solutions over complex ones
- Write self-documenting code
- Follow established patterns
- Keep functions small and focused
- Use meaningful names
- Document important decisions

---

## 13. Quick Checklist

Before committing code, ensure:

- [ ] All tests pass (`pytest`)
- [ ] Coverage targets met (`pytest --cov`)
- [ ] No `print()` statements
- [ ] Proper logging in place
- [ ] Type hints added
- [ ] Docstrings added
- [ ] Code follows architecture principles
- [ ] Domain logic in domain layer
- [ ] Dependencies injected (no globals)
- [ ] Input validated
- [ ] Exceptions handled and logged
- [ ] No changes to `league_analyzer_v1/` directory

---

## 14. Resources

- **Architecture**: `docs/ARCHITECTURE_DESIGN.md`
- **Logging**: `docs/LOGGING_STRATEGY.md`
- **Testing**: `docs/TESTING_SETUP.md`
- **Refactoring Plan**: `docs/REFACTORING_STRATEGY_REVISED.md`

---

## Remember

> "Clean code is not written by following a set of rules. You don't become a software craftsman by learning a list of heuristics. Professionalism and craftsmanship come from values that drive disciplines." - Robert C. Martin

This manifesto provides the **disciplines**. The **values** come from caring about code quality, maintainability, and the developers who will work with this code in the future.

**Let's build something great, together.** 🚀

