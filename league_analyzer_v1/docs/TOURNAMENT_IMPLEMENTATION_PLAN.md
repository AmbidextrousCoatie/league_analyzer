# Tournament Implementation Plan - BC Donaubowler Clubmeisterschaft

## Overview
This document outlines the implementation plan for adding tournament functionality to the League Analyzer application. The tournament feature will support the "BC Donaubowler Clubmeisterschaft" - a multi-month off-season tournament where players compete individually across multiple series.

## Tournament Format
- **Name**: BC Donaubowler Clubmeisterschaft
- **Duration**: Several months during off-season
- **Structure**: Each player plays multiple series (e.g., 5 occasions) of bowling games (e.g., 4 games per series)
- **Scheduling**: Players choose their own dates for each series (max one series per date)
- **Handicap**: Players receive predetermined handicap (HDC) per game that remains constant
- **Ranking**: Based on average including handicap
- **Winner**: Determined by total pins + handicap (no fancy finale planned)

## Phase 1: Display and Analysis Features

### Frontend Views

#### Tournament Overview View
**Table Columns:**
- Rank, Player Name, HDC, Pins (incl. HDC) per occasion, Total Pins (including HDC), Total average (including HDC), Total pins (w/o HDC), Total average (w/o HDC)

**Example:**
```
1, Chris, 10, 1000, 950, 1050, 1000, 4000, 200.00, 3800, 190.00
2, Chross, 0, 900, 1200, -, -, 2100, 210.00, 2100, 210.00
```

**Charts:**
- Average progression over occasions (average after occasion #n)
- Accumulated pins over occasions

#### Individual Player View
**Table Columns:**
- Rank after occasion, Player Name, HDC, pins game #1, ... pins game #n, total pins (w HDC), average (w HDC), total pins (w/o HDC), average (w/o HDC)

**Example:**
```
1, Chris, 10, 180, 190, 200, 210, 220, 1000, 200.00, 950, 190.00
2, Chris, 10, 170, 180, 190, 200, 210, 950, 190.00, 900, 180.00
```

**Charts:**
- Average progression over occasions
- Accumulated pins over occasions
- Average by game position (e.g., average of 1st game across all occasions)

## Database Schema Analysis

### Existing Columns (Reusable)
- `player_name` - Player identification
- `player_id` - Unique player identifier  
- `score` - Individual game scores
- `date` - Game dates
- `input_data` - Raw input data
- `computed_data` - Computed statistics

### New Tournament-Specific Columns
- `event_type` - "league" | "tournament" (identifies event type)
- `event_name` - Generic event name (replaces league_name for broader use)
- `game_number` - Game within series (1-4) - reuses round_number concept  
- `handicap` - Per-game handicap for tournaments (e.g., Chris gets +10 pins per game)

### Schema Implementation Strategy
**Conservative Approach (Maintaining Backward Compatibility):**
- Keep existing `league_name` → "League" mapping for existing functionality
- Add new tournament-specific fields without breaking existing code
- Use existing `season`, `week`, `round_number` fields for tournament data
- Add minimal new columns: `event_type`, `event_name`, `game_number`, `handicap`

**Data Differentiation:**
- `event_type`: "league" vs "tournament" to distinguish data types
- Existing league data: `event_type = "league"`, `event_name = league_name`
- Tournament data: `event_type = "tournament"`, `event_name = "BC Donaubowler Clubmeisterschaft"`

**Computed Fields (Not Stored):**
- `series_total`, `series_average`, `cumulative_total`, `cumulative_average` calculated dynamically

## Backend Architecture

### New Service: TournamentService
**Pattern**: Follows existing `LeagueService` and `TeamService` patterns
**Dependencies**: Uses `DataAdapterFactory` for database abstraction
**Methods**:
- `get_tournament_standings()` - Overall tournament table
- `get_player_tournament_data(player_name)` - Individual player view
- `get_tournament_series_data()` - Series progression data
- `get_tournament_statistics()` - Tournament-wide statistics

### New Data Models
- `TournamentQuery` - Query parameters for tournament data
- `TournamentPlayerData` - Individual player tournament performance
- `TournamentResults` - Complete tournament standings and statistics

### New Routes: tournament_routes.py
- `/tournament/stats` - Main tournament view
- `/tournament/get_standings` - Tournament standings API
- `/tournament/get_player_data` - Individual player data API
- `/tournament/get_series_data` - Series progression data API

## Frontend Architecture

### Template Structure
- `app/templates/tournament/stats.html` - Main tournament view
- Follows existing league/team template patterns with modular content blocks

### Content Blocks
1. **Tournament Standings Block** - Overall tournament table
2. **Player Performance Block** - Individual player detailed view
3. **Series Progression Block** - Average progression over occasions
4. **Accumulated Pins Block** - Total pins progression over occasions
5. **Game Analysis Block** - Average by game position across occasions

### JavaScript Architecture
- `tournament-stats-app.js` - Main application coordinator
- `tournament-content-renderer.js` - Content block orchestration
- Individual content block files following existing patterns

## Implementation Requirements

### Navigation
- Create new "Clubmeister" view and add to navbar
- Prepare to use new database "db_club"
- Use existing functions for displaying tables and graphs
- Use existing interfaces (dataclasses) for backend data return
- Use same modular card approach as league and team views

### Database Integration
- Extend existing `Columns` class with tournament-specific fields
- Use `db_club` database configuration
- Leverage existing `DataAdapterFactory` for database abstraction

### Data Flow
1. **Tournament View**: Shows overall standings with all players
2. **Player Selection**: Click on player to see individual detailed view
3. **Dynamic Content**: Content blocks update based on selection state

### Chart Types
- **Line Charts**: Average progression over occasions
- **Bar Charts**: Accumulated pins over occasions  
- **Tables**: Tournament standings and individual player details

## Phase 2: Data Entry (Placeholder)
- Tournament data entry frontend
- Player registration system
- Series result input forms
- Handicap management interface

## Implementation Tasks

### Phase 1 Tasks
- [ ] **Database Schema Design** - Extend Columns class with tournament fields
- [ ] **Data Models** - Create tournament data models following existing patterns
- [ ] **Tournament Service** - Implement TournamentService class
- [ ] **Tournament Routes** - Create tournament routes blueprint
- [ ] **Tournament Templates** - Create tournament stats template with content blocks
- [ ] **Frontend JavaScript** - Implement tournament frontend with content blocks
- [ ] **Navigation Integration** - Add Clubmeister link to navbar
- [ ] **Database Setup** - Prepare db_club configuration

### Phase 2 Tasks (Placeholder)
- [ ] **Data Entry Frontend** - Tournament data input forms
- [ ] **Player Management** - Registration and handicap management
- [ ] **Series Input** - Game result entry system
- [ ] **Validation** - Data validation and error handling

## Key Benefits

1. **Consistency**: Follows existing architectural patterns
2. **Modularity**: Uses proven content block system
3. **Reusability**: Leverages existing table/chart components
4. **Scalability**: Easy to extend with additional tournament features
5. **Maintainability**: Clear separation of concerns

## Technical Considerations

### Database Schema Refactoring Impact
- Changing `league_name` to `event_name` affects existing code
- Need to maintain backward compatibility
- Consider migration strategy for existing data

### Performance Considerations
- Computed fields (totals, averages) calculated on-demand
- Consider caching for frequently accessed tournament data
- Index optimization for tournament queries

### UI/UX Considerations
- Consistent with existing league/team interfaces
- Responsive design for mobile devices
- Accessibility compliance

## Success Criteria

### Phase 1 Complete When:
- [ ] Tournament standings table displays correctly
- [ ] Individual player views show detailed performance
- [ ] Charts display progression data accurately
- [ ] Navigation integrates seamlessly
- [ ] Database switching works with db_club
- [ ] All existing functionality remains intact

### Phase 2 Complete When:
- [ ] Data entry forms are functional
- [ ] Player registration system works
- [ ] Handicap management is implemented
- [ ] Data validation prevents errors
- [ ] Tournament data can be fully managed through UI

---

*This document serves as the master plan for tournament implementation. Updates and progress tracking will be maintained in this file.*
