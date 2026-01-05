"""
Game Result Repository Interface

Abstract interface for GameResult entity repositories.
Storage-agnostic - works for CSV or SQL implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from domain.entities.game_result import GameResult


class GameResultRepository(ABC):
    """
    Repository interface for GameResult entities.
    
    Storage-agnostic interface - works for CSV or SQL implementations.
    """
    
    @abstractmethod
    async def get_by_id(self, game_result_id: UUID) -> Optional[GameResult]:
        """
        Get game result by ID.
        
        Args:
            game_result_id: UUID of the game result
        
        Returns:
            GameResult if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(self) -> List[GameResult]:
        """
        Get all game results.
        
        Returns:
            List of all game results
        """
        pass
    
    @abstractmethod
    async def get_by_match(self, match_id: UUID) -> List[GameResult]:
        """
        Get all game results for a match.
        
        Args:
            match_id: UUID of the match
        
        Returns:
            List of game results for the match
        """
        pass
    
    @abstractmethod
    async def get_by_match_and_team(
        self,
        match_id: UUID,
        team_season_id: UUID
    ) -> List[GameResult]:
        """
        Get all game results for a match and team.
        
        Args:
            match_id: UUID of the match
            team_season_id: UUID of the team season
        
        Returns:
            List of game results for the match and team
        """
        pass
    
    @abstractmethod
    async def get_by_player(self, player_id: UUID) -> List[GameResult]:
        """
        Get all game results for a player.
        
        Args:
            player_id: UUID of the player
        
        Returns:
            List of game results for the player
        """
        pass
    
    @abstractmethod
    async def get_by_team(self, team_season_id: UUID) -> List[GameResult]:
        """
        Get all game results for a team.
        
        Args:
            team_season_id: UUID of the team season
        
        Returns:
            List of game results for the team
        """
        pass
    
    @abstractmethod
    async def find_by_match_and_position(
        self,
        match_id: UUID,
        team_season_id: UUID,
        position: int
    ) -> Optional[GameResult]:
        """
        Find a game result by match, team, and position.
        
        Args:
            match_id: UUID of the match
            team_season_id: UUID of the team season
            position: Lineup position (0-3)
        
        Returns:
            GameResult if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def add(self, game_result: GameResult) -> GameResult:
        """
        Add a new game result.
        
        Args:
            game_result: GameResult entity to add
        
        Returns:
            Added game result
        """
        pass
    
    @abstractmethod
    async def update(self, game_result: GameResult) -> GameResult:
        """
        Update an existing game result.
        
        Args:
            game_result: GameResult entity to update
        
        Returns:
            Updated game result
        
        Raises:
            EntityNotFoundError: If game result doesn't exist
        """
        pass
    
    @abstractmethod
    async def delete(self, game_result_id: UUID) -> None:
        """
        Delete a game result.
        
        Args:
            game_result_id: UUID of game result to delete
        
        Raises:
            EntityNotFoundError: If game result doesn't exist
        """
        pass
    
    @abstractmethod
    async def exists(self, game_result_id: UUID) -> bool:
        """
        Check if game result exists.
        
        Args:
            game_result_id: UUID to check
        
        Returns:
            True if exists, False otherwise
        """
        pass

