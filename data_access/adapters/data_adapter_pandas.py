from data_access.adapters.data_adapter import DataAdapter
from data_access.schema import Columns, ColumnsExtra
import pandas as pd
import pathlib
import operator
from typing import List, Dict, Any, Optional, Tuple, Callable, Union

from data_access.models.league_models import LeagueQuery
from data_access.models.league_models import TeamSeasonPerformance, TeamWeeklyPerformance
from data_access.models.raw_data_models import RawPlayerData, RawTeamData, RawLeagueData



# Define comparison operators
OPERATORS = {
    "eq": operator.eq,  # Equal
    "ne": operator.ne,  # Not equal
    "lt": operator.lt,  # Less than
    "le": operator.le,  # Less than or equal
    "gt": operator.gt,  # Greater than
    "ge": operator.ge,  # Greater than or equal
    "in": lambda x, y: x in y,  # In list
    "not_in": lambda x, y: x not in y,  # Not in list
    "contains": lambda x, y: y in x if isinstance(x, str) else False,  # String contains
    "startswith": lambda x, y: x.startswith(y) if isinstance(x, str) else False,  # String starts with
    "endswith": lambda x, y: x.endswith(y) if isinstance(x, str) else False,  # String ends with
}

class DataAdapterPandas(DataAdapter):
    def __init__(self, path_to_csv_data: pathlib.Path=None, df: pd.DataFrame=None):
        self.data_path = path_to_csv_data
        self.df = None
        
        if path_to_csv_data is not None and path_to_csv_data.exists():
            self._load_data()
        elif df is not None:
            self.df = df
        else:
            print(type(path_to_csv_data))
            print(type(df))
            raise ValueError("Either path_to_csv_data or df must be provided")
    
    def _load_data(self):
        """Load data from CSV file"""
        print(f"Loading data from {self.data_path}")
        self.df = pd.read_csv(self.data_path, sep=';')

    def set_dataframe(self, df):
        """Set the dataframe directly (for testing or in-memory operations)"""
        self.df = df

    def get_filtered_data(self, 
                          filters: Optional[Dict[str, Dict[str, Any]]] = None, 
                          columns: Optional[List[str]] = None,
                          sort_by: Optional[Union[str, List[str]]] = None,
                          ascending: bool = True,
                          limit: Optional[int] = None) -> pd.DataFrame:
        """
        Get filtered data from the dataframe with enhanced filtering capabilities.
        
        Args:
            filters: Dictionary of column names to filter dictionaries
                   Each filter dictionary should have:
                   - 'value': The value to filter by
                   - 'operator': The operator to use (must be one of OPERATORS keys)
            columns: List of columns to include in the result
            sort_by: Column(s) to sort by
            ascending: Sort direction (True for ascending, False for descending)
            limit: Maximum number of rows to return
            
        Returns:
            Filtered pandas DataFrame
        """
        if self.df is None:
            return pd.DataFrame()
        
        # Start with the full dataframe
        result = self.df
        
        # Apply filters
        if filters:
            for column, filter_dict in filters.items():
                if column in result.columns:
                    value = filter_dict.get('value')
                    operator_name = filter_dict.get('operator')
                    
                    if value is not None and operator_name in OPERATORS:
                        op_func = OPERATORS[operator_name]
                        
                        # Apply the filter using a vectorized operation if possible
                        if operator_name in ["in", "not_in"]:
                            if operator_name == "in":
                                result = result[result[column].isin(value)]
                            else:
                                result = result[~result[column].isin(value)]
                        elif operator_name in ["contains", "startswith", "endswith"]:
                            # String operations
                            if operator_name == "contains":
                                result = result[result[column].str.contains(value, na=False)]
                            elif operator_name == "startswith":
                                result = result[result[column].str.startswith(value, na=False)]
                            elif operator_name == "endswith":
                                result = result[result[column].str.endswith(value, na=False)]
                        else:
                            # Comparison operators
                            mask = result[column].apply(lambda x: op_func(x, value))
                            result = result[mask]
        
        # Select columns
        if columns:
            # Only include columns that exist in the dataframe
            valid_columns = [col for col in columns if col in result.columns]
            if valid_columns:
                result = result[valid_columns]
        
        # Sort the results
        if sort_by:
            if isinstance(sort_by, str):
                sort_by = [sort_by]
            
            # Only sort by columns that exist in the dataframe
            valid_sort_columns = [col for col in sort_by if col in result.columns]
            if valid_sort_columns:
                result = result.sort_values(by=valid_sort_columns, ascending=ascending)
        
        # Apply limit
        if limit is not None and limit > 0:
            result = result.head(limit)
        
        return result


    
    def get_weeks(self, season: str, league: str) -> List[int]:
        """Get available weeks for a season and league"""
        filters = {"Season": season, "League": league}
        result = self.get_filtered_data__deprecated(filters_eq=filters)
        
        if result.empty:
            return []
        
        if "Week" in result.columns:
            weeks = sorted(int(week) for week in result["Week"].unique())
            return weeks
        
        return []

    def get_league_week_data(self, query: LeagueQuery) -> pd.DataFrame:
        """Get league data for specific weeks"""
        # Convert query to filters
        filters = {}
        
        if query.season:
            filters["Season"] = query.season
        
        if query.league:
            filters["League"] = query.league
        
        if query.week is not None:
            filters["Week"] = query.week
        
        if query.team:
            filters["Team"] = query.team
        
        # Get filtered data
        result = self.get_filtered_data__deprecated(filters_eq=filters)
        
        return result

    def get_player_data(self, player_name: str) -> pd.DataFrame:
        return self.df[self.df[Columns.player_name] == player_name]
    
    def get_all_players(self) -> List[str]:
        return self.df[Columns.player_name].unique().tolist()
    
    def get_filtered_data__deprecated(self, columns: List[Columns]=None, filters_eq: dict=None, filters_lt: dict=None, filters_gt: dict=None, print_debug: bool=False) -> pd.DataFrame:
        filtered_df = self.df.copy()

        if print_debug:
            print("Initial DataFrame shape:", filtered_df.shape)
            print("Available columns:", filtered_df.columns.tolist())

        if filters_eq is not None:
            for column, value in filters_eq.items():
                if print_debug:
                    print(column + " == " + str(value))
                if value is not None:
                    if isinstance(value, list):
                        filtered_df = filtered_df[filtered_df[column].isin(value)]
                    else:
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
    
    def get_seasons(self, league_name: str=None, team_name: str=None) -> List[str]:
        filters_eq = dict()
        filters_eq[Columns.league_name] = league_name
        filters_eq[Columns.team_name] = team_name
        return self.get_filtered_data__deprecated(columns=[Columns.season], filters_eq=filters_eq)[Columns.season].unique().tolist()
    
    def get_leagues(self, season: str=None, team_name: str=None) -> List[str]:
        filters_eq = dict()
        filters_eq[Columns.season] = season
        filters_eq[Columns.team_name] = team_name
        return self.get_filtered_data__deprecated(columns=[Columns.league_name], filters_eq=filters_eq)[Columns.league_name].unique().tolist()
    
    def get_weeks__deprecated(self, league_name: str=None, season: str=None, team_name: str=None) -> List[int]:
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

        if team_name is not None:
            filters_eq[Columns.team_name] = team_name

        if filters_eq is not None:
            filtered_df = self.get_filtered_data__deprecated(columns=[Columns.week], filters_eq=filters_eq)
        
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

    def get_latest_events(self, limit=5):
        """Get the latest league events based on date."""
        # Get unique combinations of season, league, week, and date
        events = self.df[[Columns.season, Columns.league_name, Columns.week, Columns.date]].drop_duplicates()

        # Sort by date in descending order and get the latest events
        latest_events = events.sort_values(by=Columns.date, ascending=False).head(limit)

        return latest_events    

    def get_league_standings(self, season: str, league: str, week: Optional[int] = None) -> List[TeamSeasonPerformance]:
        """
        Get league standings for a specific season, league, and week.
        
        Args:
            season: The season identifier
            league: The league name
            week: The week number (if None, gets all weeks)
            
        Returns:
            List of TeamSeasonPerformance objects
        """
        # Create a query object
        query = LeagueQuery(
            season=season,
            league=league,
            max_week=week
        )
        
        print(query)
        # Get filtered data
        filters = query.to_filter_dict()
        league_data = self.get_filtered_data(filters=filters)
        
        if league_data.empty:
            return []
        
        # Group by team and week to get team performances
        team_performances = {}
        
        # Process each row in the dataframe
        for _, row in league_data.iterrows():
            team_id = row[Columns.team_name]  # Using team name as ID for now
            team_name = row[Columns.team_name]
            week_num = row[Columns.week]
            score = row[Columns.score]
            points = row[Columns.points]
            players_per_team = row.get(Columns.players_per_team, 4)  # Get players per team or default to 4
            
            # Initialize team data if not exists
            if team_id not in team_performances:
                team_performances[team_id] = {
                    'team_id': team_id,
                    'team_name': team_name,
                    'total_score': 0,
                    'total_points': 0,
                    'total_number_of_games': 0,
                    'weekly_performances': {}
                }
            
            # Initialize week data if not exists
            if week_num not in team_performances[team_id]['weekly_performances']:
                team_performances[team_id]['weekly_performances'][week_num] = {
                    'score': 0,
                    'points': 0,
                    'number_of_games': 0,
                    'players_per_team': players_per_team
                }
            
            # Add score and points
            team_performances[team_id]['weekly_performances'][week_num]['score'] += score
            team_performances[team_id]['weekly_performances'][week_num]['points'] += points
            team_performances[team_id]['weekly_performances'][week_num]['number_of_games'] += 1
            # Update team totals
            team_performances[team_id]['total_score'] += score
            team_performances[team_id]['total_points'] += points
            team_performances[team_id]['total_number_of_games'] += 1
        # Convert to TeamSeasonPerformance objects
        result = []
        for team_id, data in team_performances.items():
            # Calculate average (using players_per_team from each week)
            total_games = 0
            for week_num, week_data in data['weekly_performances'].items():
                # Each player plays one game per week
                total_games += week_data['players_per_team']
            
            # @todo: this is a hack to normalize the score, the factor 2.5 is arbitrary, fix it in the structure
            average = data['total_score'] / (total_games) if total_games > 0 else 0
            
            # Create weekly performance objects
            weekly_performances = []
            for week_num, week_data in data['weekly_performances'].items():
                print(week_data)
                weekly_performances.append( 
                    TeamWeeklyPerformance(
                        team_id=data['team_id'],
                        team_name=data['team_name'],
                        week=week_num,
                        score=week_data['score'],
                        points=week_data['points'],
                        number_of_games=week_data['number_of_games'],
                        players_per_team=week_data['players_per_team']
                    )
                )
            
            # Sort weekly performances by week
            weekly_performances.sort(key=lambda x: x.week)
            
            # Create the TeamSeasonPerformance
            result.append(
                TeamSeasonPerformance(
                    team_id=data['team_id'],
                    team_name=data['team_name'],
                    total_score=data['total_score'],
                    total_points=data['total_points'],
                    average=round(average, 2),
                    weekly_performances=weekly_performances
                )
            )
        
        return result
    
    def _convert_to_raw_player_data(self, row: pd.Series) -> RawPlayerData:
        """Convert a pandas Series to RawPlayerData"""
        return RawPlayerData(
            player_name=str(row[Columns.player_name]),
            team_name=str(row[Columns.team_name]),
            week=int(row[Columns.week]),
            round_number=int(row[Columns.round_number]),
            score=int(row[Columns.score]),
            points=float(row[Columns.points]),
            calculated_score=bool(not pd.isna(row[Columns.input_data]))
        )

    def _convert_to_raw_team_data(self, team_df: pd.DataFrame) -> RawTeamData:
        """Convert team DataFrame to RawTeamData"""
        players = [
            self._convert_to_raw_player_data(row)
            for _, row in team_df.iterrows()
        ]
        return RawTeamData(
            team_name=str(team_df[Columns.team_name].iloc[0]),
            season=str(team_df[Columns.season].iloc[0]),
            players=players
        )

    def get_raw_team_data(self, team: str, season: str) -> RawTeamData:
        """Get raw team data as DTO"""
        filters = {
            Columns.team_name: {'value': team, 'operator': 'eq'},
            Columns.season: {'value': season, 'operator': 'eq'}
        }
        team_df = self.get_filtered_data(filters=filters)
        if team_df.empty:
            return None
        return self._convert_to_raw_team_data(team_df)

    def get_raw_league_data(self, league: str, season: str) -> RawLeagueData:
        """Get raw league data as DTO"""
        filters = {
            Columns.league_name: {'value': league, 'operator': 'eq'},
            Columns.season: {'value': season, 'operator': 'eq'}
        }
        league_df = self.get_filtered_data(filters=filters)
        if league_df.empty:
            return None
            
        teams = []
        for team in league_df[Columns.team_name].unique():
            team_df = league_df[league_df[Columns.team_name] == team]
            teams.append(self._convert_to_raw_team_data(team_df))
            
        return RawLeagueData(
            league_name=league,
            season=season,
            teams=teams
        )
    