"""
Match Scoring Repository Interface

Abstract interface for MatchScoring entity repositories.
Storage-agnostic - works for CSV or SQL implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from domain.entities.match_scoring import MatchScoring


class MatchScoringRepository(ABC):
    """
    Repository interface for MatchScoring entities.
    
    Storage-agnostic interface - works for CSV or SQL implementations.
    """
    
    @abstractmethod
    async def get_by_id(self, scoring_id: UUID) -> Optional[MatchScoring]:
        """
        Get match scoring by ID.
        
        Args:
            scoring_id: UUID of the match scoring
        
        Returns:
            MatchScoring if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(self) -> List[MatchScoring]:
        """
        Get all match scorings.
        
        Returns:
            List of all match scorings
        """
        pass
    
    @abstractmethod
    async def get_by_match(self, match_id: UUID) -> List[MatchScoring]:
        """
        Get all match scorings for a match (all scoring systems).
        
        Args:
            match_id: UUID of the match
        
        Returns:
            List of match scorings for the match
        """
        pass
    
    @abstractmethod
    async def get_by_match_and_system(
        self,
        match_id: UUID,
        scoring_system_id: str
    ) -> Optional[MatchScoring]:
        """
        Get match scoring for a specific match and scoring system.
        
        Args:
            match_id: UUID of the match
            scoring_system_id: ID of the scoring system
        
        Returns:
            MatchScoring if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_scoring_system(self, scoring_system_id: str) -> List[MatchScoring]:
        """
        Get all match scorings for a scoring system.
        
        Args:
            scoring_system_id: ID of the scoring system
        
        Returns:
            List of match scorings for the scoring system
        """
        pass
    
    @abstractmethod
    async def add(self, scoring: MatchScoring) -> MatchScoring:
        """
        Add a new match scoring.
        
        Args:
            scoring: MatchScoring entity to add
        
        Returns:
            Added match scoring
        """
        pass
    
    @abstractmethod
    async def update(self, scoring: MatchScoring) -> MatchScoring:
        """
        Update an existing match scoring.
        
        Args:
            scoring: MatchScoring entity to update
        
        Returns:
            Updated match scoring
        
        Raises:
            EntityNotFoundError: If match scoring doesn't exist
        """
        pass
    
    @abstractmethod
    async def delete(self, scoring_id: UUID) -> None:
        """
        Delete a match scoring.
        
        Args:
            scoring_id: UUID of match scoring to delete
        
        Raises:
            EntityNotFoundError: If match scoring doesn't exist
        """
        pass
    
    @abstractmethod
    async def exists(self, scoring_id: UUID) -> bool:
        """
        Check if match scoring exists.
        
        Args:
            scoring_id: UUID to check
        
        Returns:
            True if exists, False otherwise
        """
        pass

