"""
LeagueSeason Repository Interface

Abstract interface for LeagueSeason entity repositories.
Storage-agnostic - works for CSV or SQL implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from domain.entities.league_season import LeagueSeason
from domain.value_objects.season import Season


class LeagueSeasonRepository(ABC):
    """
    Repository interface for LeagueSeason entities.
    
    Storage-agnostic interface - works for CSV or SQL implementations.
    """
    
    @abstractmethod
    async def get_by_id(self, league_season_id: UUID) -> Optional[LeagueSeason]:
        """
        Get league season by ID.
        
        Args:
            league_season_id: UUID of the league season
        
        Returns:
            LeagueSeason if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(self) -> List[LeagueSeason]:
        """
        Get all league seasons.
        
        Returns:
            List of all league seasons
        """
        pass
    
    @abstractmethod
    async def get_by_league(
        self,
        league_id: UUID
    ) -> List[LeagueSeason]:
        """
        Get all league seasons for a league.
        
        Args:
            league_id: UUID of the league
        
        Returns:
            List of league seasons for the league
        """
        pass
    
    @abstractmethod
    async def get_by_season(
        self,
        season: Season
    ) -> List[LeagueSeason]:
        """
        Get all league seasons for a specific season.
        
        Args:
            season: Season value object
        
        Returns:
            List of league seasons for the season
        """
        pass
    
    @abstractmethod
    async def get_by_league_and_season(
        self,
        league_id: UUID,
        season: Season
    ) -> Optional[LeagueSeason]:
        """
        Get league season by league and season.
        
        Args:
            league_id: UUID of the league
            season: Season value object
        
        Returns:
            LeagueSeason if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def add(self, league_season: LeagueSeason) -> LeagueSeason:
        """
        Add a new league season.
        
        Args:
            league_season: LeagueSeason entity to add
        
        Returns:
            Added league season
        """
        pass
    
    @abstractmethod
    async def update(self, league_season: LeagueSeason) -> LeagueSeason:
        """
        Update an existing league season.
        
        Args:
            league_season: LeagueSeason entity to update
        
        Returns:
            Updated league season
        
        Raises:
            EntityNotFoundError: If league season doesn't exist
        """
        pass
    
    @abstractmethod
    async def delete(self, league_season_id: UUID) -> None:
        """
        Delete a league season.
        
        Args:
            league_season_id: UUID of league season to delete
        
        Raises:
            EntityNotFoundError: If league season doesn't exist
        """
        pass
    
    @abstractmethod
    async def exists(self, league_season_id: UUID) -> bool:
        """
        Check if league season exists.
        
        Args:
            league_season_id: UUID to check
        
        Returns:
            True if exists, False otherwise
        """
        pass

