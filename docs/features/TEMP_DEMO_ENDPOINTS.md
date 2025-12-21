# Temporary Demo Endpoints

**Status:** ⚠️ TEMPORARY - Will be removed in Phase 2

## Overview

These endpoints demonstrate Phase 1 domain services (`StandingsCalculator` and `StatisticsCalculator`) working with test data. They are **temporary** and will be replaced when Phase 2 (Application Layer) is implemented.

## Endpoints

All endpoints are prefixed with `/api/temp/demo` to make it clear they are temporary.

### 1. Get League Standings
```
GET /api/temp/demo/standings
```

Returns league standings calculated using `StandingsCalculator` domain service.

**Response:**
```json
{
  "league_name": "Demo League",
  "season": "2024-25",
  "standings": [
    {
      "team_id": "...",
      "team_name": "Team Alpha",
      "position": 1,
      "total_score": 2280.0,
      "total_points": 4.0,
      "average_score": 190.0,
      "weekly_performances": [
        {
          "week": 1,
          "score": 780.0,
          "points": 2.0,
          "games": 4
        }
      ]
    }
  ],
  "note": "TEMPORARY DEMO ENDPOINT - Will be replaced in Phase 2"
}
```

### 2. Get Team Statistics
```
GET /api/temp/demo/team-statistics/{team_name}
```

Returns team statistics calculated using `StatisticsCalculator` domain service.

**Parameters:**
- `team_name`: Name of the team (e.g., "Team Alpha", "Team Beta", "Team Gamma")

**Response:**
```json
{
  "team_id": "...",
  "team_name": "Team Alpha",
  "total_score": 2280.0,
  "total_points": 4.0,
  "games_played": 12,
  "average_score": 190.0,
  "best_score": 210.0,
  "worst_score": 160.0,
  "weekly_performances": [...],
  "note": "TEMPORARY DEMO ENDPOINT - Will be replaced in Phase 2"
}
```

### 3. Get Player Statistics
```
GET /api/temp/demo/player-statistics/{player_name}
```

Returns player statistics calculated using `StatisticsCalculator` domain service.

**Parameters:**
- `player_name`: Name of the player (e.g., "Player 1A", "Player 2B", etc.)

**Response:**
```json
{
  "player_id": "...",
  "player_name": "Player 1A",
  "total_score": 570.0,
  "total_points": 1.5,
  "games_played": 3,
  "average_score": 190.0,
  "best_score": 200.0,
  "worst_score": 180.0,
  "note": "TEMPORARY DEMO ENDPOINT - Will be replaced in Phase 2"
}
```

### 4. Get Demo Data Structure
```
GET /api/temp/demo/demo-data
```

Returns the raw demo data structure (useful for debugging).

## Demo Page

A demo page is available at:
```
GET /demo
```

This page provides a visual interface to:
- View league standings
- View team statistics (select from dropdown)
- View player statistics (select from dropdown)

## Test Data

The demo endpoints use test data similar to the test fixtures in `tests/conftest.py`:

- **League:** "Demo League" (Season: 2024-25)
- **Teams:** Team Alpha, Team Beta, Team Gamma
- **Players:** 4 players per team (Player 1A-4A, Player 1B-4B, Player 1C-4C)
- **Games:** 4 games across 2 weeks

## Implementation Details

### Data Creation
The `create_demo_data()` function in `presentation/api/temp_demo_routes.py` creates:
- A league with 3 teams
- 12 players (4 per team)
- 4 games with realistic scores
- Player-to-team mapping

### Domain Services Used
- `StandingsCalculator.calculate_standings()` - Calculates league standings
- `StatisticsCalculator.calculate_team_statistics()` - Calculates team stats
- `StatisticsCalculator.calculate_player_statistics()` - Calculates player stats

## Removal Plan

When Phase 2 (Application Layer) is implemented:

1. ✅ Remove `presentation/api/temp_demo_routes.py`
2. ✅ Remove the router registration in `main.py`:
   ```python
   from presentation.api.temp_demo_routes import router as temp_demo_router
   app.include_router(temp_demo_router)
   ```
3. ✅ Remove the `/demo` route from `main.py`
4. ✅ Remove `league_analyzer_v1/app/templates/demo.html`
5. ✅ Remove this documentation file

## Notes

- These endpoints use test data only - no real database access
- All endpoints are clearly marked as TEMPORARY
- The demo page includes a warning banner
- All responses include a `note` field indicating they are temporary

