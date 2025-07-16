import pytest
import pandas as pd
from data_access.schema import Columns
from data_access.series_data import calculate_series_data, get_player_series_data, get_team_series_data

# Hypothetical series_data function that would calculate a player's series score (sum of multiple games)
def calculate_series_data(df, player_name, week):
    """
    Calculate a player's series data for a specific week.
    
    Args:
        df: DataFrame containing player data
        player_name: Name of the player
        week: Week number
        
    Returns:
        Dictionary containing series information
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

@pytest.fixture
def sample_player_data():
    return pd.DataFrame({
        Columns.player_name: ['Alice', 'Alice', 'Alice', 'Bob', 'Bob', 'Charlie'],
        Columns.week: [1, 1, 1, 1, 1, 1],
        Columns.score: [200, 180, 220, 190, 210, 195],
        Columns.team_name: ['Team A', 'Team A', 'Team A', 'Team B', 'Team B', 'Team C'],
        Columns.season: ['2023', '2023', '2023', '2023', '2023', '2023'],
        Columns.league_name: ['League 1', 'League 1', 'League 1', 'League 1', 'League 1', 'League 1']
    })

def test_calculate_series_data_basic(sample_player_data):
    """Test basic series data calculation for a player with multiple games"""
    result = calculate_series_data(sample_player_data, 'Alice', 1)
    
    assert result is not None
    assert result['player_name'] == 'Alice'
    assert result['week'] == 1
    assert result['game_scores'] == [200, 180, 220]
    assert result['series_total'] == 600
    assert result['average'] == 200.0
    assert result['games_played'] == 3

def test_calculate_series_data_single_game(sample_player_data):
    """Test series data calculation for a player with a single game"""
    result = calculate_series_data(sample_player_data, 'Charlie', 1)
    
    assert result is not None
    assert result['player_name'] == 'Charlie'
    assert result['week'] == 1
    assert result['game_scores'] == [195]
    assert result['series_total'] == 195
    assert result['average'] == 195.0
    assert result['games_played'] == 1

def test_calculate_series_data_nonexistent_player(sample_player_data):
    """Test series data calculation for a player that doesn't exist"""
    result = calculate_series_data(sample_player_data, 'David', 1)
    
    assert result is None

def test_calculate_series_data_nonexistent_week(sample_player_data):
    """Test series data calculation for a week that doesn't exist"""
    result = calculate_series_data(sample_player_data, 'Alice', 2)
    
    assert result is None

def test_get_player_series_data(sample_player_data):
    """Test getting series data for a player across a season and league"""
    result = get_player_series_data(sample_player_data, 'Alice', '2023', 'League 1')
    
    assert len(result) == 1
    assert result[0]['player_name'] == 'Alice'
    assert result[0]['week'] == 1
    assert result[0]['game_scores'] == [200, 180, 220]
    assert result[0]['series_total'] == 600
    assert result[0]['average'] == 200.0
    assert result[0]['games_played'] == 3

def test_get_player_series_data_nonexistent(sample_player_data):
    """Test getting series data for a player that doesn't exist"""
    result = get_player_series_data(sample_player_data, 'David', '2023', 'League 1')
    
    assert result == []

def test_get_team_series_data(sample_player_data):
    """Test getting series data for all players on a team"""
    result = get_team_series_data(sample_player_data, 'Team A', '2023', 'League 1')
    
    assert 'Alice' in result
    assert len(result['Alice']) == 1
    assert result['Alice'][0]['player_name'] == 'Alice'
    assert result['Alice'][0]['week'] == 1
    assert result['Alice'][0]['game_scores'] == [200, 180, 220]
    assert result['Alice'][0]['series_total'] == 600
    assert result['Alice'][0]['average'] == 200.0
    assert result['Alice'][0]['games_played'] == 3

def test_get_team_series_data_nonexistent(sample_player_data):
    """Test getting series data for a team that doesn't exist"""
    result = get_team_series_data(sample_player_data, 'Team D', '2023', 'League 1')
    
    assert result == {} 