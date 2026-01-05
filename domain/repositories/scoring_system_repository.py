"""
ScoringSystem Repository Interface

Abstract interface for ScoringSystem persistence operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from domain.entities.scoring_system import ScoringSystem


class ScoringSystemRepository(ABC):
    """Abstract repository for ScoringSystem entities."""
    
    @abstractmethod
    async def get_by_id(self, scoring_system_id: UUID) -> Optional[ScoringSystem]:
        """
        Get scoring system by ID.
        
        Args:
            scoring_system_id: UUID of the scoring system
        
        Returns:
            ScoringSystem if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(self) -> List[ScoringSystem]:
        """
        Get all scoring systems.
        
        Returns:
            List of all scoring systems
        """
        pass
    
    @abstractmethod
    async def find_by_name(self, name: str) -> Optional[ScoringSystem]:
        """
        Find scoring system by name.
        
        Args:
            name: Name of the scoring system
        
        Returns:
            ScoringSystem if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def add(self, scoring_system: ScoringSystem) -> ScoringSystem:
        """
        Add a new scoring system.
        
        Args:
            scoring_system: ScoringSystem entity to add
        
        Returns:
            Added ScoringSystem entity
        """
        pass
    
    @abstractmethod
    async def update(self, scoring_system: ScoringSystem) -> ScoringSystem:
        """
        Update an existing scoring system.
        
        Args:
            scoring_system: ScoringSystem entity to update
        
        Returns:
            Updated ScoringSystem entity
        """
        pass
    
    @abstractmethod
    async def delete(self, scoring_system_id: UUID) -> bool:
        """
        Delete a scoring system.
        
        Args:
            scoring_system_id: UUID of the scoring system to delete
        
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def exists(self, scoring_system_id: UUID) -> bool:
        """
        Check if scoring system exists.
        
        Args:
            scoring_system_id: UUID of the scoring system
        
        Returns:
            True if exists, False otherwise
        """
        pass

