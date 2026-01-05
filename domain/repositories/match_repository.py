"""
Match Repository Interface

Abstract interface for Match entity repositories.
Storage-agnostic - works for CSV or SQL implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from domain.entities.match import Match, MatchStatus


class MatchRepository(ABC):
    """
    Repository interface for Match entities.
    
    Storage-agnostic interface - works for CSV or SQL implementations.
    """
    
    @abstractmethod
    async def get_by_id(self, match_id: UUID) -> Optional[Match]:
        """
        Get match by ID.
        
        Args:
            match_id: UUID of the match
        
        Returns:
            Match if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Match]:
        """
        Get all matches.
        
        Returns:
            List of all matches
        """
        pass
    
    @abstractmethod
    async def get_by_event(self, event_id: UUID) -> List[Match]:
        """
        Get all matches for an event.
        
        Args:
            event_id: UUID of the event
        
        Returns:
            List of matches for the event
        """
        pass
    
    @abstractmethod
    async def get_by_event_and_round(
        self,
        event_id: UUID,
        round_number: int
    ) -> List[Match]:
        """
        Get all matches for a specific event and round.
        
        Args:
            event_id: UUID of the event
            round_number: Round number within the event
        
        Returns:
            List of matches for the event and round
        """
        pass
    
    @abstractmethod
    async def get_by_team(self, team_season_id: UUID) -> List[Match]:
        """
        Get all matches for a team (as team1 or team2).
        
        Args:
            team_season_id: UUID of the team season
        
        Returns:
            List of matches involving the team
        """
        pass
    
    @abstractmethod
    async def find_match(
        self,
        event_id: UUID,
        round_number: int,
        team1_team_season_id: UUID,
        team2_team_season_id: UUID
    ) -> Optional[Match]:
        """
        Find a match by event, round, and teams.
        
        Args:
            event_id: UUID of the event
            round_number: Round number
            team1_team_season_id: UUID of team1
            team2_team_season_id: UUID of team2
        
        Returns:
            Match if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_status(self, status: MatchStatus) -> List[Match]:
        """
        Get all matches with a specific status.
        
        Args:
            status: Match status to filter by
        
        Returns:
            List of matches with the status
        """
        pass
    
    @abstractmethod
    async def add(self, match: Match) -> Match:
        """
        Add a new match.
        
        Args:
            match: Match entity to add
        
        Returns:
            Added match
        """
        pass
    
    @abstractmethod
    async def update(self, match: Match) -> Match:
        """
        Update an existing match.
        
        Args:
            match: Match entity to update
        
        Returns:
            Updated match
        
        Raises:
            EntityNotFoundError: If match doesn't exist
        """
        pass
    
    @abstractmethod
    async def delete(self, match_id: UUID) -> None:
        """
        Delete a match.
        
        Args:
            match_id: UUID of match to delete
        
        Raises:
            EntityNotFoundError: If match doesn't exist
        """
        pass
    
    @abstractmethod
    async def exists(self, match_id: UUID) -> bool:
        """
        Check if match exists.
        
        Args:
            match_id: UUID to check
        
        Returns:
            True if exists, False otherwise
        """
        pass

