import pandas as pd
from data_access.adapters.data_adapter_factory import DataAdapterFactory, DataAdapterSelector   
from typing import List
from data_access.schema import Columns, ColumnsExtra

class Server:
    # fetches basic dataframes from data adapter
    # converts basic dataframes to aggregated dataframes
    # forwards aggregated dataframes to app
    def __init__(self):
        self.data_adapter = DataAdapterFactory.get_adapter(DataAdapterSelector.PANDAS)

    def get_player_data(self, player_name: str) -> pd.DataFrame:
        return self.data_adapter.get_player_data(player_name)
    
    def get_seasons(self) -> List[str]:
        return self.data_adapter.get_seasons()
    
    def get_leagues(self, season: str=None) -> List[str]:
        return self.data_adapter.get_leagues(season=season)
    
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
        return self.data_adapter.get_weeks(league_name=league_name, season=season)
    

    def get_teams_in_league_season(self, league_name:str, season:str, debug_output:bool=False) -> List[str]:
        filters = {Columns.league_name: league_name, Columns.season: season}
        
        columns = [Columns.team_name]
        if debug_output:
            print ("get_teams_in_league_season: filter:" + str(filters) + " | columns:" + str(columns))
        return self.data_adapter.get_filtered_data(columns=columns, filters_eq=filters)[Columns.team_name].unique().tolist()

    def aggregate_league_table(self, data_individual: pd.DataFrame, data_team: pd.DataFrame, week:int, debug: bool=False) -> pd.DataFrame:
        """
        High level query on the database.
        Aggregates the league table for a given week.

        Both input dataframes conain the columns are grouped by team_name.

        Args:
            data_individual (pd.DataFrame): The individual data for the week.
            data_team (pd.DataFrame): The team data for the week.
            week (int): The week number.
            debug (bool): Whether to print debug information.

        Returns:
            pd.DataFrame: The aggregated league table.
        """
        data_individual_count = data_individual.groupby(Columns.team_name).size()
        data_individual = data_individual.groupby(Columns.team_name).sum() 
        
        data_team_count = data_team.groupby(Columns.team_name).size()
        data_team = data_team.groupby(Columns.team_name).sum()  

        data_league = data_individual.copy()

        # add average score
        data_league[ColumnsExtra.score_average] = round(data_individual[Columns.score] / data_individual_count, 2)
        data_league[Columns.points] += data_team[Columns.points]
        data_league[Columns.week] = week
        #data_league[ColumnsExtra.position] = 1

        if debug:
            print(data_league.sort_values(by=Columns.points, ascending=False))
        return data_league.reset_index(Columns.team_name).sort_values(by=Columns.points, ascending=False) #, data_week_team

    def get_league_history(self, league_name: str, season: str, week: int=None, depth: int=None, debug_output:bool=False) -> pd.DataFrame:
        """
        High level query on the database.
        Fetches the league history for a given league and season up until a given week.

        collects the results of multple weeks using the get_league_week method and concatenates them into a single dataframe.

        Args:
            league_name (str): The name of the league.
            season (str): The season.
            week (int): The week number.
            depth (int): The depth of the history.
            debug_output (bool): Whether to print debug information.

        Returns:
            pd.DataFrame: The league history for the given league, season and week. Columns: team_name, points, score, week, score_average
        """
        if debug_output:
            print("Entering: week: " + str(week) + " | depth: " + str(depth))
        if depth is None:
            depth = 0
        # history should not be deeper than the current week
        depth = min(depth, week)
        print([i for i in range(week-depth, week+1)])
        if debug_output:
            print("after validation: week: " + str(week) + " | depth: " + str(depth))
        data_league_history = pd.DataFrame()
        for week_current in range(week-depth, week+1):
            if debug_output:
                print(f"fetching week {week_current}")
            data_week = self.get_league_week(league_name=league_name, season=season, week=week_current)
            if data_league_history.empty:
                data_league_history = data_week
            else:
                data_league_history = pd.concat([data_league_history, data_week])
            if debug_output:
                print(data_league_history)
        

        return data_league_history
        # Apply base filters
        return self.get_league_standings(league_name=league_name, season=season, week=week)

        
        
        for current_week in range(week-depth, week):
            pass

    def get_league_week(self, league_name: str, season: str, week: int) -> pd.DataFrame:
        """
        High level database query.
        Coposes a table that represent's a league's results in a given week.

        A datafranme for individual results and one for team results are fetched, both dataframes are filtered for league_name, season and week.
        Both dataframes contain the columns team_name, points, score and week.
        
        The dataframes are aggregated into a single dataframe that contains the columns team_name, points, score, week and score_average.
        The score_average is the average score of the individual results as well as the teams' results.

        The aggregated dataframe is sorted by points and returned

        Args:
            league_name (str): The name of the league.
            season (str): The season.
            week (int): The week number.

        Returns:
            pd.DataFrame: The league standings for the given week. Columns: team_name, points, score, week, score_average
        """
        filters_eq_individual = {Columns.league_name: league_name, Columns.season: season, Columns.week: week, Columns.computed_data: False}
        filters_eq_team = {Columns.league_name: league_name, Columns.season: season, Columns.week: week, Columns.computed_data: True}
        
        columns = [Columns.team_name, Columns.points, Columns.score, Columns.week]
        data_week_individual = self.data_adapter.get_filtered_data(columns=columns, filters_eq=filters_eq_individual)
        data_week_team = self.data_adapter.get_filtered_data(columns=columns, filters_eq=filters_eq_team)
        #print("data individual: " + str(data_week_individual))
        #print("data team: " + str(data_week_team))
        return self.aggregate_league_table(data_week_individual, data_week_team, week)

    def get_league_standings(self, league_name: str, season: str, week: int) -> pd.DataFrame:
        """
        High level database query.
        Coposes a table that represent's a league's standings in a given week, e.g. the sum of all scores and points up until the given week

        A datafranme for individual results and one for team results are fetched, both dataframes are filtered for league_name, season and weeks.
        Both dataframes contain the columns team_name, points, score and weeks.
        
        The dataframes are aggregated into a single dataframe that contains the columns team_name, points, score, weeks and score_average.
        The score_average is the average score of the individual results as well as the teams' results.

        The aggregated dataframe is sorted by points and returned

        Args:
            league_name (str): The name of the league.
            season (str): The season.
            week (int): The week number.

        Returns:
            pd.DataFrame: The league standings for the given week. Columns: team_name, points, score, week, score_average
        """
        filters_eq_individual = {Columns.league_name: league_name, Columns.season: season, Columns.computed_data: False}
        filters_lt_individual = {Columns.week: week+1}
        filters_eq_team = {Columns.league_name: league_name, Columns.season: season, Columns.computed_data: True}
        filters_lt_team = {Columns.week: week+1}
        
        columns = [Columns.team_name, Columns.points, Columns.score]
        data_week_individual = self.data_adapter.get_filtered_data(columns=columns, filters_eq=filters_eq_individual, filters_lt=filters_lt_individual)
        data_week_team = self.data_adapter.get_filtered_data(columns=columns, filters_eq=filters_eq_team, filters_lt=filters_lt_team)

        return self.aggregate_league_table(data_week_individual, data_week_team, week)        


    def __depr__get_league_standings_history(self, league_name: str, season: str, week: int) -> pd.DataFrame:
        
        columns = [Columns.team_name, Columns.points, Columns.score, Columns.week]
        filters_player = {Columns.league_name: league_name, Columns.season: season, Columns.computed_data: False}
        filters_team = {Columns.league_name: league_name, Columns.season: season, Columns.computed_data: True}
        data_player = self.data_adapter.get_filtered_data(columns=columns, filters_eq=filters_player)
        data_team = self.data_adapter.get_filtered_data(columns=columns, filters_eq=filters_team)
       
        data_player = data_player.groupby([Columns.week,Columns.team_name])

        # number of games per match per team is stored in the size of the groupby. this would also accounts for absent players that didnt score anything but does not interfere with the average score calculation
        number_of_games = data_player.size()
        data_player = data_player.sum()
        data_team = data_team.groupby([Columns.week,Columns.team_name]).sum()
       
        # add points from team total and average scores
        data_league = data_player
        data_league[Columns.points] += data_team[Columns.points]
        data_league[ColumnsExtra.score_average] = round(data_player[Columns.score] / number_of_games, 2)
        #print(data_league)

