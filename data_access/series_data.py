import pandas as pd
from typing import Dict, Any, Optional, List
from data_access.schema import Columns
from app.models.series_data import SeriesData

def calculate_series_data(
    data: List[Dict[str, Any]],
    x_field: str,
    y_field: str,
    name: str,
    label_x: str,
    label_y: str,
    query_params: Dict[str, Any]
) -> SeriesData:
    """Calculate series data from raw data."""
    series = SeriesData(
        label_x_axis=label_x,
        label_y_axis=label_y,
        name=name
    )
    
    # Store query parameters
    series.query_params = query_params
    
    # Group data by x_field
    grouped_data: Dict[str, List[float]] = {}
    for item in data:
        key = str(item[x_field])
        if key not in grouped_data:
            grouped_data[key] = []
        grouped_data[key].append(float(item[y_field]))
    
    # Add data to series
    for key, values in grouped_data.items():
        series.add_data(key, values)
    
    return series

def get_player_series_data(
    data: List[Dict[str, Any]],
    player_name: str,
    x_field: str,
    y_field: str,
    name: str,
    label_x: str,
    label_y: str,
    query_params: Dict[str, Any]
) -> SeriesData:
    """Get series data for a specific player."""
    # Filter data for player
    player_data = [item for item in data if item.get('player_name') == player_name]
    
    return calculate_series_data(
        data=player_data,
        x_field=x_field,
        y_field=y_field,
        name=name,
        label_x=label_x,
        label_y=label_y,
        query_params=query_params
    )

def get_team_series_data(
    data: List[Dict[str, Any]],
    team_name: str,
    x_field: str,
    y_field: str,
    name: str,
    label_x: str,
    label_y: str,
    query_params: Dict[str, Any]
) -> SeriesData:
    """Get series data for a specific team."""
    # Filter data for team
    team_data = [item for item in data if item.get('team_name') == team_name]
    
    return calculate_series_data(
        data=team_data,
        x_field=x_field,
        y_field=y_field,
        name=name,
        label_x=label_x,
        label_y=label_y,
        query_params=query_params
    )

def calculate_series_data_from_df(df: pd.DataFrame, player_name: str, week: int) -> Optional[Dict[str, Any]]:
    """
    Calculate a player's series data for a specific week.
    
    Args:
        df: DataFrame containing player data
        player_name: Name of the player
        week: Week number
        
    Returns:
        Dictionary containing series information or None if no data found
    """
    # Filter data for the specific player and week
    player_data = df[(df[Columns.player_name] == player_name) & (df[Columns.week] == week)]
    
    if player_data.empty:
        return None
    
    # Calculate series total (sum of all scores)
    series_total = player_data[Columns.score].sum()
    
    # Get individual game scores
    game_scores = player_data[Columns.score].tolist()
    
    # Calculate average
    average = series_total / len(game_scores) if game_scores else 0
    
    return {
        'player_name': player_name,
        'week': week,
        'game_scores': game_scores,
        'series_total': series_total,
        'average': average,
        'games_played': len(game_scores)
    }

def get_player_series_data_across_season(df: pd.DataFrame, player_name: str, season: str, league: str) -> List[Dict[str, Any]]:
    """
    Get series data for a player across all weeks in a season and league.
    
    Args:
        df: DataFrame containing player data
        player_name: Name of the player
        season: Season identifier
        league: League name
        
    Returns:
        List of dictionaries containing series information for each week
    """
    # Filter data for the specific player, season, and league
    player_data = df[
        (df[Columns.player_name] == player_name) & 
        (df[Columns.season] == season) & 
        (df[Columns.league_name] == league)
    ]
    
    if player_data.empty:
        return []
    
    # Get unique weeks
    weeks = player_data[Columns.week].unique()
    
    # Calculate series data for each week
    series_data = []
    for week in weeks:
        week_data = calculate_series_data_from_df(player_data, player_name, week)
        if week_data:
            series_data.append(week_data)
    
    return series_data

def get_team_series_data_across_season(df: pd.DataFrame, team_name: str, season: str, league: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get series data for all players on a team across all weeks in a season and league.
    
    Args:
        df: DataFrame containing player data
        team_name: Name of the team
        season: Season identifier
        league: League name
        
    Returns:
        Dictionary mapping player names to lists of series data for each week
    """
    # Filter data for the specific team, season, and league
    team_data = df[
        (df[Columns.team_name] == team_name) & 
        (df[Columns.season] == season) & 
        (df[Columns.league_name] == league)
    ]
    
    if team_data.empty:
        return {}
    
    # Get unique players
    players = team_data[Columns.player_name].unique()
    
    # Calculate series data for each player
    team_series_data = {}
    for player in players:
        player_series = get_player_series_data_across_season(df, player, season, league)
        if player_series:
            team_series_data[player] = player_series
    
    return team_series_data 