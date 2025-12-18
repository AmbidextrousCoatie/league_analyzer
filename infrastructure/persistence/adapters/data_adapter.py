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

