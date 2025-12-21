"""
Player Repository Interface

Abstract interface for Player entity repositories.
Storage-agnostic - works for CSV or SQL implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from domain.entities.player import Player


class PlayerRepository(ABC):
    """
    Repository interface for Player entities.
    
    Storage-agnostic interface - works for CSV or SQL implementations.
    """
    
    @abstractmethod
    async def get_by_id(self, player_id: UUID) -> Optional[Player]:
        """
        Get player by ID.
        
        Args:
            player_id: UUID of the player
        
        Returns:
            Player if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Player]:
        """
        Get all players.
        
        Returns:
            List of all players
        """
        pass
    
    @abstractmethod
    async def get_by_club(
        self,
        club_id: UUID
    ) -> List[Player]:
        """
        Get all players for a club.
        
        Args:
            club_id: UUID of the club
        
        Returns:
            List of players for the club
        """
        pass
    
    @abstractmethod
    async def get_by_team(
        self,
        team_id: UUID
    ) -> List[Player]:
        """
        Get all players for a team.
        
        Args:
            team_id: UUID of the team
        
        Returns:
            List of players for the team
        """
        pass
    
    @abstractmethod
    async def find_by_name(
        self,
        name: str
    ) -> List[Player]:
        """
        Find players by name (partial match).
        
        Args:
            name: Name to search for
        
        Returns:
            List of players matching the name
        """
        pass
    
    @abstractmethod
    async def add(self, player: Player) -> Player:
        """
        Add a new player.
        
        Args:
            player: Player entity to add
        
        Returns:
            Added player
        """
        pass
    
    @abstractmethod
    async def update(self, player: Player) -> Player:
        """
        Update an existing player.
        
        Args:
            player: Player entity to update
        
        Returns:
            Updated player
        
        Raises:
            EntityNotFoundError: If player doesn't exist
        """
        pass
    
    @abstractmethod
    async def delete(self, player_id: UUID) -> None:
        """
        Delete a player.
        
        Args:
            player_id: UUID of player to delete
        
        Raises:
            EntityNotFoundError: If player doesn't exist
        """
        pass
    
    @abstractmethod
    async def exists(self, player_id: UUID) -> bool:
        """
        Check if player exists.
        
        Args:
            player_id: UUID to check
        
        Returns:
            True if exists, False otherwise
        """
        pass

