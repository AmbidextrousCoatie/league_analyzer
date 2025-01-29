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
    
    def get_filtered_data(self, columns: List[Columns]=None, filters_eq: dict=None, filters_lt: dict=None, filters_gt: dict=None, print_debug: bool=False) -> pd.DataFrame:
        filtered_df = self.df.copy()

        if print_debug:
            print("Initial DataFrame shape:", filtered_df.shape)
            print("Available columns:", filtered_df.columns.tolist())

        if filters_eq is not None:
            for column, value in filters_eq.items():
                if print_debug:
                    print(column + " == " + str(value))
                if value is not None:
                    filtered_df = filtered_df[filtered_df[column] == value]
            if print_debug:
                print(f"DataFrame shape after filtering: {filtered_df.shape}")  

        if filters_lt is not None:
            for column, value in filters_lt.items():
                if print_debug:
                    print(column + " < " + str(value))
                if value is not None:
                    filtered_df = filtered_df[filtered_df[column] < value]
            if print_debug:
                print(f"DataFrame shape after filtering: {filtered_df.shape}")  

        if filters_gt is not None:
            for column, value in filters_gt.items():
                if print_debug:
                    print(column + " > " + str(value))
                if value is not None:
                    filtered_df = filtered_df[filtered_df[column] > value]
            if print_debug:
                print(f"DataFrame shape after filtering: {filtered_df.shape}")  

        # extract columns
        if columns is not None:
            filtered_df = filtered_df[columns] 
            if print_debug:
                print("extracting columns: " + str(columns))
                print(f"DataFrame shape after extracting columns: {filtered_df.shape}")  
        return filtered_df
    
    def get_seasons(self, league_name: str=None) -> List[str]:
        if league_name is not None:
            return self.df[self.df[Columns.league_name] == league_name][Columns.season].unique().tolist()
        else:
            return self.df[Columns.season].unique().tolist()
    
    def get_leagues(self, season: str=None) -> List[str]:
        if season is not None:
            return self.df[self.df[Columns.season] == season][Columns.league_name].unique().tolist()
        else:
            return self.df[Columns.league_name].unique().tolist()
    
    def get_weeks(self, league_name: str=None, season: str=None) -> List[int]:
        """
        Fetches the weeks all available weeks in the database, filtered by league_name and season if provided.
        If league_name and season are provided, the weeks are fetched for the given league and season.
        If only one of the two is provided, the weeks are fetched for all leagues or seasons respectively.

        Args:
            league_name (str): The name of the league.
            season (str): The season.

        Returns:
            List[int]: The weeks.
        """
        filters_eq = dict()

        if league_name is not None:
            filters_eq[Columns.league_name] = league_name

        if season is not None:
            filters_eq[Columns.season] = season

        if filters_eq is not None:
            filtered_df = self.get_filtered_data(columns=[Columns.week], filters_eq=filters_eq)
        
        try:
            # Get unique weeks, sort them, and convert to list
            weeks = sorted(filtered_df[Columns.week].unique().tolist())
            # Filter out None/NaN values if any
            weeks = [week for week in weeks if week is not None]
            #print(f"Available weeks: {weeks}")  # Debug output
            return weeks
        except Exception as e:
            print(f"Error getting weeks: {str(e)}")
            return []
    
    def get_league_match_day(self, league_name: str, season: str, week: int) -> pd.DataFrame:
        return self.df[(self.df[Columns.league_name] == league_name) & (self.df[Columns.season] == season) & (self.df[Columns.week] == week)]
    
    def get_league_season(self, league_name: str, season: str, week: int=None) -> pd.DataFrame:
        if week is None:
            return self.df[self.df[Columns.league_name] == league_name][self.df[Columns.season] == season]
        else:
            return self.df[self.df[Columns.league_name] == league_name][self.df[Columns.season] == season][self.df[Columns.week] <= week]

    def get_league_standings(self, league_name: str, season: str, week: int, cumulative: bool=False) -> pd.DataFrame:
        deprecated = True
        return None
        
        league_results = self.get_league_match_day(league_name=league_name, season=season, week=week) if not cumulative else self.get_league_season(league_name=league_name, season=season, week=week)
        
        league_standings_table = pd.DataFrame(columns=[Columns.team_name, Columns.points, ColumnsExtra.average_score])

        team_results_all = league_results.groupby(Columns.team_name)
        for team_name, team_results in team_results_all:
            
            points = team_results[Columns.points].sum()
            average_score = round(team_results[Columns.score].mean() / 2.0, 2)
            print(team_name)
            print(points)
            print(average_score)
            print(team_results)
            
            team_results_all[ColumnsExtra.average_score] = team_results_all[Columns.points] / team_results_all[Columns.match_number]
            league_standings_table = league_standings_table.append(team_results_all, ignore_index=True)


        results = league_results.groupby(Columns.team_name).sum().sort_values(by=Columns.points, ascending=False)
        print(results)
      
        team_data = [{'Team': 'Team1', 'TotalPoints': 100, 'Average': 190, 'positionChange': +1, 'MatchPoints': 70, 'MatchAverage': 180},
                     {'Team': 'Team2', 'TotalPoints': 90, 'Average': 185, 'positionChange': -1, 'MatchPoints': 60, 'MatchAverage': 175}]
                    
        return {'standings': team_data}


        