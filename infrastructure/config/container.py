"""
Dependency Injection Container

Configures and provides dependencies for the application.
"""

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

# Import modules that will be wired (we'll add these as we create them)
# from infrastructure.persistence.repositories import ...
# from infrastructure.persistence.adapters import ...
# from application.command_handlers import ...
# from application.query_handlers import ...


class Container(containers.DeclarativeContainer):
    """
    Dependency injection container.
    
    Configures all dependencies for the application.
    """
    
    # Configuration
    config = providers.Configuration()
    
    # Logging
    logger = providers.Singleton(
        # Will configure logging here
    )
    
    # Repositories (will be added as we create them)
    # team_repository = providers.Factory(...)
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

