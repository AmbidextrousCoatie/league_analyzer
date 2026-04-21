# Week 9 Scope Discussion: Team Queries & Commands

**Date:** 2025-01-19  
**Approach:** Test-Driven Development (TDD)  
**Goal:** Define scope, use cases, DTOs, and handlers before implementation

---

## Overview

Week 9 focuses on **Team-focused queries and commands**. We need to understand:
1. **Use cases** - What problems are we solving?
2. **Expected frontend data** - What should users see?
3. **Handlers** - What orchestration is needed?
4. **DTOs** - What data structures do we need?

---

## 1. GetTeamStatistics Query

### Use Case
**As a user, I want to see comprehensive statistics for a team across one or more seasons, so I can understand their overall performance.**

### Expected Frontend Data

**Top Graph: Team Progression Over Seasons**
- X-axis: Seasons (chronological)
- Y-axis: League level/position
- Shows: Which league the team finished in each season
- Visual: Line chart or bar chart showing league progression
- Highlights: Promotions (up), Relegations (down)

**Main Statistics Card:**
- Team name, club name
- Total games played (across all seasons/filtered)
- Total score (sum of all team scores)
- Average score per match
- **League average score** (for comparison) ⭐ NEW
- Best single match score
- Worst single match score
- Total points (team match points + individual points)
- Average points per match
- **Maximum points per match** (based on scoring system) ⭐ NEW
- **Points percentage** (average / maximum * 100) ⭐ NEW
- Win/Loss/Tie record

**Season Breakdown (if multiple seasons):**
- Per-season statistics
- League name and level for each season
- Final position in league
- Promotion/relegation indicators
- **League average for that specific league in that season** ⭐
- **Average points per match** (for that season)
- **Maximum points per match** (based on scoring system for that season)
- **Points percentage** (average_points / maximum_points * 100) ⭐

**Weekly Performance Chart:**
- Line/bar chart showing team score per week
- Points per week
- Win/Loss indicators

**Best/Worst Games Section:** ⭐ NEW
- **N Best Games** (N defaults to 5, parameterizable)
  - Score, league, season, opponent, date
  - Ordered by score (highest first)
- **N Worst Games** (N defaults to 5, parameterizable)
  - Score, league, season, opponent, date
  - Ordered by score (lowest first)
- **N Biggest Wins** (N defaults to 5, parameterizable)
  - Score difference, final score, league, season, opponent, date
  - Ordered by margin (largest first)
- **N Biggest Losses** (N defaults to 5, parameterizable)
  - Score difference, final score, league, season, opponent, date
  - Ordered by margin (largest first)

**Position Performance Section:** ⭐ NEW
- Average score per position (0-3)
- Win rate per position
- Total points per position
- Best/worst performing positions highlighted

**Recent Form Section:** ⭐ NEW
- Last N matches (N configurable, default 5)
- Form string (e.g., "WWLWW")
- Points earned in recent period
- Win rate in recent period

**Clutch Performance Section:** ⭐ NEW
- **Close Matches Summary** (matches within threshold M, defaults to 50 pins)
  - Total count of close matches
  - Total wins in close matches
  - Total losses in close matches
  - Total ties in close matches
  - Win rate in close matches
  - **Aggregated by opponent:** "4 wins, 3 losses against Team X @ threshold M"
  - **Note:** Exhaustive match list not needed, just aggregated counts
- **Histogram** (optional): Distribution of match margins
  - X-axis: Score difference ranges (e.g., 0-10, 11-20, etc.)
  - Y-axis: Number of matches

**Filters:**
- **All time** (default) / **Season** / **Season Week** ⭐ UPDATED
- League filter (specific league or all leagues)

### Query Parameters
```python
@dataclass
class GetTeamStatisticsQuery(Query):
    team_id: UUID  # Required: Which team?
    filter_type: str = "all_time"  # "all_time", "season", "season_week"
    season: Optional[str] = None  # Required if filter_type == "season" or "season_week"
    week: Optional[int] = None  # Required if filter_type == "season_week"
    league_id: Optional[UUID] = None  # Optional: Filter by league
    best_worst_count: int = 5  # Number of best/worst games to return (default: 5)
    clutch_threshold: int = 50  # Score difference threshold for "clutch" matches (default: 50)
```

### DTO Structure
```python
@dataclass
class SeasonProgressionDTO:
    """Single data point for team progression chart."""
    season: str
    league_id: UUID
    league_name: str
    league_level: int
    final_position: Optional[int]
    promotion: bool
    relegation: bool

@dataclass
class SeasonStatisticsDTO:
    """Statistics for a single season."""
    season: str
    league_id: UUID
    league_name: str
    league_level: int
    league_abbreviation: Optional[str]
    games_played: int
    total_score: int
    average_score: float
    league_average_score: float  # ⭐ League average for THIS specific league in THIS season
    best_score: int
    worst_score: int
    total_points: float
    average_points: float  # Points per match
    maximum_points_per_match: float  # ⭐ Based on scoring system for THIS season
    points_percentage: float  # ⭐ (average_points / maximum_points_per_match) * 100
    wins: int
    losses: int
    ties: int
    final_position: Optional[int]  # If season completed

@dataclass
class WeeklyPerformanceDTO:
    """Performance for a single week."""
    week: int
    season: str
    league_name: str
    total_score: int
    total_points: float
    matches_played: int
    wins: int
    losses: int
    ties: int

@dataclass
class GameRecordDTO:
    """Record of a single game (best/worst/biggest win/loss)."""
    match_id: UUID
    score: int
    opponent_score: Optional[int] = None  # For biggest win/loss
    score_difference: Optional[int] = None  # For biggest win/loss
    league_id: UUID
    league_name: str
    league_level: int
    season: str
    opponent_team_id: UUID
    opponent_team_name: str
    date: Optional[datetime] = None
    week: Optional[int] = None

@dataclass
class OpponentClutchSummaryDTO:
    """Clutch performance summary for a specific opponent."""
    opponent_team_id: UUID
    opponent_team_name: str
    wins: int
    losses: int
    ties: int
    total_close_matches: int
    win_rate: float

@dataclass
class ClutchPerformanceDTO:
    """Clutch performance statistics."""
    total_close_matches: int
    wins_in_close_matches: int
    losses_in_close_matches: int
    ties_in_close_matches: int
    win_rate_in_close_matches: float
    threshold: int  # Score difference threshold used
    opponent_summaries: List[OpponentClutchSummaryDTO]  # Aggregated by opponent
    # Note: Exhaustive match list not included - use separate "closest matches" query if needed

@dataclass
class PositionPerformanceDTO:
    """Performance statistics for a specific position (0-3)."""
    position: int
    games_played: int
    average_score: float
    total_points: float
    wins: int
    losses: int
    ties: int
    win_rate: float

@dataclass
class RecentFormDTO:
    """Recent form statistics (last N matches)."""
    last_n_matches: int  # N value used
    form_string: str  # e.g., "WWLWW"
    matches: List[GameRecordDTO]  # Last N matches
    points_in_period: float
    wins_in_period: int
    losses_in_period: int
    ties_in_period: int
    win_rate_in_period: float

@dataclass
class TeamStatisticsDTO:
    """Complete team statistics."""
    team_id: UUID
    team_name: str
    club_id: UUID
    club_name: str
    
    # Filter information
    filter_type: str  # "all_time", "season", "season_week"
    season: Optional[str] = None
    week: Optional[int] = None
    
    # Overall statistics (aggregated across filters)
    total_games_played: int
    total_score: int
    average_score: float
    league_average_score: float  # ⭐ Overall league average (weighted average across all seasons/leagues)
    best_score: int
    worst_score: int
    total_points: float
    average_points: float  # Overall average points per match
    # Note: maximum_points_per_match and points_percentage are per-season only (scoring systems can differ)
    total_wins: int
    total_losses: int
    total_ties: int
    
    # Team progression chart data
    season_progression: List[SeasonProgressionDTO]  # ⭐ NEW: For top graph
    
    # Per-season breakdown
    season_statistics: List[SeasonStatisticsDTO]
    
    # Weekly performance (for charts)
    weekly_performances: List[WeeklyPerformanceDTO]
    
    # Best/Worst games ⭐ NEW
    best_games: List[GameRecordDTO]
    worst_games: List[GameRecordDTO]
    biggest_wins: List[GameRecordDTO]
    biggest_losses: List[GameRecordDTO]
    
    # Clutch performance ⭐ NEW
    clutch_performance: ClutchPerformanceDTO
    
    # Position performance ⭐ NEW
    position_performance: List[PositionPerformanceDTO]
    
    # Recent form ⭐ NEW
    recent_form: RecentFormDTO
    
    calculated_at: datetime
```

### Handler Responsibilities
- Load team and club information
- Load all team seasons (filtered by filter_type/season/week/league if specified)
- Load all matches for those team seasons
- Load all game results and position comparisons
- Load scoring systems **per season** to determine maximum points per match
- **Calculate league averages per season** (for each league the team participated in, in that specific season)
- **Calculate overall league average** (weighted average across all seasons/leagues)
- Use `StatisticsCalculator` domain service for calculations
- Aggregate statistics across seasons
- Build season progression chart data
- Build weekly performance list
- Identify best/worst games and biggest wins/losses
- **Calculate clutch matches (within threshold) - aggregate by opponent, don't store exhaustive list**
- Calculate clutch performance statistics (aggregated counts)
- **Calculate position performance** (average score and win rate per position 0-3)
- **Calculate recent form** (last N matches, form string, points in period)
- Map to DTOs

### League Average Calculation Logic
- **Per Season:** Calculate league average for the specific league the team was in during that season
- **If team changes leagues:** Each season uses its own league's average (e.g., Season 1 in League A uses League A average, Season 2 in League B uses League B average)
- **Overall:** Weighted average across all seasons (accounting for different leagues)

### Shared Logic Note
- Clutch performance calculation shares logic with `GetClosestMatches` query
- Both use same low-level aggregation (calculate score differences)
- Clutch performance: aggregates by opponent
- Closest matches: sorts by margin
- **Extract shared logic into helper method** (can move to domain service later if reused)

### Repositories Needed
- `TeamRepository` - Get team info
- `ClubRepository` - Get club info
- `TeamSeasonRepository` - Get team seasons
- `LeagueSeasonRepository` - Get league season info
- `LeagueRepository` - Get league info
- `EventRepository` - Get events (for week mapping)
- `MatchRepository` - Get matches
- `GameResultRepository` - Get game results
- `PositionComparisonRepository` - Get position comparisons
- `MatchScoringRepository` - Get match scoring
- `ScoringSystemRepository` - Get scoring systems (for max points calculation)
- `StandingsCalculator` - Calculate league averages

---

## 2. GetTeamPerformance Query

### Use Case
**As a user, I want to see performance trends and metrics for a team over time, so I can identify patterns and improvements.**

**Note:** ⚠️ **OUT OF SCOPE FOR NOW** - Consistency metrics removed per user request. Focus on trends and streaks only.

### Expected Frontend Data

**Performance Metrics:**
- Average score trend (line chart over time)
- Points trend (line chart)
- Win rate trend
- ~~Consistency metrics~~ ⚠️ REMOVED (out of scope)
- Streak analysis (current win/loss streak, longest streaks)

**Performance Indicators:**
- Is team improving or declining?
- Best/worst periods
- Clutch performance (performance in close matches) - moved to GetTeamStatistics

**Comparison:**
- Team performance vs league average
- Team performance vs own historical average

### Query Parameters
```python
@dataclass
class GetTeamPerformanceQuery(Query):
    team_id: UUID
    filter_type: str = "all_time"  # "all_time", "season", "season_week"
    season: Optional[str] = None
    week: Optional[int] = None
    league_id: Optional[UUID] = None
    metric: str = "all"  # "score", "points", "win_rate", "all"
```

### DTO Structure
```python
@dataclass
class PerformanceTrendDTO:
    """Single data point in a trend."""
    week: int
    season: str
    value: float  # Score, points, or win rate
    matches_played: int

@dataclass
class StreakDTO:
    """Streak information."""
    current_streak_type: str  # "win", "loss", "tie"
    current_streak_length: int
    longest_win_streak: int
    longest_loss_streak: int

@dataclass
class TeamPerformanceDTO:
    """Complete team performance analysis."""
    team_id: UUID
    team_name: str
    
    # Trends
    score_trend: List[PerformanceTrendDTO]
    points_trend: List[PerformanceTrendDTO]
    win_rate_trend: List[PerformanceTrendDTO]
    
    # Streaks
    streaks: StreakDTO
    
    # Comparison
    vs_league_average: float  # Difference from league average
    vs_historical_average: float  # Difference from team's historical average
    
    calculated_at: datetime
```

### Handler Responsibilities
- Load team and matches (similar to GetTeamStatistics)
- Calculate trends over time
- Calculate streaks
- ~~Calculate consistency metrics~~ ⚠️ REMOVED
- Compare to league averages
- Compare to historical averages
- Map to DTOs

### Repositories Needed
- Same as GetTeamStatistics
- `StandingsCalculator` - For league averages

---

## 3. GetTeamHistory Query

### Use Case
**As a user, I want to see the complete history of a team across all seasons, including league changes, promotions, relegations, and achievements.**

### Expected Frontend Data

**Timeline View:**
- Chronological list of seasons
- League name and level for each season
- Final position in league
- Promotion/relegation indicators
- Season statistics summary

**Achievements:**
- League championships
- Best season performance
- Longest streaks
- Notable records

**League Progression:**
- Visual chart showing league level over time
- Promotion/relegation events highlighted

### Query Parameters
```python
@dataclass
class GetTeamHistoryQuery(Query):
    team_id: UUID
    include_statistics: bool = True  # Include detailed stats per season
```

### DTO Structure
```python
@dataclass
class SeasonHistoryDTO:
    """History entry for a single season."""
    season: str
    league_id: UUID
    league_name: str
    league_level: int
    league_abbreviation: Optional[str]
    final_position: Optional[int]
    total_games: int
    wins: int
    losses: int
    ties: int
    total_points: float
    average_score: float
    promotion: bool  # Promoted to higher league
    relegation: bool  # Relegated to lower league
    championship: bool  # Won the league

@dataclass
class AchievementDTO:
    """Achievement or record."""
    type: str  # "championship", "promotion", "best_score", "longest_streak"
    season: str
    description: str
    value: Optional[float] = None

@dataclass
class TeamHistoryDTO:
    """Complete team history."""
    team_id: UUID
    team_name: str
    club_id: UUID
    club_name: str
    
    # History timeline
    seasons: List[SeasonHistoryDTO]  # Ordered chronologically
    
    # Achievements
    achievements: List[AchievementDTO]
    
    # Summary statistics
    total_seasons: int
    total_games: int
    total_wins: int
    total_losses: int
    total_ties: int
    highest_league_level: int
    current_league_level: Optional[int]
    
    calculated_at: datetime
```

### Handler Responsibilities
- Load all team seasons (chronologically ordered)
- Load league information for each season
- Calculate final positions (using standings)
- Identify promotions/relegations (compare league levels)
- Identify championships (position == 1)
- Calculate achievements
- Aggregate summary statistics
- Map to DTOs

### Repositories Needed
- `TeamRepository`
- `ClubRepository`
- `TeamSeasonRepository`
- `LeagueSeasonRepository`
- `LeagueRepository`
- `EventRepository`
- `MatchRepository`
- `StandingsCalculator` - For final positions

---

## 4. GetTeamAnalysis Query

### Use Case
**As a user, I want to see deep analysis and insights about a team's performance, including strengths, weaknesses, and recommendations.**

### Expected Frontend Data

**Analysis Sections:**

1. **Strengths:**
   - What the team does well
   - Best performing positions
   - Best performing weeks/seasons

2. **Weaknesses:**
   - Areas for improvement
   - Underperforming positions
   - Problematic patterns

3. **Insights:**
   - Performance patterns
   - Consistency analysis
   - Trend analysis
   - Comparison insights

4. **Recommendations:**
   - Suggested improvements
   - Focus areas

### Query Parameters
```python
@dataclass
class GetTeamAnalysisQuery(Query):
    team_id: UUID
    season: Optional[str] = None  # Optional: Analyze specific season
    league_id: Optional[UUID] = None  # Optional: Analyze specific league
```

### DTO Structure
```python
@dataclass
class PositionAnalysisDTO:
    """Analysis for a specific position."""
    position: int
    average_score: float
    win_rate: float
    total_points: float
    strength_rating: str  # "strong", "average", "weak"

@dataclass
class StrengthDTO:
    """Identified strength."""
    category: str  # "position", "consistency", "clutch", etc.
    description: str
    evidence: str  # Supporting data

@dataclass
class WeaknessDTO:
    """Identified weakness."""
    category: str
    description: str
    evidence: str
    impact: str  # "high", "medium", "low"

@dataclass
class InsightDTO:
    """Performance insight."""
    type: str  # "trend", "pattern", "comparison"
    title: str
    description: str
    data: Dict[str, Any]  # Supporting data

@dataclass
class RecommendationDTO:
    """Recommendation for improvement."""
    priority: str  # "high", "medium", "low"
    category: str
    recommendation: str
    rationale: str

@dataclass
class TeamAnalysisDTO:
    """Complete team analysis."""
    team_id: UUID
    team_name: str
    
    # Position analysis
    position_analysis: List[PositionAnalysisDTO]
    
    # Strengths and weaknesses
    strengths: List[StrengthDTO]
    weaknesses: List[WeaknessDTO]
    
    # Insights
    insights: List[InsightDTO]
    
    # Recommendations
    recommendations: List[RecommendationDTO]
    
    # Overall assessment
    overall_assessment: str  # Summary text
    
    calculated_at: datetime
```

### Handler Responsibilities
- Load all team data (similar to GetTeamStatistics)
- Analyze position performance
- Identify patterns and trends
- Compare to league averages
- Generate insights using domain logic
- Generate recommendations
- Map to DTOs

### Repositories Needed
- Same as GetTeamStatistics
- `StatisticsCalculator` - For analysis calculations

---

## 5. CreateTeam Command

### Use Case
**As an administrator, I want to create a new team, so I can add teams to the system.**

### Expected Frontend Data

**Form Fields:**
- Team name (required)
- Club selection (required)
- Team number (required, default: 1)

**Success Response:**
- Created team ID
- Success message
- Team details

### Command Structure
```python
@dataclass
class CreateTeamCommand(Command):
    name: str
    club_id: UUID
    team_number: int = 1
```

### Handler Responsibilities
- Validate club exists
- Validate team name is not empty
- Validate team number is positive
- Check for duplicate team (same club + team number)
- Create Team entity
- Save via repository
- Return result DTO

### Repositories Needed
- `TeamRepository` - Create team
- `ClubRepository` - Validate club exists

---

## 6. UpdateTeam Command

### Use Case
**As an administrator, I want to update team information (name, club, team number), so I can correct or modify team data.**

### Expected Frontend Data

**Form Fields (all optional):**
- Team name
- Club selection
- Team number

**Success Response:**
- Updated team ID
- Success message
- Updated team details

### Command Structure
```python
@dataclass
class UpdateTeamCommand(Command):
    team_id: UUID
    name: Optional[str] = None
    club_id: Optional[UUID] = None
    team_number: Optional[int] = None
```

### Handler Responsibilities
- Validate team exists
- Validate club exists (if provided)
- Validate team name (if provided)
- Validate team number (if provided)
- Check for duplicates (if club/team_number changed)
- Update Team entity (use entity methods: `update_name()`, `assign_to_club()`, `update_team_number()`)
- Save via repository
- Return result DTO

### Repositories Needed
- `TeamRepository` - Update team
- `ClubRepository` - Validate club (if provided)

---

## 7. DeleteTeam Command

### Use Case
**As an administrator, I want to delete a team, so I can remove teams that are no longer active.**

### Expected Frontend Data

**Confirmation:**
- Team details for confirmation
- Warning about related data (team seasons, matches)

**Success Response:**
- Deleted team ID
- Success message

### Command Structure
```python
@dataclass
class DeleteTeamCommand(Command):
    team_id: UUID
    force: bool = False  # Force delete even if team has related data
```

### Handler Responsibilities
- Validate team exists
- Check for related data (team seasons, matches)
- If related data exists and force=False, raise error
- If force=True or no related data, delete team
- Return result DTO

### Repositories Needed
- `TeamRepository` - Delete team
- `TeamSeasonRepository` - Check for related team seasons
- `MatchRepository` - Check for related matches (indirectly via team seasons)

---

## Summary: DTOs Needed

### New DTOs to Create:
1. `TeamStatisticsDTO` + `SeasonStatisticsDTO` + `WeeklyPerformanceDTO` + `SeasonProgressionDTO` + `GameRecordDTO` + `ClutchPerformanceDTO` + `OpponentClutchSummaryDTO`
2. `TeamPerformanceDTO` + `PerformanceTrendDTO` + `StreakDTO`
3. `TeamHistoryDTO` + `SeasonHistoryDTO` + `AchievementDTO`
4. `TeamAnalysisDTO` + `PositionAnalysisDTO` + `StrengthDTO` + `WeaknessDTO` + `InsightDTO` + `RecommendationDTO`
5. `ClosestMatchesDTO` + `ClosestMatchDTO` ⭐ NEW

### Command Result DTOs:
- `CreateTeamResultDTO` (extends `CommandResultDTO`)
- `UpdateTeamResultDTO` (extends `CommandResultDTO`)
- `DeleteTeamResultDTO` (extends `CommandResultDTO`)

---

## Summary: Handlers Needed

1. `GetTeamStatisticsHandler` (includes clutch performance aggregation)
2. `GetTeamPerformanceHandler`
3. `GetTeamHistoryHandler`
4. `GetTeamAnalysisHandler`
5. `GetClosestMatchesHandler` ⭐ NEW (uses shared logic with clutch performance)
6. `CreateTeamHandler`
7. `UpdateTeamHandler`
8. `DeleteTeamHandler`

---

## Additional Suggestions

Based on the reference implementation and common analytics needs, here are additional features to consider:

### 1. **Position Performance Analysis** ⭐ SUGGESTED

**Intent:** Identify which positions (0-3) are team strengths vs weaknesses.

**What it shows:**
- Average score per position (e.g., Position 0 averages 210, Position 3 averages 180)
- Win rate per position (e.g., Position 0 wins 70% of matches, Position 3 wins 40%)
- Best/worst performing positions
- **Use Case:** Help team identify where they're strong (maybe Position 0-1) vs weak (maybe Position 3), so they can focus training/lineup changes

**Example:** "Your team's Position 0 averages 210 pins with 75% win rate (strong), but Position 3 averages 175 pins with 30% win rate (weak spot)"

**DTO:** `PositionPerformanceDTO` with position, average_score, win_rate, games_played, total_points

### 2. **Opponent Analysis** ⭐ SUGGESTED
- Win rate vs specific opponents
- Average score vs specific opponents
- **Use Case:** Understand team performance against different opponents
- **DTO:** `OpponentPerformanceDTO` with opponent_name, games_played, wins, losses, average_score

### 3. **Season Comparison** ⭐ SUGGESTED
- Compare current season to previous seasons
- Show improvement/decline indicators
- **Use Case:** Track team progress over time
- **DTO:** Already covered in `SeasonStatisticsDTO`, but could add comparison fields

### 4. **Match Timeline** ⭐ SUGGESTED
- Chronological list of all matches (with filters)
- Visual timeline showing wins/losses
- **Use Case:** See match history at a glance
- **DTO:** Could reuse `MatchWeekSummaryDTO` or create `MatchTimelineDTO`

### 5. **League Comparison** ⭐ SUGGESTED
- Team performance vs league average (already mentioned)
- Team ranking within league
- Percentile ranking
- **Use Case:** Understand team's position relative to league
- **DTO:** Add to `SeasonStatisticsDTO` or create separate `LeagueComparisonDTO`

### 6. **Home vs Away Performance** ⭐ SUGGESTED (if venue data available)
- Performance breakdown by venue
- Home advantage analysis
- **Use Case:** Understand venue impact on performance
- **Note:** Requires venue data in Event entity

### 7. **Recent Form** ⭐ SUGGESTED

**Intent:** Show how the team is performing RIGHT NOW (recent matches), not just overall statistics.

**What it shows:**
- Last N matches performance (N configurable, default 5)
- Form indicator string (e.g., "WWLWW" = Win, Win, Loss, Win, Win)
- Points earned in recent period
- Win rate in recent period
- **Use Case:** Quick indicator of current team momentum - are they on a hot streak or struggling recently? Helps understand if team is improving or declining.

**Example:** "Recent form: WWLWW (4 wins, 1 loss in last 5 matches) - 8.5 points in last 5 matches"

**DTO:** `RecentFormDTO` with last_n_matches, form_string (e.g., "WWLWW"), points_in_period, wins_in_period, losses_in_period, win_rate_in_period

### 8. **Milestones** ⭐ SUGGESTED
- First match date
- 100th match milestone
- 1000th point milestone
- **Use Case:** Celebrate team achievements
- **DTO:** `MilestoneDTO` with type, description, date, value

---

## Decisions Made ✅

1. **Position Performance:** ✅ **INCLUDED**
   - **Intent:** Identify which positions (0-3) are strengths vs weaknesses
   - Shows: Average score per position, win rate per position
   - **Use Case:** Help team identify where to focus training/lineup changes

2. **Recent Form:** ✅ **INCLUDED**
   - **Intent:** Show current team momentum (last N matches)
   - Shows: Form string (e.g., "WWLWW"), points in recent period, win rate
   - **Use Case:** Quick indicator of current performance trend

3. **Maximum Points:** ✅ **PER SEASON**
   - Calculate per season (scoring systems can differ)
   - Show both: `average_points` (points per match) AND `points_percentage` (percentage of maximum)

4. **League Average:** ✅ **PER SEASON + OVERALL**
   - **Per Season:** Calculate league average for the specific league in that specific season
   - **If team changes leagues:** Each season uses its own league's average
   - **Overall:** Weighted average across all seasons/leagues
   - **Priority:** Season-level is primary, overall is supplementary

5. **Shared Logic Extraction:** ✅ **HELPER METHOD**
   - Extract shared aggregation logic into helper method
   - Can move to domain service later if reused

---

## Remaining Questions

1. **GetTeamStatistics vs GetTeamPerformance:**
   - Should these be separate queries or combined?
   - **Proposal:** Keep separate - Statistics = raw data + records, Performance = trends/analysis

2. **GetTeamAnalysis complexity:**
   - How sophisticated should the analysis be?
   - **Proposal:** Start with basic analysis (position strengths, trends), expand later

3. **Team deletion:**
   - Should we soft-delete (mark as inactive) or hard-delete?
   - **Proposal:** Start with hard-delete, add soft-delete later if needed

4. **Filtering:**
   - All queries support: all_time / season / season_week ✅ AGREED
   - **Proposal:** Implement consistently across all queries

5. **Performance:**
   - Should we cache statistics calculations?
   - **Proposal:** No caching initially, optimize later if needed

---

## Implementation Order (TDD Approach)

### Phase 1: Commands (Simplest, Good TDD Practice)

1. **CreateTeam Command**
   - Write failing test
   - Implement handler
   - Refactor

2. **UpdateTeam Command**
   - Write failing test
   - Implement handler
   - Refactor

3. **DeleteTeam Command**
   - Write failing test
   - Implement handler
   - Refactor

### Phase 2: Core Statistics Query

4. **GetTeamStatistics Query** (foundation, most complex)
   - Write failing test for basic statistics
   - Implement basic handler
   - Add season progression chart
   - Add league averages
   - Add maximum points calculation
   - Add best/worst games
   - Add biggest wins/losses
   - Add clutch performance
   - Refactor

### Phase 3: Supporting Queries

5. **GetClosestMatches Query** ⭐ NEW (uses shared logic with clutch performance)
   - Write failing test
   - Extract shared aggregation logic
   - Implement handler (sorts by margin)
   - Refactor

6. **GetTeamHistory Query** (uses similar data)
   - Write failing test
   - Implement handler
   - Refactor

7. **GetTeamPerformance Query** (builds on statistics, simplified)
   - Write failing test
   - Implement handler (trends and streaks only)
   - Refactor

8. **GetTeamAnalysis Query** (most complex, uses others)
   - Write failing test
   - Implement handler
   - Refactor

---

## Next Steps

1. **Review and agree on scope**
2. **Clarify any questions**
3. **Start with CreateTeam Command** (TDD approach)
4. **Implement incrementally** (one handler at a time)

---

**Ready to proceed?** Let's start with `CreateTeam` command using TDD! 🚀
