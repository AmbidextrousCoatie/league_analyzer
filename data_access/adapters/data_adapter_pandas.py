from data_access.adapters.data_adapter import DataAdapter
from data_access.schema import Columns
import pandas as pd
import pathlib
from typing import List

class DataAdapterPandas(DataAdapter):
    def __init__(self, path_to_csv_data: pathlib.Path=None, df: pd.DataFrame=None):
        if path_to_csv_data is not None and path_to_csv_data.exists():
            print(f"Loading data from {path_to_csv_data}")
            self.df = pd.read_csv(path_to_csv_data, sep=';')
        elif df is not None:
            self.df = df
        else:
            print(type(path_to_csv_data))
            print(type(df))
            raise ValueError("Either path_to_csv_data or df must be provided")
    
    def get_player_data(self, player_name: str) -> pd.DataFrame:
        return self.df[self.df[Columns.player_name] == player_name]
    
    def get_all_players(self) -> List[str]:
        return self.df[Columns.player_name].unique().tolist()
    
    def get_filtered_data(self, filters: dict) -> pd.DataFrame:
        filtered_df = self.df.copy()
        for column, value in filters.items():
            filtered_df = filtered_df[filtered_df[column] == value]
        return filtered_df 