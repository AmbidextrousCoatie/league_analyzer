# Docstring Template Guide

This guide provides templates for writing consistent docstrings following Google-style format.

---

## Module Docstring

```python
"""
[Module Name] - [Brief Description]

[Detailed description of the module's purpose and responsibilities]

This module [what it does and why it exists].

Modules:
    [submodule1]: [description]
    [submodule2]: [description]

See Also:
    [related module or documentation]
    docs/architecture/[layer]_layer.md - Detailed layer documentation

Example:
    >>> from [module] import [Class]
    >>> instance = [Class]()
    >>> instance.method()
    result
"""
```

---

## Class Docstring

```python
class ClassName:
    """
    [Brief description of the class]
    
    [Detailed description of what the class represents and its purpose]
    
    The class [what it does] and [why it exists]. It [key responsibilities].
    
    Attributes:
        attr1 (Type): Description of attribute
        attr2 (Type): Description of attribute
    
    Example:
        >>> instance = ClassName(param1="value")
        >>> instance.method()
        result
    
    See Also:
        RelatedClass - Related class
        docs/architecture/[layer]_layer.md - Architecture documentation
    
    Note:
        Important note about usage or behavior
    """
```

---

## Function/Method Docstring

```python
def function_name(param1: Type, param2: Optional[Type] = None) -> ReturnType:
    """
    [Brief one-line description]
    
    [Optional detailed description explaining what the function does,
    why it exists, and any important behavior or side effects]
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: None)
    
    Returns:
        Description of return value
    
    Raises:
        ExceptionType: When this exception is raised
    
    Example:
        >>> result = function_name("value1", param2="value2")
        >>> print(result)
        output
    
    Note:
        Important note about usage
    
    See Also:
        related_function - Related function
    """
```

---

## Property Docstring

```python
@property
def property_name(self) -> Type:
    """
    [Brief description of the property]
    
    [Optional detailed description]
    
    Returns:
        Description of return value
    
    Example:
        >>> instance.property_name
        value
    """
```

---

## Examples by Layer

### Domain Layer - Entity

```python
class Game:
    """
    Domain entity representing a bowling game/match.
    
    A Game represents a match between two teams in a league during a specific
    week. Games contain results for each player and enforce business rules
    such as preventing duplicate results and ensuring teams are different.
    
    Attributes:
        id: Unique identifier for the game
        league_id: ID of the league this game belongs to
        season: Season value object
        week: Week number in the season
        team_id: ID of the team
        opponent_team_id: ID of the opposing team
        results: List of game results for players
    
    Example:
        >>> from domain.value_objects.season import Season
        >>> game = Game(
        ...     league_id=uuid4(),
        ...     season=Season("2024-25"),
        ...     week=1,
        ...     team_id=uuid4(),
        ...     opponent_team_id=uuid4()
        ... )
        >>> len(game.results)
        0
    
    See Also:
        domain.value_objects.game_result.GameResult
        docs/architecture/domain_layer.md - Domain layer documentation
    """
```

### Domain Layer - Value Object

```python
class Score:
    """
    Immutable value object representing a bowling score.
    
    Scores are always between 0 and 300 (perfect game). The Score value
    object enforces this invariant and provides arithmetic operations
    that maintain immutability.
    
    Attributes:
        value: The score value (0-300)
    
    Example:
        >>> score1 = Score(200)
        >>> score2 = Score(150)
        >>> average = (score1 + score2) / 2
        >>> print(average.value)
        175.0
    
    Raises:
        InvalidScore: If score is outside valid range (0-300)
    
    See Also:
        domain.value_objects.points.Points
        docs/architecture/domain_layer.md - Domain layer documentation
    """
```

### Domain Layer - Domain Service

```python
class HandicapCalculator:
    """
    Domain service for calculating player handicaps.
    
    HandicapCalculator provides stateless methods for calculating handicaps
    based on game results and handicap settings. It supports multiple
    calculation methods (cumulative average, moving window) and applies
    business rules such as maximum handicap caps.
    
    This is a domain service because the calculation logic is complex and
    doesn't naturally belong to a single entity.
    
    Attributes:
        BASE_SCORE: Standard base score for handicap calculation (200)
    
    Example:
        >>> calculator = HandicapCalculator()
        >>> results = [GameResult(...), GameResult(...)]
        >>> settings = HandicapSettings(enabled=True, method=...)
        >>> handicap = calculator.calculate_handicap(results, settings)
        >>> print(handicap.value)
        15.5
    
    See Also:
        domain.value_objects.handicap.Handicap
        domain.value_objects.handicap_settings.HandicapSettings
        docs/architecture/domain_layer.md - Domain layer documentation
    """
    
    BASE_SCORE = 200.0
    
    @staticmethod
    def calculate_handicap(
        results: List[GameResult],
        settings: HandicapSettings
    ) -> Optional[Handicap]:
        """
        Calculate handicap for a player based on their game results.
        
        Uses the handicap settings to determine calculation method (cumulative
        average or moving window) and applies the configured percentage.
        The result is capped at the maximum handicap if specified.
        
        Args:
            results: List of game results for the player (must be non-empty)
            settings: Handicap settings (method, percentage, max cap)
        
        Returns:
            Calculated handicap value, or None if:
            - Handicap is disabled in settings
            - No results provided
            - Insufficient results for calculation method
        
        Raises:
            InvalidHandicapCalculation: If calculation fails due to invalid data
        
        Example:
            >>> results = [
            ...     GameResult(player_id=..., score=Score(180), ...),
            ...     GameResult(player_id=..., score=Score(190), ...),
            ...     GameResult(player_id=..., score=Score(200), ...)
            ... ]
            >>> settings = HandicapSettings(
            ...     enabled=True,
            ...     method=HandicapCalculationMethod.CUMULATIVE_AVERAGE,
            ...     percentage=0.9,
            ...     max_handicap=50.0
            ... )
            >>> handicap = HandicapCalculator.calculate_handicap(results, settings)
            >>> print(handicap.value)
            9.0
        
        See Also:
            HandicapCalculator.apply_handicap_with_capping - Apply handicap to score
        """
```

### Application Layer - Command

```python
class CreateGame(Command):
    """
    Command to create a new game.
    
    This command represents the intent to create a new game in the system.
    It contains all the data needed to create a game entity.
    
    Attributes:
        league_id: ID of the league
        season: Season identifier
        week: Week number
        team_id: ID of the team
        opponent_team_id: ID of the opponent team
    
    Example:
        >>> command = CreateGame(
        ...     league_id=uuid4(),
        ...     season="2024-25",
        ...     week=1,
        ...     team_id=uuid4(),
        ...     opponent_team_id=uuid4()
        ... )
    
    See Also:
        application.command_handlers.create_game_handler.CreateGameHandler
        docs/architecture/application_layer.md - Application layer documentation
    """
```

### Application Layer - Command Handler

```python
class CreateGameHandler(CommandHandler[CreateGame, GameDTO]):
    """
    Handler for CreateGame command.
    
    Orchestrates the creation of a new game by:
    1. Validating the command
    2. Creating the domain entity
    3. Saving via repository
    4. Publishing domain events
    5. Returning DTO
    
    Dependencies:
        game_repository: Repository for game persistence
        event_bus: Event bus for publishing domain events
    
    Example:
        >>> handler = CreateGameHandler(
        ...     game_repository=game_repo,
        ...     event_bus=event_bus
        ... )
        >>> command = CreateGame(...)
        >>> result = handler.handle(command)
        >>> print(result.id)
        uuid
    
    See Also:
        application.commands.create_game.CreateGame
        docs/architecture/application_layer.md - Application layer documentation
    """
```

### Infrastructure Layer - Repository

```python
class GameRepository(Repository[Game, UUID]):
    """
    Repository for Game entity persistence.
    
    Provides data access operations for Game entities. Abstracts the underlying
    data storage mechanism (Pandas, SQLite, MySQL) through adapters.
    
    Dependencies:
        adapter: Data adapter for data access
    
    Example:
        >>> adapter = PandasDataAdapter(data_path=Path("data/"))
        >>> repo = GameRepository(adapter=adapter)
        >>> game = repo.get_by_id(game_id)
        >>> repo.save(game)
    
    See Also:
        infrastructure.persistence.adapters.data_adapter.DataAdapter
        docs/architecture/infrastructure_layer.md - Infrastructure layer documentation
    """
```

---

## Best Practices

### ✅ Do

- Write clear, concise descriptions
- Include examples for complex functions
- Document all parameters and return values
- Use type hints (they complement docstrings)
- Link to related documentation
- Keep docstrings up to date with code

### ❌ Don't

- Repeat what's obvious from the code
- Write overly verbose docstrings
- Forget to update docstrings when code changes
- Use docstrings for implementation details
- Document private methods (use comments instead)

---

## Checklist

Before committing, ensure:

- [ ] All public classes have docstrings
- [ ] All public functions/methods have docstrings
- [ ] All parameters are documented
- [ ] Return values are documented
- [ ] Exceptions are documented
- [ ] Examples are included (for complex functions)
- [ ] Links to architecture docs are included
- [ ] Type hints match docstring descriptions

---

## See Also

- [Documentation Strategy](DOCUMENTATION_STRATEGY.md) - Overall documentation approach
- [Google Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [PEP 257](https://www.python.org/dev/peps/pep-0257/)

