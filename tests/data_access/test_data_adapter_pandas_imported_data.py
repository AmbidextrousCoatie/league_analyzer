import pytest
import pandas as pd 
import pathlib
from data_access.adapters.data_adapter import DataAdapter
from data_access.adapters.data_adapter_pandas import DataAdapterPandas
from data_access.schema import Columns

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