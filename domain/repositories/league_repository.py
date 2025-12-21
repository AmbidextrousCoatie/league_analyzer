"""
League Repository Interface

Abstract interface for League entity repositories.
Storage-agnostic - works for CSV or SQL implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from domain.entities.league import League
from domain.value_objects.season import Season


class LeagueRepository(ABC):
    """
    Repository interface for League entities.
    
    Storage-agnostic interface - works for CSV or SQL implementations.
    """
    
    @abstractmethod
    async def get_by_id(self, league_id: UUID) -> Optional[League]:
        """
        Get league by ID.
        
        Args:
            league_id: UUID of the league
        
        Returns:
            League if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(self) -> List[League]:
        """
        Get all leagues.
        
        Returns:
            List of all leagues
        """
        pass
    
    @abstractmethod
    async def get_by_season(
        self,
        season: Season
    ) -> List[League]:
        """
        Get all leagues for a season.
        
        Args:
            season: Season value object
        
        Returns:
            List of leagues for the season
        """
        pass
    
    @abstractmethod
    async def find_by_name(
        self,
        name: str
    ) -> List[League]:
        """
        Find leagues by name (partial match).
        
        Args:
            name: Name to search for
        
        Returns:
            List of leagues matching the name
        """
        pass
    
    @abstractmethod
    async def add(self, league: League) -> League:
        """
        Add a new league.
        
        Args:
            league: League entity to add
        
        Returns:
            Added league
        """
        pass
    
    @abstractmethod
    async def update(self, league: League) -> League:
        """
        Update an existing league.
        
        Args:
            league: League entity to update
        
        Returns:
            Updated league
        
        Raises:
            EntityNotFoundError: If league doesn't exist
        """
        pass
    
    @abstractmethod
    async def delete(self, league_id: UUID) -> None:
        """
        Delete a league.
        
        Args:
            league_id: UUID of league to delete
        
        Raises:
            EntityNotFoundError: If league doesn't exist
        """
        pass
    
    @abstractmethod
    async def exists(self, league_id: UUID) -> bool:
        """
        Check if league exists.
        
        Args:
            league_id: UUID to check
        
        Returns:
            True if exists, False otherwise
        """
        pass

