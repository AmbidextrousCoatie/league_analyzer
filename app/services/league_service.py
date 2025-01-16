from business_logic.statistics import query_database
from app.services.data_manager import DataManager
from data_access.schema import Columns
from data_access.adapters.data_adapter import DataAdapter
from data_access.adapters.data_adapter_factory import DataAdapterFactory, DataAdapterSelector
import pandas as pd

class LeagueService:
    def __init__(self, adapter_type: DataAdapterSelector = DataAdapterSelector.PANDAS):
        self.data_adapter: DataAdapter = DataAdapterFactory.get_adapter(adapter_type)

    def get_valid_combinations(self):
        """Returns all existing combinations in the database"""
        combinations = self.df[[Columns.season, Columns.league_name, Columns.week]].drop_duplicates()
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
            weeks = sorted(self.df[Columns.week].unique().tolist())
            # Filter out None/NaN values if any
            weeks = [week for week in weeks if week is not None]
            #print(f"Available weeks: {weeks}")  # Debug output
            return weeks
        except Exception as e:
            print(f"Error getting weeks: {str(e)}")
            return []

    def get_standings_table(self, league:str, season:str, week:int=None, cumulative=False, include_changes=False):
        """Calculate standings for a specific match day or cumulative standings"""
        # Apply base filters
        
        standings_week = self.data_adapter.get_league_standings(league_name=league, season=season, week=week, cumulative=cumulative)

        df_filtered = query_database(df, filters)
        # Apply match day filter
        if match_day is not None:
            if cumulative:
                df_filtered = df_filtered[df_filtered[Columns.week] <= match_day]
            else:
                df_filtered = df_filtered[df_filtered[Columns.week] == match_day]
        
        # Calculate standings
        if not df_filtered.empty:
            standings = df_filtered.groupby('Team').agg({
                'Points': 'sum',
                'Score': 'mean'
            }).reset_index()
            print(standings)
            standings.columns = ['Team', 'Points', 'Average']
            standings = standings.sort_values(['Points', 'Average'], ascending=[False, False])
            
            # Calculate position changes if requested
            if include_changes and match_day and match_day > 1:
                # Get previous match day standings
                prev_filters = filters.copy()
                df_prev = query_database(df, prev_filters)
                df_prev = df_prev[df_prev[Columns.week] <= (match_day - 1)]
                
                prev_standings = df_prev.groupby('Team').agg({
                    'Points': 'sum',
                    'Score': 'mean'
                }).reset_index()
                
                prev_standings.columns = ['Team', 'Points', 'Average']
                prev_standings = prev_standings.sort_values(['Points', 'Average'], ascending=[False, False])
                
                # Calculate position changes (fixed calculation)
                current_positions = {team: pos for pos, team in enumerate(standings['Team'], 1)}
                prev_positions = {team: pos for pos, team in enumerate(prev_standings['Team'], 1)}
                
                # Positive number means team moved up, negative means team moved down
                standings['PositionChange'] = standings['Team'].apply(
                    lambda team: prev_positions.get(team, 0) - current_positions.get(team, 0)
                )
                
            return standings
        
        return pd.DataFrame(columns=['Team', 'Points', 'Average'])

    def get_table(self, season, league, week=None, cumulative=False):
        """Get combined table data for frontend"""
        
        standings_week = self.data_adapter.get_league_standings(season=season, league=league, week=week, cumulative=cumulative)
        
        filters = {
            Columns.season: season,
            Columns.league_name: league #,
            #Columns.input_data: True
        }
        
        try:
            week_value = int(match_day) if match_day and match_day.strip() else None
            print(f"Processing week: {week_value}")
        except ValueError:
            print(f"Invalid match day value: {match_day}")
            week_value = None
        
        # Get match day standings
        match_day_standings = pd.DataFrame()
        if week_value is not None:
            match_day_standings = self.get_standings_table(
                self.df, filters, week_value, cumulative=False, include_changes=False
            )
            print(f"Match day standings found: {not match_day_standings.empty}")
        
        # Get cumulative standings
        season_standings = self.get_standings_table(
            self.df, filters, week_value, cumulative=True, include_changes=(week_value > 1)
        )
        
        # Combine the data for frontend
        combined_data = []
        for _, row in season_standings.iterrows():
            team_data = {
                'Team': row['Team'],
                'TotalPoints': row['Points'],
                'Average': row['Average'] ,
                'positionChange': row.get('PositionChange', 0)
            }
            
            if not match_day_standings.empty:
                match_team = match_day_standings[match_day_standings['Team'] == row['Team']]
                if not match_team.empty:
                    team_data.update({
                        'MatchPoints': match_team['Points'].iloc[0],
                        'MatchAverage': match_team['Average'].iloc[0] 
                    })
            
            combined_data.append(team_data)
        
        return {'standings': combined_data}