# Documentation Index

This directory contains all documentation for League Analyzer v2.

## Documentation Structure

```
docs/
├── index.md                    # Master documentation index
├── README.md                   # This file
│
├── architecture/               # Architecture documentation
│   ├── overview.md
│   ├── ARCHITECTURE_DESIGN.md
│   └── ARCHITECTURE_REVIEW.md
│
├── standards/                  # Development standards
│   ├── DEVELOPMENT_MANIFESTO.md
│   ├── MANIFESTO_QUICK_REFERENCE.md
│   └── MANIFESTO_SUMMARY.md
│
├── documentation/             # Documentation meta-docs
│   ├── DOCUMENTATION_STRATEGY.md
│   ├── DOCUMENTATION_RECOMMENDATION.md
│   └── DOCSTRING_TEMPLATE.md
│
├── planning/                  # Strategic planning
│   ├── REFACTORING_STRATEGY_REVISED.md
│   ├── SCOPE_ANALYSIS.md
│   └── TECH_STACK_ANALYSIS.md
│
├── guides/                    # Getting started and setup guides
│   ├── QUICK_START_GUIDE.md
│   ├── TESTING_SETUP.md
│   └── TEST_COVERAGE_GAPS.md
│
├── features/                  # Feature documentation
│   ├── DI/
│   │   ├── DI_LEARNING_GUIDE.md
│   │   └── DI_ADAPTER_IMPLEMENTATION.md
│   ├── logging/
│   │   ├── LOGGING_STRATEGY.md
│   │   └── LOGGING_QUICK_REFERENCE.md
│   ├── fastAPI/
│   │   └── FASTAPI_DEPLOYMENT_GUIDE.md
│   └── handicap/
│       ├── HANDICAP_FEATURE.md
│       └── HANDICAP_CALCULATION_ENHANCEMENT.md
│
├── pm/                        # Project management
│   ├── PHASE1_PROGRESS.md
│   ├── PHASE1_WEEK1_COMPLETE.md
│   └── PHASE1_WEEK2_COMPLETE.md
│
└── decisions/                 # Architecture Decision Records
    └── 004-documentation-strategy.md
```

## Core Documentation

### Development Standards
- **[Development Manifesto](standards/DEVELOPMENT_MANIFESTO.md)** - Core principles, practices, and standards
- **[Manifesto Quick Reference](standards/MANIFESTO_QUICK_REFERENCE.md)** - Quick checklist and common patterns
- **[Manifesto Summary](standards/MANIFESTO_SUMMARY.md)** - Executive summary

### Architecture & Design
- **[Architecture Overview](architecture/overview.md)** - High-level architecture
- **[Architecture Design](architecture/ARCHITECTURE_DESIGN.md)** - System architecture (Clean Architecture, DDD, CQRS)
- **[Architecture Review](architecture/ARCHITECTURE_REVIEW.md)** - Initial architecture analysis of v1

### Planning & Strategy
- **[Refactoring Strategy](planning/REFACTORING_STRATEGY_REVISED.md)** - Phased refactoring plan
- **[Scope Analysis](planning/SCOPE_ANALYSIS.md)** - Current and desired scope
- **[Tech Stack Analysis](planning/TECH_STACK_ANALYSIS.md)** - Technology choices and rationale

### Guides
- **[Quick Start Guide](guides/QUICK_START_GUIDE.md)** - Getting started guide
- **[Testing Setup](guides/TESTING_SETUP.md)** - Testing framework and practices
- **[Test Coverage Gaps](guides/TEST_COVERAGE_GAPS.md)** - Coverage analysis and gaps

### Features
- **[Dependency Injection](features/DI/DI_LEARNING_GUIDE.md)** - Complete DI tutorial and patterns
- **[DI Implementation](features/DI/DI_ADAPTER_IMPLEMENTATION.md)** - DI implementation for data adapters
- **[Logging Strategy](features/logging/LOGGING_STRATEGY.md)** - Logging guidelines and best practices
- **[Logging Quick Reference](features/logging/LOGGING_QUICK_REFERENCE.md)** - Quick reference guide
- **[FastAPI Deployment](features/fastAPI/FASTAPI_DEPLOYMENT_GUIDE.md)** - Deployment instructions
- **[Handicap Feature](features/handicap/HANDICAP_FEATURE.md)** - Handicap implementation
- **[Handicap Calculation Enhancement](features/handicap/HANDICAP_CALCULATION_ENHANCEMENT.md)** - Enhanced handicap features

### Documentation
- **[Documentation Strategy](documentation/DOCUMENTATION_STRATEGY.md)** - Documentation approach
- **[Documentation Recommendation](documentation/DOCUMENTATION_RECOMMENDATION.md)** - Documentation recommendations
- **[Docstring Template](documentation/DOCSTRING_TEMPLATE.md)** - Docstring templates and examples

## Implementation Progress

### Phase 1: Foundation & Domain Models
- **[Phase 1 Progress](pm/PHASE1_PROGRESS.md)** - Overall progress status
- **[Phase 1 Week 1 Complete](pm/PHASE1_WEEK1_COMPLETE.md)** - Project structure and DI setup
- **[Phase 1 Week 2 Complete](pm/PHASE1_WEEK2_COMPLETE.md)** - Domain models implementation

## Quick Links

- **Start Here**: [Development Manifesto](standards/DEVELOPMENT_MANIFESTO.md)
- **Architecture**: [Architecture Overview](architecture/overview.md)
- **Getting Started**: [Quick Start Guide](guides/QUICK_START_GUIDE.md)
- **Testing**: [Testing Setup](guides/TESTING_SETUP.md)
- **Logging**: [Logging Strategy](features/logging/LOGGING_STRATEGY.md)
- **Planning**: [Refactoring Strategy](planning/REFACTORING_STRATEGY_REVISED.md)

## Contributing

When adding new documentation:

1. **Place in appropriate directory:**
   - `standards/` - Development standards and principles
   - `documentation/` - Documentation about documentation
   - `planning/` - Strategic planning and analysis
   - `guides/` - Getting started and setup guides
   - `features/` - Feature-specific documentation
   - `pm/` - Project management and progress tracking
   - `decisions/` - Architecture Decision Records (ADRs)
   - `architecture/` - Architecture documentation

2. **Update documentation:**
   - Update `index.md` with new links
   - Update this `README.md` if structure changes
   - Link from relevant documents

3. **Follow standards:**
   - Clear, concise writing
   - Include examples
   - Use proper formatting
   - Follow [Documentation Strategy](documentation/DOCUMENTATION_STRATEGY.md)

## See Also

- **[Master Index](index.md)** - Complete documentation index with all links
- **[Documentation Strategy](documentation/DOCUMENTATION_STRATEGY.md)** - Documentation approach and standards
