"""
Pandas Data Adapter Implementation

Pandas-based implementation of DataAdapter interface.
"""

from pathlib import Path
from typing import Optional
import pandas as pd
from infrastructure.logging import get_logger
from infrastructure.persistence.adapters.data_adapter import DataAdapter

logger = get_logger(__name__)


class PandasDataAdapter(DataAdapter):
    """
    Pandas implementation of DataAdapter.
    
    Reads data from CSV files using pandas.
    """
    
    def __init__(self, data_path: Path):
        """
        Initialize Pandas adapter.
        
        Args:
            data_path: Path to CSV data file
        
        Raises:
            ValueError: If data_path doesn't exist
        """
        if not data_path.exists():
            raise ValueError(f"Data file not found: {data_path}")
        
        self.data_path = data_path
        self._data: Optional[pd.DataFrame] = None
        logger.debug(f"Initialized PandasDataAdapter with path: {data_path}")
    
    def _load_data(self) -> pd.DataFrame:
        """Load data from CSV file."""
        if self._data is None:
            logger.debug(f"Loading data from {self.data_path}")
            self._data = pd.read_csv(self.data_path)
            logger.info(f"Loaded {len(self._data)} rows from {self.data_path}")
        return self._data
    
    def get_league_data(self, league_id: str, season: Optional[str] = None) -> pd.DataFrame:
        """Get league data."""
        logger.debug(f"Getting league data: league={league_id}, season={season}")
        data = self._load_data()
        
        # Filter by league
        filtered = data[data['league'] == league_id]
        
        # Filter by season if provided
        if season:
            filtered = filtered[filtered['season'] == season]
        
        logger.debug(f"Found {len(filtered)} rows for league {league_id}")
        return filtered
    
    def get_team_data(self, team_id: str, season: Optional[str] = None) -> pd.DataFrame:
        """Get team data."""
        logger.debug(f"Getting team data: team={team_id}, season={season}")
        data = self._load_data()
        
        # Filter by team
        filtered = data[data['team'] == team_id]
        
        # Filter by season if provided
        if season:
            filtered = filtered[filtered['season'] == season]
        
        logger.debug(f"Found {len(filtered)} rows for team {team_id}")
        return filtered
    
    def get_player_data(self, player_id: str, season: Optional[str] = None) -> pd.DataFrame:
        """Get player data."""
        logger.debug(f"Getting player data: player={player_id}, season={season}")
        data = self._load_data()
        
        # Filter by player
        filtered = data[data['player'] == player_id]
        
        # Filter by season if provided
        if season:
            filtered = filtered[filtered['season'] == season]
        
        logger.debug(f"Found {len(filtered)} rows for player {player_id}")
        return filtered
    
    def get_game_data(self, game_id: str) -> pd.DataFrame:
        """Get game data."""
        logger.debug(f"Getting game data: game={game_id}")
        data = self._load_data()
        
        # Filter by game
        filtered = data[data['game_id'] == game_id]
        
        logger.debug(f"Found {len(filtered)} rows for game {game_id}")
        return filtered

