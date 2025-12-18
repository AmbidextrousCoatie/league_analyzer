# Contributing to League Analyzer

Thank you for your interest in contributing! Please read this guide before submitting code.

## Getting Started

1. **Read the Manifesto**: Start with [Development Manifesto](docs/DEVELOPMENT_MANIFESTO.md)
2. **Understand Architecture**: Review [Architecture Design](docs/ARCHITECTURE_DESIGN.md)
3. **Set Up Environment**: Follow setup instructions in README
4. **Run Tests**: Ensure all tests pass before starting

## Development Process

### 1. Before Starting

- Read and understand the task/issue
- Check existing code for similar patterns
- Plan where your code belongs (domain/application/infrastructure)

### 2. Development

- **Write tests first** (TDD: Red → Green → Refactor)
- Follow architecture principles (Clean Architecture, DDD)
- Use logging (NO `print()` statements)
- Add type hints to all functions
- Keep code simple and focused

### 3. Before Committing

Run the checklist:

- [ ] All tests pass (`pytest`)
- [ ] Coverage targets met (`pytest --cov`)
- [ ] No `print()` statements
- [ ] Proper logging in place
- [ ] Type hints added
- [ ] Docstrings added
- [ ] Code follows architecture principles
- [ ] Domain logic in domain layer
- [ ] Dependencies injected (no globals)

### 4. Commit Message

Follow the commit message format (see `.gitmessage`):

```
<type>(<scope>): <subject>

<body>
```

## Code Standards

### Architecture

- **Domain Layer**: Pure business logic, no external dependencies
- **Application Layer**: Use cases, orchestration
- **Infrastructure Layer**: External concerns (database, APIs)
- **Presentation Layer**: API endpoints, UI

### Testing

- **TDD**: Write tests first
- **Coverage**: Domain 100%, Application 90%+, Infrastructure 80%+
- **Test Structure**: Mirror source structure

### Logging

```python
from infrastructure.logging import get_logger

logger = get_logger(__name__)
logger.info("Message")
```

### Type Hints

```python
def calculate_handicap(
    game_results: List[GameResult],
    settings: HandicapSettings
) -> Optional[Handicap]:
    ...
```

## Questions?

- Check [Development Manifesto](docs/DEVELOPMENT_MANIFESTO.md)
- Review existing code for patterns
- Ask for clarification if needed

## Thank You!

Your contributions make this project better. Let's build something great together! 🚀

