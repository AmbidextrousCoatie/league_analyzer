"""
Dependency Injection Container

Configures and provides dependencies for the application.
"""

from pathlib import Path
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

# Import adapters
from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
from infrastructure.persistence.adapters.data_adapter import DataAdapter

# Import logging
from infrastructure.logging import get_logger


class Container(containers.DeclarativeContainer):
    """
    Dependency injection container.
    
    Configures all dependencies for the application.
    
    Usage:
        container = Container()
        container.config.data_path.from_value(Path("data/league.csv"))
        adapter = container.data_adapter()
    """
    
    # Configuration
    config = providers.Configuration()
    
    # Data Adapter
    # Factory: Creates new instance each time (can be changed to Singleton if needed)
    data_adapter = providers.Factory(
        PandasDataAdapter,
        data_path=config.data_path
    )
    
    # Logger factory (creates logger for specific name)
    logger_factory = providers.Factory(
        get_logger
    )
    
    # Repositories (will be added as we create them)
    # team_repository = providers.Factory(
    #     PandasTeamRepository,
    #     adapter=data_adapter
    # )
    # league_repository = providers.Factory(...)
    # game_repository = providers.Factory(...)
    # player_repository = providers.Factory(...)
    
    # Unit of Work
    # unit_of_work = providers.Factory(...)
    
    # Command Handlers (will be added as we create them)
    # create_game_handler = providers.Factory(...)
    # update_game_handler = providers.Factory(...)
    
    # Query Handlers (will be added as we create them)
    # get_league_standings_handler = providers.Factory(...)
    # get_team_stats_handler = providers.Factory(...)


# Global container instance
container = Container()

