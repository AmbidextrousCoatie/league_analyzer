from data_access.interfaces import DataAdapter
import pandas as pd
from typing import List

class DataAdapterPandas(DataAdapter):
    def __init__(self):
        self.df = pd.read_csv('database/data/bowling_ergebnisse.csv', sep=';')
    
    def get_player_data(self, player_name: str) -> pd.DataFrame:
        return self.df[self.df['Player'] == player_name]
    
    def get_all_players(self) -> List[str]:
        return self.df['Player'].unique().tolist()
    
    def get_filtered_data(self, filters: dict) -> pd.DataFrame:
        filtered_df = self.df.copy()
        for column, value in filters.items():
            filtered_df = filtered_df[filtered_df[column] == value]
        return filtered_df 