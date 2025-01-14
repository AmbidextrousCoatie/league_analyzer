from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Optional

class DataAdapter(ABC):
    @abstractmethod
    def get_player_data(self, player_name: str) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_all_players(self) -> List[str]:
        pass
    
    @abstractmethod
    def get_filtered_data(self, filters: dict) -> pd.DataFrame:
        pass 