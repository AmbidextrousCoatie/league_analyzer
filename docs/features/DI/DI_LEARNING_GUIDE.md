# Dependency Injection Learning Guide

## What is Dependency Injection?

**Dependency Injection (DI)** is a design pattern where objects receive their dependencies from external sources rather than creating them internally.

### The Problem Without DI

```python
# ❌ Bad: Tight coupling, hard to test
class LeagueService:
    def __init__(self):
        self.adapter = DataAdapterFactory.create_adapter(DataAdapterSelector.PANDAS)
        # LeagueService is tightly coupled to DataAdapterFactory
        # Hard to test (can't easily mock the adapter)
        # Hard to change (must modify LeagueService to use different adapter)
```

### The Solution With DI

```python
# ✅ Good: Loose coupling, easy to test
class LeagueService:
    def __init__(self, adapter: DataAdapter):
        self.adapter = adapter
        # LeagueService receives adapter from outside
        # Easy to test (can inject mock adapter)
        # Easy to change (just inject different adapter)
```

## Benefits of DI

1. **Loose Coupling**: Classes don't depend on concrete implementations
2. **Testability**: Easy to inject mocks/stubs for testing
3. **Flexibility**: Easy to swap implementations
4. **Single Responsibility**: Classes focus on their core logic
5. **Dependency Inversion**: Depend on abstractions, not concretions

## DI Patterns

### 1. Constructor Injection (Recommended)

Dependencies are injected via constructor:

```python
class LeagueService:
    def __init__(self, adapter: DataAdapter, logger: Logger):
        self.adapter = adapter
        self.logger = logger
```

**Benefits:**
- Dependencies are explicit
- Required dependencies are clear
- Immutable (can't change after construction)

### 2. Setter Injection

Dependencies are injected via setter methods:

```python
class LeagueService:
    def set_adapter(self, adapter: DataAdapter):
        self.adapter = adapter
```

**Use When:**
- Dependencies are optional
- Need to change dependencies at runtime

### 3. Interface Injection

Dependencies are injected via interface methods:

```python
class LeagueService:
    def inject(self, adapter: DataAdapter, logger: Logger):
        self.adapter = adapter
        self.logger = logger
```

**Use When:**
- Multiple dependencies
- Complex injection scenarios

## DI Container

A **DI Container** (also called IoC Container) manages dependencies automatically:

```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    # Configure dependencies
    adapter = providers.Factory(DataAdapterPandas, path="data/")
    logger = providers.Singleton(Logger)
    
    # Configure services that depend on other dependencies
    league_service = providers.Factory(
        LeagueService,
        adapter=adapter,
        logger=logger
    )

# Use container
container = Container()
service = container.league_service()  # Dependencies automatically injected!
```

## Applying DI to Data Adapters

### Step 1: Define Adapter Interface

```python
from abc import ABC, abstractmethod

class DataAdapter(ABC):
    """Abstract interface for data adapters."""
    
    @abstractmethod
    def get_league_data(self, league_id: str) -> pd.DataFrame:
        """Get league data."""
        pass
    
    @abstractmethod
    def get_team_data(self, team_id: str) -> pd.DataFrame:
        """Get team data."""
        pass
```

### Step 2: Implement Adapter

```python
class PandasDataAdapter(DataAdapter):
    """Pandas implementation of DataAdapter."""
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self._load_data()
    
    def get_league_data(self, league_id: str) -> pd.DataFrame:
        # Implementation
        pass
```

### Step 3: Configure in DI Container

```python
from dependency_injector import containers, providers
from pathlib import Path

class Container(containers.DeclarativeContainer):
    # Configuration
    config = providers.Configuration()
    
    # Adapter factory - creates adapter based on config
    adapter = providers.Factory(
        PandasDataAdapter,
        data_path=config.data_path
    )
    
    # Service that uses adapter
    league_service = providers.Factory(
        LeagueService,
        adapter=adapter
    )

# Setup
container = Container()
container.config.data_path.from_value(Path("data/league.csv"))

# Use
service = container.league_service()  # Adapter automatically injected!
```

### Step 4: Use in Code

```python
from dependency_injector.wiring import Provide, inject

class LeagueService:
    @inject
    def __init__(self, adapter: DataAdapter = Provide[Container.adapter]):
        self.adapter = adapter
    
    def get_standings(self):
        data = self.adapter.get_league_data("league_1")
        # Process data...
```

## Real-World Example: Data Adapters

### Before (Without DI)

```python
# ❌ Tight coupling
class LeagueService:
    def __init__(self, database: str = None):
        self.adapter = DataAdapterFactory.create_adapter(
            DataAdapterSelector.PANDAS,
            database=database
        )
        # Hard to test - can't easily mock adapter
        # Hard to change - must modify this class
```

### After (With DI)

```python
# ✅ Loose coupling
class LeagueService:
    def __init__(self, adapter: DataAdapter, logger: Logger):
        self.adapter = adapter  # Injected dependency
        self.logger = logger    # Injected dependency
    
    def get_standings(self):
        self.logger.info("Getting league standings")
        data = self.adapter.get_league_data("league_1")
        return self._process_data(data)

# Configure in DI container
class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    # Adapter provider
    adapter = providers.Factory(
        PandasDataAdapter,
        data_path=config.data_path
    )
    
    # Logger provider
    logger = providers.Singleton(
        get_logger,
        name="LeagueService"
    )
    
    # Service provider (dependencies auto-injected)
    league_service = providers.Factory(
        LeagueService,
        adapter=adapter,
        logger=logger
    )

# Use
container = Container()
container.config.data_path.from_value(Path("data/"))
service = container.league_service()  # Dependencies injected!
```

## Testing With DI

DI makes testing much easier:

```python
# Test with mock adapter
def test_league_service():
    # Create mock adapter
    mock_adapter = Mock(spec=DataAdapter)
    mock_adapter.get_league_data.return_value = pd.DataFrame({"team": ["A", "B"]})
    
    # Inject mock
    service = LeagueService(adapter=mock_adapter, logger=Mock())
    
    # Test
    result = service.get_standings()
    assert len(result) == 2
    
    # Verify adapter was called
    mock_adapter.get_league_data.assert_called_once_with("league_1")
```

## Best Practices

### 1. Depend on Abstractions

```python
# ✅ Good: Depend on interface
def __init__(self, adapter: DataAdapter):
    self.adapter = adapter

# ❌ Bad: Depend on concrete class
def __init__(self):
    self.adapter = PandasDataAdapter()
```

### 2. Use Type Hints

```python
# ✅ Good: Type hints make dependencies clear
def __init__(self, adapter: DataAdapter, logger: Logger):
    self.adapter = adapter
    self.logger = logger
```

### 3. Keep Constructors Simple

```python
# ✅ Good: Just assign dependencies
def __init__(self, adapter: DataAdapter):
    self.adapter = adapter

# ❌ Bad: Complex logic in constructor
def __init__(self, adapter: DataAdapter):
    self.adapter = adapter
    self._initialize_cache()  # Move to separate method
    self._setup_connections()  # Move to separate method
```

### 4. Use DI Container for Complex Dependencies

```python
# ✅ Good: Container manages complex dependencies
container.league_service()  # All dependencies resolved automatically

# ❌ Bad: Manual dependency construction
adapter = PandasDataAdapter(path)
logger = get_logger("LeagueService")
service = LeagueService(adapter, logger)
```

## Common Patterns

### Factory Pattern with DI

```python
class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    # Factory that creates adapter based on config
    adapter_factory = providers.Factory(
        lambda adapter_type, path: {
            "pandas": PandasDataAdapter(path),
            "sqlite": SQLiteDataAdapter(path)
        }[adapter_type],
        adapter_type=config.adapter_type,
        path=config.data_path
    )
```

### Singleton Pattern with DI

```python
class Container(containers.DeclarativeContainer):
    # Singleton: Same instance every time
    logger = providers.Singleton(
        get_logger,
        name="App"
    )
    
    # Factory: New instance every time
    adapter = providers.Factory(
        PandasDataAdapter,
        path=config.data_path
    )
```

## Summary

**Dependency Injection:**
- ✅ Injects dependencies from outside
- ✅ Makes code testable
- ✅ Reduces coupling
- ✅ Increases flexibility

**DI Container:**
- ✅ Manages dependencies automatically
- ✅ Resolves dependency chains
- ✅ Configures once, uses everywhere

**For Data Adapters:**
- ✅ Define `DataAdapter` interface
- ✅ Implement `PandasDataAdapter`, `SQLiteDataAdapter`, etc.
- ✅ Configure in DI container
- ✅ Inject into services that need them

**Result:**
- ✅ Easy to test (inject mocks)
- ✅ Easy to change (swap implementations)
- ✅ Clean architecture (dependencies point inward)

