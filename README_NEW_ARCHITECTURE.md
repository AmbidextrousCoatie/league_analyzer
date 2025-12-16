# New Architecture - League Analyzer v2

This document describes the new clean architecture structure for League Analyzer.

## Directory Structure

```
league_analyzer/
├── domain/                      # Domain Layer (Core Business Logic)
│   ├── entities/               # Domain entities with identity
│   ├── value_objects/          # Immutable value objects
│   ├── domain_services/        # Domain services
│   ├── domain_events/          # Domain events
│   └── exceptions/             # Domain exceptions
│
├── application/                # Application Layer (Use Cases)
│   ├── commands/              # Write operations (commands)
│   ├── queries/               # Read operations (queries)
│   ├── command_handlers/      # Command handlers
│   ├── query_handlers/        # Query handlers
│   └── dto/                   # Data Transfer Objects
│
├── infrastructure/             # Infrastructure Layer (Technical Details)
│   ├── persistence/          # Data access
│   │   ├── repositories/     # Repository implementations
│   │   └── adapters/         # Data adapters (SQLite, MySQL, Pandas)
│   ├── import_export/         # Import/Export services
│   ├── event_handlers/        # Domain event handlers
│   └── config/               # DI container, logging, settings
│
└── presentation/              # Presentation Layer (API)
    └── api/                   # REST API endpoints
        ├── v1/
        │   ├── commands/     # Write endpoints
        │   └── queries/      # Read endpoints
        └── middleware/       # API middleware
```

## Architecture Principles

### Clean Architecture
- **Dependency Rule**: Dependencies point inward. Domain has no dependencies.
- **Layer Separation**: Clear boundaries between layers.
- **Testability**: Each layer can be tested independently.

### CQRS (Command Query Responsibility Segregation)
- **Commands**: Write operations that change state.
- **Queries**: Read operations that don't change state.
- Separate handlers and models for reads and writes.

### Domain-Driven Design
- **Rich Domain Models**: Entities contain business logic.
- **Value Objects**: Immutable objects defined by value.
- **Domain Services**: Business logic that doesn't fit in entities.
- **Domain Events**: Important domain occurrences.

### Dependency Injection
- All dependencies injected via container.
- Loose coupling between components.
- Easy to test and mock.

## Getting Started

### Phase 1: Foundation (Weeks 1-3)

1. **Week 1**: Project structure ✅ (current)
   - Directory structure created
   - DI container setup
   - Logging and configuration
   - Base classes and interfaces

2. **Week 2**: Domain Models
   - Create entities (Team, League, Game, Player)
   - Create value objects (Score, Points, Season)
   - Add domain validation

3. **Week 3**: Domain Services & Events
   - Create domain services
   - Define domain events
   - Create event bus

## Key Files

- `infrastructure/config/container.py` - Dependency injection container
- `infrastructure/config/settings.py` - Application settings
- `infrastructure/config/logging_config.py` - Logging configuration
- `domain/domain_events/event_bus.py` - Domain event bus
- `domain/exceptions/domain_exception.py` - Domain exceptions
- `infrastructure/persistence/repositories/base_repository.py` - Repository interface
- `infrastructure/persistence/unit_of_work.py` - Unit of Work pattern

## Next Steps

1. Create domain entities (Team, League, Game, Player)
2. Create value objects (Score, Points, Season)
3. Implement repositories
4. Create command and query handlers
5. Wire everything together in the DI container

