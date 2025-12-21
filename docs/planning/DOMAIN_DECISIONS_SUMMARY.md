# Domain Design Decisions Summary

**Date:** 2025-12-21  
**Status:** Decisions made for Phase 2 implementation

---

## Overview

This document summarizes the key design decisions made for Phase 2 domain model implementation. These decisions guide the entity design, repository interfaces, and application layer implementation.

---

## 1. Event Lifecycle States ✅

**Decision:** Event states are: `scheduled`, `preparing`, `in_progress`, `completed`, `cancelled`, `disputed`

**Implementation:**
- Add `status` field to `Event` entity
- Use enum or string values
- State transitions should be validated

**Code:**
```python
class EventStatus(Enum):
    SCHEDULED = "scheduled"
    PREPARING = "preparing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
```

---

## 2. Team Vacancy Handling ✅

**Decision:** `TeamSeason.vacancy_status` with values: `active`, `vacant`, `forfeit`

**Implementation:**
- Add `vacancy_status` field to `TeamSeason` entity
- Default: `active`
- Can be set to `vacant` or `forfeit` when team cannot participate

**Code:**
```python
class VacancyStatus(Enum):
    ACTIVE = "active"
    VACANT = "vacant"
    FORFEIT = "forfeit"

@dataclass
class TeamSeason:
    # ... existing fields
    vacancy_status: VacancyStatus = VacancyStatus.ACTIVE
```

---

## 3. Player Eligibility & Roster ✅

**Decision:** Simplified eligibility model for Phase 2

**Rules:**
- Player-to-club association comes from external DB
- **Current rule**: All players of a club are eligible for all teams of that club
- **Future rule** (placeholder): Will depend on:
  - Which team roster player was submitted to prior to season
  - Where player already played during season
  - Team switching conditions

**Implementation:**
- No separate `Roster` entity needed for Phase 2
- Eligibility check: `Player.club_id` matches `TeamSeason.club_id`
- Mock/placeholder for future roster logic

**Code:**
```python
def is_player_eligible_for_team(player: Player, team_season: TeamSeason) -> bool:
    """
    Check if player is eligible for team.
    
    Phase 2: Simple club-based eligibility
    Future: Will check roster submission and previous games
    """
    # Current: Club-based eligibility
    return player.club_id == team_season.club_id
    
    # Future: Add roster and game history checks
    # TODO: Implement roster-based eligibility
```

---

## 4. Score Entry Timing ✅

**Decision:** Support both real-time and batch score entry

**Implementation:**
- Real-time: Update `GameResult.score` during event
- Batch: Allow corrections after event completion
- Validation: Ensure scores are within valid range (0-300 for scratch)

**Code:**
```python
class GameResult:
    def update_score(self, new_score: Score) -> None:
        """Update score (can be called during or after event)"""
        # Validation
        if not (0 <= float(new_score) <= 300):
            raise InvalidScore(...)
        self.score = new_score
        self.updated_at = datetime.utcnow()
```

---

## 5. Standings Publication ✅

**Decision:** `Standings.status` with values: `provisional`, `final`, `disputed`

**Implementation:**
- Add `status` field to standings calculation result
- Default: `provisional` during season
- Can be set to `final` after event/season completion
- Can be set to `disputed` if there are issues

**Code:**
```python
class StandingsStatus(Enum):
    PROVISIONAL = "provisional"
    FINAL = "final"
    DISPUTED = "disputed"

@dataclass
class Standings:
    # ... existing fields
    status: StandingsStatus = StandingsStatus.PROVISIONAL
```

---

## 6. Handicap Management ✅

**Decision:** Focus on scratch league for Phase 2

**Rules:**
- Handicap can be added as rule to `league_season` definition (similar to scoring system)
- For Phase 2: Scratch scores only (no handicap)
- Handicap calculation logic deferred to later phase

**Implementation:**
- Add optional `handicap_settings` to `LeagueSeason`
- If `handicap_settings` is None → scratch scores only
- If `handicap_settings` is present → apply handicap (future)

**Code:**
```python
@dataclass
class LeagueSeason:
    # ... existing fields
    scoring_system_id: str
    handicap_settings: Optional[HandicapSettings] = None  # Optional for Phase 2
    
    def has_handicap_enabled(self) -> bool:
        """Check if handicap is enabled for this league season"""
        return self.handicap_settings is not None
```

---

## 7. Substitution Rules ✅

**Decision:** Simplified for Phase 2

**Rules:**
- All eligible players can appear in any match during season in any combination
- No explicit substitution tracking for Phase 2
- Mock placeholder for future complex substitution rules

**Implementation:**
- No `Substitution` entity needed for Phase 2
- Any eligible player can be assigned to any position in any match
- Placeholder for future substitution logic

**Code:**
```python
def assign_player_to_position(
    game: Game,
    player: Player,
    position: int,
    team_season: TeamSeason
) -> None:
    """
    Assign player to position in game.
    
    Phase 2: Simple assignment (no substitution tracking)
    Future: Will check substitution rules and history
    """
    # Current: Simple assignment
    if not is_player_eligible_for_team(player, team_season):
        raise InvalidPlayerAssignment(...)
    
    # TODO: Future - Check substitution rules
    # TODO: Future - Track substitution history
```

---

## 8. Disqualification Handling ✅

**Decision:** 
- `is_disqualified` flag on individual/team results
- Disqualification reason as free text attribute on event
- Should not happen often

**Implementation:**
- `GameResult.is_disqualified` (boolean)
- `Event.disqualification_reason` (optional string)
- Can be set at event level or result level

**Code:**
```python
@dataclass
class GameResult:
    # ... existing fields
    is_disqualified: bool = False

@dataclass
class Event:
    # ... existing fields
    disqualification_reason: Optional[str] = None
    
    def mark_disqualified(self, reason: str) -> None:
        """Mark event as having disqualifications"""
        self.disqualification_reason = reason
        self.status = EventStatus.DISPUTED
```

---

## Summary of Phase 2 Simplifications

### What We're Simplifying:
1. ✅ **Roster**: No separate roster entity, simple club-based eligibility
2. ✅ **Handicap**: Scratch scores only, handicap deferred
3. ✅ **Substitutions**: No tracking, any eligible player can play
4. ✅ **Eligibility**: Simple club-based check

### What We're Implementing:
1. ✅ **Event States**: Full lifecycle state management
2. ✅ **Vacancy Status**: Team vacancy tracking
3. ✅ **Score Entry**: Real-time and batch support
4. ✅ **Standings Status**: Provisional/final/disputed
5. ✅ **Disqualification**: Flags and reasons

### Future Enhancements (Post-Phase 2):
- Complex roster management
- Handicap calculation and application
- Substitution rules and tracking
- Team switching conditions
- Advanced eligibility rules

---

## Next Steps

1. **Update Domain Entities**: Add new fields based on decisions
2. **Create Value Objects**: EventStatus, VacancyStatus, StandingsStatus
3. **Update GameResult**: Add is_disqualified
4. **Update Event**: Add status, disqualification_reason
5. **Update TeamSeason**: Add vacancy_status
6. **Update LeagueSeason**: Add optional handicap_settings
7. **Create Eligibility Service**: Simple club-based check (with placeholder)

---

## References

- Domain Scopes: `docs/planning/DOMAIN_SCOPES_AND_LIFECYCLE.md`
- Data Schema: `docs/planning/DATA_SCHEMA_ANALYSIS.md`
- Current Entities: `domain/entities/`

---

**Decisions documented and ready for implementation!** 🎳

