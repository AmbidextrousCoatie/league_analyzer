# Responsive Data Display Specification

## Overview
This document defines what data components should be displayed for each filter combination and what API parameters are required.

## Filter Combinations

| ID | League | Season | Week | Team | Display Name |
|----|--------|--------|------|------|--------------|
| F1 | ✓      | ❌     | ❌   | ❌   | League Overview |
| F2 | ✓      | ✓      | ❌   | ❌   | Season Overview |
| F3 | ✓      | ✓      | ✓    | ❌   | Match Day View |
| F4 | ✓      | ✓      | ✓    | ✓    | Team Details |
| F5 | ✓      | ✓      | ❌   | ✓    | Team Season View |

## Data Components Specification

| Component ID | Display Name | Data Type | F1 | F2 | F3 | F4 | F5 | API Endpoint | Required Filters | Description |
|-------------|--------------|-----------|----|----|----|----|----|--------------|-----------------|-----------| 
| **AGGREGATION COMPONENTS (League-wide over time)** |
| AGG01 | League Averages History | Line Chart | ✓ | ❌ | ❌ | ❌ | ❌ | `/league/get_league_averages_history` | league | League average scores by season |
| AGG02 | Points to Win History | Line Chart | ✓ | ❌ | ❌ | ❌ | ❌ | `/league/get_points_to_win_history` | league | Points needed to win each season |
| AGG03 | Top Team Performances | Table | ✓ | ❌ | ❌ | ❌ | ❌ | `/league/get_top_team_performances` | league | Best team seasons (top 10 all-time, top 3 per season) |
| AGG04 | Top Individual Performances | Table | ✓ | ❌ | ❌ | ❌ | ❌ | `/league/get_top_individual_performances` | league | Best individual averages (top 10 all-time, top 5 per season) |
| AGG05 | Record Games | Table | ✓ | ❌ | ❌ | ❌ | ❌ | `/league/get_record_games` | league | Highest team/individual games per season and all-time |
| **SEASON COMPONENTS (Season-specific data)** |
| SEA01 | Season Timetable | Visual Timeline | ❌ | ✓ | ❌ | ❌ | ❌ | `/league/get_season_timetable` | league, season | Match day schedule with completion status |
| SEA02 | Final League Standings | Table | ❌ | ✓ | ❌ | ❌ | ❌ | `/league/get_league_history` | league, season | Final season standings |
| SEA03 | Individual Season Averages | Table | ❌ | ✓ | ❌ | ❌ | ❌ | `/league/get_individual_averages` | league, season | Player averages sorted by performance |
| SEA04 | Points Progress Chart | Line Chart | ❌ | ✓ | ❌ | ❌ | ✓ | `/league/get_team_points` | league, season | Cumulative points over season |
| SEA05 | Position Progress Chart | Line Chart | ❌ | ✓ | ❌ | ❌ | ✓ | `/league/get_team_positions` | league, season | Position changes over season |
| SEA06 | Points per Match Day | Scatter Chart | ❌ | ✓ | ❌ | ❌ | ✓ | `/league/get_team_points` | league, season | Weekly points distribution |
| SEA07 | Average Progress Chart | Line Chart | ❌ | ✓ | ❌ | ❌ | ✓ | `/league/get_team_averages` | league, season | Average scores over season |
| **MATCH DAY COMPONENTS (Week-specific data)** |
| MAT01 | Week Standings | Table | ❌ | ❌ | ✓ | ❌ | ❌ | `/league/get_league_week_table` | league, season, week | Current standings after specific week |
| MAT02 | Honor Scores | Cards/Lists | ❌ | ❌ | ✓ | ❌ | ❌ | `/league/get_honor_scores` | league, season, week | Top individual/team scores for week |
| **TEAM COMPONENTS (Team-specific data)** |
| TEA01 | Team Week Details (Classic) | Table | ❌ | ❌ | ❌ | ✓ | ❌ | `/league/get_team_week_details_table` | league, season, week, team | Classic team score sheet |
| TEA02 | Team Week Details (New) | Table | ❌ | ❌ | ❌ | ✓ | ❌ | `/league/get_team_individual_scores_table` | league, season, week, team | Individual player focus |
| TEA03 | Team Week Details (Head-to-Head) | Table | ❌ | ❌ | ❌ | ✓ | ❌ | `/league/get_team_week_head_to_head_table` | league, season, week, team | Head-to-head format |
| TEA04 | Team Season History | Table | ❌ | ❌ | ❌ | ❌ | ✓ | `/team/get_team_history` | team | Team's performance across seasons |
| TEA05 | Team Season Statistics | Charts | ❌ | ❌ | ❌ | ❌ | ✓ | Various team endpoints | team, season | Team-specific season analysis |

## Content Block Mapping

| Content Block | Components | Filter Combination |
|---------------|------------|-------------------|
| LeagueAggregationBlock | AGG01, AGG02, AGG03, AGG04, AGG05 | F1 (League only) |
| LeagueSeasonOverviewBlock | SEA01, SEA02, SEA03, SEA04, SEA05, SEA06 | F2 (League + Season) |
| MatchDayBlock | MAT01, MAT02 | F3 (League + Season + Week) |
| TeamDetailsBlock | TEA01, TEA02, TEA03 | F4 (League + Season + Week + Team) |
| TeamSeasonBlock | TEA04, TEA05, SEA04, SEA05, SEA06, SEA07 | F5 (League + Season + Team) |

## Implementation Priority

### Phase 1: Use Existing Endpoints
- SEA02 (League History) ✅ 
- SEA04 (Team Points) ✅
- SEA05 (Team Positions) ✅
- SEA07 (Team Averages) ✅
- MAT01 (Week Standings) ✅
- MAT02 (Honor Scores) ✅
- TEA01-TEA03 (Team Details) ✅

### Phase 2: Create New Endpoints
- SEA01 (Season Timetable)
- SEA03 (Individual Averages) 
- AGG01-AGG05 (All aggregation endpoints)
- TEA04-TEA05 (Team season analysis)

### Phase 3: Content Block Implementation
- Update existing blocks to match specification
- Create TeamSeasonBlock for F5 combination
- Remove old SeasonOverviewBlock (replaced by targeted blocks)

## API Parameter Standards

### Required Parameters by Endpoint Type
- **Aggregation**: `league`
- **Season**: `league`, `season`  
- **Match Day**: `league`, `season`, `week`
- **Team Week**: `league`, `season`, `week`, `team`
- **Team Season**: `league`, `season`, `team` OR `team`, `season`

### Response Format Standards
- **Tables**: TableData object with columns, data, config
- **Charts**: Object with data, labels, sorting info
- **Lists**: Array of objects with consistent properties

## Filter State Management

### State Object Structure
```javascript
{
  league: string | null,
  season: string | null, 
  week: string | null,
  team: string | null,
  database: string
}
```

### Visibility Rules
1. Only one primary content block should be visible at a time
2. Filter controls always visible
3. Content determined by most specific filter combination
4. Empty/null filters treated as "not selected"

## Error Handling Standards

### Missing Endpoints
- Log warning to console
- Show placeholder or hide component
- Don't break other components

### API Errors
- Graceful degradation
- User-friendly error messages
- Retry mechanisms where appropriate

### Data Validation
- Check response structure before rendering
- Handle empty datasets gracefully
- Validate required properties exist