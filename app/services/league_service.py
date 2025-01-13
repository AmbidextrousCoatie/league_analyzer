from business_logic.statistics import query_database
from app.services.data_manager import DataManager
from database.definitions import Columns
import pandas as pd

class LeagueService:
    def __init__(self):
        self.data_manager = DataManager()
        self.df = self.data_manager.df

    def get_valid_combinations(self):
        """Returns all existing combinations in the database"""
        combinations = self.df[['Season', 'League', 'Week']].drop_duplicates()
        print(combinations)
        return combinations.to_dict('records')

    def get_seasons(self):
        """Returns all possible seasons"""
        return sorted(self.df[Columns.season].unique().tolist())

    def get_leagues(self):
        """Returns all possible leagues"""
        return sorted(self.df[Columns.league_name].unique().tolist())

    def get_weeks(self):
        """Returns all possible match days"""
        try:
            # Get unique weeks, sort them, and convert to list
            weeks = sorted(self.df['Week'].unique().tolist())
            # Filter out None/NaN values if any
            weeks = [week for week in weeks if week is not None]
            print(f"Available weeks: {weeks}")  # Debug output
            return weeks
        except Exception as e:
            print(f"Error getting weeks: {str(e)}")
            return []

    def get_table(self, season, league, match_day=None):
        # Build filters based on selections
        filters = {
            'Season': season,
            'League': league
        }
        
        # Only add Week filter if match_day is provided and valid
        if match_day and match_day.strip():
            try:
                week_value = int(match_day)
                filters['Week'] = week_value
            except ValueError:
                print(f"Invalid match day value: {match_day}")
        
        print(f"Final filters: {filters}")  # Debug log
        
        # Get filtered data
        df_filtered = query_database(self.df, filters)
        
        if df_filtered.empty:
            return []
        
        # Group by team and calculate stats
        table_data = df_filtered.groupby('Team').agg({
            'Match Number': 'count',  # Games played
            'Points': 'sum',
            'Score': 'mean'
        }).reset_index()
        
        print(f"Aggregated data:\n{table_data}")  # Debug log
        
        # Rename columns for clarity
        table_data.columns = ['Team', 'Games', 'Points', 'Average']
        
        # Sort by points (descending) and average (descending)
        table_data = table_data.sort_values(['Points', 'Average'], ascending=[False, False])
        
        return table_data.to_dict('records')