"""
Position Comparison Repository Interface

Abstract interface for PositionComparison entity repositories.
Storage-agnostic - works for CSV or SQL implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from domain.entities.position_comparison import PositionComparison


class PositionComparisonRepository(ABC):
    """
    Repository interface for PositionComparison entities.
    
    Storage-agnostic interface - works for CSV or SQL implementations.
    """
    
    @abstractmethod
    async def get_by_id(self, comparison_id: UUID) -> Optional[PositionComparison]:
        """
        Get position comparison by ID.
        
        Args:
            comparison_id: UUID of the position comparison
        
        Returns:
            PositionComparison if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(self) -> List[PositionComparison]:
        """
        Get all position comparisons.
        
        Returns:
            List of all position comparisons
        """
        pass
    
    @abstractmethod
    async def get_by_match(self, match_id: UUID) -> List[PositionComparison]:
        """
        Get all position comparisons for a match.
        
        Args:
            match_id: UUID of the match
        
        Returns:
            List of position comparisons for the match
        """
        pass
    
    @abstractmethod
    async def get_by_match_and_position(
        self,
        match_id: UUID,
        position: int
    ) -> Optional[PositionComparison]:
        """
        Get position comparison for a specific match and position.
        
        Args:
            match_id: UUID of the match
            position: Lineup position (0-3)
        
        Returns:
            PositionComparison if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_player(self, player_id: UUID) -> List[PositionComparison]:
        """
        Get all position comparisons involving a player (as team1 or team2).
        
        Args:
            player_id: UUID of the player
        
        Returns:
            List of position comparisons involving the player
        """
        pass
    
    @abstractmethod
    async def add(self, comparison: PositionComparison) -> PositionComparison:
        """
        Add a new position comparison.
        
        Args:
            comparison: PositionComparison entity to add
        
        Returns:
            Added position comparison
        """
        pass
    
    @abstractmethod
    async def update(self, comparison: PositionComparison) -> PositionComparison:
        """
        Update an existing position comparison.
        
        Args:
            comparison: PositionComparison entity to update
        
        Returns:
            Updated position comparison
        
        Raises:
            EntityNotFoundError: If position comparison doesn't exist
        """
        pass
    
    @abstractmethod
    async def delete(self, comparison_id: UUID) -> None:
        """
        Delete a position comparison.
        
        Args:
            comparison_id: UUID of position comparison to delete
        
        Raises:
            EntityNotFoundError: If position comparison doesn't exist
        """
        pass
    
    @abstractmethod
    async def exists(self, comparison_id: UUID) -> bool:
        """
        Check if position comparison exists.
        
        Args:
            comparison_id: UUID to check
        
        Returns:
            True if exists, False otherwise
        """
        pass

