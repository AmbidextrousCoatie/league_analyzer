# Architecture Overview

## Core Principles

League Analyzer v2 follows **Clean Architecture** principles with clear layer separation and dependency rules.

### 1. Clean Architecture

Dependencies point **inward**:
- Domain layer has **no dependencies**
- Application layer depends on Domain
- Infrastructure layer depends on Domain and Application
- Presentation layer depends on all inner layers

### 2. Domain-Driven Design (DDD)

- **Rich Domain Models**: Entities contain business logic
- **Value Objects**: Immutable domain concepts
- **Domain Services**: Stateless services for complex logic
- **Domain Events**: Event-driven side effects

### 3. CQRS (Command Query Responsibility Segregation)

- **Commands**: Write operations (change state)
- **Queries**: Read operations (read data)
- **Separate Handlers**: Command handlers vs query handlers

### 4. Dependency Injection

- Constructor injection for all dependencies
- DI container manages dependencies
- Interface-based design (depend on abstractions)

### 5. Event-Driven Architecture

- Domain events for side effects
- Event bus for publishing/handling
- Loose coupling between components

---

## Layer Structure

```
┌─────────────────────────────────────────────────────────┐
│              Presentation Layer                          │
│  API Routes, Web Templates, Frontend Components        │
│  Dependencies: Application, Infrastructure             │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│            Application Layer                            │
│  Commands (Write) | Queries (Read)                     │
│  Command Handlers | Query Handlers                      │
│  DTOs, Validators                                       │
│  Dependencies: Domain                                   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Domain Layer                               │
│  Entities, Value Objects, Domain Services               │
│  Domain Events, Domain Exceptions                       │
│  Dependencies: NONE                                     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│         Infrastructure Layer                            │
│  Repositories, Adapters, Event Handlers                 │
│  Import/Export Services, Unit of Work                  │
│  Dependencies: Domain                                   │
└─────────────────────────────────────────────────────────┘
```

---

## Layer Responsibilities

### Domain Layer (Core)
- **Business logic** and rules
- **Domain models** (entities, value objects)
- **Domain services** (complex business logic)
- **Domain events** (side effects)
- **No dependencies** on other layers

### Application Layer (Use Cases)
- **Orchestration** of domain objects
- **Commands** (write operations)
- **Queries** (read operations)
- **DTOs** (data transfer objects)
- **Depends on**: Domain layer only

### Infrastructure Layer (Technical)
- **Data access** (repositories, adapters)
- **External services** (logging, configuration)
- **Event handlers** (domain event side effects)
- **Depends on**: Domain layer only

### Presentation Layer (Interface)
- **API endpoints** (REST)
- **Request/response** handling
- **Validation** (input validation)
- **Depends on**: Application and Infrastructure layers

---

## Key Patterns

### Repository Pattern
- Abstracts data access
- Domain layer doesn't know about data storage
- Easy to swap implementations (Pandas → SQLite → MySQL)

### Unit of Work Pattern
- Transaction management
- Ensures consistency
- Groups related operations

### Dependency Injection
- Loose coupling
- Testability
- Flexibility

### Domain Events
- Decouple side effects
- Event-driven architecture
- Easy to add new handlers

---

## Directory Structure

```
league_analyzer/
├── domain/                      # Domain Layer
│   ├── entities/               # Domain entities
│   ├── value_objects/          # Value objects
│   ├── domain_services/        # Domain services
│   ├── domain_events/          # Domain events
│   └── exceptions/             # Domain exceptions
│
├── application/                # Application Layer
│   ├── commands/               # Commands (write)
│   ├── queries/               # Queries (read)
│   ├── command_handlers/       # Command handlers
│   ├── query_handlers/         # Query handlers
│   └── dto/                    # Data Transfer Objects
│
├── infrastructure/             # Infrastructure Layer
│   ├── persistence/            # Data access
│   │   ├── repositories/      # Repository implementations
│   │   └── adapters/          # Data adapters
│   ├── event_handlers/         # Event handlers
│   ├── import_export/          # Import/Export services
│   └── config/                 # Configuration, DI, logging
│
└── presentation/               # Presentation Layer
    └── api/                    # REST API endpoints
        └── v1/
            ├── commands/       # Write endpoints
            └── queries/        # Read endpoints
```

---

## Data Flow

### Write Operation (Command)
```
API Endpoint → Command → Command Handler → Domain Entity → Repository → Adapter → Database
                                    ↓
                              Domain Event → Event Handler → Side Effects
```

### Read Operation (Query)
```
API Endpoint → Query → Query Handler → Repository → Adapter → Database → DTO → Response
```

---

## Testing Strategy

- **Domain Layer**: 100% coverage target (critical business logic)
- **Application Layer**: 90%+ coverage target
- **Infrastructure Layer**: 80%+ coverage target
- **Unit Tests**: Fast, isolated tests
- **Integration Tests**: Component interaction tests

---

## Next Steps

- [Layer Details](layers.md) - Detailed layer descriptions
- [Domain Layer](domain_layer.md) - Domain layer architecture
- [Application Layer](application_layer.md) - Application layer architecture
- [Infrastructure Layer](infrastructure_layer.md) - Infrastructure layer architecture
- [Presentation Layer](presentation_layer.md) - Presentation layer architecture

---

## See Also

- [Architecture Design](../reference/ARCHITECTURE_DESIGN.md) - Detailed design document
- [Architecture Review](../reference/ARCHITECTURE_REVIEW.md) - Architecture analysis
- [Development Manifesto](../reference/DEVELOPMENT_MANIFESTO.md) - Development principles

