# Frontend Refactoring Plan: Team Statistics Architecture

## 🎯 Project Goals

Transform the monolithic `team/stats.html` (799 lines) into a maintainable, modular architecture with:
- **Reliable filtering** with hierarchical data scoping
- **Clean data handling** with consistent API interfaces  
- **Dynamic content** based on active filters
- **Consistent UI** with URL-based state management
- **Reusable components** for future development

## 🚫 Constraints & Preservation

### Must NOT Change:
- ✅ Backend route signatures (`/team/get_*`, `/league/get_*`)
- ✅ Chart function signatures (`createLineChart`, `createAreaChart_vanilla`, etc.)
- ✅ Table function signatures (`createTable`, `createTableBootstrap3`, etc.)
- ✅ Existing CSS classes or component templates
- ✅ Database schemas or data processing logic

### Interface Preservation Strategy:
- Extract existing functions into modules with same signatures
- Add coordination layer on top (no replacement)
- Incremental migration (function by function)
- Zero breaking changes to existing APIs

## 🏗️ New Architecture Overview

### Core Components:
```
├── FilterManager          # Handles filter state & validation
├── URLStateManager        # Syncs state with URL parameters  
├── ContentRenderer        # Orchestrates content block rendering
├── DataManager           # Manages API calls & caching
└── ContentBlocks/        # Reusable display components
    ├── TeamHistoryBlock
    ├── ClutchAnalysisBlock
    ├── LeagueComparisonBlock
    └── ConsistencyMetricsBlock
```

## 📂 Proposed File Structure

```
app/static/js/
├── core/
│   ├── filter-manager.js      # Filter state management
│   ├── url-state-manager.js   # URL synchronization
│   ├── content-renderer.js    # Content orchestration
│   └── data-manager.js        # API calls & caching
├── content-blocks/
│   ├── base-content-block.js  # Abstract base class
│   ├── team-history-block.js  # Team position history
│   ├── clutch-analysis-block.js # Clutch performance
│   ├── league-comparison-block.js # Team vs league
│   ├── consistency-metrics-block.js # Consistency stats
│   └── special-matches-block.js # Highlights table
├── legacy/
│   ├── team-chart-utils.js    # Extracted chart functions
│   ├── team-filter-utils.js   # Extracted filter functions
│   └── team-data-utils.js     # Extracted data functions
├── config/
│   ├── filter-schemas.js      # View-specific filter hierarchies
│   ├── content-modes.js       # Content block combinations
│   └── api-endpoints.js       # Centralized endpoint definitions
└── team-stats-app.js          # Main application entry point

app/templates/team/
├── stats.html                 # Simplified main template
├── components/
│   ├── filter-controls.html   # Reusable filter UI
│   ├── content-container.html # Dynamic content area
│   └── loading-states.html    # Loading indicators
└── blocks/                    # Individual content block templates
    ├── team-history.html
    ├── clutch-analysis.html
    ├── league-comparison.html
    └── consistency-metrics.html
```

## 🔄 Migration Strategy (4 Phases)

### Phase 1: Extract & Modularize (No Breaking Changes)
**Goal**: Break down the monolithic file while preserving exact functionality

**Steps**:
1. Extract existing functions to modules with identical signatures
2. Create legacy utility files 
3. Update main template to import modules
4. Verify functionality unchanged

**Files Created**:
- `legacy/team-chart-utils.js` - All chart functions
- `legacy/team-filter-utils.js` - All filter functions  
- `legacy/team-data-utils.js` - All data fetching functions

**Validation**: Original functionality works identically

### Phase 2: Add State Management Layer (Additive Only)
**Goal**: Add URL-based state management calling existing functions

**Steps**:
1. Create `FilterManager` that calls existing filter functions
2. Add `URLStateManager` for browser state synchronization
3. Create `ContentRenderer` that calls existing chart functions
4. Add URL parameter parsing (backward compatible)

**Files Created**:
- `core/filter-manager.js`
- `core/url-state-manager.js` 
- `core/content-renderer.js`
- `team-stats-app.js` (coordinator)

**New Features**: 
- URL reflects current state
- Shareable links
- Browser back/forward support
- Consistent filter behavior

### Phase 3: Implement Content Blocks (Gradual Replacement)
**Goal**: Replace individual functions with content block system

**Steps**:
1. Create `BaseContentBlock` abstract class
2. Implement one content block at a time
3. Each block uses existing chart/table functions
4. Gradually replace function calls with block rendering
5. Add dynamic content modes based on filter state

**Migration Order**:
1. `TeamHistoryBlock` (simple chart)
2. `LeagueComparisonBlock` (area chart + table)
3. `ClutchAnalysisBlock` (bar chart + stats)
4. `ConsistencyMetricsBlock` (metrics display)
5. `SpecialMatchesBlock` (tables)

**Files Created**:
- `content-blocks/base-content-block.js`
- `content-blocks/team-history-block.js`
- `content-blocks/league-comparison-block.js`
- `content-blocks/clutch-analysis-block.js`
- `content-blocks/consistency-metrics-block.js`
- `content-blocks/special-matches-block.js`

### Phase 4: Advanced Features & Optimization
**Goal**: Add advanced filtering and performance optimizations

**Steps**:
1. Implement flexible filter hierarchies
2. Add data caching and request deduplication
3. Create reusable filter schemas for other views
4. Add loading states and error handling
5. Performance optimization and testing

**Files Created**:
- `config/filter-schemas.js`
- `config/content-modes.js`
- `core/data-manager.js`
- `templates/team/components/` (UI components)

## 📋 Implementation Details

### Filter Schema Example (Team-Centric View):
```javascript
const TEAM_FILTER_SCHEMA = {
  hierarchy: ['database', 'team', 'season', 'week'],
  contentModes: {
    0: 'database-overview',
    1: 'team-selection-prompt', 
    2: 'team-all-seasons',
    3: 'team-season-analysis',
    4: 'team-week-performance'
  },
  apiEndpoints: {
    teams: '/team/get_teams',
    seasons: '/team/get_available_seasons',
    weeks: '/team/get_available_weeks'
  }
}
```

### Content Mode Definitions:
```javascript
const CONTENT_MODES = {
  'team-all-seasons': {
    title: 'Team Complete History',
    layout: 'dashboard-grid',
    blocks: [
      { type: 'team-history-block', container: 'chart-main' },
      { type: 'league-comparison-block', container: 'chart-secondary' }, 
      { type: 'consistency-metrics-block', container: 'stats-sidebar' },
      { type: 'special-matches-block', container: 'table-full' }
    ]
  },
  
  'team-season-analysis': {
    title: 'Team Season Deep-Dive',
    layout: 'two-column',
    blocks: [
      { type: 'clutch-analysis-block', container: 'main-content' },
      { type: 'consistency-metrics-block', container: 'sidebar' },
      { type: 'special-matches-block', container: 'full-width' }
    ]
  }
}
```

### Content Block Implementation:
```javascript
class TeamHistoryBlock extends BaseContentBlock {
  constructor() {
    super({
      id: 'team-history',
      dataEndpoint: '/team/get_team_history',
      requiredFilters: ['team'],
      template: 'blocks/team-history.html'
    });
  }
  
  async fetchData(filterState) {
    // Use existing API endpoint - no changes
    const response = await fetch(`${this.dataEndpoint}?team_name=${filterState.team}`);
    return response.json();
  }
  
  render(data, containerId) {
    // Call existing chart function - no changes to chart interface
    updateTeamHistory(filterState.team);
  }
}
```

## 🎯 Success Metrics

### Maintainability:
- ✅ Reduce main template from 799 to <100 lines
- ✅ Modular code with single responsibilities  
- ✅ Reusable components across views
- ✅ Clear separation of concerns

### Functionality:
- ✅ All existing features work identically
- ✅ URL-based state management
- ✅ Consistent filter behavior across views
- ✅ Reliable data handling with proper error states
- ✅ Dynamic content based on filter selection

### Developer Experience:
- ✅ Easy to add new content blocks
- ✅ Clear debugging with modular architecture
- ✅ Safe incremental migration
- ✅ Zero breaking changes to existing APIs

## 🚀 Next Steps

1. **Start Phase 1**: Extract existing functions to modules
2. **Create base file structure**: Set up directories and placeholder files
3. **Implement Phase 1**: Modularize while preserving exact functionality  
4. **Test & Validate**: Ensure no regressions
5. **Continue to Phase 2**: Add state management layer

**Risk Mitigation**: Each phase can be deployed independently, allowing rollback if issues occur.

## 📚 Technical References

### Key Design Patterns:
- **Command Pattern**: Content blocks encapsulate rendering logic
- **Observer Pattern**: State changes trigger content updates
- **Strategy Pattern**: Different filter schemas for different views
- **Facade Pattern**: Legacy utilities hide complexity during migration

### Dependencies Preserved:
- Chart.js and ECharts (existing chart libraries)
- Bootstrap CSS framework  
- Existing table utilities
- Current API endpoint structure

This plan provides a clear, safe path from the current monolithic architecture to a maintainable, modular system while preserving all existing functionality and interfaces.