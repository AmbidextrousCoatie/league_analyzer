import pandas as pd
import numpy as np
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
    

    def get_honor_scores(self, league_name:str=None, season:str=None, week:int=None, team_name:str=None, player_name:str=None, individual_scores:int=1, team_scores:int=1, indivdual_averages:int=1, team_averages:int=1) -> pd.DataFrame:
        filters_eq = {Columns.league_name: league_name, Columns.season: season, Columns.week: week, Columns.team_name: team_name, Columns.player_name: player_name}
        columns = [Columns.team_name, Columns.player_name, Columns.score, Columns.input_data, Columns.players_per_team]

        data = self.data_adapter.get_filtered_data(columns=columns, filters_eq=filters_eq)


        # individual scores
        if individual_scores > 0:
            individual_scores_df = data[data[Columns.input_data]==True][[Columns.player_name, Columns.score]].sort_values(by=Columns.score, ascending=False).head(individual_scores).copy()

        # team scores
        if team_scores > 0:
            team_scores_df = data[data[Columns.input_data]==False][[Columns.team_name, Columns.score]].sort_values(by=Columns.score, ascending=False).head(team_scores).copy()

        # individual averages - now including player name in result
        if indivdual_averages > 0:
            individual_averages_df = (data[data[Columns.input_data]==True]
                                    .groupby(Columns.player_name)[[Columns.score]]
                                    .mean()
                                    .sort_values(by=Columns.score, ascending=False)
                                    .head(indivdual_averages)
                                    .reset_index()  # This keeps the player_name column
                                    .copy())

        # team averages - now including team name in result
        if team_averages > 0:
            team_averages_df = (data[data[Columns.input_data]==False]
                            .groupby(Columns.team_name)[[Columns.score]]
                            .mean()
                            .sort_values(by=Columns.score, ascending=False)
                            .head(team_averages)
                            .reset_index()  # This keeps the team_name column
                            .copy())
        return individual_scores_df, team_scores_df, individual_averages_df, team_averages_df

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
 
        if week is None:
            week = int(max(self.get_weeks(league_name=league_name, season=season)))
        # history should not be deeper than the current week
        if depth is None:
            depth = 0
        if depth == -1:
            depth = week
 
        depth = min(depth, week)
        
        if debug_output:
            print("after validation: week: " + str(week) + " | depth: " + str(depth))
            print([i for i in range(week-depth, week+1)])
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

    def get_team_week(self, league_name: str, season: str, team_name: str,week: int) -> pd.DataFrame:
        filters_eq = {Columns.league_name: league_name, Columns.team_name: team_name, Columns.season: season, Columns.week: week}
        
        
        columns = [Columns.score, Columns.points, Columns.week]


        return self.data_adapter.get_filtered_data(columns=columns, filters_eq=filters_eq)

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


    def get_team_positions_during_season(self, league_name: str, season: str, cumulated: bool=False) -> pd.DataFrame:
        """Get team positions for each week during the season for all teams.
        Returns DataFrame with teams as rows and weeks as columns."""
        # Get all weekly standings
        #standings = self.get_league_standings(league_name, season)
        standings = self.get_league_history(league_name, season, depth=-1, debug_output=False)[[Columns.team_name, Columns.points, Columns.week, ColumnsExtra.score_average]]
        
        weekly_ranks = standings.sort_values([Columns.week, Columns.points, ColumnsExtra.score_average], ascending=[True, False, False])
        weekly_ranks[ColumnsExtra.position_weekly] = weekly_ranks.groupby(Columns.week)[Columns.points].rank(ascending=False, method='min')
        #print("weekly_ranks")
        #print(weekly_ranks)
        # 2. Cumulative rankings (based on total points up to each week)
        # First, get cumulative points for each team
        cumulative = weekly_ranks.sort_values(Columns.week)
        cumulative[ColumnsExtra.points_cumulative] = cumulative.groupby(Columns.team_name)[Columns.points].cumsum()
        
        # Then, rank teams based on cumulative points within each week
        cumulative[ColumnsExtra.position_cumulative] = cumulative.groupby(Columns.week)[ColumnsExtra.points_cumulative].rank(ascending=False, method='min')
        
        # Combine all information
        result = cumulative.sort_values([Columns.week, Columns.points], ascending=[True, False])
        #print("result")
        #print(result)
        result = result[[Columns.team_name, Columns.week, Columns.points, ColumnsExtra.position_weekly, ColumnsExtra.points_cumulative, ColumnsExtra.position_cumulative]]
        

        #print(result)   
        return result


        standings = standings.groupby(Columns.week) 

        print("###############################")
        data_cumulated = pd.DataFrame()
        for week, data in standings:
            #data_cumulated = data_cumulated.append(data)
            print("week: " + str(week))
            print(data.sort_values(by=Columns.team_name, ascending=False))
        print("###############################")


        standings[ColumnsExtra.points_cumulative] = standings.groupby(Columns.team_name)[Columns.points].cumsum()
        print(standings)

        # Extract positions for all teams for each week
        positions = []
        weeks = sorted(standings[Columns.week].unique())
        for output_name, column_name in [('Points', Columns.points), ('PointsCumulated',ColumnsExtra.points_cumulative)]:
            for week in weeks:
                # Get week data and sort by points to determine positions
                week_data = standings[standings[Columns.week] == week].sort_values(
                    by=Columns.points, 
                    ascending=False
                ).reset_index(drop=True)

                week_data_cumulated = standings[standings[Columns.week] == week].sort_values(
                    by=ColumnsExtra.points_cumulative, 
                    ascending=False
                ).reset_index(drop=True)
                
                # Add position and team data for each team in this week
                for index, row in week_data.iterrows():
                    positions.append({
                        'week': week,
                        'team': row[Columns.team_name],
                        'points': index + 1,  # position is 1-based
                        'points_cumulated': week_data_cumulated.index[index] + 1
                    })
        
        # Convert to wide format: teams as rows, weeks as columns
        positions_df = pd.DataFrame(positions)
        print(positions_df)
        positions_wide = positions_df.pivot(
            index='team',
            columns='week',
            position_per_week=ColumnsExtra.position
        )
        
        return positions_wide

    def get_team_averages_during_season(self, league_name: str, season: str) -> pd.DataFrame:
        """Get team average points for each week during the season for all teams.
        Returns DataFrame with teams as rows and weeks as columns."""
        # Get all weekly standings
        standings = self.get_league_standings(league_name, season)
        
        # Extract averages for all teams for each week
        averages = []
        weeks = sorted(standings['week'].unique())
        
        for week in weeks:
            week_data = standings[standings['week'] == week]
            for _, row in week_data.iterrows():
                averages.append({
                    'week': week,
                    'team': row['team'],
                    'average': row['average']
                })
        
        # Convert to wide format: teams as rows, weeks as columns
        averages_df = pd.DataFrame(averages)
        averages_wide = averages_df.pivot(
            index='team',
            columns='week',
            values='average'
        )
        
        return averages_wide

    def get_team_week_details(self, league_name: str, season: str, team_name: str, week: int, debug_output: bool=False) -> dict:
        """Get detailed team results for a specific week including individual and team stats"""
        
        # Get individual player results
        player_filters = {
            Columns.league_name: league_name,
            Columns.season: season,
            Columns.team_name: team_name,
            Columns.week: week,
            Columns.computed_data: False
        }
        
        player_opponent_filters = {
            Columns.league_name: league_name,
            Columns.season: season,
            Columns.team_name_opponent: team_name,
            Columns.week: week,
            Columns.computed_data: False
        }

        player_columns = [
            Columns.player_name,
            Columns.score,
            Columns.points,
            Columns.team_name_opponent,
            Columns.match_number,
            Columns.position, 
            Columns.week
        ]
        
        player_data = self.data_adapter.get_filtered_data(
            columns=player_columns,
            filters_eq=player_filters
        )
        if debug_output:
            print("player_data: \n" + str(player_data))
        
        player_opponent_data = self.data_adapter.get_filtered_data(
            columns=player_columns,
            filters_eq=player_opponent_filters
        )
        if debug_output:
            print("player_opponent_data: \n" + str(player_opponent_data))

        # Get team results
        team_filters = {
            Columns.league_name: league_name,
            Columns.season: season,
            Columns.team_name: team_name,
            Columns.week: week,
            Columns.computed_data: True
        }

        team_opponent_filters = {
            Columns.league_name: league_name,
            Columns.season: season,
            Columns.team_name_opponent: team_name,
            Columns.week: week,
            Columns.computed_data: True
        }
        
        columns_team = [Columns.score, Columns.points, Columns.team_name, Columns.team_name_opponent, Columns.week]



        team_data = self.data_adapter.get_filtered_data(
            columns=columns_team,
            filters_eq=team_filters
        )
        if debug_output:
            print("team_data: \n" + str(team_data))
        

        team_opponent_data = self.data_adapter.get_filtered_data(
            columns=columns_team,
            filters_eq=team_opponent_filters
        )
        if debug_output:
            print("team_opponent_data: \n" + str(team_opponent_data))

        # Get number of games
        n_games = len(player_data[Columns.team_name_opponent].unique())
        
        # Prepare player rows
        rows = []
        # Group by player to get their games
        player_groups = player_data.groupby(Columns.player_name)
        player_groups = sorted(player_groups, key=lambda x: x[1][Columns.position].iloc[0])
        
        for player_name, player_games in player_groups:
            player_row = {
                'type': 'player',
                'Position': int(player_games[Columns.position].iloc[0]),  # Get player's position
                'Name': player_name
            }
            
            # Add each game's scores and points
            for game_idx, (_, game) in enumerate(player_games.iterrows(), 1):
                player_row[f'Score_{game_idx}'] = int(game[Columns.score])
                player_row[f'Points_{game_idx}'] = float(round(game[Columns.points], 1))
                
            # Add totals

            player_row.update({
                'Points_Total': float(round(player_games[Columns.points].sum(), 1)),
                'Score_Total': int(player_games[Columns.score].sum()),
                'Score_Average': float(round(player_games[Columns.score].mean(), 2)) if not np.isnan(player_games[Columns.score].mean()) else 0
            })
            
            rows.append(player_row)
        
        # Add team row
        team_row = {
            'type': 'team',
            'Position': '-',
            'Name': team_name
        }

        opponent_row = {
            'type': 'opponent',
            'Position': '-',
            'Name': 'Opponents'
        }
        
        # Add team scores and points for each game
        for game_idx, (_, game) in enumerate(team_data.iterrows(), 1):
            team_row[f'Score_{game_idx}'] = int(game[Columns.score])
            team_row[f'Points_{game_idx}'] = float(round(game[Columns.points], 1))
        

        # Add opponent scores and points for each game
        for game_idx, (_, game) in enumerate(team_opponent_data.iterrows(), 1):
            opponent_row[f'Score_{game_idx}'] = int(game[Columns.score])
            opponent_row[f'Points_{game_idx}'] = float(round(game[Columns.points], 1))

        # Add team totals
        team_row.update({
            'Points_Total': float(round(team_data[Columns.points].sum(), 1)),
            'Score_Total': int(team_data[Columns.score].sum()),
            'Score_Average': float(round(player_data[Columns.score].mean(), 2)) if not np.isnan(team_data[Columns.score].mean()) else 0
        })

        # Add opponent totals
        opponent_row.update({
            'Points_Total': float(round(team_opponent_data[Columns.points].sum(), 1)),
            'Score_Total': int(team_opponent_data[Columns.score].sum()),
            'Score_Average': float(round(team_opponent_data[Columns.score].mean(), 2)) if not np.isnan(team_opponent_data[Columns.score].mean()) else 0
        })
        
        rows.append(team_row)
        rows.append(opponent_row)

        # Prepare header groups for the table
        header_groups = [
            { 'title': 'Player', 'colspan': 2 }
        ]
        
        # Add game columns
        for game_idx in range(1, n_games + 1):
            header_groups.append({ 
                'title': f'Game {game_idx}', 
                'colspan': 2 
            })
        
        # Add totals column
        header_groups.append({ 
            'title': 'Total', 
            'colspan': 3 
        })

        # Create columns based on number of games
        columns = [
            {
                'key': 'Position',
                'title': 'Pos',
                'className': 'text-center'
            },
            {
                'key': 'Name',
                'title': 'Name',
                'className': 'text-start'
            }
        ]
        
        # Add columns for each game
        for game_idx in range(1, n_games + 1):
            columns.extend([
                {
                    'key': f'Score_{game_idx}',
                    'title': 'Score',
                    'className': 'text-center'
                },
                {
                    'key': f'Points_{game_idx}',
                    'title': 'Pts',
                    'className': 'text-center'
                }
            ])
        
        # Add total columns
        columns.extend([
            {
                'key': 'Points_Total',
                'title': 'Points',
                'className': 'text-center'
            },
            {
                'key': 'Score_Total',
                'title': 'Score',
                'className': 'text-center'
            },
            {
                'key': 'Score_Average',
                'title': 'Avg',
                'className': 'text-center',
                'formatter': '(value || 0).toFixed(1)'
            }
        ])

        # Create the complete table configuration matching the component's expected structure
        table_config = {
            'data': rows,  # The actual data rows
            'columns': columns,  # Column definitions
            'headerGroups': header_groups,  # Header group definitions
            'rowNumbering': False,  # Disable row numbers
            'positionChange': False,  # Disable position change indicators
            'metadata': {  # Additional metadata
                'league': league_name,
                'season': season,
                'week': week,
                'location': 'TBD'
            }
        }
        if debug_output:
            print(table_config)
        return table_config



