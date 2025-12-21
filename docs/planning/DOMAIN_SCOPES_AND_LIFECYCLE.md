# Domain Scopes & Lifecycle Analysis

**Date:** 2025-12-21  
**Purpose:** Identify all scopes/phases in the bowling league domain and their data requirements

---

## Overview

The bowling league system operates across multiple scopes/phases, each with different concerns and data requirements. Understanding these scopes helps us design the domain model correctly.

---

## Identified Scopes

### 1. League/Tournament Preparation
**When:** Before season starts  
**Concerns:**
- When are events scheduled?
- Where do they take place (venues)?
- Which teams are part of which season?
- League configuration (scoring system, rules)
- Season calendar (weeks, dates)

**Data Requirements:**
- League definition
- League-season configuration
- Team registration for season
- Event scheduling
- Venue assignment
- Calendar/calendar management

**Key Questions:**
- Can teams join mid-season?
- Can events be rescheduled?
- Are there bye weeks?

---

### 2. Event Preparation
**When:** Before each event/match  
**Concerns:**
- Manage roster of teams that participate
- Are teams eligible?
- Is a team vacant?
- Player availability
- Lineup submission deadlines

**Data Requirements:**
- Team eligibility status
- Player availability
- Roster submission
- Vacancy tracking
- Lineup validation rules

**Key Questions:**
- When must lineups be submitted?
- What happens if a team can't field 4 players?
- Can players be substituted before the event starts?

---

### 3. During Event
**When:** Event is happening  
**Concerns:**
- Keep track of active roster
- Subbing / position changes
- Scores (real-time)
- Disqualifications
- Match progress

**Data Requirements:**
- Active roster (who's actually playing)
- Position assignments
- Score entry (real-time)
- Substitution tracking
- Disqualification records
- Match status (in-progress, completed)

**Key Questions:**
- Can players be substituted during the event?
- Can positions be changed?
- How are scores entered (real-time vs batch)?
- What triggers a disqualification?

---

### 4. During/After Event
**When:** During and after event completion  
**Concerns:**
- Finalize scores
- Calculate points
- Update standings
- Publish results
- Handle disputes

**Data Requirements:**
- Final scores
- Points calculation
- Standings update
- Result publication
- Dispute records

**Key Questions:**
- Can scores be corrected after event?
- How are disputes handled?
- When are standings published?
- Are there provisional vs final standings?

---

## Additional Scopes to Consider

### 5. Pre-Season Setup
**When:** Before league/tournament preparation  
**Concerns:**
- League creation/configuration
- Club registration
- Player registration
- Team formation
- Rule definition

**Data Requirements:**
- League creation
- Club management
- Player registration
- Team formation
- Rule configuration

**Key Questions:**
- How are leagues created?
- How are clubs registered?
- How are players registered?
- How are teams formed?

---

### 6. Post-Season / Archive
**When:** After season ends  
**Concerns:**
- Season closure
- Final standings
- Historical records
- Statistics compilation
- Archive preservation

**Data Requirements:**
- Final standings
- Historical records
- Statistics aggregation
- Archive data
- Season summary

**Key Questions:**
- How are seasons closed?
- What data is archived?
- How long are records kept?
- Are there season summaries?

---

### 7. Handicap Management
**When:** Throughout season  
**Concerns:**
- Handicap calculation
- Handicap updates
- Handicap validation
- Handicap history

**Data Requirements:**
- Handicap settings (per league/season)
- Handicap calculation rules
- Player handicap history
- Handicap application to scores

**Key Questions:**
- When are handicaps recalculated?
- How are handicaps applied?
- Can handicaps be manually adjusted?
- Is there handicap history?

---

### 8. Statistics & Analytics
**When:** Throughout and after season  
**Concerns:**
- Real-time statistics
- Historical statistics
- Performance trends
- Comparative analysis

**Data Requirements:**
- Player statistics
- Team statistics
- League statistics
- Historical comparisons
- Trend analysis

**Key Questions:**
- What statistics are tracked?
- How are statistics calculated?
- Are statistics real-time or batch?
- What comparisons are needed?

---

### 9. Match Scheduling & Pairings
**When:** Before and during season  
**Concerns:**
- Who plays whom?
- When do matches occur?
- Round-robin scheduling
- Tournament brackets

**Data Requirements:**
- Match pairings
- Schedule generation
- Round-robin logic
- Tournament bracket
- Bye weeks

**Key Questions:**
- How are matches scheduled?
- Is it round-robin or tournament?
- How are pairings determined?
- Can schedules be adjusted?

---

### 10. Validation & Rule Enforcement
**When:** Throughout all phases  
**Concerns:**
- Data validation
- Rule enforcement
- Eligibility checks
- Constraint validation

**Data Requirements:**
- Validation rules
- Business rules
- Eligibility criteria
- Constraint definitions

**Key Questions:**
- What rules need enforcement?
- When are validations performed?
- How are rule violations handled?
- Can rules be overridden?

---

### 11. Player Management
**When:** Throughout season  
**Concerns:**
- Player registration
- Player transfers
- Player availability
- Player injuries
- Player statistics

**Data Requirements:**
- Player registration
- Transfer records
- Availability status
- Injury records
- Player history

**Key Questions:**
- Can players transfer mid-season?
- How is availability tracked?
- Are injuries tracked?
- What player history is kept?

---

### 12. Team Management
**When:** Throughout season  
**Concerns:**
- Team composition
- Team changes
- Team vacancies
- Team statistics

**Data Requirements:**
- Team roster
- Roster changes
- Vacancy status
- Team history

**Key Questions:**
- Can teams change composition?
- How are vacancies handled?
- What team history is tracked?
- Can teams merge/split?

---

## Scope Interaction Matrix

| Scope | 1. Prep | 2. Event Prep | 3. During | 4. After | 5. Pre-Season | 6. Archive | 7. Handicap | 8. Stats | 9. Schedule | 10. Validation | 11. Player | 12. Team |
|-------|---------|---------------|-----------|----------|---------------|------------|-------------|----------|-------------|----------------|------------|----------|
| **1. League/Tournament Prep** | - | Creates events | - | - | Uses setup | - | Configures | - | Generates | Validates | Registers | Registers |
| **2. Event Preparation** | Uses schedule | - | Prepares | - | Uses setup | - | Checks | - | Uses | Validates | Checks | Checks |
| **3. During Event** | - | Uses prep | - | Records | - | - | Applies | Updates | - | Validates | Tracks | Tracks |
| **4. After Event** | - | - | Uses data | - | - | Archives | Updates | Calculates | - | Validates | Updates | Updates |
| **5. Pre-Season Setup** | Creates | - | - | - | - | - | Configures | - | - | Defines | Registers | Forms |
| **6. Archive** | - | - | - | Uses | - | - | Archives | Archives | Archives | - | Archives | Archives |
| **7. Handicap** | Configures | Checks | Applies | Updates | Configures | Archives | - | Uses | - | Validates | Tracks | - |
| **8. Statistics** | - | - | Updates | Calculates | - | Uses | Uses | - | - | - | Tracks | Tracks |
| **9. Scheduling** | Generates | Uses | - | - | - | - | - | - | - | Validates | Considers | Considers |
| **10. Validation** | Validates | Validates | Validates | Validates | Validates | - | Validates | - | Validates | - | Validates | Validates |
| **11. Player Mgmt** | Registers | Checks | Tracks | Updates | Registers | Archives | Tracks | Tracks | Considers | Validates | - | Assigns |
| **12. Team Mgmt** | Registers | Checks | Tracks | Updates | Forms | Archives | - | Tracks | Considers | Validates | Contains | - |

---

## Data Model Implications

### Entities Needed by Scope

**1. League/Tournament Preparation:**
- League, LeagueSeason, Event, Venue, TeamSeason

**2. Event Preparation:**
- TeamSeason, Player, Roster, Eligibility

**3. During Event:**
- Game, GameResult, ActiveRoster, Substitution

**4. After Event:**
- GameResult, Points, Standings

**5. Pre-Season Setup:**
- League, Club, Player, Team

**6. Archive:**
- All entities (read-only)

**7. Handicap Management:**
- HandicapSettings, HandicapHistory, Player

**8. Statistics:**
- All entities (aggregated)

**9. Scheduling:**
- Event, Match, Schedule

**10. Validation:**
- All entities (rules)

**11. Player Management:**
- Player, PlayerTransfer, Availability

**12. Team Management:**
- Team, TeamSeason, Roster, Vacancy

---

## Key Design Questions & Decisions

### Q1: Event Lifecycle States ✅ DECIDED
- **Decision**: `scheduled`, `preparing`, `in_progress`, `completed`, `cancelled`, `disputed`
- **Implementation**: `Event.status` field with enum/string values

### Q2: Team Vacancy Handling ✅ DECIDED
- **Decision**: `TeamSeason.vacancy_status` (active, vacant, forfeit)
- **Implementation**: Add `vacancy_status` field to `TeamSeason` entity

### Q3: Roster vs Active Roster ✅ DECIDED
- **Decision**: Simplified approach for now
  - Player-to-club association comes from external DB
  - Eligibility rules:
    - Initially: All players of a club eligible for all teams of that club
    - Future: Will depend on:
      - Which team roster player was submitted to prior to season
      - Where player already played during season
      - Team switching conditions (to be handled later)
- **Implementation**: 
  - For now: No separate Roster entity needed
  - Use `Player.club_id` → `TeamSeason.club_id` for eligibility
  - Mock placeholder for future roster logic

### Q4: Score Entry Timing ✅ DECIDED
- **Decision**: Support both (real-time during event, batch correction after)
- **Implementation**: 
  - Real-time: Update `GameResult.score` during event
  - Batch: Allow corrections after event completion

### Q5: Standings Publication ✅ DECIDED
- **Decision**: `Standings.status` (provisional, final, disputed)
- **Implementation**: Add `status` field to standings calculation result

### Q6: Handicap Management ✅ DECIDED
- **Decision**: Focus on scratch league for now
  - Handicap can be added as rule to `league_season` definition (similar to scoring system)
  - For Phase 2: Scratch scores only
- **Implementation**: 
  - Add `handicap_settings` to `LeagueSeason` (optional)
  - If present, apply handicap; if not, scratch scores only
  - Handicap calculation logic deferred to later phase

### Q7: Substitution Rules ✅ DECIDED
- **Decision**: Simplified for now
  - Assume all eligible players can appear in any match during season in any combination
  - Mock placeholder for future substitution logic
- **Implementation**: 
  - No explicit substitution tracking for Phase 2
  - Any eligible player can be assigned to any position in any match
  - Placeholder/mock for future complex substitution rules

### Q8: Disqualification Handling ✅ DECIDED
- **Decision**: 
  - `is_disqualified` flag on individual/team results
  - Disqualification reason as free text attribute on event
  - Should not happen often
- **Implementation**: 
  - `GameResult.is_disqualified` (boolean)
  - `Event.disqualification_reason` (optional string)
  - Can be set at event level or result level

---

## Proposed Domain Model Additions

Based on these scopes, we may need:

1. **Event Entity** (separate from Game)
   - Represents league week/day
   - Contains multiple Games/Matches

2. **Roster Entity**
   - Submitted roster for event
   - Links TeamSeason → Players → Positions

3. **ActiveRoster Entity**
   - Actual players during event
   - Can differ from submitted roster (substitutions)

4. **Substitution Entity**
   - Records of player substitutions
   - When, why, who replaced whom

5. **Eligibility Entity**
   - Player/team eligibility rules
   - Checks before event

6. **Vacancy Entity**
   - Team vacancy tracking
   - Status, reason, impact

7. **Disqualification Entity**
   - Disqualification records
   - Reason, impact on scores

8. **Schedule Entity**
   - Match scheduling
   - Pairings, dates, venues

9. **Standings Entity**
   - Calculated standings
   - Status (provisional/final)
   - Version/timestamp

10. **HandicapHistory Entity**
    - Historical handicap values
    - When calculated, what value

---

## Next Steps

1. **Prioritize Scopes**: Which scopes are most important for Phase 2?
2. **Define Entities**: Which entities are needed for MVP?
3. **Design Lifecycle**: How do entities transition through states?
4. **Define Rules**: What business rules apply to each scope?
5. **Design APIs**: What operations are needed for each scope?

---

## References

- Current Schema: `league_analyzer_v1/database/schema.json`
- Data Analysis: `docs/planning/DATA_SCHEMA_ANALYSIS.md`
- Domain Entities: `domain/entities/`

---

**Ready for discussion and prioritization!** 🎳

