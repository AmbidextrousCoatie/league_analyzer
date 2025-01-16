import pandas as pd
from data_access.pd_dataframes import fetch_column, fetch_data
from data_access.schema import Columns
from app.services.data_manager import DataManager
from business_logic.statistics import calculate_score_average_player, calculate_games_count_player

class PlayerService:
    def __init__(self):
        self.data_manager = DataManager()

    def get_all_players(self):
        players = fetch_column(
            database_df=self.data_manager.df,
            column_name=Columns.player_name,
            unique=True,
            as_list=True
        )
        return [{'id': name, 'name': name} for name in sorted(players)]

    def get_personal_stats(self, player_name: str, season: str = 'all'):
        df = self.data_manager.df
        print(player_name)
        # Filter for the specific player
        player_df = fetch_data(df, values_to_filter_for={Columns.player_name: player_name})

        player_id = player_df.iloc[0][Columns.player_id]
        print(player_id)
        # Calculate all-time average
        # Calculate all-time average
        all_time_average = calculate_score_average_player(player_df, player_name)
        all_time_game_count = len(player_df)

        # Calculate per-season average
        per_season_average = calculate_score_average_player(player_df, player_name, group_by=Columns.season)
        per_season_game_count = calculate_games_count_player(player_df, player_name, group_by=Columns.season)
        print(per_season_average)
        seasons = per_season_average.index.to_list() 
        averages = per_season_average.values.tolist()
        gamecount = [30] # per_season_game_count.values.tolist()

        # TODO: Add team comparison
        stats = {
            'name': player_name,
            'id': int(player_id),
            'team': player_df.iloc[0][Columns.team_name],
            'average': [all_time_average] + averages,
            'game_count': [all_time_game_count] + gamecount,
            'season': ["all time"] + seasons,

        }

        #print(stats)
    
        return stats
    
    def get_team_comparison(self, player_id: str, season: str = 'all'):
        """Compare player stats with team averages"""
        pass
    
    def get_historical_data(self, player_id: str):
        """Get historical performance data"""
        pass
    
    def get_all_players(self):
        """Get list of all players for selection"""
        players = fetch_column(
            database_df=self.data_manager.df,
            column_name=Columns.player_name,
            unique=True,
            as_list=True
        )
        return [{'id': name, 'name': name} for name in sorted(players)]

    def search_players(self, search_term):
        """Search players by name"""
        # Get all players first
        all_players = self.get_all_players()
        
        # Filter players based on search term
        if search_term:
            search_term = search_term.lower()
            filtered_players = [
                player for player in all_players 
                if search_term in player['name'].lower()
            ]
            return filtered_players
        
        return all_players

