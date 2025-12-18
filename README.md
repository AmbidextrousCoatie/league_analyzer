# League Analyzer

> **Development Manifesto**: All development follows our [Development Manifesto](docs/DEVELOPMENT_MANIFESTO.md). Read it before contributing.

## Quick Links

- 📋 [Development Manifesto](docs/DEVELOPMENT_MANIFESTO.md) - Core principles and practices
- 📚 [Documentation Index](docs/README.md) - All documentation
- 🏗️ [Architecture Design](docs/ARCHITECTURE_DESIGN.md) - System architecture
- 🧪 [Testing Setup](docs/TESTING_SETUP.md) - Testing framework and practices
- 📝 [Logging Strategy](docs/LOGGING_STRATEGY.md) - Logging guidelines
- 🔄 [Refactoring Strategy](docs/REFACTORING_STRATEGY_REVISED.md) - Development plan
- 📖 [Contributing Guide](CONTRIBUTING.md) - How to contribute

## Development Principles

- ✅ **Test-Driven Development (TDD)** - Write tests first
- ✅ **Clean Architecture** - Domain → Application → Infrastructure → Presentation
- ✅ **Domain-Driven Design (DDD)** - Rich domain models with business logic
- ✅ **CQRS** - Separate commands and queries
- ✅ **Dependency Injection** - No globals, no singletons
- ✅ **Logging Only** - NO `print()` statements
- ✅ **Type Hints** - Always use type annotations
- ✅ **100% Domain Coverage** - Critical business logic fully tested

See [Development Manifesto](docs/DEVELOPMENT_MANIFESTO.md) for complete guidelines.

---

## Project Overview

League Analyzer is a bowling league statistics and analytics application.

### Current Status

- ✅ Phase 1: Foundation & Domain Models (Complete)
- ✅ Test Framework Setup (159 tests, 76% coverage)
- ✅ Logging Infrastructure (Standard library, no dependencies)
- 🚧 Phase 2: Application Layer (In Progress)

### Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Vue.js 3 + TypeScript (planned)
- **Testing**: pytest + pytest-cov
- **Architecture**: Clean Architecture + DDD + CQRS

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Start development server
python main.py
```

## Project Structure

```
league_analyzer/
├── domain/              # Domain layer (business logic)
├── application/         # Application layer (use cases)
├── infrastructure/      # Infrastructure layer (external concerns)
├── presentation/        # Presentation layer (API endpoints)
├── tests/              # Test suite
└── docs/               # Documentation
```

## Development Workflow

1. **Read the Manifesto**: [Development Manifesto](docs/DEVELOPMENT_MANIFESTO.md)
2. **Write Tests First**: Follow TDD principles
3. **Follow Architecture**: Domain → Application → Infrastructure → Presentation
4. **Use Logging**: NO `print()` statements
5. **Run Tests**: `pytest` must pass before committing

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

[Your License Here]
