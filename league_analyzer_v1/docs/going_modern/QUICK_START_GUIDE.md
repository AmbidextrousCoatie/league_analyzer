# Quick Start Guide - Clean Architecture Rebuild

**Goal:** Get started with the rebuild in the next hour

---

## Step 1: Create New Project Structure (15 minutes)

Create the new directory structure alongside your existing code:

```
league_analyzer_v2/
├── domain/
│   ├── __init__.py
│   ├── entities/
│   │   ├── __init__.py
│   │   ├── team.py
│   │   ├── league.py
│   │   ├── game.py
│   │   └── player.py
│   ├── value_objects/
│   │   ├── __init__.py
│   │   ├── score.py
│   │   └── points.py
│   └── domain_services/
│       ├── __init__.py
│       └── standings_calculator.py
├── application/
│   ├── __init__.py
│   ├── use_cases/
│   │   ├── __init__.py
│   │   └── league/
│   │       ├── __init__.py
│   │       └── get_league_standings.py
│   └── dto/
│       ├── __init__.py
│       └── league_dto.py
├── infrastructure/
│   ├── __init__.py
│   ├── persistence/
│   │   ├── __init__.py
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   └── league_repository.py
│   │   └── adapters/
│   │       ├── __init__.py
│   │       └── pandas_adapter.py
│   └── config/
│       ├── __init__.py
│       └── di_container.py
└── presentation/
    ├── __init__.py
    ├── api/
    │   ├── __init__.py
    │   └── v1/
    │       ├── __init__.py
    │       └── league_routes.py
    └── web/
        ├── __init__.py
        └── templates/
```

**Action:** Create these directories now.

---

## Step 2: Install Dependencies (5 minutes)

```bash
pip install dependency-injector pydantic pytest pytest-mock
```

**Action:** Run this command.

---

## Step 3: Set Up Dependency Injection Container (20 minutes)

Create `infrastructure/config/di_container.py`:

```python
from dependency_injector import containers, providers
from infrastructure.persistence.repositories.league_repository import LeagueRepository
from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
from application.use_cases.league.get_league_standings import GetLeagueStandingsUseCase

class Container(containers.DeclarativeContainer):
    """Dependency Injection Container"""
    
    # Configuration
    config = providers.Configuration()
    
    # Adapters
    data_adapter = providers.Singleton(
        PandasDataAdapter,
        database_path=config.database.path
    )
    
    # Repositories
    league_repository = providers.Factory(
        LeagueRepository,
        adapter=data_adapter
    )
    
    # Use Cases
    get_league_standings_use_case = providers.Factory(
        GetLeagueStandingsUseCase,
        repository=league_repository
    )
```

**Action:** Create this file with basic structure.

---

## Step 4: Create Your First Domain Entity (30 minutes)

Create `domain/entities/team.py`:

```python
from dataclasses import dataclass
from typing import List, Optional
from domain.value_objects.score import Score
from domain.value_objects.points import Points

@dataclass
class Team:
    """Team domain entity with business logic"""
    
    name: str
    league_name: str
    season: str
    
    def __post_init__(self):
        """Validate domain invariants"""
        if not self.name:
            raise ValueError("Team name cannot be empty")
        if not self.league_name:
            raise ValueError("League name cannot be empty")
    
    def calculate_total_points(self, games: List['Game']) -> Points:
        """Calculate total points from games - business logic in domain"""
        total = sum(game.points.value for game in games if game.team_name == self.name)
        return Points(total)
    
    def calculate_average_score(self, games: List['Game']) -> Score:
        """Calculate average score - business logic in domain"""
        team_games = [g for g in games if g.team_name == self.name]
        if not team_games:
            return Score(0.0)
        total_score = sum(game.score.value for game in team_games)
        return Score(total_score / len(team_games))
```

**Action:** Create this file and start thinking about what behavior belongs in the domain.

---

## Step 5: Create Your First Value Object (15 minutes)

Create `domain/value_objects/score.py`:

```python
from dataclasses import dataclass
from typing import Union

@dataclass(frozen=True)
class Score:
    """Immutable Score value object"""
    
    value: float
    
    def __post_init__(self):
        """Validate score"""
        if self.value < 0:
            raise ValueError("Score cannot be negative")
    
    def __add__(self, other: 'Score') -> 'Score':
        """Add two scores"""
        return Score(self.value + other.value)
    
    def __truediv__(self, divisor: Union[int, float]) -> 'Score':
        """Divide score by a number"""
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        return Score(self.value / divisor)
    
    def __str__(self) -> str:
        return f"{self.value:.2f}"
```

**Action:** Create this file - notice it's immutable (frozen) and has behavior.

---

## Step 6: Create Your First Repository Interface (15 minutes)

Create `infrastructure/persistence/repositories/league_repository.py`:

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.league import League
from domain.entities.team import Team

class LeagueRepository(ABC):
    """Repository interface for League data access"""
    
    @abstractmethod
    def get_league(self, league_name: str, season: str) -> Optional[League]:
        """Get a league by name and season"""
        pass
    
    @abstractmethod
    def get_all_leagues(self) -> List[str]:
        """Get all league names"""
        pass
    
    @abstractmethod
    def get_teams_in_league(self, league_name: str, season: str) -> List[Team]:
        """Get all teams in a league for a season"""
        pass
```

**Action:** Create this interface - notice it uses domain entities, not DataFrames.

---

## Step 7: Create Your First Use Case (20 minutes)

Create `application/use_cases/league/get_league_standings.py`:

```python
from dataclasses import dataclass
from typing import List
from infrastructure.persistence.repositories.league_repository import LeagueRepository
from application.dto.league_dto import LeagueStandingsDTO

@dataclass
class GetLeagueStandingsRequest:
    """Request DTO for getting league standings"""
    league_name: str
    season: str
    week: int

class GetLeagueStandingsUseCase:
    """Use case for getting league standings"""
    
    def __init__(self, repository: LeagueRepository):
        self._repository = repository
    
    def execute(self, request: GetLeagueStandingsRequest) -> LeagueStandingsDTO:
        """Execute the use case"""
        # Get domain entities
        league = self._repository.get_league(request.league_name, request.season)
        teams = self._repository.get_teams_in_league(request.league_name, request.season)
        games = self._repository.get_games_for_week(
            request.league_name, 
            request.season, 
            request.week
        )
        
        # Use domain logic to calculate standings
        standings = league.calculate_standings(teams, games, request.week)
        
        # Map to DTO
        return LeagueStandingsDTO.from_domain(standings)
```

**Action:** Create this use case - notice it orchestrates, doesn't contain business logic.

---

## Step 8: Create Your First API Route (15 minutes)

Create `presentation/api/v1/league_routes.py`:

```python
from flask import Blueprint, request, jsonify
from infrastructure.config.di_container import Container
from application.use_cases.league.get_league_standings import (
    GetLeagueStandingsUseCase,
    GetLeagueStandingsRequest
)

bp = Blueprint('league_v1', __name__)

# Initialize DI container
container = Container()
container.config.database.path.from_env('DATABASE_PATH', 'database/data/db_real.csv')

@bp.route('/league/standings', methods=['GET'])
def get_league_standings():
    """Get league standings endpoint"""
    try:
        # Validate request
        league_name = request.args.get('league')
        season = request.args.get('season')
        week = int(request.args.get('week', 1))
        
        if not league_name or not season:
            return jsonify({'error': 'League and season required'}), 400
        
        # Create request DTO
        request_dto = GetLeagueStandingsRequest(
            league_name=league_name,
            season=season,
            week=week
        )
        
        # Get use case from container
        use_case = container.get_league_standings_use_case()
        
        # Execute use case
        result = use_case.execute(request_dto)
        
        # Return response
        return jsonify(result.to_dict()), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

**Action:** Create this route - notice it's thin, just handles HTTP concerns.

---

## What You've Built

In about 2 hours, you've created:

1. ✅ **Clean project structure** - Organized by layers
2. ✅ **Dependency injection** - Loose coupling
3. ✅ **Domain entity** - With business logic
4. ✅ **Value object** - Immutable, validated
5. ✅ **Repository interface** - Data access abstraction
6. ✅ **Use case** - Application logic
7. ✅ **API route** - Thin HTTP layer

This is the foundation of clean architecture!

---

## Next Steps

1. **Complete the implementations** - Fill in the actual logic
2. **Add tests** - Test each layer independently
3. **Migrate one endpoint** - Start with simplest one
4. **Iterate** - Build out more use cases

---

## Learning Checklist

As you build, make sure you understand:

- [ ] Why domain entities have behavior (not just data)
- [ ] Why value objects are immutable
- [ ] Why repositories abstract data access
- [ ] Why use cases orchestrate (don't contain business logic)
- [ ] Why routes are thin (just HTTP concerns)
- [ ] Why dependency injection enables testing

---

**You're ready to start building! 🚀**

