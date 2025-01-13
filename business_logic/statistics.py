import pandas as pd
from database.definitions import Columns
from data_access.pd_dataframes import fetch_data, fetch_column


def query_database(database_df: pd.DataFrame, filters: dict = None, column_name: Columns = None, group_by: Columns = None) -> pd.DataFrame:
    df_filtered = database_df.copy()  # Start with a copy of the full DataFrame
    
    if filters:
        for key, value in filters.items():
            if value is None or value == [None]:
                continue
            
            if not isinstance(value, list):
                value = [value]
            
            df_filtered = df_filtered[df_filtered[key].isin(value)]
    
    if group_by is not None:
        df_filtered = df_filtered.groupby(group_by)
    
    return df_filtered

def calculate_score_average(database_df: pd.DataFrame, filters: dict = None, group_by: Columns = None) -> float:
    return round(fetch_column(database_df, Columns.score, filters, group_by=group_by)[Columns.score].mean(), 2)

    
def calculate_score_min(database_df: pd.DataFrame, filters: dict = None, group_by: Columns = None) -> int:
    return int(fetch_column(database_df, Columns.score, filters, group_by=group_by)[Columns.score].min())

def calculate_score_max(database_df: pd.DataFrame, filters: dict = None, group_by: Columns = None) -> int:
    return int(fetch_column(database_df, Columns.score, filters, group_by=group_by)[Columns.score].max())

def calculate_games_count(database_df: pd.DataFrame, filters: dict = None, group_by: Columns = None) -> int:
    return fetch_column(database_df, Columns.score, filters, group_by=group_by)[Columns.score].size()

    
def calculate_score_average_player(database_df: pd.DataFrame, player_name: str, season: str = None, group_by: Columns = None) -> float:
    return calculate_score_average(database_df, filters={Columns.player_name: [player_name], Columns.season: [season]}, group_by=group_by)

def calculate_score_average_team(database_df: pd.DataFrame, team_name: str, season: str = None, group_by: Columns = None) -> float:
    return calculate_score_average(database_df, filters={Columns.team_name: [team_name], Columns.season: [season]}, group_by=group_by)

def calculate_score_average_league(database_df: pd.DataFrame, league_name: str, season: str = None, group_by: Columns = None) -> float:
    return calculate_score_average(database_df, filters={Columns.league_name: [league_name], Columns.season: [season]}, group_by=group_by)



# Player-specific methods
def calculate_score_min_player(database_df: pd.DataFrame, player_name: str, season: str = None, group_by: Columns = None) -> float:
    return calculate_score_min(database_df, filters={Columns.player_name: [player_name], Columns.season: [season]}, group_by=group_by)

def calculate_score_max_player(database_df: pd.DataFrame, player_name: str, season: str = None, group_by: Columns = None) -> float:
    return calculate_score_max(database_df, filters={Columns.player_name: [player_name], Columns.season: [season]}, group_by=group_by)

def calculate_games_count_player(database_df: pd.DataFrame, player_name: str, season: str = None, group_by: Columns = None) -> int:
    return calculate_games_count(database_df, filters={Columns.player_name: [player_name], Columns.season: [season]}, group_by=group_by)

# Team-specific methods
def calculate_score_min_team(database_df: pd.DataFrame, team_name: str, season: str = None, group_by: Columns = None) -> float:
    return calculate_score_min(database_df, filters={Columns.team_name: [team_name], Columns.season: [season]}, group_by=group_by)

def calculate_score_max_team(database_df: pd.DataFrame, team_name: str, season: str = None, group_by: Columns = None) -> float:
    return calculate_score_max(database_df, filters={Columns.team_name: [team_name], Columns.season: [season]}, group_by=group_by)

def calculate_games_count_team(database_df: pd.DataFrame, team_name: str, season: str = None, group_by: Columns = None) -> int:
    return calculate_games_count(database_df, filters={Columns.team_name: [team_name], Columns.season: [season]}, group_by=group_by)

# League-specific methods
def calculate_score_min_league(database_df: pd.DataFrame, league_name: str, season: str = None, group_by: Columns = None) -> float:
    return calculate_score_min(database_df, filters={Columns.league_name: [league_name], Columns.season: [season]}, group_by=group_by)

def calculate_score_max_league(database_df: pd.DataFrame, league_name: str, season: str = None, group_by: Columns = None) -> float:
    return calculate_score_max(database_df, filters={Columns.league_name: [league_name], Columns.season: [season]}, group_by=group_by)

def calculate_games_count_league(database_df: pd.DataFrame, league_name: str, season: str = None, group_by: Columns = None) -> int:
    return calculate_games_count(database_df, filters={Columns.league_name: [league_name], Columns.season: [season]}, group_by=group_by)