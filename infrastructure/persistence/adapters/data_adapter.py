"""
Data Adapter Interface

Abstract interface for data adapters. All data adapters must implement this interface.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import pandas as pd


class DataAdapter(ABC):
    """
    Abstract interface for data adapters.
    
    Data adapters abstract the data source (CSV, SQLite, MySQL, etc.)
    and provide a consistent interface for accessing data.
    """
    
    @abstractmethod
    def get_league_data(self, league_id: str, season: Optional[str] = None) -> pd.DataFrame:
        """
        Get league data.
        
        Args:
            league_id: League identifier
            season: Optional season filter
        
        Returns:
            DataFrame with league data
        """
        pass
    
    @abstractmethod
    def get_team_data(self, team_id: str, season: Optional[str] = None) -> pd.DataFrame:
        """
        Get team data.
        
        Args:
            team_id: Team identifier
            season: Optional season filter
        
        Returns:
            DataFrame with team data
        """
        pass
    
    @abstractmethod
    def get_player_data(self, player_id: str, season: Optional[str] = None) -> pd.DataFrame:
        """
        Get player data.
        
        Args:
            player_id: Player identifier
            season: Optional season filter
        
        Returns:
            DataFrame with player data
        """
        pass
    
    @abstractmethod
    def get_game_data(self, game_id: str) -> pd.DataFrame:
        """
        Get game data.
        
        Args:
            game_id: Game identifier
        
        Returns:
            DataFrame with game data
        """
        pass
    
    # Event-specific methods for write operations
    @abstractmethod
    def get_event_data(self) -> pd.DataFrame:
        """
        Get all event data.
        
        Returns:
            DataFrame with all event data
        """
        pass
    
    @abstractmethod
    def save_event_data(self, df: pd.DataFrame) -> None:
        """
        Save event data to storage.
        
        Args:
            df: DataFrame with event data to save
        """
        pass
    
    # LeagueSeason-specific methods for write operations
    @abstractmethod
    def get_league_season_data(self) -> pd.DataFrame:
        """
        Get all league season data.
        
        Returns:
            DataFrame with all league season data
        """
        pass
    
    @abstractmethod
    def save_league_season_data(self, df: pd.DataFrame) -> None:
        """
        Save league season data to storage.
        
        Args:
            df: DataFrame with league season data to save
        """
        pass
    
    # TeamSeason-specific methods for write operations
    @abstractmethod
    def get_team_season_data(self) -> pd.DataFrame:
        """
        Get all team season data.
        
        Returns:
            DataFrame with all team season data
        """
        pass
    
    @abstractmethod
    def save_team_season_data(self, df: pd.DataFrame) -> None:
        """
        Save team season data to storage.
        
        Args:
            df: DataFrame with team season data to save
        """
        pass
    
    # Game-specific methods for write operations
    @abstractmethod
    def get_game_data(self) -> pd.DataFrame:
        """
        Get all game data.
        
        Returns:
            DataFrame with all game data
        """
        pass
    
    @abstractmethod
    def save_game_data(self, df: pd.DataFrame) -> None:
        """
        Save game data to storage.
        
        Args:
            df: DataFrame with game data to save
        """
        pass
    
    # Player-specific methods for write operations
    @abstractmethod
    def get_player_data(self) -> pd.DataFrame:
        """
        Get all player data.
        
        Returns:
            DataFrame with all player data
        """
        pass
    
    @abstractmethod
    def save_player_data(self, df: pd.DataFrame) -> None:
        """
        Save player data to storage.
        
        Args:
            df: DataFrame with player data to save
        """
        pass
    
    # League-specific methods for write operations
    @abstractmethod
    def get_league_data(self) -> pd.DataFrame:
        """
        Get all league data.
        
        Returns:
            DataFrame with all league data
        """
        pass
    
    @abstractmethod
    def save_league_data(self, df: pd.DataFrame) -> None:
        """
        Save league data to storage.
        
        Args:
            df: DataFrame with league data to save
        """
        pass
    
    # Team-specific methods for write operations
    @abstractmethod
    def get_team_data(self) -> pd.DataFrame:
        """
        Get all team data.
        
        Returns:
            DataFrame with all team data
        """
        pass
    
    @abstractmethod
    def save_team_data(self, df: pd.DataFrame) -> None:
        """
        Save team data to storage.
        
        Args:
            df: DataFrame with team data to save
        """
        pass

