from data_access.adapters.data_adapter import DataAdapter
from data_access.schema import Columns, ColumnsExtra
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
    
    def get_league_match_day(self, league_name: str, season: str, week: int) -> pd.DataFrame:
        return self.df[self.df[Columns.league_name] == league_name][self.df[Columns.season] == season][self.df[Columns.week] == week]
    
    def get_league_season(self, league_name: str, season: str, week: int=None) -> pd.DataFrame:
        if week is None:
            return self.df[self.df[Columns.league_name] == league_name][self.df[Columns.season] == season]
        else:
            return self.df[self.df[Columns.league_name] == league_name][self.df[Columns.season] == season][self.df[Columns.week] <= week]

    def get_league_standings(self, league_name: str, season: str, week: int, cumulative: bool=False) -> pd.DataFrame:
        league_results = self.get_league_match_day(league_name=league_name, season=season, week=week) if not cumulative else self.get_league_season(league_name=league_name, season=season, week=week)
        
        league_standings_table = pd.DataFrame(columns=[Columns.team_name, Columns.points, ColumnsExtra.average_score])

        team_results_all = league_results.groupby(Columns.team_name)
        for team_name, team_results in team_results_all:
            
            points = team_results[Columns.points].sum()
            average_score = team_results[Columns.score].mean() / 2.0
            print(team_name)
            print(points)
            print(average_score)
            print(team_results)
            
            team_results_all[ColumnsExtra.average_score] = team_results_all[Columns.points] / team_results_all[Columns.match_number]
            league_standings_table = league_standings_table.append(team_results_all, ignore_index=True)

        


        results = league_results.groupby(Columns.team_name).sum().sort_values(by=Columns.points, ascending=False)
        print(results)
        return results

        