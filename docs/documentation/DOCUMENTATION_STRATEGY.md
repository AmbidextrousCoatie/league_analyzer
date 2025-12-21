# Documentation Strategy

## Overview

This document defines our comprehensive documentation strategy for League Analyzer v2. We use a **hybrid approach** combining:

1. **Docstrings** (in code) → **API Reference** (generated)
2. **Separate Markdown Files** → **Architecture & Guides** (manual)

---

## Documentation Philosophy

### Why Hybrid?

**Docstrings for API Reference:**
- ✅ Single source of truth (code)
- ✅ Always in sync with implementation
- ✅ Standard Python practice (PEP 257)
- ✅ IDE support (autocomplete, tooltips)
- ✅ Can generate beautiful HTML docs automatically

**Separate Docs for Architecture:**
- ✅ More flexible formatting (diagrams, tables)
- ✅ Can include design decisions and rationale
- ✅ Easier to write long-form explanations
- ✅ Can reference multiple modules/classes together

### Rule: **Docstrings for "what" and "how", Separate docs for "why"**

---

## Documentation Structure

```
docs/
├── index.md                          # Master documentation index
├── api/                              # Generated API reference (from docstrings)
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── presentation/
├── architecture/                     # Architecture documentation
│   ├── overview.md                   # Architecture overview
│   ├── layers.md                     # Layer descriptions
│   ├── domain_layer.md               # Domain layer details
│   ├── application_layer.md          # Application layer details
│   ├── infrastructure_layer.md       # Infrastructure layer details
│   └── presentation_layer.md        # Presentation layer details
├── guides/                           # How-to guides
│   ├── QUICK_START_GUIDE.md
│   ├── TESTING_SETUP.md
│   └── TEST_COVERAGE_GAPS.md
├── features/                         # Feature documentation
│   ├── DI/
│   ├── logging/
│   ├── fastAPI/
│   └── handicap/
├── standards/                        # Development standards
│   ├── DEVELOPMENT_MANIFESTO.md
│   ├── MANIFESTO_QUICK_REFERENCE.md
│   └── MANIFESTO_SUMMARY.md
├── documentation/                    # Documentation meta-docs
│   ├── DOCUMENTATION_STRATEGY.md
│   ├── DOCUMENTATION_RECOMMENDATION.md
│   └── DOCSTRING_TEMPLATE.md
├── planning/                         # Strategic planning
│   ├── REFACTORING_STRATEGY_REVISED.md
│   ├── SCOPE_ANALYSIS.md
│   └── TECH_STACK_ANALYSIS.md
├── pm/                               # Project management
│   └── (progress docs)
└── decisions/                        # Architecture Decision Records (ADRs)
    └── 004-documentation-strategy.md
```

---

## Docstring Standards

### Format: Google Style

We use **Google-style docstrings** (PEP 257 compliant):

```python
def calculate_handicap(
    results: List[GameResult],
    settings: HandicapSettings
) -> Optional[Handicap]:
    """
    Calculate handicap for a player based on their game results.
    
    Uses the handicap settings to determine calculation method (cumulative
    average or moving window) and applies the configured percentage.
    
    Args:
        results: List of game results for the player
        settings: Handicap settings (method, percentage, max cap)
    
    Returns:
        Calculated handicap value, or None if insufficient data
    
    Raises:
        InvalidHandicapCalculation: If calculation fails
    
    Example:
        >>> results = [GameResult(...), GameResult(...)]
        >>> settings = HandicapSettings(enabled=True, method=...)
        >>> handicap = calculate_handicap(results, settings)
        >>> print(handicap.value)
        15.5
    """
    pass
```

### Required Sections

1. **Summary** (one line)
2. **Description** (optional, multi-line)
3. **Args** (for functions/methods with parameters)
4. **Returns** (for functions/methods that return values)
5. **Raises** (for functions/methods that raise exceptions)
6. **Example** (optional, but recommended for complex functions)
7. **Note** (optional, for important notes)
8. **See Also** (optional, for related functions/classes)

### Module Docstrings

```python
"""
Domain Layer - Core Business Logic

This module contains the domain entities, value objects, and domain services
that represent the core business logic of the League Analyzer application.

The domain layer has no dependencies on other layers and can be tested
independently.

Modules:
    entities: Domain entities (Team, League, Game, Player)
    value_objects: Immutable value objects (Score, Points, Season)
    domain_services: Domain services (HandicapCalculator)
    domain_events: Domain events and event bus
    exceptions: Domain-specific exceptions

See Also:
    docs/architecture/domain_layer.md - Detailed domain layer documentation
"""
```

### Class Docstrings

```python
class HandicapCalculator:
    """
    Domain service for calculating player handicaps.
    
    HandicapCalculator provides stateless methods for calculating handicaps
    based on game results and handicap settings. It supports multiple
    calculation methods (cumulative average, moving window) and applies
    business rules such as maximum handicap caps.
    
    Attributes:
        BASE_SCORE: Standard base score for handicap calculation (200)
    
    Example:
        >>> calculator = HandicapCalculator()
        >>> results = [GameResult(...), ...]
        >>> settings = HandicapSettings(enabled=True, ...)
        >>> handicap = calculator.calculate_handicap(results, settings)
    
    See Also:
        domain.value_objects.handicap.Handicap
        domain.value_objects.handicap_settings.HandicapSettings
    """
    BASE_SCORE = 200.0
    
    @staticmethod
    def calculate_handicap(...):
        """..."""
        pass
```

---

## Documentation Generation

### Tool: **MkDocs** (recommended) or **Sphinx**

**Why MkDocs?**
- ✅ Simple Markdown-based
- ✅ Beautiful themes (Material)
- ✅ Easy to configure
- ✅ Fast build times
- ✅ Good for API docs + guides

**Why Sphinx?**
- ✅ More powerful (can generate from docstrings)
- ✅ Standard Python tool
- ✅ More features
- ❌ More complex setup

### Setup

1. **Install MkDocs and plugins:**
```bash
pip install mkdocs mkdocs-material mkdocstrings[python]
```

2. **Generate API docs from docstrings:**
```bash
mkdocs build
mkdocs serve  # Preview locally
```

3. **Deploy:**
```bash
mkdocs gh-deploy  # Deploy to GitHub Pages
```

---

## What Goes Where?

### In Docstrings (Code)

✅ **API Reference Information:**
- Function/method signatures
- Parameter descriptions
- Return value descriptions
- Exception types
- Usage examples
- Type information

### In Separate Markdown Files

✅ **Architecture & Design:**
- Layer descriptions
- Design patterns used
- Architecture decisions (ADRs)
- Rationale for choices
- Diagrams and visualizations

✅ **Guides & Tutorials:**
- Getting started guides
- Step-by-step tutorials
- Best practices
- Common patterns
- Migration guides

✅ **Reference:**
- Development manifesto
- Refactoring strategy
- Testing guidelines
- Logging guidelines

---

## Documentation Checklist

### For Each Module

- [ ] Module docstring (purpose, overview)
- [ ] All public classes documented
- [ ] All public functions/methods documented
- [ ] Type hints on all functions
- [ ] Examples in docstrings (for complex functions)
- [ ] Links to architecture docs (in module docstring)

### For Each Layer

- [ ] Architecture overview document
- [ ] Layer responsibilities documented
- [ ] Interfaces documented
- [ ] Dependencies documented
- [ ] Examples of usage

### For Each Feature

- [ ] Feature overview document
- [ ] Usage guide
- [ ] API reference (from docstrings)
- [ ] Examples
- [ ] Related documentation linked

---

## Documentation Maintenance

### When to Update Docs

1. **Code Changes:**
   - Update docstrings immediately
   - Regenerate API docs

2. **Architecture Changes:**
   - Update architecture docs
   - Create ADR if major decision

3. **New Features:**
   - Add feature documentation
   - Update guides if needed
   - Add examples

### Review Process

- Docs reviewed with code in PRs
- Architecture docs reviewed separately
- API docs auto-generated (always in sync)

---

## Examples

### Good Docstring

```python
def add_result(self, result: GameResult) -> None:
    """
    Add a game result for a player.
    
    Validates that the player doesn't already have a result for this game
    and publishes a GameResultAdded domain event.
    
    Args:
        result: GameResult value object containing player's score and points
    
    Raises:
        InvalidGameData: If player already has a result for this game
    
    Example:
        >>> game = Game(league_id=..., season=..., week=1, ...)
        >>> result = GameResult(player_id=..., score=Score(200), points=Points(2))
        >>> game.add_result(result)
        >>> len(game.results)
        1
    """
    if self._find_result(result.player_id) is not None:
        raise InvalidGameData(
            f"Player {result.player_id} already has a result for this game"
        )
    self.results.append(result)
    DomainEventBus.publish(GameResultAdded(...))
```

### Good Architecture Doc

```markdown
# Domain Layer

## Overview

The domain layer contains the core business logic of the League Analyzer
application. It has no dependencies on other layers and can be tested
independently.

## Responsibilities

- Business logic and rules
- Domain model definitions
- Domain events
- Domain exceptions

## Key Components

### Entities
- `Team`: Represents a bowling team
- `League`: Represents a bowling league
- `Game`: Represents a game/match
- `Player`: Represents a player

### Value Objects
- `Score`: Immutable score value
- `Points`: Immutable points value
- `Season`: Season identifier

See [API Reference](../api/domain/) for detailed API documentation.
```

---

## Next Steps

1. ✅ Set up MkDocs configuration
2. ✅ Create master documentation index
3. ✅ Create architecture documentation structure
4. ✅ Add docstrings to existing code
5. ✅ Generate API documentation
6. ✅ Link everything together

---

## Resources

- [Google Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [PEP 257 - Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
- [MkDocs Documentation](https://www.mkdocs.org/)
- [mkdocstrings Plugin](https://mkdocstrings.github.io/)

