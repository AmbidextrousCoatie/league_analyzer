# League Stats Page Refactoring Plan

## Current State Analysis

### Template Structure
- **File**: `app/templates/league/stats.html`
- **Size**: 1,426 lines (even larger than the original team stats!)
- **JavaScript**: ~800 lines of inline JavaScript
- **Content Blocks**: 10 major sections

### Major Content Sections Identified

1. **Season Overview Block**
   - Container: League history table
   - Data: Season overview data
   - Shows: Historical league performance

2. **Position Progress Block**
   - Container: `positionChart` (Chart.js)
   - Data: Position progression over time
   - Shows: Team positions throughout season

3. **Points Progress Block**
   - Container: Points chart area
   - Data: Points progression over time  
   - Shows: Points accumulated over time

4. **Match Day Points Block**
   - Container: Points per match day chart
   - Data: Weekly point distribution
   - Shows: Points scored each week

5. **Match Day Averages Block**
   - Container: Average per match day chart
   - Data: Weekly average scores
   - Shows: Average scores by week

6. **Match Day Positions Block**
   - Container: Position per match day chart
   - Data: Weekly position data
   - Shows: League positions by week

7. **Points vs Average Block**
   - Container: Points vs average chart
   - Data: Comparative performance data
   - Shows: Team performance vs league average

8. **Week Standings Block**
   - Container: `tableLeagueWeek`
   - Data: Current week standings
   - Shows: League table for selected week

9. **Honor Scores Block**
   - Container: Multiple tables for top scores
   - Data: Best individual/team performances
   - Shows: Top scores, averages, achievements

10. **Team Details Block**
    - Container: `scoreSheetTable`
    - Data: Detailed team performance
    - Shows: Score sheets and team analysis

### Current Filter Hierarchy
The league stats uses a different filter hierarchy than team stats:
- **League Filter Order**: Season → League → Week → Team
- **Content Modes**:
  - `season-only`: Season overview and historical data
  - `season-league`: League-specific analysis
  - `season-league-week`: Week-specific standings
  - `season-league-week-team`: Team-specific details

## Refactoring Strategy

### Phase 1: Extract JavaScript Modules
Create modular JavaScript files similar to team stats:

1. **`league-filter-utils.js`** - Button management and filter UI updates
2. **`league-chart-utils.js`** - Chart rendering functions
3. **`league-data-utils.js`** - Data fetching and table management

### Phase 2: Implement League State Management
Create league-specific state management:

1. **`league-stats-app.js`** - Main coordinator for league stats
2. **Enhanced FilterManager** - Support for league filter hierarchy
3. **League ContentRenderer** - Orchestrates league content blocks

### Phase 3: Create League Content Blocks
Implement content blocks for each major section:

1. **`season-overview-block.js`** - Historical league data
2. **`position-progress-block.js`** - Position progression chart
3. **`points-progress-block.js`** - Points progression chart  
4. **`match-day-points-block.js`** - Weekly points chart
5. **`match-day-averages-block.js`** - Weekly averages chart
6. **`match-day-positions-block.js`** - Weekly positions chart
7. **`points-vs-average-block.js`** - Comparative performance
8. **`week-standings-block.js`** - Current week league table
9. **`honor-scores-block.js`** - Top performances
10. **`team-details-block.js`** - Detailed team analysis

### Phase 4: Enhanced Event System Integration
- Configure SmartEventRouter for league-specific event mapping
- Implement selective updates based on filter changes
- Add cross-block communication for league data

## Content Mode Configuration

### League Content Modes
```javascript
contentModes: {
    'no-selection': {
        title: 'League Statistics',
        description: 'Select season and league to view statistics',
        blocks: []
    },
    'season-only': {
        title: 'Season Overview',
        description: 'Historical data across all leagues',
        blocks: ['season-overview', 'honor-scores']
    },
    'season-league': {
        title: 'League Analysis',
        description: 'Comprehensive league performance analysis',
        blocks: ['season-overview', 'position-progress', 'points-progress', 'honor-scores']
    },
    'season-league-week': {
        title: 'Week Analysis', 
        description: 'Current week standings and performance',
        blocks: ['week-standings', 'match-day-points', 'match-day-averages', 'match-day-positions', 'points-vs-average']
    },
    'season-league-week-team': {
        title: 'Team Analysis',
        description: 'Detailed team performance analysis',
        blocks: ['team-details', 'week-standings', 'points-vs-average']
    }
}
```

### Enhanced Event Mapping
```javascript
// League-specific event routing
coreEventMapping: {
    'filter-changed-season': ['season-overview', 'position-progress', 'points-progress', 'honor-scores'],
    'filter-changed-league': ['season-overview', 'position-progress', 'points-progress', 'week-standings', 'honor-scores'],
    'filter-changed-week': ['week-standings', 'match-day-points', 'match-day-averages', 'match-day-positions', 'points-vs-average', 'team-details'],
    'filter-changed-team': ['team-details'] // Only team details block cares about team selection
}
```

## Performance Benefits

### Current Issues
- Every filter change triggers all content updates
- Position chart re-renders when only team selection changes
- Honor scores reload when week changes (unnecessary)
- Sequential content loading with no progress feedback

### Expected Improvements
- **Team selection**: Only team-details block updates (90% faster)
- **Week selection**: 5 blocks update instead of 10 (50% faster)
- **League selection**: 6 blocks update instead of 10 (40% faster)
- **Season selection**: All blocks update (same as before, but coordinated)

## Implementation Plan

### Step 1: Create Base Structure
1. Backup original `stats.html` as `stats_original_backup.html`
2. Extract JavaScript to modular files
3. Update template to use module imports
4. Test basic functionality

### Step 2: Implement State Management
1. Create `league-stats-app.js` based on team stats pattern
2. Configure FilterManager for league filter hierarchy
3. Create LeagueContentRenderer
4. Test state management and URL synchronization

### Step 3: Migrate Content Blocks
1. Start with simple blocks (season-overview, week-standings)
2. Migrate chart blocks (position-progress, points-progress, etc.)
3. Implement complex blocks (honor-scores, team-details)
4. Test each block integration

### Step 4: Enhanced Event System
1. Configure SmartEventRouter for league events
2. Implement selective block updates
3. Add cross-block communication
4. Performance testing and optimization

## File Structure

### New JavaScript Files
```
app/static/js/
├── league-stats-app.js                    # Main league stats coordinator
├── league/                                # League-specific modules
│   ├── league-filter-utils.js            # Filter UI management
│   ├── league-chart-utils.js             # Chart rendering functions
│   └── league-data-utils.js              # Data fetching and tables
└── content-blocks/                       # League content blocks
    ├── season-overview-block.js
    ├── position-progress-block.js
    ├── points-progress-block.js
    ├── match-day-points-block.js
    ├── match-day-averages-block.js
    ├── match-day-positions-block.js
    ├── points-vs-average-block.js
    ├── week-standings-block.js
    ├── honor-scores-block.js
    └── team-details-block.js
```

### Template Structure
```
app/templates/league/
├── stats.html                            # Clean, modular template
├── stats_original_backup.html            # Original 1426-line version
└── includes/                             # Template partials (if needed)
```

## Risk Mitigation

### Backup Strategy
- Keep original template as backup
- Implement progressive enhancement approach
- Maintain backward compatibility during transition

### Testing Strategy
- Test each phase independently
- Smoke test all functionality after each phase
- Compare performance before/after implementation

### Rollback Plan
- Original template preserved for quick rollback
- Modular approach allows partial rollback if needed
- Legacy functions preserved for compatibility

## Success Metrics

### Performance Targets
- **50%+ reduction** in unnecessary API calls
- **40%+ faster** filter interactions
- **Improved user feedback** with loading states

### Code Quality Targets
- **90%+ reduction** in template size
- **Modular architecture** with reusable components
- **Comprehensive documentation** and debug tools

## Next Steps

1. **Start with Phase 1**: Extract JavaScript modules from monolithic template
2. **Progressive implementation**: One phase at a time with testing
3. **Continuous validation**: Ensure functionality is preserved throughout
4. **Performance monitoring**: Measure improvements at each step

This refactoring will transform the league stats page from a 1426-line monolith into a clean, modular, high-performance system using the same proven architecture as the team stats page.