# ADR 004: Documentation Strategy

**Status**: Accepted  
**Date**: 2025-12-18  
**Deciders**: Development Team

---

## Context

We need a comprehensive documentation strategy that:
1. Documents all layers, modules, and functions
2. Aggregates all loose markdown files
3. Provides clear API reference
4. Maintains architecture documentation
5. Stays in sync with code

## Decision

We will use a **hybrid approach**:

1. **Docstrings (in code)** → **API Reference** (generated)
   - Google-style docstrings for all public APIs
   - Generate HTML docs using MkDocs + mkdocstrings
   - Single source of truth (code)

2. **Separate Markdown Files** → **Architecture & Guides**
   - Architecture documentation
   - Design decisions (ADRs)
   - Tutorials and guides
   - Reference documentation

## Rationale

### Why Docstrings for API Reference?

- ✅ **Single source of truth**: Code is the documentation
- ✅ **Always in sync**: Docstrings are in the same file as code
- ✅ **IDE support**: Autocomplete and tooltips show docstrings
- ✅ **Standard practice**: PEP 257, Google style guide
- ✅ **Auto-generation**: Can generate beautiful HTML docs

### Why Separate Docs for Architecture?

- ✅ **Flexibility**: Can include diagrams, tables, long explanations
- ✅ **Design decisions**: Can explain "why" not just "what"
- ✅ **Cross-module**: Can reference multiple modules together
- ✅ **Easier to write**: Long-form documentation is easier in markdown

### Why MkDocs?

- ✅ **Simple**: Markdown-based, easy to learn
- ✅ **Beautiful**: Material theme looks professional
- ✅ **Fast**: Quick build times
- ✅ **Flexible**: Can include both generated API docs and markdown files
- ✅ **Easy deployment**: GitHub Pages integration

## Consequences

### Positive

- Clear separation between API reference and architecture docs
- API docs always in sync with code
- Easy to maintain (docstrings in code)
- Professional documentation site
- Good developer experience (IDE support)

### Negative

- Requires discipline to keep docstrings updated
- Need to set up MkDocs infrastructure
- Two places to maintain (but clear separation)

### Mitigation

- Code review includes docstring review
- Automated checks for missing docstrings (future)
- Clear templates and examples
- Documentation in development manifesto

## Implementation

1. ✅ Create documentation strategy document
2. ✅ Set up MkDocs configuration
3. ✅ Create master documentation index
4. ✅ Create architecture documentation structure
5. 🚧 Add docstrings to existing code
6. 🚧 Generate API documentation
7. 🚧 Link everything together

## See Also

- [Documentation Strategy](../DOCUMENTATION_STRATEGY.md) - Complete strategy document
- [Docstring Template](../DOCSTRING_TEMPLATE.md) - Docstring templates
- [Development Manifesto](../standards/DEVELOPMENT_MANIFESTO.md) - Development principles

