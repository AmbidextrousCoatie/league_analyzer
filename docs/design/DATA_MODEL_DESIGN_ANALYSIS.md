# Data Model Design Analysis: Raw vs Processed Data Storage

## Current State

The current `Game` table mixes:
- **Raw data**: `score`, `handicap`, `is_disqualified`
- **Computed data**: `points` (calculated from comparing scores)
- **Redundant data**: `opponent_id`, `opponent_team_season_id` (can be derived from match context)

**Issues:**
1. Points are tied to a specific scoring system but stored directly
2. If scoring system changes, all points need recalculation
3. Opponent data is redundant (can be derived from match context)
4. No clear separation between immutable raw data and computed results
5. Team match results are computed on-the-fly, not stored

---

## Design Options

### Option 1: Separate Raw + Processed Tables

**Structure:**
```
GameResult (Raw - Immutable)
├── id
├── event_id
├── player_id
├── team_season_id
├── position
├── match_number
├── round_number
├── score (raw pins)
├── handicap
└── is_disqualified

GamePoints (Processed - Computed)
├── id
├── game_result_id (FK)
├── scoring_system_id (FK)
├── individual_points
├── opponent_game_result_id (FK, optional)
└── computed_at

MatchResult (Aggregated)
├── id
├── event_id
├── match_number
├── round_number
├── team1_team_season_id (FK)
├── team2_team_season_id (FK)
├── team1_total_score
├── team2_total_score
├── team1_total_points
├── team2_total_points
├── scoring_system_id (FK)
└── computed_at
```

**Pros:**
- ✅ Clear separation of concerns (raw vs computed)
- ✅ Raw data is immutable and preserved
- ✅ Can reprocess with different scoring schemes without losing original data
- ✅ Multiple scoring systems can coexist (historical comparison)
- ✅ Easier to audit/debug (see what was computed vs what was input)
- ✅ Team match results stored explicitly (no need to aggregate on-the-fly)
- ✅ Opponent relationship stored once in MatchResult, not duplicated per GameResult

**Cons:**
- ❌ More complex queries (requires joins)
- ❌ More tables to maintain
- ❌ Potential for data inconsistency if processing fails partway
- ❌ More storage overhead (though minimal)
- ❌ Need to ensure GamePoints/MatchResult stay in sync with GameResult

**Use Cases:**
- Historical data analysis with different scoring systems
- Auditing and compliance requirements
- Complex scoring systems that may change over time
- Need to compare "what if" scenarios

---

### Option 2: Single Table with Computed Columns

**Structure:**
```
Game (Current approach - enhanced)
├── id
├── event_id
├── player_id
├── team_season_id
├── position
├── match_number
├── round_number
├── score (raw)
├── handicap
├── is_disqualified
├── individual_points (computed)
├── scoring_system_id (FK) - tracks which system was used
└── opponent_id, opponent_team_season_id (removed - redundant)

Match (New - Aggregated)
├── id
├── event_id
├── match_number
├── round_number
├── team1_team_season_id
├── team2_team_season_id
├── team1_total_score
├── team2_total_score
├── team1_total_points
├── team2_total_points
└── scoring_system_id
```

**Pros:**
- ✅ Simpler queries (everything in one place for individual games)
- ✅ Easier to understand (less normalization)
- ✅ Atomic updates (raw + computed together)
- ✅ Less storage overhead
- ✅ Faster reads (no joins needed for basic queries)

**Cons:**
- ❌ Mixing raw and computed data (violates single responsibility)
- ❌ Harder to reprocess with different schemes (would need to overwrite)
- ❌ Risk of losing raw data if overwritten incorrectly
- ❌ Computed columns need to be kept in sync manually
- ❌ If scoring system changes, need to recalculate all historical data
- ❌ No easy way to compare "what if" scenarios

**Use Cases:**
- Simple applications with fixed scoring systems
- Performance-critical reads
- When storage is a concern
- When scoring systems rarely change

---

### Option 3: Hybrid Approach (RECOMMENDED)

**Structure:**
```
GameResult (Raw - Immutable)
├── id
├── event_id
├── player_id
├── team_season_id
├── position
├── match_number
├── round_number
├── score (raw pins)
├── handicap
└── is_disqualified

Match (Aggregated - Core Entity)
├── id
├── event_id
├── match_number
├── round_number
├── team1_team_season_id (FK)
├── team2_team_season_id (FK)
├── team1_total_score (computed, cached)
├── team2_total_score (computed, cached)
└── status (scheduled, in_progress, completed, cancelled)

MatchScoring (Processed - Scoring Results)
├── id
├── match_id (FK)
├── scoring_system_id (FK)
├── team1_individual_points (sum of individual game points)
├── team2_individual_points
├── team1_match_points (team match points: 2 or 3)
├── team2_match_points
├── computed_at
└── UNIQUE(match_id, scoring_system_id) -- one row per scoring system
```

**Key Design Decisions:**
1. **GameResult**: Pure raw data, immutable after creation
2. **Match**: Core entity that groups games, stores team totals (computed but cached)
3. **MatchScoring**: Stores scoring results per scoring system (allows multiple systems)
4. **Opponent relationship**: Stored in Match (team1 vs team2), not duplicated in GameResult

**Pros:**
- ✅ Clean separation: raw data separate from computed results
- ✅ Match is a first-class entity (matches are the core business concept)
- ✅ Multiple scoring systems supported without data duplication
- ✅ Team totals cached in Match (fast reads)
- ✅ Individual points computed on-demand or cached in MatchScoring
- ✅ Opponent relationship clear (team1 vs team2 in Match)
- ✅ Can reprocess scoring without touching raw data
- ✅ Simpler than Option 1 (no separate GamePoints table needed)

**Cons:**
- ❌ Slightly more complex than Option 2 (two tables instead of one)
- ❌ Need to ensure MatchScoring stays in sync
- ❌ Individual game points computed on-the-fly (or cached in MatchScoring)

**Use Cases:**
- **Best for most scenarios** - balances flexibility with simplicity
- When you need to support multiple scoring systems
- When matches are the primary business entity
- When you want to cache team totals for performance

---

## Recommendation: Option 3 (Hybrid)

### Round Robin Tournament Structure

**Understanding the Structure:**
- **League**: Contains n teams
- **Event** (Week/Day): One event per week/day
- **Round**: Within each event, there are (n-1) rounds of round-robin play
  - Each team plays every other team exactly once per event
  - Example: 4 teams → 3 rounds, 6 matches total (2 matches per round)
- **Match**: Two teams competing in a specific round
  - `match_number`: Identifies concurrent matches within a round (0, 1, 2, ...)
  - Multiple matches can occur simultaneously in the same round
- **GameResult**: Individual player's performance in a match
  - `position`: Player's lineup position (0-3, typically 4 players per team)
  - Position matters for individual point comparisons (Position 0 vs Position 0, etc.)

**Example Structure (4 teams, 1 event):**
```
Event #1 (Week 1, 2024-10-12)
├── Round 1
│   ├── Match 0: Team A vs Team B
│   │   ├── Team A: [Player 0: 166, Player 1: 183, Player 2: 202, Player 3: 226]
│   │   └── Team B: [Player 0: 191, Player 1: 212, Player 2: 214, Player 3: 237]
│   └── Match 1: Team C vs Team D
│       └── ...
├── Round 2
│   ├── Match 0: Team A vs Team C
│   └── Match 1: Team B vs Team D
└── Round 3
    ├── Match 0: Team A vs Team D
    └── Match 1: Team B vs Team C
```

**Scoring Logic:**
1. **Individual Points**: Compare players at same position
   - Position 0 vs Position 0: Winner gets 1 point (or 0.5 for tie)
   - Position 1 vs Position 1: Winner gets 1 point (or 0.5 for tie)
   - ... (for all positions)
   - Sum individual points → Team's individual point total
2. **Team Points**: Compare team totals (sum of all players' scores)
   - Team A total (166+183+202+226=777) vs Team B total (191+212+214+237=854)
   - Winner gets team match points (2 or 3, depending on scoring system)

### Rationale

1. **Matches are the core business entity** - Teams play matches, not individual games
2. **Scoring systems may change** - Historical data should support reprocessing
3. **Performance matters** - Caching team totals in Match avoids repeated aggregation
4. **Flexibility** - MatchScoring allows multiple scoring systems without duplicating GameResult
5. **Clean architecture** - Raw data separate from computed results
6. **Round-robin structure** - Matches are uniquely identified by (event, round_number, team1, team2)

### Implementation Strategy

**Phase 1: Create Match Entity**
- Extract match information from GameResult
- Create Match table with team1/team2 relationships
- Identify matches by (event_id, round_number, team1, team2)
- Migrate existing data

**Phase 2: Create MatchScoring**
- Compute scoring results per scoring system
- Store individual position-by-position comparisons
- Store team totals and team match points
- Support reprocessing when scoring system changes

**Phase 3: Clean up GameResult**
- Remove redundant opponent fields
- Remove individual_points (compute from MatchScoring or on-demand)
- Keep only raw, immutable data (score, position, handicap, etc.)

### Table Schemas

```sql
-- Raw game results (immutable)
-- Represents one player's performance in one match
CREATE TABLE game_result (
    id UUID PRIMARY KEY,
    match_id UUID NOT NULL REFERENCES match(id),  -- Links to match (which contains event_id)
    player_id UUID NOT NULL REFERENCES player(id),
    team_season_id UUID NOT NULL REFERENCES team_season(id),
    position INTEGER NOT NULL CHECK (position >= 0 AND position <= 3),
    score DECIMAL(6,1) NOT NULL CHECK (score >= 0),
    handicap DECIMAL(5,1),
    is_disqualified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    -- Ensure one result per player per match per position
    UNIQUE(match_id, player_id, position)
);

-- Match entity (core business concept)
-- Represents a match between two teams in a specific round
-- In round-robin: each team plays every other team once per event
CREATE TABLE match (
    id UUID PRIMARY KEY,
    event_id UUID NOT NULL REFERENCES event(id),
    round_number INTEGER NOT NULL CHECK (round_number >= 1),
    match_number INTEGER NOT NULL CHECK (match_number >= 0),  -- Concurrent match identifier
    team1_team_season_id UUID NOT NULL REFERENCES team_season(id),
    team2_team_season_id UUID NOT NULL REFERENCES team_season(id),
    team1_total_score DECIMAL(8,1) NOT NULL DEFAULT 0,  -- Sum of team1 player scores
    team2_total_score DECIMAL(8,1) NOT NULL DEFAULT 0,  -- Sum of team2 player scores
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled',  -- scheduled, in_progress, completed, cancelled
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    -- Unique constraint: one match per (event, round, team1, team2) combination
    -- Note: (A vs B) and (B vs A) are the same match, so we enforce team1 < team2 ordering
    UNIQUE(event_id, round_number, team1_team_season_id, team2_team_season_id),
    CHECK (team1_team_season_id != team2_team_season_id)
);

-- Individual position comparisons (for individual points)
-- Stores the result of comparing players at the same position
CREATE TABLE position_comparison (
    id UUID PRIMARY KEY,
    match_id UUID NOT NULL REFERENCES match(id),
    position INTEGER NOT NULL CHECK (position >= 0 AND position <= 3),
    team1_player_id UUID NOT NULL REFERENCES player(id),
    team2_player_id UUID NOT NULL REFERENCES player(id),
    team1_score DECIMAL(6,1) NOT NULL,
    team2_score DECIMAL(6,1) NOT NULL,
    -- Outcome: 'team1_win', 'team2_win', 'tie'
    outcome VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(match_id, position)
);

-- Scoring results per match and scoring system
-- Stores computed points based on a specific scoring system
CREATE TABLE match_scoring (
    id UUID PRIMARY KEY,
    match_id UUID NOT NULL REFERENCES match(id),
    scoring_system_id VARCHAR(50) NOT NULL REFERENCES scoring_system(id),
    -- Individual points: sum of position-by-position wins
    team1_individual_points DECIMAL(5,1) NOT NULL DEFAULT 0,
    team2_individual_points DECIMAL(5,1) NOT NULL DEFAULT 0,
    -- Team match points: based on team total comparison (2 or 3 points)
    team1_match_points DECIMAL(5,1) NOT NULL DEFAULT 0,
    team2_match_points DECIMAL(5,1) NOT NULL DEFAULT 0,
    computed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(match_id, scoring_system_id)
);

-- Indexes for performance
CREATE INDEX idx_game_result_match ON game_result(match_id);
CREATE INDEX idx_game_result_team ON game_result(team_season_id);
CREATE INDEX idx_game_result_player ON game_result(player_id);
CREATE INDEX idx_match_event_round ON match(event_id, round_number);
CREATE INDEX idx_match_teams ON match(team1_team_season_id, team2_team_season_id);
CREATE INDEX idx_position_comparison_match ON position_comparison(match_id);
CREATE INDEX idx_position_comparison_position ON position_comparison(position);
CREATE INDEX idx_match_scoring_match ON match_scoring(match_id);
CREATE INDEX idx_match_scoring_system ON match_scoring(scoring_system_id);
```

### Data Processing Flow

**Step 1: Ingest Raw Data**
- Create `game_result` records for each player's score
- Each record links to a `match_id` (match must exist first or be created)

**Step 2: Create/Update Match**
- Group `game_result` records by (event_id, round_number, team1, team2)
- Create `match` record if it doesn't exist
- Calculate and store `team1_total_score` and `team2_total_score` (sum of all player scores)

**Step 3: Create Position Comparisons**
- For each position (0-3) in the match:
  - Find team1's player at position X
  - Find team2's player at position X
  - Compare scores and determine outcome (team1_win, team2_win, tie)
  - Store in `position_comparison` table

**Step 4: Compute Scoring**
- For each scoring system:
  - Calculate individual points: Count wins/ties from `position_comparison`
  - Calculate team match points: Compare `team1_total_score` vs `team2_total_score`
  - Store results in `match_scoring` table

**Step 5: Query Results**
- Join `match` + `match_scoring` + `position_comparison` for complete match information
- Individual game results available via `game_result` table

### Migration Path

**Phase 1: Create New Tables**
1. Create `match` table
2. Create `position_comparison` table
3. Create `match_scoring` table
4. Create `game_result` table (or rename existing `Game` table)

**Phase 2: Migrate Existing Data**
1. Extract matches from existing `Game` records:
   - Group by (event_id, round_number, match_number, team_season_id pairs)
   - Create `match` records with team1/team2
   - Calculate team totals
2. Migrate `Game` records to `game_result`:
   - Link to `match_id` instead of storing event/round/match_number separately
   - Keep only raw data (score, position, handicap, is_disqualified)
3. Create `position_comparison` records:
   - For each match, compare players at same positions
   - Store outcomes
4. Compute and populate `match_scoring`:
   - Use league season's scoring system
   - Calculate individual and team points
   - Store results

**Phase 3: Update Application Code**
1. Update domain entities (`Match`, `MatchScoring`, `GameResult`)
2. Update repositories
3. Update domain services (scoring calculators)
4. Update API endpoints
5. Update frontend to display match-based data

**Phase 4: Cleanup**
1. Deprecate old `Game` table fields (opponent_id, opponent_team_season_id, points)
2. Remove redundant fields after migration is verified

---

## Decision Matrix

| Criteria | Option 1 | Option 2 | Option 3 (Hybrid) |
|----------|----------|----------|-------------------|
| **Simplicity** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Flexibility** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Performance** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Maintainability** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Scalability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Data Integrity** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Winner: Option 3 (Hybrid)** - Best balance across all criteria

---

## Next Steps

1. Review and approve design
2. Create entity classes for `Match` and `MatchScoring`
3. Create migration script to transform existing `Game` data
4. Update domain services to use new structure
5. Update API endpoints
6. Update frontend to display match-based data

