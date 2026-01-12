# Phase 3 Implementation Guide: Application Layer - CQRS

**Date:** 2025-01-07  
**Status:** Implementation Guide  
**Approach:** Use Case Driven → Queries & Commands

---

## Overview

Phase 3 implements the Application Layer using CQRS (Command Query Responsibility Segregation). The key principle: **Derive queries and commands from use cases**.

---

## Implementation Strategy

### Step 1: Identify Use Cases

Start by identifying what users need to do:

#### Read Use Cases (Queries)
1. **View League Standings** - See current league rankings
2. **View League History** - See how standings changed over time
3. **View Game Overview** - See match results and details
4. **View League Week Table** - See standings for a specific week
5. **View Season League Standings** - See standings for a specific season
6. **View Team Week Details** - See team performance for a specific week
7. **View Team vs Team Comparison** - Compare two teams head-to-head
8. **View Team Statistics** - See overall team performance
9. **View Team Performance** - See team performance trends
10. **View Team History** - See team's historical performance
11. **View Team Analysis** - See detailed team analysis
12. **View Player Statistics** - See player performance
13. **View Player Performance** - See player performance trends

#### Write Use Cases (Commands)
1. **Create Game** - Add a new game/match
2. **Update Game** - Modify an existing game
3. **Delete Game** - Remove a game
4. **Create Team** - Add a new team
5. **Update Team** - Modify an existing team
6. **Delete Team** - Remove a team
7. **Create Player** - Add a new player
8. **Update Player** - Modify an existing player
9. **Import Excel** - Import data from Excel file

---

## Step-by-Step Implementation

### Week 7: Start with First Use Case

**Recommended Starting Point:** `GetLeagueStandings`

This is a good first query because:
- It's a core use case
- Uses existing domain services (`StandingsCalculator`)
- Relatively straightforward
- Provides immediate value

#### Implementation Steps:

1. **Define the Query**
   ```python
   # application/queries/league/get_league_standings_query.py
   @dataclass(frozen=True)
   class GetLeagueStandingsQuery(Query):
       league_id: UUID
       season: Optional[str] = None
       week: Optional[int] = None
   ```

2. **Define the Response DTO**
   ```python
   # application/dto/league_dto.py
   @dataclass
   class LeagueStandingsDTO:
       league_id: UUID
       league_name: str
       season: str
       week: Optional[int]
       standings: List[TeamStandingDTO]
   ```

3. **Implement the Handler**
   ```python
   # application/query_handlers/league/get_league_standings_handler.py
   class GetLeagueStandingsHandler(QueryHandler):
       def __init__(
           self,
           league_repository: LeagueRepository,
           game_repository: GameRepository,
           standings_calculator: StandingsCalculator
       ):
           self._league_repo = league_repository
           self._game_repo = game_repository
           self._calculator = standings_calculator
       
       async def handle(self, query: GetLeagueStandingsQuery) -> LeagueStandingsDTO:
           # 1. Load league
           # 2. Load games
           # 3. Use StandingsCalculator
           # 4. Map to DTO
           # 5. Return
   ```

4. **Write Tests First (TDD)**
   ```python
   # tests/application/query_handlers/test_get_league_standings_handler.py
   def test_handle_returns_standings_for_league():
       # Arrange
       # Act
       # Assert
   ```

---

## Recommended Implementation Order

### Phase 3A: Core Queries (Week 7-8)

**Priority 1: Essential Read Operations**
1. ✅ `GetLeagueStandings` - Most important query
2. ✅ `GetGameOverview` - View match details
3. ✅ `GetTeamStatistics` - Team performance
4. ✅ `GetPlayerStatistics` - Player performance

**Priority 2: Supporting Queries**
5. ✅ `GetLeagueHistory` - Historical data
6. ✅ `GetLeagueWeekTable` - Week-specific standings
7. ✅ `GetTeamWeekDetails` - Team performance by week
8. ✅ `GetTeamVsTeamComparison` - Head-to-head comparison

### Phase 3B: First Commands (Week 8-9)

**Start with Simple Commands:**
1. ✅ `CreateGame` - Add new game
2. ✅ `UpdateGame` - Modify game
3. ✅ `DeleteGame` - Remove game

**Then Team Commands:**
4. ✅ `CreateTeam` - Add new team
5. ✅ `UpdateTeam` - Modify team
6. ✅ `DeleteTeam` - Remove team

### Phase 3C: Advanced Features (Week 10-11)

1. ✅ `ImportExcel` - Excel import functionality
2. ✅ Event handlers - Side effects on domain events
3. ✅ Cache invalidation - Performance optimization

---

## Implementation Pattern

### For Each Use Case:

1. **Identify the Use Case**
   - What does the user want to do?
   - What data do they need?
   - What are the inputs/outputs?

2. **Create the Query/Command**
   - Immutable dataclass
   - Contains all necessary inputs
   - Inherits from base class

3. **Create the DTO**
   - Response structure
   - Maps from domain to presentation
   - No business logic

4. **Implement the Handler**
   - Orchestrates domain logic
   - Uses repositories
   - Uses domain services
   - Maps to DTOs

5. **Write Tests**
   - Test handler logic
   - Mock dependencies
   - Test error cases

6. **Wire Up in DI Container**
   - Register handler
   - Register dependencies

---

## Example: Complete Implementation

### Use Case: "View League Standings"

#### 1. Query Definition
```python
# application/queries/league/get_league_standings_query.py
from dataclasses import dataclass
from uuid import UUID
from typing import Optional
from application.queries.base_query import Query

@dataclass(frozen=True)
class GetLeagueStandingsQuery(Query):
    """Query to get league standings."""
    league_id: UUID
    season: Optional[str] = None
    week: Optional[int] = None
```

#### 2. Response DTO
```python
# application/dto/league_dto.py
from dataclasses import dataclass
from uuid import UUID
from typing import List, Optional

@dataclass
class TeamStandingDTO:
    team_id: UUID
    team_name: str
    position: int
    points: int
    games_played: int
    wins: int
    losses: int
    ties: int

@dataclass
class LeagueStandingsDTO:
    league_id: UUID
    league_name: str
    season: str
    week: Optional[int]
    standings: List[TeamStandingDTO]
```

#### 3. Handler Implementation
```python
# application/query_handlers/league/get_league_standings_handler.py
from typing import Protocol
from uuid import UUID
from domain.repositories.league_repository import LeagueRepository
from domain.repositories.game_repository import GameRepository
from domain.domain_services.standings_calculator import StandingsCalculator
from application.queries.league.get_league_standings_query import GetLeagueStandingsQuery
from application.dto.league_dto import LeagueStandingsDTO, TeamStandingDTO

class GetLeagueStandingsHandler:
    """Handler for GetLeagueStandingsQuery."""
    
    def __init__(
        self,
        league_repository: LeagueRepository,
        game_repository: GameRepository,
        standings_calculator: StandingsCalculator
    ):
        self._league_repo = league_repository
        self._game_repo = game_repository
        self._calculator = standings_calculator
    
    async def handle(self, query: GetLeagueStandingsQuery) -> LeagueStandingsDTO:
        # 1. Load league
        league = await self._league_repo.get_by_id(query.league_id)
        if not league:
            raise ValueError(f"League {query.league_id} not found")
        
        # 2. Load games
        if query.season:
            games = await self._game_repo.get_by_league_and_season(
                query.league_id, 
                query.season
            )
        else:
            games = await self._game_repo.get_by_league(query.league_id)
        
        # Filter by week if specified
        if query.week:
            games = [g for g in games if g.week == query.week]
        
        # 3. Calculate standings using domain service
        standings = self._calculator.calculate_standings(games)
        
        # 4. Map to DTO
        standing_dtos = [
            TeamStandingDTO(
                team_id=standing.team_id,
                team_name=standing.team_name,
                position=standing.position,
                points=standing.points,
                games_played=standing.games_played,
                wins=standing.wins,
                losses=standing.losses,
                ties=standing.ties
            )
            for standing in standings
        ]
        
        # 5. Return DTO
        return LeagueStandingsDTO(
            league_id=league.id,
            league_name=league.name,
            season=query.season or "current",
            week=query.week,
            standings=standing_dtos
        )
```

#### 4. Tests
```python
# tests/application/query_handlers/test_get_league_standings_handler.py
import pytest
from uuid import uuid4
from application.query_handlers.league.get_league_standings_handler import GetLeagueStandingsHandler
from application.queries.league.get_league_standings_query import GetLeagueStandingsQuery

@pytest.fixture
def handler(mock_league_repo, mock_game_repo, standings_calculator):
    return GetLeagueStandingsHandler(
        mock_league_repo,
        mock_game_repo,
        standings_calculator
    )

async def test_handle_returns_standings_for_league(handler, sample_league, sample_games):
    # Arrange
    query = GetLeagueStandingsQuery(league_id=sample_league.id)
    
    # Act
    result = await handler.handle(query)
    
    # Assert
    assert result.league_id == sample_league.id
    assert len(result.standings) > 0
```

---

## Key Principles

### 1. Use Case First
- Start with: "What does the user need?"
- Then create: Query/Command → Handler → DTO

### 2. Handler Responsibilities
- **Orchestrate** - Coordinate repositories and services
- **Don't contain business logic** - That's in domain services
- **Map to DTOs** - Convert domain models to presentation models

### 3. DTOs
- **No business logic** - Pure data structures
- **Presentation-focused** - Optimized for API responses
- **Can differ from domain models** - Different shape if needed

### 4. Testing
- **Test handlers in isolation** - Mock all dependencies
- **Test error cases** - Missing data, invalid inputs
- **Test mapping** - Ensure DTOs are correct

---

## Next Steps

1. **Start with `GetLeagueStandings`** - Implement first query
2. **Follow the pattern** - Use as template for other queries
3. **Iterate** - Add queries one by one
4. **Then commands** - Start with simple CRUD operations

---

## Questions to Ask for Each Use Case

1. **What data is needed?** → Query inputs
2. **What data is returned?** → DTO structure
3. **What repositories are needed?** → Handler dependencies
4. **What domain services are needed?** → Handler dependencies
5. **What validation is needed?** → Handler logic
6. **What errors can occur?** → Error handling

---

## Resources

- **Base Classes:** `application/queries/base_query.py`, `application/commands/base_command.py`
- **Handler Interfaces:** `application/query_handlers/base_handler.py`, `application/command_handlers/base_handler.py`
- **Domain Services:** `domain/domain_services/` (StandingsCalculator, StatisticsCalculator, HandicapCalculator)
- **Repositories:** `domain/repositories/` (16 repository interfaces)

---

**Ready to start? Begin with `GetLeagueStandings` query!**
