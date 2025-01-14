import pytest
import pandas as pd
from data_access.adapters.data_adapter import DataAdapter
from data_access.adapters.data_adapter_pandas import DataAdapterPandas
from data_access.schema import Columns

@pytest.fixture
def sample_df():
    """Create a sample DataFrame for testing"""
    return pd.DataFrame({
        Columns.player_name: ['Player1', 'Player1', 'Player2', 'Player3'],
        Columns.score: [200, 180, 150, 190],
        Columns.season: ['2023', '2023', '2023', '2023'],
        Columns.team_name: ['TeamA', 'TeamA', 'TeamB', 'TeamC'],
        Columns.league_name: ['League1', 'League1', 'League1', 'League1']
    })

@pytest.fixture
def adapter(sample_df):
    """Create a PandasAdapter instance with sample data"""
    adapter = DataAdapterPandas(df=sample_df)
    return adapter

def test_adapter_implements_interface(adapter):
    """Test that PandasAdapter implements DataAdapter interface"""
    assert isinstance(adapter, DataAdapter)

def test_get_all_players(adapter):
    """Test getting list of all unique players"""
    players = adapter.get_all_players()
    assert isinstance(players, list)
    assert set(players) == {'Player1', 'Player2', 'Player3'}

def test_get_player_data(adapter):
    """Test getting data for a specific player"""
    player_data = adapter.get_player_data('Player1')
    assert isinstance(player_data, pd.DataFrame)
    assert len(player_data) == 2  # Player1 has 2 entries
    assert all(player_data[Columns.player_name] == 'Player1')

def test_get_filtered_data(adapter):
    """Test filtering data with multiple conditions"""
    filters = {
        Columns.team_name: 'TeamA',
        Columns.season: '2023'
    }
    filtered_data = adapter.get_filtered_data(filters)
    assert isinstance(filtered_data, pd.DataFrame)
    assert len(filtered_data) == 2
    assert all(filtered_data[Columns.team_name] == 'TeamA')
    assert all(filtered_data[Columns.season] == '2023')

def test_get_player_data_nonexistent(adapter):
    """Test getting data for a player that doesn't exist"""
    player_data = adapter.get_player_data('NonexistentPlayer')
    assert isinstance(player_data, pd.DataFrame)
    assert len(player_data) == 0

def test_get_filtered_data_no_matches(adapter):
    """Test filtering with conditions that match no records"""
    filters = {Columns.season: '2024'}
    filtered_data = adapter.get_filtered_data(filters)
    assert isinstance(filtered_data, pd.DataFrame)
    assert len(filtered_data) == 0