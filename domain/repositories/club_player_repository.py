"""
ClubPlayer Repository Interface

Abstract interface for ClubPlayer persistence operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from domain.entities.club_player import ClubPlayer


class ClubPlayerRepository(ABC):
    """
    Abstract repository for ClubPlayer entities.
    
    Defines the contract for persisting and retrieving club-player relationships.
    """
    
    @abstractmethod
    async def get_by_id(self, club_player_id: UUID) -> Optional[ClubPlayer]:
        """
        Get club player by ID.
        
        Args:
            club_player_id: UUID of the club player relationship
        
        Returns:
            ClubPlayer entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(self) -> List[ClubPlayer]:
        """
        Get all club player relationships.
        
        Returns:
            List of all ClubPlayer entities
        """
        pass
    
    @abstractmethod
    async def get_by_player(self, player_id: UUID) -> List[ClubPlayer]:
        """
        Get all club memberships for a player.
        
        Args:
            player_id: UUID of the player
        
        Returns:
            List of ClubPlayer entities for this player
        """
        pass
    
    @abstractmethod
    async def get_by_club(self, club_id: UUID) -> List[ClubPlayer]:
        """
        Get all players for a club.
        
        Args:
            club_id: UUID of the club
        
        Returns:
            List of ClubPlayer entities for this club
        """
        pass
    
    @abstractmethod
    async def add(self, club_player: ClubPlayer) -> ClubPlayer:
        """
        Add a new club player relationship.
        
        Args:
            club_player: ClubPlayer entity to add
        
        Returns:
            Added ClubPlayer entity (may have generated ID)
        """
        pass
    
    @abstractmethod
    async def update(self, club_player: ClubPlayer) -> ClubPlayer:
        """
        Update an existing club player relationship.
        
        Args:
            club_player: ClubPlayer entity to update
        
        Returns:
            Updated ClubPlayer entity
        """
        pass
    
    @abstractmethod
    async def delete(self, club_player_id: UUID) -> bool:
        """
        Delete a club player relationship.
        
        Args:
            club_player_id: UUID of the club player relationship to delete
        
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def exists(self, club_player_id: UUID) -> bool:
        """
        Check if a club player relationship exists.
        
        Args:
            club_player_id: UUID of the club player relationship
        
        Returns:
            True if exists, False otherwise
        """
        pass

