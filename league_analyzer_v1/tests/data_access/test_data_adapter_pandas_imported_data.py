import pytest
import pandas as pd 
import pathlib
from data_access.adapters.data_adapter import DataAdapter
from data_access.adapters.data_adapter_pandas import DataAdapterPandas
from data_access.schema import Columns, ColumnsExtra

@pytest.fixture
def path_to_csv_test_data():
    return pathlib.Path(".\\tests\\data_access\\test_data\\bowling_ergebnisse.csv").absolute()


@pytest.fixture
def adapter(path_to_csv_test_data):
    """Create a PandasAdapter instance with sample data"""
    adapter = DataAdapterPandas(path_to_csv_data=path_to_csv_test_data)
    return adapter

def test_adapter_implements_interface(adapter):
    """Test that PandasAdapter implements DataAdapter interface"""
    assert isinstance(adapter, DataAdapter)

def test_get_league_standings(adapter):
    league_name = "LL1 Nord"
    league_season = "18/19"
    league_week = 3
    standings = adapter.get_league_standings(league_name=league_name, season=league_season, week=league_week)
    standings_cumulative = adapter.get_league_standings(league_name=league_name, season=league_season, week=league_week, cumulative=True)

    assert len(standings) > 0
    assert "LL1 Nord" in standings.index
    assert "18/19" in standings.index
    assert league_week in standings.index
