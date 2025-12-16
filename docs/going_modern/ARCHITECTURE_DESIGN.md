# Architecture Design - League Analyzer v2

**Date:** 2025-01-27  
**Based on:** Scope Analysis and Architecture Review

---

## Architecture Overview

### Core Principles

1. **Clean Architecture** - Dependency rule, clear layer boundaries
2. **CQRS** - Separate read and write operations
3. **Domain-Driven Design** - Rich domain models with behavior
4. **Dependency Injection** - Loose coupling, testability
5. **Event-Driven** - Domain events for side effects

---

## Layer Structure

```
┌─────────────────────────────────────────────────────────┐
│              Presentation Layer                          │
│  API Routes, Web Templates, Frontend Components        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│            Application Layer                            │
│  Commands (Write) | Queries (Read)                      │
│  Command Handlers | Query Handlers                      │
│  DTOs, Validators                                       │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Domain Layer                               │
│  Entities, Value Objects, Domain Services               │
│  Domain Events, Domain Exceptions                       │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│         Infrastructure Layer                            │
│  Repositories, Adapters, Event Handlers                 │
│  Import/Export Services, Unit of Work                  │
└─────────────────────────────────────────────────────────┘
```

---

## Domain Layer Design

### Entities

#### Team
```python
@dataclass
class Team:
    id: UUID
    name: str
    league_id: UUID
    created_at: datetime
    updated_at: datetime
    
    def add_player(self, player: Player) -> None:
        """Business logic: Add player to team"""
        if player.team_id is not None:
            raise ValueError("Player already on a team")
        player.assign_to_team(self.id)
    
    def remove_player(self, player: Player) -> None:
        """Business logic: Remove player from team"""
        if player.team_id != self.id:
            raise ValueError("Player not on this team")
        player.remove_from_team()
```

#### League
```python
@dataclass
class League:
    id: UUID
    name: str
    season: str
    teams: List[Team]
    
    def add_team(self, team: Team) -> None:
        """Business logic: Add team to league"""
        if team in self.teams:
            raise ValueError("Team already in league")
        self.teams.append(team)
        DomainEventBus.publish(TeamAddedToLeague(league_id=self.id, team_id=team.id))
    
    def calculate_standings(self, week: int) -> List[Standing]:
        """Business logic: Calculate standings"""
        # Domain logic here
        pass
```

#### Game
```python
@dataclass
class Game:
    id: UUID
    league_id: UUID
    season: str
    week: int
    round_number: int
    date: datetime
    team_id: UUID
    opponent_team_id: UUID
    results: List[GameResult]
    created_at: datetime
    updated_at: datetime
    
    def __post_init__(self):
        """Validate domain invariants"""
        self._validate_teams_different()
        self._validate_results_complete()
        self._validate_date_in_season()
    
    def _validate_teams_different(self):
        if self.team_id == self.opponent_team_id:
            raise ValueError("Team cannot play against itself")
    
    def add_result(self, result: GameResult) -> None:
        """Business logic: Add game result"""
        if result.player_id in [r.player_id for r in self.results]:
            raise ValueError("Player already has result for this game")
        self.results.append(result)
        DomainEventBus.publish(GameResultAdded(game_id=self.id, result=result))
    
    def update_result(self, player_id: UUID, new_score: Score) -> None:
        """Business logic: Update game result"""
        result = self._find_result(player_id)
        if result is None:
            raise ValueError("Result not found")
        result.update_score(new_score)
        DomainEventBus.publish(GameResultUpdated(game_id=self.id, player_id=player_id))
```

### Value Objects

#### Score
```python
@dataclass(frozen=True)
class Score:
    value: float
    
    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Score cannot be negative")
        if self.value > 300:  # Business rule
            raise ValueError("Score cannot exceed 300")
    
    def __add__(self, other: 'Score') -> 'Score':
        return Score(self.value + other.value)
    
    def __truediv__(self, divisor: Union[int, float]) -> 'Score':
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        return Score(self.value / divisor)
```

#### Points
```python
@dataclass(frozen=True)
class Points:
    value: float
    
    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Points cannot be negative")
    
    def __add__(self, other: 'Points') -> 'Points':
        return Points(self.value + other.value)
```

#### GameResult
```python
@dataclass(frozen=True)
class GameResult:
    player_id: UUID
    position: int
    score: Score
    points: Points
    is_team_total: bool
    
    def __post_init__(self):
        if self.position < 1 or self.position > 4:
            raise ValueError("Position must be between 1 and 4")
```

### Domain Services

#### StandingsCalculator
```python
class StandingsCalculator:
    """Domain service for calculating standings"""
    
    @staticmethod
    def calculate(teams: List[Team], games: List[Game], week: int) -> List[Standing]:
        """Calculate standings for a given week"""
        standings = []
        for team in teams:
            team_games = [g for g in games if g.week <= week and 
                         (g.team_id == team.id or g.opponent_team_id == team.id)]
            total_points = sum(g.get_points_for_team(team.id) for g in team_games)
            total_score = sum(g.get_score_for_team(team.id) for g in team_games)
            avg_score = total_score / len(team_games) if team_games else Score(0)
            
            standings.append(Standing(
                team=team,
                points=total_points,
                score=total_score,
                average=avg_score,
                games_played=len(team_games)
            ))
        
        return sorted(standings, key=lambda s: s.points.value, reverse=True)
```

### Domain Events

```python
@dataclass
class GameCreated(DomainEvent):
    game_id: UUID
    league_id: UUID
    season: str
    week: int

@dataclass
class GameUpdated(DomainEvent):
    game_id: UUID
    changes: Dict[str, Any]

@dataclass
class GameDeleted(DomainEvent):
    game_id: UUID

@dataclass
class DataImported(DomainEvent):
    source: str
    records_imported: int
    league_id: UUID
    season: str
```

---

## Application Layer Design

### Commands (Write Operations)

#### CreateGameCommand
```python
@dataclass
class CreateGameCommand:
    league_id: UUID
    season: str
    week: int
    round_number: int
    date: datetime
    team_id: UUID
    opponent_team_id: UUID
    results: List[GameResultDTO]
```

#### UpdateGameCommand
```python
@dataclass
class UpdateGameCommand:
    game_id: UUID
    results: Optional[List[GameResultDTO]] = None
    date: Optional[datetime] = None
```

#### ImportExcelCommand
```python
@dataclass
class ImportExcelCommand:
    file_path: str
    league_id: UUID
    season: str
    preview_only: bool = False
```

### Queries (Read Operations)

#### GetLeagueStandingsQuery
```python
@dataclass
class GetLeagueStandingsQuery:
    league_id: UUID
    season: str
    week: int
```

#### GetTeamStatisticsQuery
```python
@dataclass
class GetTeamStatisticsQuery:
    team_id: UUID
    season: Optional[str] = None
    week: Optional[int] = None
```

### Command Handlers

#### CreateGameHandler
```python
class CreateGameHandler:
    def __init__(
        self,
        game_repository: GameRepository,
        league_repository: LeagueRepository,
        team_repository: TeamRepository,
        unit_of_work: UnitOfWork,
        event_bus: EventBus
    ):
        self._game_repository = game_repository
        self._league_repository = league_repository
        self._team_repository = team_repository
        self._unit_of_work = unit_of_work
        self._event_bus = event_bus
    
    def handle(self, command: CreateGameCommand) -> GameDTO:
        # Validate league exists
        league = self._league_repository.get_by_id(command.league_id)
        if league is None:
            raise LeagueNotFoundError(command.league_id)
        
        # Validate teams exist
        team = self._team_repository.get_by_id(command.team_id)
        opponent = self._team_repository.get_by_id(command.opponent_team_id)
        if team is None or opponent is None:
            raise TeamNotFoundError()
        
        # Create domain entity
        game = Game(
            id=uuid4(),
            league_id=command.league_id,
            season=command.season,
            week=command.week,
            round_number=command.round_number,
            date=command.date,
            team_id=command.team_id,
            opponent_team_id=command.opponent_team_id,
            results=[self._map_result(dto) for dto in command.results]
        )
        
        # Save
        with self._unit_of_work:
            self._game_repository.add(game)
            self._unit_of_work.commit()
        
        # Publish events
        self._event_bus.publish(GameCreated(
            game_id=game.id,
            league_id=game.league_id,
            season=game.season,
            week=game.week
        ))
        
        return GameDTO.from_domain(game)
```

### Query Handlers

#### GetLeagueStandingsHandler
```python
class GetLeagueStandingsHandler:
    def __init__(
        self,
        league_repository: LeagueRepository,
        game_repository: GameRepository,
        standings_calculator: StandingsCalculator,
        cache: Cache
    ):
        self._league_repository = league_repository
        self._game_repository = game_repository
        self._standings_calculator = standings_calculator
        self._cache = cache
    
    def handle(self, query: GetLeagueStandingsQuery) -> LeagueStandingsDTO:
        # Check cache
        cache_key = f"standings:{query.league_id}:{query.season}:{query.week}"
        cached = self._cache.get(cache_key)
        if cached:
            return cached
        
        # Get data
        league = self._league_repository.get_by_id(query.league_id)
        teams = self._league_repository.get_teams(query.league_id, query.season)
        games = self._game_repository.get_by_league_and_season(
            query.league_id, 
            query.season
        )
        
        # Calculate standings (domain service)
        standings = self._standings_calculator.calculate(teams, games, query.week)
        
        # Map to DTO
        dto = LeagueStandingsDTO.from_domain(standings)
        
        # Cache result
        self._cache.set(cache_key, dto, ttl=3600)
        
        return dto
```

---

## Infrastructure Layer Design

### Repositories

#### GameRepository Interface
```python
class GameRepository(ABC):
    @abstractmethod
    def add(self, game: Game) -> None:
        pass
    
    @abstractmethod
    def get_by_id(self, game_id: UUID) -> Optional[Game]:
        pass
    
    @abstractmethod
    def get_by_league_and_season(
        self, 
        league_id: UUID, 
        season: str
    ) -> List[Game]:
        pass
    
    @abstractmethod
    def update(self, game: Game) -> None:
        pass
    
    @abstractmethod
    def delete(self, game_id: UUID) -> None:
        pass
```

#### PandasGameRepository Implementation
```python
class PandasGameRepository(GameRepository):
    def __init__(self, adapter: PandasDataAdapter):
        self._adapter = adapter
    
    def add(self, game: Game) -> None:
        # Map domain entity to DataFrame row
        row = self._map_to_row(game)
        self._adapter.append_row(row)
    
    def get_by_id(self, game_id: UUID) -> Optional[Game]:
        df = self._adapter.get_filtered_data(
            filters={'id': {'value': str(game_id), 'operator': 'eq'}}
        )
        if df.empty:
            return None
        return self._map_to_domain(df.iloc[0])
    
    def _map_to_domain(self, row: pd.Series) -> Game:
        """Map DataFrame row to domain entity"""
        return Game(
            id=UUID(row['id']),
            league_id=UUID(row['league_id']),
            # ... map all fields
        )
    
    def _map_to_row(self, game: Game) -> Dict:
        """Map domain entity to DataFrame row"""
        return {
            'id': str(game.id),
            'league_id': str(game.league_id),
            # ... map all fields
        }
```

### Unit of Work

```python
class UnitOfWork:
    def __init__(self):
        self.games = GameRepository()
        self.teams = TeamRepository()
        self.leagues = LeagueRepository()
        self._committed = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._committed:
            self.rollback()
    
    def commit(self):
        """Commit all changes atomically"""
        # Save all repositories
        self.games.save()
        self.teams.save()
        self.leagues.save()
        self._committed = True
    
    def rollback(self):
        """Rollback all changes"""
        self.games.rollback()
        self.teams.rollback()
        self.leagues.rollback()
```

### Import/Export Services

#### ExcelImporter
```python
class ExcelImporter:
    def __init__(
        self,
        parser: ExcelParser,
        mapper: DataMapper,
        validator: DataValidator,
        game_repository: GameRepository
    ):
        self._parser = parser
        self._mapper = mapper
        self._validator = validator
        self._game_repository = game_repository
    
    def import_file(
        self, 
        file_path: str, 
        league_id: UUID, 
        season: str
    ) -> ImportResult:
        # Parse Excel
        raw_data = self._parser.parse(file_path)
        
        # Map to domain models
        games = self._mapper.map_to_games(raw_data, league_id, season)
        
        # Validate
        validation_result = self._validator.validate_all(games)
        if not validation_result.is_valid:
            return ImportResult(
                success=False,
                errors=validation_result.errors,
                games_preview=games
            )
        
        # Check duplicates
        duplicates = self._check_duplicates(games)
        if duplicates:
            return ImportResult(
                success=False,
                errors=[f"Duplicate games found: {duplicates}"],
                games_preview=games
            )
        
        # Save
        with UnitOfWork() as uow:
            for game in games:
                uow.games.add(game)
            uow.commit()
        
        return ImportResult(
            success=True,
            games_imported=len(games),
            games_preview=games
        )
```

---

## Dependency Injection Container

```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    # Configuration
    config = providers.Configuration()
    
    # Adapters
    data_adapter = providers.Singleton(
        PandasDataAdapter,
        database_path=config.database.path
    )
    
    # Repositories
    game_repository = providers.Factory(
        PandasGameRepository,
        adapter=data_adapter
    )
    
    team_repository = providers.Factory(
        PandasTeamRepository,
        adapter=data_adapter
    )
    
    league_repository = providers.Factory(
        PandasLeagueRepository,
        adapter=data_adapter
    )
    
    # Domain Services
    standings_calculator = providers.Singleton(
        StandingsCalculator
    )
    
    # Unit of Work
    unit_of_work = providers.Factory(
        UnitOfWork,
        games=game_repository,
        teams=team_repository,
        leagues=league_repository
    )
    
    # Event Bus
    event_bus = providers.Singleton(
        EventBus
    )
    
    # Command Handlers
    create_game_handler = providers.Factory(
        CreateGameHandler,
        game_repository=game_repository,
        league_repository=league_repository,
        team_repository=team_repository,
        unit_of_work=unit_of_work,
        event_bus=event_bus
    )
    
    # Query Handlers
    get_league_standings_handler = providers.Factory(
        GetLeagueStandingsHandler,
        league_repository=league_repository,
        game_repository=game_repository,
        standings_calculator=standings_calculator,
        cache=providers.Singleton(Cache)
    )
```

---

## API Layer Design

### Command Endpoints

```python
@bp.route('/api/v1/games', methods=['POST'])
def create_game():
    try:
        # Validate request
        request_data = CreateGameRequest(**request.json)
        
        # Create command
        command = CreateGameCommand(
            league_id=UUID(request_data.league_id),
            season=request_data.season,
            week=request_data.week,
            round_number=request_data.round_number,
            date=request_data.date,
            team_id=UUID(request_data.team_id),
            opponent_team_id=UUID(request_data.opponent_team_id),
            results=[GameResultDTO(**r) for r in request_data.results]
        )
        
        # Get handler from container
        handler = container.create_game_handler()
        
        # Execute command
        result = handler.handle(command)
        
        return jsonify(result.to_dict()), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except DomainException as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Query Endpoints

```python
@bp.route('/api/v1/leagues/<league_id>/standings', methods=['GET'])
def get_league_standings(league_id):
    try:
        # Validate request
        week = int(request.args.get('week', 1))
        season = request.args.get('season')
        
        if not season:
            return jsonify({'error': 'Season required'}), 400
        
        # Create query
        query = GetLeagueStandingsQuery(
            league_id=UUID(league_id),
            season=season,
            week=week
        )
        
        # Get handler from container
        handler = container.get_league_standings_handler()
        
        # Execute query
        result = handler.handle(query)
        
        return jsonify(result.to_dict()), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

## Event Handling

### Event Handlers

```python
class UpdateStandingsOnGameCreated:
    def __init__(self, standings_calculator: StandingsCalculator, cache: Cache):
        self._standings_calculator = standings_calculator
        self._cache = cache
    
    def handle(self, event: GameCreated):
        # Invalidate cache for affected standings
        cache_keys = [
            f"standings:{event.league_id}:{event.season}:{event.week}",
            f"standings:{event.league_id}:{event.season}:*"  # All weeks
        ]
        for key in cache_keys:
            self._cache.delete_pattern(key)
```

### Event Bus Registration

```python
# In application startup
event_bus = container.event_bus()
event_bus.subscribe(
    GameCreated,
    container.update_standings_handler()
)
event_bus.subscribe(
    GameUpdated,
    container.update_standings_handler()
)
event_bus.subscribe(
    GameDeleted,
    container.update_standings_handler()
)
```

---

## Summary

This architecture design provides:

1. ✅ **Clean Architecture** - Clear layer boundaries
2. ✅ **CQRS** - Separate read and write
3. ✅ **Domain-Driven Design** - Rich domain models
4. ✅ **Dependency Injection** - Loose coupling
5. ✅ **Event-Driven** - Domain events for side effects
6. ✅ **Validation** - Multi-layer validation
7. ✅ **Transactions** - Unit of Work pattern
8. ✅ **Import/Export** - Excel import service

**Ready for implementation!**

