import pandas as pd


from abc import ABC, abstractmethod
from typing import List


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

    @abstractmethod
    def get_league_standings(self, league_name: str, season: str, week: int, cumulative: bool=False) -> pd.DataFrame:
        pass

