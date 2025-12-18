# Documentation Index

This directory contains all documentation for League Analyzer v2.

## Core Documentation

### Development Principles
- **[Development Manifesto](DEVELOPMENT_MANIFESTO.md)** - Core principles, practices, and standards
- **[Manifesto Quick Reference](MANIFESTO_QUICK_REFERENCE.md)** - Quick checklist and common patterns
- **[Manifesto Summary](MANIFESTO_SUMMARY.md)** - Executive summary

### Architecture & Design
- **[Architecture Design](ARCHITECTURE_DESIGN.md)** - System architecture (Clean Architecture, DDD, CQRS)
- **[Architecture Review](ARCHITECTURE_REVIEW.md)** - Initial architecture analysis of v1

### Development Planning
- **[Refactoring Strategy (Revised)](REFACTORING_STRATEGY_REVISED.md)** - Phased refactoring plan
- **[Scope Analysis](SCOPE_ANALYSIS.md)** - Current and desired scope
- **[Tech Stack Analysis](TECH_STACK_ANALYSIS.md)** - Technology choices and rationale

### Testing
- **[Testing Setup](TESTING_SETUP.md)** - Testing framework and practices
- **[Test Coverage Gaps](TEST_COVERAGE_GAPS.md)** - Coverage analysis and gaps

### Logging
- **[Logging Strategy](LOGGING_STRATEGY.md)** - Logging guidelines and best practices
- **[Logging Quick Reference](LOGGING_QUICK_REFERENCE.md)** - Quick reference guide

### Deployment & Setup
- **[FastAPI Deployment Guide](FASTAPI_DEPLOYMENT_GUIDE.md)** - Deployment instructions
- **[Quick Start Guide](QUICK_START_GUIDE.md)** - Getting started guide

### Dependency Injection
- **[DI Learning Guide](DI_LEARNING_GUIDE.md)** - Complete DI tutorial and patterns
- **[DI Adapter Implementation](DI_ADAPTER_IMPLEMENTATION.md)** - DI implementation for data adapters

## Implementation Progress

### Phase 1: Foundation & Domain Models
- **[Phase 1 Week 1 Complete](PHASE1_WEEK1_COMPLETE.md)** - Project structure and DI setup
- **[Phase 1 Week 2 Complete](going_modern/PHASE1_WEEK2_COMPLETE.md)** - Domain models implementation
- **[Handicap Feature](going_modern/HANDICAP_FEATURE.md)** - Handicap implementation
- **[Handicap Calculation Enhancement](going_modern/HANDICAP_CALCULATION_ENHANCEMENT.md)** - Enhanced handicap features

## Documentation Structure

```
docs/
├── README.md (this file)
├── DEVELOPMENT_MANIFESTO.md
├── ARCHITECTURE_DESIGN.md
├── REFACTORING_STRATEGY_REVISED.md
├── TESTING_SETUP.md
├── LOGGING_STRATEGY.md
└── going_modern/
    └── (implementation progress docs)
```

## Quick Links

- **Start Here**: [Development Manifesto](DEVELOPMENT_MANIFESTO.md)
- **Architecture**: [Architecture Design](ARCHITECTURE_DESIGN.md)
- **Testing**: [Testing Setup](TESTING_SETUP.md)
- **Logging**: [Logging Strategy](LOGGING_STRATEGY.md)
- **Planning**: [Refactoring Strategy](REFACTORING_STRATEGY_REVISED.md)

## Contributing

When adding new documentation:

1. Place in appropriate directory (`docs/` for general docs, `docs/going_modern/` for implementation progress)
2. Update this index
3. Link from relevant documents
4. Follow documentation standards (clear, concise, examples)

