# URI Design Strategy for Multi-Context Resources

**Date:** 2025-01-27  
**Context:** Players compete in different teams over time and may participate in tournaments

---

## Problem Statement

Players are **independent entities** that:
- Move between teams over time
- Change clubs over time
- Compete in leagues (regular season)
- Compete in tournaments (special events)
- Have results across multiple contexts

**Challenge:** Design URI patterns that support flexible querying across all these contexts.

---

## Domain Model Context

### Current Domain Support
- ✅ `Event.event_type` can be "league" or "tournament"
- ✅ `ClubPlayer` tracks club memberships over time (date_entry, date_exit)
- ✅ `GameResult` links players to `team_season_id` (can change over time)
- ✅ Players can have results in multiple leagues/seasons

### Key Relationships
```
Player → ClubPlayer → Club (membership over time)
Player → GameResult → TeamSeason (team assignments over time)
Player → GameResult → Event → LeagueSeason (league participation)
Player → GameResult → Event (event_type: "tournament") (tournament participation)
```

---

## URI Design Principles

### 1. **Resource Hierarchy**
- Top-level resources: `/leagues`, `/clubs`, `/players`, `/tournaments`
- Sub-resources follow natural hierarchy
- Use query parameters for filtering, not path segments

### 2. **Context Flexibility**
- Support multiple entry points (player-centric, club-centric, league-centric)
- Allow filtering by any relevant context
- Don't force a single "primary" context

### 3. **RESTful Best Practices**
- Resources are nouns
- Hierarchical paths reflect relationships
- Query parameters for filtering/options
- Consistent patterns across similar resources

---

## Recommended URI Patterns

### **League Domain** (League-wide queries)

```
# League standings (current)
/leagues/{abbreviation}/standings?season=25/26
/leagues/{abbreviation}/standings?season=25/26&week=1

# League standings filtered by club (optional)
/leagues/{abbreviation}/standings?season=25/26&club={slug}

# League history
/leagues/{abbreviation}/history?seasons=24/25,25/26
```

**Rationale:** League is the primary resource, club is optional filter.

---

### **Team Domain** (Team-specific queries)

```
# Team score sheet (current - club-centric entry)
/clubs/{slug}/teams/{number}/seasons/{season}/score-sheet
/clubs/{slug}/teams/{number}/seasons/{season}/score-sheet?week=1

# Team statistics
/clubs/{slug}/teams/{number}/seasons/{season}/stats

# Team history (all seasons)
/clubs/{slug}/teams/{number}/history

# Alternative: League-centric team lookup (if needed)
/leagues/{abbreviation}/seasons/{season}/teams/{club-slug}/{number}/score-sheet
```

**Rationale:** Teams belong to clubs, so club-centric entry makes sense. League-centric alternative available if needed.

---

### **Player Domain** (Player-specific queries) ⭐ **KEY FOCUS**

#### **Option A: Player-Centric (Recommended)**

```
# Player overview (all contexts)
/players/{id}/overview

# Player stats filtered by context
/players/{id}/stats?season=25/26
/players/{id}/stats?league={abbreviation}&season=25/26
/players/{id}/stats?team={club-slug}/{number}&season=25/26
/players/{id}/stats?tournament={tournament-id}
/players/{id}/stats?club={slug}&season=25/26

# Player history (all teams/clubs/leagues)
/players/{id}/history
/players/{id}/teams  # List all teams player has played for
/players/{id}/clubs  # List all clubs player has been member of
/players/{id}/leagues  # List all leagues player has competed in
/players/{id}/tournaments  # List all tournaments player has competed in

# Player stats for specific league
/players/{id}/leagues/{abbreviation}/stats?season=25/26

# Player stats for specific tournament
/players/{id}/tournaments/{tournament-id}/stats

# Player stats for specific team (historical)
/players/{id}/teams/{club-slug}/{number}/stats?season=25/26
```

**Rationale:** 
- Player is independent entity, deserves top-level resource
- Flexible filtering via query parameters
- Supports all contexts (league, tournament, team, club)

#### **Option B: Club-Centric Player Entry (Alternative)**

```
# Player stats via club entry point
/clubs/{slug}/players/{id}/stats?season=25/26
/clubs/{slug}/players/{id}/stats?league={abbreviation}&season=25/26
/clubs/{slug}/players/{id}/history

# Cross-club player lookup (if player moved clubs)
/players/{id}/stats?club={slug}&season=25/26
```

**Rationale:**
- Works if most queries start from club context
- Still supports player-centric queries
- More consistent with team pattern

**Recommendation:** Use **Option A** (player-centric) as primary, with club-centric as alternative entry point.

---

### **Tournament Domain** (Tournament-specific queries)

```
# Tournament standings
/tournaments/{tournament-id}/standings

# Tournament player stats
/tournaments/{tournament-id}/players/{id}/stats

# Tournament team stats
/tournaments/{tournament-id}/teams/{club-slug}/{number}/stats

# All tournaments
/tournaments
/tournaments?season=25/26
/tournaments?club={slug}
```

**Rationale:** Tournaments are distinct from leagues, deserve own resource path.

---

## Query Parameter Conventions

### **Common Parameters**
- `season` - Filter by season (e.g., "25/26", "2025-26")
- `league` - Filter by league abbreviation
- `club` - Filter by club slug
- `team` - Filter by team (format: "{club-slug}/{number}")
- `tournament` - Filter by tournament ID
- `week` - Filter by week number
- `from_date`, `to_date` - Date range filter

### **Examples**
```
# Player stats across all contexts in season 25/26
/players/{id}/stats?season=25/26

# Player stats for specific league and season
/players/{id}/stats?league=bayl&season=25/26

# Player stats for specific team in season
/players/{id}/stats?team=bk-muenchen/3&season=25/26

# Player stats for tournament
/players/{id}/stats?tournament={tournament-id}

# Player stats filtered by club and date range
/players/{id}/stats?club=bk-muenchen&from_date=2025-01-01&to_date=2025-12-31
```

---

## Implementation Strategy

### **Phase 1: Current Implementation** ✅
- League routes: `/leagues/{abbreviation}/standings`
- Team routes: `/clubs/{slug}/teams/{number}/seasons/{season}/score-sheet`

### **Phase 2: Player Routes** (Next)
- Implement player-centric routes: `/players/{id}/stats`
- Support filtering by league, team, tournament, season
- Add player history endpoints

### **Phase 3: Tournament Routes** (Future)
- Implement tournament routes: `/tournaments/{id}/standings`
- Support tournament-specific queries

### **Phase 4: Cross-Domain Queries** (Future)
- Club overview: `/clubs/{slug}/overview?season=25/26`
- League overview: `/leagues/{abbreviation}/overview?season=25/26`

---

## Comparison: Player-Centric vs Club-Centric

### **Player-Centric** (Recommended)
```
✅ Pros:
- Player is independent entity
- Supports players moving between clubs/teams
- Natural for tournament queries (no club context)
- Flexible filtering
- Clear resource hierarchy

❌ Cons:
- Requires player ID lookup (but slug can be added)
- Less intuitive if most queries start from club
```

### **Club-Centric** (Alternative)
```
✅ Pros:
- Consistent with team pattern
- Natural entry point if club is primary context
- Easier navigation from club page

❌ Cons:
- Awkward for players who moved clubs
- Tournament queries don't fit well
- Less flexible
```

---

## Final Recommendation

### **Primary Pattern: Player-Centric**

```
/players/{id}/stats?{filters}
/players/{id}/history
/players/{id}/teams
/players/{id}/clubs
/players/{id}/leagues
/players/{id}/tournaments
```

### **Alternative Entry Points** (for convenience)

```
# Club-centric (for club pages)
/clubs/{slug}/players/{id}/stats?season=25/26

# League-centric (for league pages)
/leagues/{abbreviation}/players/{id}/stats?season=25/26

# Tournament-centric (for tournament pages)
/tournaments/{tournament-id}/players/{id}/stats
```

### **Slug Support** (for human-readable URLs)

```
# Add player slug resolution
/players/{slug}/stats  # Resolve slug → player_id
/players/{slug}/history
```

---

## Example Use Cases

### **Use Case 1: Player moved between teams**
```
# Player's complete history
GET /players/{id}/history

# Player's stats for team A in season 24/25
GET /players/{id}/stats?team=club-a/1&season=24/25

# Player's stats for team B in season 25/26
GET /players/{id}/stats?team=club-b/2&season=25/26
```

### **Use Case 2: Player in tournament**
```
# Player's tournament stats
GET /players/{id}/stats?tournament={tournament-id}

# Or via tournament entry point
GET /tournaments/{tournament-id}/players/{id}/stats
```

### **Use Case 3: Player across multiple leagues**
```
# Player's stats in BayL
GET /players/{id}/stats?league=bayl&season=25/26

# Player's stats in LL N1
GET /players/{id}/stats?league=ll-n1&season=25/26

# Player's stats across all leagues
GET /players/{id}/leagues
```

### **Use Case 4: Club wants to see all player stats**
```
# Via club entry point
GET /clubs/{slug}/players/{id}/stats?season=25/26

# Or via player entry point with club filter
GET /players/{id}/stats?club={slug}&season=25/26
```

---

## Migration Path

1. **Keep current routes** (league, team) ✅
2. **Add player routes** with flexible filtering
3. **Add tournament routes** when tournament support is added
4. **Add slug resolution** for players (similar to clubs)
5. **Add alternative entry points** as needed for UX

---

## Summary

**Key Decision:** Use **player-centric routes** (`/players/{id}/...`) as primary pattern, with flexible query parameter filtering for all contexts (league, team, club, tournament).

**Rationale:** Players are independent entities that move between contexts, so they deserve top-level resource status with flexible filtering rather than being nested under a single context.
