import pandas as pd
from data_access.pd_dataframes import fetch_column, fetch_data
from database.definitions import Columns
from app.services.data_manager import DataManager
from business_logic.statistics import calculate_score_average_player
from business_logic.statistics import calculate_score_average_team

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
        
        # Filter for the specific player
        player_df = fetch_data(df, values_to_filter_for={Columns.player_name: player_name})
        
        # Calculate all-time average
        all_time_average = calculate_score_average_player(player_df, player_name)
        
        return {
            'name': player_name,
            'id': 12,
            'all_time_average': all_time_average
        }
    
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