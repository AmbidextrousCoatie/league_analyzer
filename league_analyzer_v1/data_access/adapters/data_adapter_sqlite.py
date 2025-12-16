from data_access.adapters.data_adapter import DataAdapter
import pandas as pd
from typing import List

class DataAdapterSqlite(DataAdapter):
    def __init__(self):
        self.df = pd.DataFrame({"ERROR": ["SQLITE NOT IMPLEMENTED YET"]})
    
    def get_player_data(self, player_name: str) -> pd.DataFrame:
        return self.df
    
    def get_all_players(self) -> List[str]:
        return self.df.columns.tolist()
    
    def get_filtered_data(self, filters: dict) -> pd.DataFrame:
        filtered_df = self.df.copy()
        return filtered_df 