# GetTeamStatistics Implementation Dependencies

## Dependency Analysis

### 1. Basic Statistics (Foundation)
**Dependencies:**
- Matches (via `match_repo.get_by_team()`)
- GameResults (via `game_result_repo.get_by_match()`)
- PositionComparisons (via `position_comparison_repo.get_by_match()`)
- ScoringSystem (via `scoring_system_repo.get_by_id()`)

**Output:**
- Total games played
- Total score, average score
- Total points, average points
- Wins, losses, ties

**Complexity:** Low
**Order:** 1 (Foundation)

---

### 2. Best/Worst Games
**Dependencies:**
- Matches (already loaded)
- GameResults (already loaded)
- League info (for DTO)
- Opponent info (for DTO)

**Logic:**
- Sort matches by team score (descending for best, ascending for worst)
- Take top N

**Complexity:** Low
**Order:** 2 (Simple, uses basic stats data)

---

### 3. Biggest Wins/Losses
**Dependencies:**
- Matches (already loaded)
- GameResults (already loaded)
- Calculate score differences

**Logic:**
- Calculate score difference per match
- Sort by difference (descending for wins, ascending for losses)
- Take top N

**Complexity:** Low
**Order:** 3 (Simple, uses basic stats data)

---

### 4. Position Performance
**Dependencies:**
- PositionComparisons (already loaded)
- GameResults (already loaded)
- ScoringSystem (already loaded)

**Logic:**
- Group by position (0-3)
- Calculate wins/losses/ties per position
- Calculate average score per position
- Calculate total points per position

**Complexity:** Medium
**Order:** 4 (Uses position comparisons)

---

### 5. Recent Form
**Dependencies:**
- Matches (sorted by date)
- PositionComparisons (for win/loss/tie)
- Events (for date)

**Logic:**
- Sort matches by date (descending)
- Take last N matches
- Build form string (W/L/T)
- Calculate points in period

**Complexity:** Medium
**Order:** 5 (Needs sorted matches)

---

### 6. Weekly Performance
**Dependencies:**
- Events (for week mapping)
- Matches (grouped by week)
- GameResults (per week)
- PositionComparisons (per week)

**Logic:**
- Map events to weeks
- Group matches by week
- Aggregate scores and points per week
- Count wins/losses/ties per week

**Complexity:** Medium
**Order:** 6 (Needs events for week mapping)

---

### 7. Clutch Performance
**Dependencies:**
- Matches (already loaded)
- GameResults (already loaded)
- PositionComparisons (for win/loss/tie)
- Opponent info (for aggregation)

**Logic:**
- Calculate score difference per match
- Filter matches within threshold
- Count wins/losses/ties in close matches
- Aggregate by opponent

**Complexity:** Medium
**Order:** 7 (Reuses win/loss logic)

---

### 8. Season Progression
**Dependencies:**
- TeamSeasons (already loaded)
- LeagueSeasons (for league info)
- League (for level, name)
- Standings (for final positions) - OR calculate from matches

**Logic:**
- Group team seasons by season
- Get league info for each season
- Calculate final position (from standings or matches)
- Determine promotions/relegations

**Complexity:** Medium-High
**Order:** 8 (Needs league info and positions)

---

### 9. Per-Season Statistics
**Dependencies:**
- Everything from basic stats (per season)
- League averages (needs all matches in league season)
- ScoringSystem (per season, for max points)

**Logic:**
- Group matches by season
- Calculate stats per season
- Calculate league average per season (all teams in league)
- Calculate max points per match (from scoring system)
- Calculate points percentage

**Complexity:** High
**Order:** 9 (Most complex, needs league averages)

---

## Implementation Order Summary

1. ✅ Basic Statistics (Foundation)
2. Best/Worst Games (Simple)
3. Biggest Wins/Losses (Simple)
4. Position Performance (Medium)
5. Recent Form (Medium)
6. Weekly Performance (Medium)
7. Clutch Performance (Medium)
8. Season Progression (Medium-High)
9. Per-Season Statistics (High)

## Missing Repository

The handler needs `EventRepository` for:
- Weekly performance (week mapping)
- Recent form (date sorting)

Add to handler constructor.
