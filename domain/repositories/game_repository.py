"""
Game Repository Interface

Abstract interface for Game entity repositories.
Storage-agnostic - works for CSV or SQL implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from domain.entities.game import Game
from domain.value_objects.season import Season


class GameRepository(ABC):
    """
    Repository interface for Game entities.
    
    Storage-agnostic interface - works for CSV or SQL implementations.
    """
    
    @abstractmethod
    async def get_by_id(self, game_id: UUID) -> Optional[Game]:
        """
        Get game by ID.
        
        Args:
            game_id: UUID of the game
        
        Returns:
            Game if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Game]:
        """
        Get all games.
        
        Returns:
            List of all games
        """
        pass
    
    @abstractmethod
    async def get_by_event(
        self,
        event_id: UUID
    ) -> List[Game]:
        """
        Get all games for an event.
        
        Args:
            event_id: UUID of the event
        
        Returns:
            List of games for the event
        """
        pass
    
    @abstractmethod
    async def get_by_league(
        self,
        league_id: UUID
    ) -> List[Game]:
        """
        Get all games for a league.
        
        Args:
            league_id: UUID of the league
        
        Returns:
            List of games for the league
        """
        pass
    
    @abstractmethod
    async def get_by_week(
        self,
        league_id: UUID,
        week: int
    ) -> List[Game]:
        """
        Get games for a specific week.
        
        Args:
            league_id: UUID of the league
            week: Week number
        
        Returns:
            List of games for the week
        """
        pass
    
    @abstractmethod
    async def get_by_team(
        self,
        team_id: UUID
    ) -> List[Game]:
        """
        Get all games for a team (as team or opponent).
        
        Args:
            team_id: UUID of the team
        
        Returns:
            List of games involving the team
        """
        pass
    
    @abstractmethod
    async def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Game]:
        """
        Get games within a date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
        
        Returns:
            List of games in the date range
        """
        pass
    
    @abstractmethod
    async def add(self, game: Game) -> Game:
        """
        Add a new game.
        
        Args:
            game: Game entity to add
        
        Returns:
            Added game
        """
        pass
    
    @abstractmethod
    async def update(self, game: Game) -> Game:
        """
        Update an existing game.
        
        Args:
            game: Game entity to update
        
        Returns:
            Updated game
        
        Raises:
            EntityNotFoundError: If game doesn't exist
        """
        pass
    
    @abstractmethod
    async def delete(self, game_id: UUID) -> None:
        """
        Delete a game.
        
        Args:
            game_id: UUID of game to delete
        
        Raises:
            EntityNotFoundError: If game doesn't exist
        """
        pass
    
    @abstractmethod
    async def exists(self, game_id: UUID) -> bool:
        """
        Check if game exists.
        
        Args:
            game_id: UUID to check
        
        Returns:
            True if exists, False otherwise
        """
        pass

