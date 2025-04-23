import pandas as pd

from data_access.schema import Columns, ColumnsExtra
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional



class DataAdapter(ABC):
    """Abstract base class for data adapters"""
    
    # Define standard operators that all adapters should support
    OPERATORS = {
        "eq": "Equal to",
        "ne": "Not equal to",
        "lt": "Less than",
        "le": "Less than or equal to",
        "gt": "Greater than",
        "ge": "Greater than or equal to",
        "in": "In list",
        "not_in": "Not in list",
        "contains": "String contains",
        "startswith": "String starts with",
        "endswith": "String ends with"
    }
    
    @abstractmethod
    def get_player_data(self, player_name: str, season: str) -> pd.DataFrame:
        """Get player data for a specific season"""
        pass

    @abstractmethod
    def get_all_players(self) -> List[str]:
        pass

    @abstractmethod
    def get_filtered_data(self, filters: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
        """Get filtered data based on provided filters
        
        Args:
            filters: Dictionary of column names to filter dictionaries
                   Each filter dictionary should have:
                   - 'value': The value to filter by
                   - 'operator': The operator to use (must be one of OPERATORS keys)
        
        Returns:
            DataFrame containing the filtered data
        """
        pass

    @abstractmethod
    def get_league_standings(self, league_name: str, season: str) -> pd.DataFrame:
        """Get league standings for a specific season"""
        pass

