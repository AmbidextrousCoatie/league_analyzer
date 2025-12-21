# Data Schema Analysis & Database Design Discussion

**Date:** 2025-12-21  
**Purpose:** Analyze existing relational CSV schema and discuss database representation for Phase 2

---

## Executive Summary

This document analyzes the existing relational CSV schema (`league_analyzer_v1/database/relational_csv/`) and proposes how to represent the data in our clean architecture domain model. We'll discuss:

1. **Current Schema Structure** - What exists today
2. **Key Entities & Relationships** - Core domain concepts
3. **Events & Results** - How games/matches are represented
4. **Proposed Domain Model** - How to map to our entities
5. **Open Questions** - Decisions to make

---

## 1. Current Relational Schema Overview

### Core Tables

#### 1.1 League & Season Structure
- **`league`**: League definition (id, long_name, level, division)
- **`league_season`**: League + Season combination (id, league_id, season, scoring_system_id, number_of_teams, players_per_team)
- **`scoring_system`**: Points calculation rules (individual/team match win/tie/loss points)

#### 1.2 Organization Structure
- **`club`**: Bowling clubs/organizations (id, name, short_name)
- **`team_season`**: Team participation in a league season (id, league_season_id, club_id, team_number)
- **`player`**: Individual players (id, given_name, family_name, full_name, date_of_birth, dominant_hand)
- **`player_club_membership`**: Player-club relationships over time

#### 1.3 Venue & Location
- **`venue`**: Bowling alleys/venues (id, name, full_name, city, country, pinsetter)
- **`venue_name`**: Alternative names for venues

#### 1.4 Events & Results
- **`event`**: A game/match event (id, league_season_id, event_type, league_week, date, venue_id, oil_pattern_id, status, notes)
- **`game_result`**: Individual player results in an event (id, event_id, player_id, team_season_id, lineup_position, score, is_disqualified, round_number, match_number, handicap)

---

## 2. Key Entities & Relationships

### Entity Relationship Diagram (Conceptual)

```
League (1) ──< (N) LeagueSeason ──< (N) TeamSeason
                                              │
                                              │ (N)
                                              │
                                              ▼
                                          (N) Player
                                              │
                                              │ (N)
                                              │
                                              ▼
                                          GameResult
                                              │
                                              │ (1)
                                              │
                                              ▼
                                            Event
                                              │
                                              │ (1)
                                              │
                                              ▼
                                           Venue
```

### Key Relationships

1. **League → LeagueSeason**: One league has many seasons
2. **LeagueSeason → TeamSeason**: One season has many teams
3. **TeamSeason → Player**: Many players belong to a team (via game_result)
4. **Event → GameResult**: One event has many player results
5. **TeamSeason → GameResult**: One team has many results across events
6. **Player → GameResult**: One player has many results across events

---

## 3. Events & Results Structure

### Event Types

From the schema, events have:
- **`event_type`**: Currently "league" (could expand to "tournament", "playoff", etc.)
- **`league_week`**: Week number in the league season
- **`tournament_stage`**: For tournaments (e.g., "quarterfinal", "semifinal")
- **`date`**: When the event occurred
- **`venue_id`**: Where it happened
- **`status`**: "completed", "scheduled", "cancelled", etc.

### Game Result Structure

Each `game_result` represents:
- **Player**: Who played (player_id)
- **Team**: Which team they played for (team_season_id)
- **Position**: Lineup position (0-3, typically 4 players per team)
- **Score**: Actual pins knocked down
- **Handicap**: Optional handicap applied
- **Match Context**: round_number, match_number (for multi-match events)
- **Status**: is_disqualified flag

### Match Structure

**Important Observation**: The current schema doesn't have an explicit "Match" table. Instead:
- **`match_number`** in `game_result` groups results into matches
- **`round_number`** groups matches into rounds
- Multiple teams can play in the same event (same `event_id`)
- Teams are matched against each other via `match_number`

**Example Event Structure:**
```
Event #3 (BayL, Week 1, 2024-10-12)
├── Match 0: Team A vs Team B
│   ├── Team A Player 0: 166
│   ├── Team A Player 1: 183
│   ├── Team A Player 2: 202
│   ├── Team A Player 3: 226
│   ├── Team B Player 0: 191
│   ├── Team B Player 1: 212
│   ├── Team B Player 2: 214
│   └── Team B Player 3: 237
├── Match 1: Team C vs Team D
│   └── ... (similar structure)
└── Match 2: Team E vs Team F
    └── ... (similar structure)
```

---

## 4. Points Calculation

### Scoring Systems

Two systems are defined:
1. **`liga_bayern_2pt`**: 2-point system
   - Individual: Win=1, Tie=0.5, Loss=0
   - Team: Win=2, Tie=1, Loss=0
2. **`liga_bayern_3pt`**: 3-point system
   - Individual: Win=1, Tie=0.5, Loss=0
   - Team: Win=3, Tie=1.5, Loss=0

### Points Calculation Logic

From `business_logic/lib.py`, points are calculated:

1. **Individual Points**: Compare player scores at same position
   - Higher score → 1 point
   - Tie → 0.5 points each
   - Lower score → 0 points

2. **Team Points**: Sum all player scores, compare totals
   - Higher total → Team win points (2 or 3)
   - Tie → Team tie points (1 or 1.5)
   - Lower total → 0 points

**Note**: Points are **not stored** in `game_result` table - they're calculated on-the-fly.

---

## 5. Proposed Domain Model Mapping

### 5.1 Current Domain Entities (Phase 1)

We already have:
- ✅ **`League`** - Maps to `league` table
- ✅ **`Team`** - Maps to `team_season` table (simplified)
- ✅ **`Player`** - Maps to `player` table
- ✅ **`Game`** - Maps to `event` table (simplified)

### 5.2 Gaps & Mismatches

#### Gap 1: Event vs Game Concept
- **Current Domain**: `Game` entity represents a single match between two teams
- **Schema Reality**: `Event` represents a week/day where multiple matches occur
- **Question**: Should we introduce an `Event` entity, or keep `Game` as-is?

#### Gap 2: Match Numbering
- **Current Domain**: `Game` has `round_number` but no `match_number`
- **Schema Reality**: Events have multiple matches (match_number)
- **Question**: Do we need explicit Match entity, or is match_number enough?

#### Gap 3: Team-Season Relationship
- **Current Domain**: `Team` has `league_id` (simplified)
- **Schema Reality**: Teams belong to `team_season` (team + league_season)
- **Question**: Should we model `TeamSeason` as a separate entity?

#### Gap 4: Scoring System
- **Current Domain**: No scoring system abstraction
- **Schema Reality**: `scoring_system` table with configurable points
- **Question**: Should `ScoringSystem` be a value object or entity?

#### Gap 5: Venue/Club
- **Current Domain**: No venue or club entities
- **Schema Reality**: Venues and clubs are first-class entities
- **Question**: Do we need these in the domain model?

#### Gap 6: Handicap Storage
- **Current Domain**: Handicap calculated on-the-fly
- **Schema Reality**: Handicap stored in `game_result.handicap`
- **Question**: Should we store calculated handicap or always recalculate?

---

## 6. Proposed Architecture Decisions

### Decision 1: Event vs Game Hierarchy

**Option A: Event → Match → GameResult**
```
Event (league week, date, venue)
  └── Match (match_number, team_a, team_b)
      └── GameResult (player, position, score)
```

**Option B: Game → GameResult (Current)**
```
Game (event_id, match_number, team_a, team_b, week, date)
  └── GameResult (player, position, score)
```

**Recommendation**: **Option B** (keep current `Game` entity)
- Simpler for our use case
- Matches current domain model
- Can add `Event` later if needed

### Decision 2: Team-Season Modeling

**Option A: TeamSeason Entity**
```python
class TeamSeason:
    id: UUID
    team: Team
    league_season: LeagueSeason
    team_number: int
```

**Option B: Team with League/Season Context**
```python
class Team:
    id: UUID
    name: str
    league_id: UUID  # Current
    # Add: season: Season?
```

**Recommendation**: **Option A** (TeamSeason entity)
- More accurate to reality
- Teams can participate in multiple leagues/seasons
- Better for historical queries

### Decision 3: Scoring System

**Option A: Value Object**
```python
@dataclass(frozen=True)
class ScoringSystem:
    id: str
    individual_win: float
    individual_tie: float
    individual_loss: float
    team_win: float
    team_tie: float
    team_loss: float
```

**Option B: Entity**
```python
class ScoringSystem:
    id: UUID
    name: str
    # ... same fields
```

**Recommendation**: **Option A** (Value Object)
- Scoring rules don't change often
- Immutable configuration
- Can be referenced by LeagueSeason

### Decision 4: Venue & Club

**Question**: Are these domain entities or infrastructure concerns?

**Recommendation**: **Infrastructure Concern** (for now)
- Venues and clubs are reference data
- Can be added to domain later if business logic requires
- For now, store as simple strings/IDs

### Decision 5: Handicap Storage

**Option A: Store in GameResult**
- Matches current schema
- Faster queries
- Historical accuracy

**Option B: Calculate On-the-Fly**
- Always current
- Single source of truth
- More complex queries

**Recommendation**: **Option A** (Store in GameResult)
- Performance benefit
- Historical accuracy (handicap changes over time)
- Can still recalculate for validation

---

## 7. Proposed Database Schema (Domain Model)

### 7.1 Core Entities

```python
# League & Season
League (id, name, level, division)
LeagueSeason (id, league_id, season, scoring_system_id, number_of_teams, players_per_team)
ScoringSystem (id, name, individual_win, individual_tie, individual_loss, team_win, team_tie, team_loss)

# Organization
Club (id, name, short_name)
TeamSeason (id, league_season_id, club_id, team_number)
Player (id, given_name, family_name, full_name, date_of_birth, dominant_hand)

# Events & Results
Event (id, league_season_id, event_type, league_week, date, venue_id, status, notes)
Game (id, event_id, match_number, round_number, team_a_id, team_b_id, date)
GameResult (id, game_id, player_id, team_season_id, position, score, handicap, is_disqualified)
```

### 7.2 Key Differences from Current Domain

1. **Add `Event` entity**: Represents league week/day
2. **Add `TeamSeason` entity**: Team participation in specific season
3. **Add `ScoringSystem` value object**: Configurable points
4. **Add `Club` entity**: Organization structure
5. **Store `handicap` in GameResult**: Historical accuracy

---

## 8. Open Questions for Discussion

### Q1: Event vs Game Granularity
- Should `Game` represent a single match (team A vs team B)?
- Or should `Game` represent an event (all matches in a week)?
- **Current**: Game = single match
- **Proposal**: Keep as-is, add Event if needed

### Q2: Match Numbering
- Do we need explicit `Match` entity?
- Or is `match_number` in `Game` sufficient?
- **Proposal**: `match_number` in `Game` is sufficient

### Q3: Team Identity
- Is a team the same across seasons?
- Or is each season a new team?
- **Proposal**: TeamSeason represents team in a season

### Q4: Points Storage
- Calculate on-the-fly or store?
- **Proposal**: Calculate on-the-fly (matches current approach)

### Q5: Handicap Calculation
- Store calculated handicap or always recalculate?
- **Proposal**: Store in GameResult, recalculate for validation

### Q6: Venue/Club Domain Model
- Are these domain entities?
- Or just reference data?
- **Proposal**: Reference data for now, add to domain if needed

---

## 9. Next Steps

1. **Review & Discuss**: This document with team
2. **Decide on Architecture**: Event vs Game, TeamSeason, etc.
3. **Update Domain Model**: Add missing entities/value objects
4. **Design Repository Interfaces**: Based on final schema
5. **Implement Repositories**: Phase 2 work

---

## 10. References

- Schema Definition: `league_analyzer_v1/database/schema.json`
- Relational CSV: `league_analyzer_v1/database/relational_csv/`
- Points Calculation: `league_analyzer_v1/business_logic/lib.py`
- Current Domain: `domain/entities/`

---

**Ready for discussion!** 🎳

