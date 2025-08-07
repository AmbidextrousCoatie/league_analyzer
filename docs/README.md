# League Analyzer Frontend Documentation

## Overview
This directory contains documentation for the League Analyzer frontend refactoring and content block system implementation.

## Current Architecture

### Content Block System
The application uses a modular content block architecture that allows for dynamic, responsive rendering of team statistics based on filter state.

**Core Components:**
- `ContentRenderer` - Orchestrates content blocks based on filter state
- `FilterManager` - Manages filter state and coordinates updates
- `URLStateManager` - Synchronizes application state with browser URL
- `TeamStatsApp` - Main application coordinator

**Content Blocks:**
- `TeamHistoryBlock` - Team position history across seasons
- `LeagueComparisonBlock` - Team vs league performance comparison
- `ClutchAnalysisBlock` - Performance in close games
- `ConsistencyMetricsBlock` - Statistical consistency analysis
- `SpecialMatchesBlock` - Highest/lowest scores and biggest wins/losses

### Content Modes
The system dynamically determines content layout based on active filters:

- **no-selection**: No team selected
- **team-only**: Team selected, shows complete history across all seasons
- **team-season**: Team + season selected, shows season-specific analysis
- **team-season-week**: Team + season + week selected, shows week-specific data

## File Structure

```
app/static/js/
├── core/                     # Core state management
│   ├── content-renderer.js   # Content orchestration
│   ├── filter-manager.js     # Filter state management
│   └── url-state-manager.js  # URL synchronization
├── content-blocks/           # Modular content blocks
│   ├── base-content-block.js # Base class for all blocks
│   ├── team-history-block.js
│   ├── league-comparison-block.js
│   ├── clutch-analysis-block.js
│   ├── consistency-metrics-block.js
│   └── special-matches-block.js
├── legacy/                   # Legacy compatibility layer
│   ├── team-chart-utils.js   # Chart rendering functions
│   ├── team-data-utils-fixed.js  # Data fetching functions
│   └── team-filter-utils-fixed.js # UI update functions
├── chart-adapters.js         # Chart.js adapters for content blocks
└── team-stats-app.js         # Main application entry point
```

## Key Features

### Dynamic Content Rendering
- Content blocks automatically show/hide based on filter selection
- Each block can specify required and optional filters
- Blocks render independently with proper error handling

### State Management
- URL-driven state with browser history support
- Filter state persistence across page reloads
- Centralized state coordination between components

### Legacy Compatibility
- Gradual migration from monolithic template
- Legacy functions preserved for non-migrated features
- Dual-mode operation (legacy vs modern state management)

### Chart Management
- Robust Chart.js instance cleanup to prevent memory leaks
- Canvas reuse with proper chart destruction
- Adapter layer for legacy chart function compatibility

## Development Guidelines

### Adding New Content Blocks
1. Extend `BaseContentBlock` class
2. Define required/optional filters
3. Implement `render()` method
4. Register in `ContentRenderer.initializeContentBlocks()`
5. Add to appropriate content modes

### Best Practices
- Always call `super()` in content block constructors
- Implement proper error handling in render methods
- Use consistent logging with block ID prefixes
- Clean up resources (charts, timers) in `destroy()` method

## Architecture Evolution

### Completed Phases
1. **Modular JavaScript** - Extracted inline JS to separate modules
2. **State Management** - Added URL-driven state with filter coordination
3. **Content Blocks** - Migrated legacy functions to reusable block system

### Next Phase: Enhanced Event System
- Event-driven block communication
- Smart event routing (only relevant blocks update)
- Block status coordination and progress feedback
- Cross-block data sharing

## Historical Information
Detailed implementation history and troubleshooting information can be found in the `archive/` directory.