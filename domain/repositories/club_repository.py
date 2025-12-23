"""
Club Repository Interface

Abstract interface for Club entity repositories.
Storage-agnostic - works for CSV or SQL implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from domain.entities.club import Club


class ClubRepository(ABC):
    """
    Repository interface for Club entities.
    
    Storage-agnostic interface - works for CSV or SQL implementations.
    """
    
    @abstractmethod
    async def get_by_id(self, club_id: UUID) -> Optional[Club]:
        """
        Get club by ID.
        
        Args:
            club_id: UUID of the club
        
        Returns:
            Club if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Club]:
        """
        Get all clubs.
        
        Returns:
            List of all clubs
        """
        pass
    
    @abstractmethod
    async def find_by_name(
        self,
        name: str
    ) -> List[Club]:
        """
        Find clubs by name (partial match).
        
        Args:
            name: Name to search for
        
        Returns:
            List of clubs matching the name
        """
        pass
    
    @abstractmethod
    async def add(self, club: Club) -> Club:
        """
        Add a new club.
        
        Args:
            club: Club entity to add
        
        Returns:
            Added club
        """
        pass
    
    @abstractmethod
    async def update(self, club: Club) -> Club:
        """
        Update an existing club.
        
        Args:
            club: Club entity to update
        
        Returns:
            Updated club
        """
        pass
    
    @abstractmethod
    async def delete(self, club_id: UUID) -> bool:
        """
        Delete a club by ID.
        
        Args:
            club_id: UUID of the club to delete
        
        Returns:
            True if deleted, False if not found
        """
        pass

