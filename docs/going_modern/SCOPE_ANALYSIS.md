# Application Scope Analysis

**Date:** 2025-01-27  
**Purpose:** Define current and desired scope to inform architecture decisions

---

## Current Scope (Read-Only)

### Core Functionality
The application currently provides **read-only** statistics and analytics for bowling leagues.

### Current Features

#### 1. League Statistics
- **View league standings** (by week, season)
- **View league history** (progression over time)
- **View game overviews** (match results, team vs team)
- **View season timetables** (schedule, match days)
- **View league aggregations** (averages, points to win, top performances)
- **View team vs team comparisons** (heatmaps, matrices)

#### 2. Team Statistics
- **View team performance** (scores, points, averages)
- **View team history** (all-time performance)
- **View team vs league comparison** (performance relative to league)
- **View clutch performance** (performance in close games)
- **View consistency metrics** (variance, streaks)
- **View special matches** (highest scores, biggest wins/losses)
- **View win percentage** (individual and team)

#### 3. Player Statistics
- **View player lifetime stats** (all-time performance)
- **View player season stats** (per-season breakdown)
- **View player search** (find players by name)
- **View player trends** (performance over time)

#### 4. Data Management (Current)
- **Switch between databases** (db_sim, db_real)
- **View data source information**
- **Reload data** (switch data sources)

### Current Data Flow

```
CSV Files → DataAdapter → Business Logic → Services → Routes → Frontend
```

**Characteristics:**
- ✅ Read-only operations
- ✅ CSV-based storage
- ✅ Pandas DataFrames for data manipulation
- ✅ No write operations
- ✅ No data validation on write
- ✅ No transaction support

---

## Desired Scope (Read + Write)

### Phase 1: Database Modification (Immediate Post-Refactor)

#### 1. CRUD Operations
- **Create** new games, teams, players, leagues
- **Read** existing data (already implemented)
- **Update** existing games, teams, players, leagues
- **Delete** games, teams, players, leagues

#### 2. Excel Import
- **Import league reports** from Excel files
- **Validate imported data** (schema validation, business rules)
- **Transform Excel format** to internal format
- **Handle errors** (invalid data, duplicates, missing fields)
- **Preview before import** (show what will be imported)
- **Batch import** (multiple files, multiple seasons)

#### 3. Data Validation
- **Schema validation** (required fields, data types)
- **Business rule validation** (scores within range, valid dates)
- **Referential integrity** (teams exist, players exist)
- **Duplicate detection** (prevent duplicate games)

### Phase 2: Frontend Data Entry (Future)

#### 1. League Management
- **Create/edit leagues** (name, season, teams)
- **Manage league structure** (teams, players, schedule)

#### 2. Game Entry
- **Enter game results** (scores, points, players)
- **Enter match day results** (multiple games)
- **Edit existing games** (correct mistakes)
- **Bulk entry** (enter multiple games at once)

#### 3. Tournament Management
- **Create tournaments** (structure, teams, schedule)
- **Enter tournament results** (scores, standings)
- **Manage tournament brackets** (if applicable)

---

## Architecture Implications

### 1. CQRS Pattern (Command Query Responsibility Segregation)

**Why Needed:**
- Read operations (queries) are optimized for display
- Write operations (commands) need validation and business logic
- Different models for read vs write

**Implementation:**

```
┌─────────────────────────────────────────┐
│         Command Side (Write)            │
│  Commands → Command Handlers → Domain  │
│  → Repositories → Database              │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         Query Side (Read)               │
│  Queries → Query Handlers → Read Models │
│  → Database (optimized views)           │
└─────────────────────────────────────────┘
```

**Benefits:**
- Separate optimization for reads and writes
- Clear separation of concerns
- Easier to scale independently
- Better testability

---

### 2. Domain Events

**Why Needed:**
- When a game is created, update standings
- When a player is added, update team statistics
- When data is imported, trigger validation

**Example Events:**
- `GameCreated`
- `GameUpdated`
- `GameDeleted`
- `PlayerAddedToTeam`
- `LeagueDataImported`

---

### 3. Validation Layers

**Multiple Validation Layers:**

1. **Input Validation** (API layer)
   - Request format validation
   - Required fields
   - Data types

2. **Domain Validation** (Domain layer)
   - Business rules
   - Domain invariants
   - Consistency checks

3. **Data Validation** (Infrastructure layer)
   - Schema validation
   - Referential integrity
   - Database constraints

---

### 4. Import/Export Services

**Excel Import Service:**
- Parse Excel files
- Map to domain models
- Validate data
- Transform format
- Handle errors

**Export Service:**
- Export to Excel
- Export to CSV
- Export reports

---

## Revised Architecture Design

### Domain Layer

```
domain/
├── entities/
│   ├── team.py
│   ├── league.py
│   ├── game.py          # NEW: Game entity with validation
│   ├── player.py
│   └── tournament.py    # NEW: Tournament entity
├── value_objects/
│   ├── score.py
│   ├── points.py
│   └── game_result.py   # NEW: Game result value object
├── domain_services/
│   ├── standings_calculator.py
│   ├── statistics_calculator.py
│   └── game_validator.py        # NEW: Game validation
├── domain_events/
│   ├── game_created.py          # NEW
│   ├── game_updated.py          # NEW
│   ├── game_deleted.py          # NEW
│   └── data_imported.py        # NEW
└── exceptions/
    ├── invalid_game_data.py     # NEW
    └── duplicate_game.py        # NEW
```

### Application Layer

```
application/
├── commands/                    # NEW: Write operations
│   ├── create_game.py
│   ├── update_game.py
│   ├── delete_game.py
│   ├── import_excel.py
│   └── create_team.py
├── queries/                     # Read operations
│   ├── get_league_standings.py
│   ├── get_team_statistics.py
│   └── get_player_stats.py
├── command_handlers/            # NEW
│   ├── create_game_handler.py
│   ├── update_game_handler.py
│   └── import_excel_handler.py
├── query_handlers/
│   ├── get_league_standings_handler.py
│   └── get_team_statistics_handler.py
└── dto/
    ├── command_dto.py           # NEW: Command DTOs
    ├── query_dto.py
    └── response_dto.py
```

### Infrastructure Layer

```
infrastructure/
├── persistence/
│   ├── repositories/
│   │   ├── game_repository.py      # NEW: Write operations
│   │   ├── team_repository.py      # NEW: Write operations
│   │   └── league_repository.py
│   └── unit_of_work.py             # NEW: Transaction support
├── import_export/                  # NEW
│   ├── excel_importer.py
│   ├── excel_parser.py
│   ├── data_mapper.py
│   └── validation_service.py
└── event_handlers/                 # NEW
    ├── update_standings_handler.py
    └── update_statistics_handler.py
```

### Presentation Layer

```
presentation/
├── api/
│   ├── v1/
│   │   ├── commands/               # NEW: Write endpoints
│   │   │   ├── games.py           # POST /games, PUT /games/:id, DELETE /games/:id
│   │   │   ├── teams.py
│   │   │   └── import.py          # POST /import/excel
│   │   └── queries/               # Read endpoints
│   │       ├── league.py
│   │       ├── team.py
│   │       └── player.py
│   └── middleware/
│       ├── validation_middleware.py  # NEW
│       └── error_handler.py
└── web/
    ├── admin/                      # NEW: Admin interface
    │   ├── games/
    │   │   ├── create.html
    │   │   └── edit.html
    │   └── import/
    │       └── excel.html
    └── templates/                  # Existing read-only views
```

---

## Use Cases Breakdown

### Write Use Cases (NEW)

#### 1. Create Game
```
Command: CreateGameCommand
Handler: CreateGameHandler
Validation:
  - All required fields present
  - Scores within valid range
  - Teams exist
  - Players exist
  - Date is valid
  - No duplicate game
Events:
  - GameCreated
Side Effects:
  - Update standings
  - Update statistics
  - Invalidate cache
```

#### 2. Update Game
```
Command: UpdateGameCommand
Handler: UpdateGameHandler
Validation:
  - Game exists
  - New data is valid
  - No conflicts
Events:
  - GameUpdated
Side Effects:
  - Recalculate standings
  - Recalculate statistics
  - Invalidate cache
```

#### 3. Delete Game
```
Command: DeleteGameCommand
Handler: DeleteGameHandler
Validation:
  - Game exists
  - No dependencies
Events:
  - GameDeleted
Side Effects:
  - Recalculate standings
  - Recalculate statistics
  - Invalidate cache
```

#### 4. Import Excel
```
Command: ImportExcelCommand
Handler: ImportExcelHandler
Steps:
  1. Parse Excel file
  2. Validate schema
  3. Map to domain models
  4. Validate business rules
  5. Check for duplicates
  6. Preview changes
  7. Confirm import
  8. Save to database
  9. Trigger events
Events:
  - DataImported
Side Effects:
  - Update all affected statistics
  - Invalidate cache
```

### Read Use Cases (Existing)

#### 1. Get League Standings
```
Query: GetLeagueStandingsQuery
Handler: GetLeagueStandingsHandler
Optimization:
  - Cached results
  - Optimized read model
  - Fast queries
```

---

## Data Model Considerations

### Current Model (Read-Only)
- Flat CSV structure
- Computed data mixed with input data
- No relationships enforced

### Desired Model (Read + Write)
- Normalized structure
- Clear separation: Input data vs Computed data
- Relationships enforced
- Audit trail (who created/modified, when)

### Schema Evolution

**Current Schema:**
```csv
season,league_name,week,round_number,team_name,player_name,score,points,...
```

**Desired Schema:**
```python
# Domain Models
Game:
  - id (UUID)
  - league_id
  - season
  - week
  - round_number
  - date
  - team_id
  - opponent_team_id
  - created_at
  - updated_at
  - created_by

GameResult:
  - game_id
  - player_id
  - position
  - score
  - points
  - is_team_total (boolean)

Team:
  - id (UUID)
  - name
  - league_id
  - created_at
  - updated_at

Player:
  - id (UUID)
  - name
  - team_id
  - created_at
  - updated_at
```

---

## API Design

### Command Endpoints (NEW)

```
POST   /api/v1/games                    # Create game
PUT    /api/v1/games/{id}               # Update game
DELETE /api/v1/games/{id}               # Delete game

POST   /api/v1/teams                    # Create team
PUT    /api/v1/teams/{id}               # Update team
DELETE /api/v1/teams/{id}               # Delete team

POST   /api/v1/import/excel             # Import Excel file
POST   /api/v1/import/excel/preview     # Preview import
```

### Query Endpoints (Existing)

```
GET    /api/v1/leagues/{id}/standings   # Get standings
GET    /api/v1/teams/{id}/statistics    # Get team stats
GET    /api/v1/players/{id}/stats       # Get player stats
```

---

## Validation Strategy

### Three-Layer Validation

#### 1. API Layer Validation
```python
# Request validation
class CreateGameRequest(BaseModel):
    league_id: UUID
    season: str
    week: int
    round_number: int
    team_id: UUID
    opponent_team_id: UUID
    date: datetime
    results: List[GameResultRequest]
    
    @validator('week')
    def week_must_be_positive(cls, v):
        if v < 1:
            raise ValueError('Week must be positive')
        return v
```

#### 2. Domain Layer Validation
```python
# Domain invariants
class Game:
    def __init__(self, ...):
        self._validate_teams_different()
        self._validate_scores_in_range()
        self._validate_date_in_season()
    
    def _validate_teams_different(self):
        if self.team_id == self.opponent_team_id:
            raise ValueError("Team cannot play against itself")
```

#### 3. Infrastructure Layer Validation
```python
# Database constraints
- Foreign key constraints
- Unique constraints
- Check constraints
```

---

## Import/Export Design

### Excel Import Flow

```
1. Upload Excel File
   ↓
2. Parse Excel (ExcelParser)
   ↓
3. Map to Domain Models (DataMapper)
   ↓
4. Validate Schema (SchemaValidator)
   ↓
5. Validate Business Rules (DomainValidator)
   ↓
6. Check Duplicates (DuplicateChecker)
   ↓
7. Preview Changes (PreviewService)
   ↓
8. User Confirms
   ↓
9. Execute Import (ImportHandler)
   ↓
10. Save to Database (Repository)
   ↓
11. Trigger Events (EventBus)
   ↓
12. Update Statistics (EventHandlers)
```

### Excel Export Flow

```
1. User Requests Export
   ↓
2. Query Data (QueryHandler)
   ↓
3. Format Data (DataFormatter)
   ↓
4. Generate Excel (ExcelGenerator)
   ↓
5. Return File
```

---

## Transaction Management

### Unit of Work Pattern

```python
class UnitOfWork:
    def __init__(self):
        self.games = GameRepository()
        self.teams = TeamRepository()
        self._committed = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        if not self._committed:
            self.rollback()
    
    def commit(self):
        # Save all changes atomically
        self._committed = True
    
    def rollback(self):
        # Discard all changes
        pass
```

**Usage:**
```python
with UnitOfWork() as uow:
    game = Game(...)
    uow.games.add(game)
    uow.commit()  # Atomic transaction
```

---

## Caching Strategy

### Read Side Caching
- Cache league standings (invalidate on game changes)
- Cache team statistics (invalidate on game changes)
- Cache player statistics (invalidate on game changes)

### Write Side
- No caching (always fresh data)
- Invalidate read caches on write

---

## Security Considerations (Future)

### Authentication & Authorization
- User roles (admin, viewer)
- Permission checks on write operations
- Audit logging (who did what, when)

### Data Protection
- Input sanitization
- SQL injection prevention
- XSS prevention

---

## Migration Strategy

### Phase 1: Add Write Operations (Post-Refactor)
1. Implement command handlers
2. Add write repositories
3. Add validation
4. Add API endpoints
5. Test thoroughly

### Phase 2: Excel Import
1. Integrate existing Excel parser
2. Add import service
3. Add preview functionality
4. Add API endpoint
5. Add frontend UI

### Phase 3: Frontend Data Entry
1. Create admin interface
2. Add forms for data entry
3. Add validation feedback
4. Add error handling
5. Add success notifications

---

## Key Architecture Decisions

### 1. CQRS Pattern ✅
**Decision:** Use CQRS to separate read and write operations

**Rationale:**
- Read operations optimized for display
- Write operations need validation and business logic
- Different models for read vs write
- Easier to scale independently

### 2. Domain Events ✅
**Decision:** Use domain events for side effects

**Rationale:**
- Decouple write operations from read updates
- Easy to add new side effects
- Better testability

### 3. Unit of Work ✅
**Decision:** Use Unit of Work pattern for transactions

**Rationale:**
- Atomic operations
- Consistent state
- Easy rollback

### 4. Validation Layers ✅
**Decision:** Three-layer validation (API, Domain, Infrastructure)

**Rationale:**
- Catch errors early
- Clear separation of concerns
- Comprehensive validation

### 5. Import/Export Service ✅
**Decision:** Separate service for import/export

**Rationale:**
- Reusable
- Testable
- Extensible (can add more formats)

---

## Summary

### Current State
- ✅ Read-only statistics application
- ✅ CSV-based storage
- ✅ Pandas DataFrames
- ✅ No write operations

### Target State
- ✅ Read + Write operations
- ✅ CRUD operations
- ✅ Excel import/export
- ✅ Frontend data entry
- ✅ Validation and business rules
- ✅ Transaction support
- ✅ Domain events

### Architecture Changes Needed
1. **CQRS Pattern** - Separate read and write
2. **Command Handlers** - Handle write operations
3. **Domain Events** - Handle side effects
4. **Unit of Work** - Transaction management
5. **Validation Layers** - Multi-layer validation
6. **Import/Export Services** - Data import/export

---

**This scope analysis informs all architecture decisions going forward.**

