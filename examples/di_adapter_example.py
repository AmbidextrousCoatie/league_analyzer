"""
Example: Using Dependency Injection with Data Adapters

This demonstrates how to use DI for data adapters.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.config.container import container
from infrastructure.persistence.adapters.data_adapter import DataAdapter
from infrastructure.logging import get_logger

# Configure container
# In real app, this would come from settings/config
container.config.data_path.from_value(
    Path("league_analyzer_v1/database/data/bowling_ergebnisse_real.csv")
)

# Get logger
logger = get_logger(__name__)


class LeagueService:
    """
    Example service that uses DataAdapter via dependency injection.
    
    Notice: LeagueService doesn't know about PandasDataAdapter specifically.
    It only depends on the DataAdapter interface.
    """
    
    def __init__(self, adapter: DataAdapter):
        """
        Initialize service with injected adapter.
        
        Args:
            adapter: DataAdapter instance (injected via DI)
        """
        self.adapter = adapter
        self.logger = get_logger(__name__)
        self.logger.info("LeagueService initialized")
    
    def get_league_standings(self, league_id: str, season: str = None):
        """Get league standings using injected adapter."""
        self.logger.info(f"Getting standings for league: {league_id}")
        data = self.adapter.get_league_data(league_id, season)
        self.logger.info(f"Retrieved {len(data)} rows")
        return data


def example_without_di():
    """Example: Without DI (tight coupling)"""
    print("\n=== Without DI (Tight Coupling) ===")
    
    # ❌ Bad: Service creates its own adapter
    from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
    
    adapter = PandasDataAdapter(Path("league_analyzer_v1/database/data/bowling_ergebnisse_real.csv"))
    service = LeagueService(adapter)
    
    # Hard to test - can't easily mock adapter
    # Hard to change - must modify this code to use different adapter
    print("Service created with hardcoded adapter")


def example_with_di():
    """Example: With DI (loose coupling)"""
    print("\n=== With DI (Loose Coupling) ===")
    
    # ✅ Good: Adapter injected from container
    adapter = container.data_adapter()
    service = LeagueService(adapter)
    
    # Easy to test - can inject mock adapter
    # Easy to change - just configure different adapter in container
    print("Service created with injected adapter")
    
    # Use service
    try:
        data = service.get_league_standings("league_1")
        print(f"Retrieved {len(data)} rows")
    except Exception as e:
        print(f"Error (expected if data doesn't exist): {e}")


def example_testing_with_di():
    """Example: Testing with DI (easy mocking)"""
    print("\n=== Testing With DI (Easy Mocking) ===")
    
    from unittest.mock import Mock
    
    # Create mock adapter
    mock_adapter = Mock(spec=DataAdapter)
    mock_adapter.get_league_data.return_value = Mock()  # Mock DataFrame
    mock_adapter.get_league_data.return_value.__len__ = Mock(return_value=10)
    
    # Inject mock adapter
    service = LeagueService(mock_adapter)
    
    # Test
    result = service.get_league_standings("league_1")
    
    # Verify adapter was called correctly
    mock_adapter.get_league_data.assert_called_once_with("league_1", None)
    print("[OK] Test passed - adapter was called correctly")


def example_swapping_adapters():
    """Example: Swapping adapters (flexibility)"""
    print("\n=== Swapping Adapters (Flexibility) ===")
    
    # Same service code works with different adapters!
    
    # Use Pandas adapter
    container.config.data_path.from_value(
        Path("league_analyzer_v1/database/data/bowling_ergebnisse_real.csv")
    )
    pandas_adapter = container.data_adapter()
    service1 = LeagueService(pandas_adapter)
    print("[OK] Service created with Pandas adapter")
    
    # Could easily swap to SQLite adapter (when implemented)
    # container.config.adapter_type.from_value("sqlite")
    # sqlite_adapter = container.data_adapter()
    # service2 = LeagueService(sqlite_adapter)
    # print("[OK] Service created with SQLite adapter")
    
    # Same service code, different adapters!
    print("[OK] Same service code works with different adapters!")


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Dependency Injection Example")
    logger.info("=" * 60)
    
    example_without_di()
    example_with_di()
    example_testing_with_di()
    example_swapping_adapters()
    
    logger.info("=" * 60)
    logger.info("Example completed")
    logger.info("=" * 60)

