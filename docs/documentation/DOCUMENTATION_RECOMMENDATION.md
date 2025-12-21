# Documentation Recommendation

## Answer to Your Question

**Should we use docstrings in code and generate documentation, or have separate documentation?**

**Answer: Use BOTH - Hybrid Approach**

1. **Docstrings (in code)** → Generate API Reference
2. **Separate Markdown Files** → Architecture & Guides

---

## Why This Approach?

### ✅ Advantages of Docstrings + Generated Docs

1. **Single Source of Truth**
   - Code and documentation in the same place
   - Can't get out of sync easily
   - IDE shows docstrings automatically

2. **Always Up-to-Date**
   - When code changes, docstrings change
   - Generated docs reflect current code
   - No separate maintenance burden

3. **Standard Practice**
   - PEP 257 (Python docstring conventions)
   - Google style guide (widely used)
   - Industry standard approach

4. **Developer Experience**
   - IDE autocomplete shows docstrings
   - Tooltips show documentation
   - Better code navigation

5. **Automated Generation**
   - Tools like MkDocs + mkdocstrings generate beautiful HTML
   - Can deploy to GitHub Pages
   - Professional documentation site

### ✅ Advantages of Separate Markdown Files

1. **Architecture Documentation**
   - Can explain "why" not just "what"
   - Design decisions and rationale
   - Cross-module explanations

2. **Flexibility**
   - Diagrams and visualizations
   - Long-form explanations
   - Tables and formatting

3. **Guides & Tutorials**
   - Step-by-step instructions
   - Best practices
   - Examples spanning multiple modules

---

## Recommended Structure

```
docs/
├── index.md                    # Master index (aggregates everything)
│
├── api/                        # Generated from docstrings
│   ├── domain/                 # Domain layer API
│   ├── application/            # Application layer API
│   ├── infrastructure/         # Infrastructure layer API
│   └── presentation/           # Presentation layer API
│
├── architecture/               # Architecture documentation
│   ├── overview.md             # High-level architecture
│   ├── layers.md               # Layer descriptions
│   ├── domain_layer.md         # Domain layer details
│   ├── application_layer.md    # Application layer details
│   ├── infrastructure_layer.md # Infrastructure layer details
│   └── presentation_layer.md  # Presentation layer details
│
├── guides/                     # How-to guides
│   ├── getting_started.md
│   ├── dependency_injection.md
│   ├── testing.md
│   └── logging.md
│
├── decisions/                  # Architecture Decision Records
│   ├── 001-dependency-injection.md
│   └── 004-documentation-strategy.md
│
├── standards/                  # ✅ Development standards
│   ├── DEVELOPMENT_MANIFESTO.md
│   ├── MANIFESTO_QUICK_REFERENCE.md
│   └── MANIFESTO_SUMMARY.md
│
├── planning/                    # ✅ Planning and analysis
│   ├── REFACTORING_STRATEGY_REVISED.md
│   ├── SCOPE_ANALYSIS.md
│   └── TECH_STACK_ANALYSIS.md
│
└── ...
```

---

## What Goes Where?

### In Docstrings (Code) ✅

**API Reference Information:**
- Function/method signatures
- Parameter descriptions (Args)
- Return value descriptions (Returns)
- Exception types (Raises)
- Usage examples (Example)
- Type information (complement type hints)

**Example:**
```python
def calculate_handicap(
    results: List[GameResult],
    settings: HandicapSettings
) -> Optional[Handicap]:
    """
    Calculate handicap for a player based on their game results.
    
    Args:
        results: List of game results for the player
        settings: Handicap settings (method, percentage, max cap)
    
    Returns:
        Calculated handicap value, or None if insufficient data
    
    Raises:
        InvalidHandicapCalculation: If calculation fails
    
    Example:
        >>> handicap = calculate_handicap(results, settings)
        >>> print(handicap.value)
        15.5
    """
```

### In Separate Markdown Files ✅

**Architecture & Design:**
- Layer descriptions and responsibilities
- Design patterns used
- Architecture decisions (ADRs)
- Rationale for choices
- Diagrams and visualizations

**Guides & Tutorials:**
- Getting started guides
- Step-by-step tutorials
- Best practices
- Common patterns
- Migration guides

**Reference:**
- Development manifesto
- Refactoring strategy
- Testing guidelines
- Logging guidelines

---

## Implementation Plan

### Phase 1: Setup ✅

- [x] Create documentation strategy document
- [x] Set up MkDocs configuration
- [x] Create master documentation index
- [x] Create architecture documentation structure
- [x] Create docstring templates

### Phase 2: Add Docstrings 🚧

- [ ] Add docstrings to domain layer
- [ ] Add docstrings to application layer
- [ ] Add docstrings to infrastructure layer
- [ ] Add docstrings to presentation layer

### Phase 3: Generate Docs 🚧

- [ ] Install MkDocs and plugins
- [ ] Generate API documentation
- [ ] Link architecture docs
- [ ] Deploy documentation site

### Phase 4: Maintain 📋

- [ ] Update docstrings with code changes
- [ ] Review docs in code reviews
- [ ] Keep architecture docs updated

---

## Tools & Setup

### Recommended: MkDocs + mkdocstrings

**Installation:**
```bash
pip install mkdocs mkdocs-material mkdocstrings[python]
```

**Configuration:**
- `mkdocs.yml` - Already created ✅
- Material theme for beautiful docs
- mkdocstrings plugin for API generation

**Usage:**
```bash
mkdocs build      # Build documentation
mkdocs serve      # Preview locally
mkdocs gh-deploy  # Deploy to GitHub Pages
```

### Alternative: Sphinx

More powerful but more complex:
- Better for large projects
- More features
- Standard Python tool
- More complex setup

---

## Best Practices

### Docstrings

1. **Use Google Style**
   - Clear, consistent format
   - Standard Python practice

2. **Include Examples**
   - Especially for complex functions
   - Shows usage patterns

3. **Link to Architecture Docs**
   - Use `See Also` section
   - Connect API to architecture

4. **Keep It Updated**
   - Update docstrings with code
   - Review in PRs

### Architecture Docs

1. **Explain "Why"**
   - Not just "what" (that's in docstrings)
   - Design decisions and rationale

2. **Use Diagrams**
   - Visual representations
   - Layer diagrams
   - Flow diagrams

3. **Keep It Current**
   - Update when architecture changes
   - Create ADRs for major decisions

---

## Example: Complete Documentation

### Code (with docstrings)

```python
"""
Domain Layer - Core Business Logic

This module contains domain entities, value objects, and domain services
that represent the core business logic.

See Also:
    docs/architecture/domain_layer.md - Detailed domain layer documentation
"""

class HandicapCalculator:
    """
    Domain service for calculating player handicaps.
    
    See Also:
        docs/architecture/domain_layer.md - Domain layer documentation
    """
    
    @staticmethod
    def calculate_handicap(...) -> Optional[Handicap]:
        """
        Calculate handicap for a player.
        
        See Also:
            docs/architecture/domain_layer.md - Domain layer documentation
        """
        pass
```

### Architecture Doc (separate)

```markdown
# Domain Layer

## Overview

The domain layer contains core business logic...

## HandicapCalculator

The HandicapCalculator is a domain service that...

See [API Reference](../api/domain/domain_services.html#handicapcalculator)
for detailed API documentation.
```

### Generated API Doc (from docstrings)

Automatically generated HTML showing:
- Class description
- Method signatures
- Parameters
- Return values
- Examples
- Links to architecture docs

---

## Summary

**Recommendation: Hybrid Approach**

1. ✅ **Docstrings in code** → Generate API Reference
2. ✅ **Separate markdown files** → Architecture & Guides
3. ✅ **MkDocs** → Generate beautiful documentation site
4. ✅ **Master index** → Aggregates everything

**Benefits:**
- API docs always in sync (from code)
- Architecture docs flexible (separate files)
- Professional documentation site
- Good developer experience
- Easy to maintain

---

## Next Steps

1. Review this recommendation
2. Start adding docstrings to existing code
3. Set up MkDocs (if not already done)
4. Generate API documentation
5. Link everything together

---

## See Also

- [Documentation Strategy](DOCUMENTATION_STRATEGY.md) - Complete strategy
- [Docstring Template](DOCSTRING_TEMPLATE.md) - Templates and examples
- [Master Index](index.md) - Aggregated documentation
- [Development Manifesto](../standards/DEVELOPMENT_MANIFESTO.md) - Development principles

