from typing import Optional, List, Dict, Any, Union
from data_access.adapters.data_adapter import DataAdapter
from enum import Enum
from database.config import path_to_csv_data
from abc import ABC, abstractmethod
from data_access.models.league_models import TeamSeasonPerformance

class DataAdapterSelector(Enum):
    """Enum for selecting data adapter type"""
    PANDAS = "pandas"
    MYSQL = "mysql"
    SQLITE = "sqlite"

class DataAdapterFactory:
    @staticmethod
    def create_adapter(adapter_type: DataAdapterSelector) -> DataAdapter:
        if adapter_type == DataAdapterSelector.PANDAS:
            from data_access.adapters.data_adapter_pandas import DataAdapterPandas
            return DataAdapterPandas(path_to_csv_data=path_to_csv_data)
        elif adapter_type == DataAdapterSelector.MYSQL:
            from data_access.adapters.data_adapter_mysql import MySQLAdapter
            return MySQLAdapter()
        elif adapter_type == DataAdapterSelector.SQLITE:
            from data_access.adapters.data_adapter_sqlite import SQLiteAdapter
            return SQLiteAdapter()
        else:
            raise ValueError(f"Unknown adapter type: {adapter_type}")

class DataAdapter(ABC):
    """Abstract base class for data adapters"""
    
    @abstractmethod
    def get_filtered_data(self, filters: Optional[Dict[str, Any]] = None, 
                         columns: Optional[List[str]] = None,
                         sort_by: Optional[Union[str, List[str]]] = None,
                         ascending: bool = True,
                         limit: Optional[int] = None):
        """Get filtered data"""
        pass
    
    @abstractmethod
    def get_weeks(self, season: str, league: str) -> List[int]:
        """Get available weeks for a season and league"""
        pass
    
    @abstractmethod
    def get_league_standings(self, season: str, league: str, week: Optional[int] = None) -> List[TeamSeasonPerformance]:
        """Get league standings for a specific season, league, and week"""
        pass 