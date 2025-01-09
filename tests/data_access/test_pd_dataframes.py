import pytest
import pandas as pd
from data_access.pd_dataframes import fetch_column
from business_logic.statistics import calculate_score_average
from database.definitions import Columns

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'id': [1, 2, 2, 3],
        Columns.player_name: ['Alice', 'Bob', 'Bob', 'Charlie'],
        'age': [25, 30, 30, 35],
        Columns.score: [100, 110, 120, 130]
    })

@pytest.fixture
def sample_col_name():
    return pd.DataFrame({
        Columns.player_name: ['Alice', 'Bob', 'Bob', 'Charlie']
    })


def test_fetch_column_basic(sample_df, sample_col_name):
    result = fetch_column(sample_df, Columns.player_name)
    assert isinstance(result, pd.DataFrame)
    assert result.size == sample_col_name.size
    assert len(result) == 4

def test_fetch_column_unique(sample_df):
    result = fetch_column(sample_df, Columns.player_name, unique=True)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3  # Should have removed duplicate 'Bob'

def test_fetch_column_as_list(sample_df):
    result = fetch_column(sample_df, Columns.player_name, as_list=True)
    assert isinstance(result, list)
    assert result == ['Alice', 'Bob', 'Bob', 'Charlie']

def test_fetch_column_unique_as_list(sample_df):
    result = fetch_column(sample_df, Columns.player_name, unique=True, as_list=True)
    assert isinstance(result, list)
    assert result == ['Alice', 'Bob', 'Charlie']

def test_fetch_column_nonexistent(sample_df):
    with pytest.raises(KeyError):
        fetch_column(sample_df, 'nonexistent_column') 

def test_scoring(sample_df):
    result = calculate_score_average(sample_df)
    print(result)
    assert result == 115.00

def test_scoring_with_filters(sample_df):
    result = calculate_score_average(sample_df, filters={Columns.player_name: ['Alice']})
    print(result)
    assert result == 100.00