"""
Team Repository Interface

Abstract interface for Team entity repositories.
Storage-agnostic - works for CSV or SQL implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from domain.entities.team import Team


class TeamRepository(ABC):
    """
    Repository interface for Team entities.
    
    Storage-agnostic interface - works for CSV or SQL implementations.
    """
    
    @abstractmethod
    async def get_by_id(self, team_id: UUID) -> Optional[Team]:
        """
        Get team by ID.
        
        Args:
            team_id: UUID of the team
        
        Returns:
            Team if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Team]:
        """
        Get all teams.
        
        Returns:
            List of all teams
        """
        pass
    
    @abstractmethod
    async def get_by_league(
        self,
        league_id: UUID
    ) -> List[Team]:
        """
        Get all teams for a league.
        
        Args:
            league_id: UUID of the league
        
        Returns:
            List of teams for the league
        """
        pass
    
    @abstractmethod
    async def find_by_name(
        self,
        name: str
    ) -> List[Team]:
        """
        Find teams by name (partial match).
        
        Args:
            name: Name to search for
        
        Returns:
            List of teams matching the name
        """
        pass
    
    @abstractmethod
    async def add(self, team: Team) -> Team:
        """
        Add a new team.
        
        Args:
            team: Team entity to add
        
        Returns:
            Added team
        """
        pass
    
    @abstractmethod
    async def update(self, team: Team) -> Team:
        """
        Update an existing team.
        
        Args:
            team: Team entity to update
        
        Returns:
            Updated team
        
        Raises:
            EntityNotFoundError: If team doesn't exist
        """
        pass
    
    @abstractmethod
    async def delete(self, team_id: UUID) -> None:
        """
        Delete a team.
        
        Args:
            team_id: UUID of team to delete
        
        Raises:
            EntityNotFoundError: If team doesn't exist
        """
        pass
    
    @abstractmethod
    async def exists(self, team_id: UUID) -> bool:
        """
        Check if team exists.
        
        Args:
            team_id: UUID to check
        
        Returns:
            True if exists, False otherwise
        """
        pass

