from typing import Optional
from data_access.adapters.data_adapter import DataAdapter
from enum import Enum
from database.config import path_to_csv_data

class DataAdapterSelector(Enum):
    PANDAS = "pandas"
    MYSQL = "mysql"
    SQLITE = "sqlite"

class DataAdapterFactory:
    @staticmethod
    def get_adapter(adapter_type: DataAdapterSelector) -> DataAdapter:
        if adapter_type == DataAdapterSelector.PANDAS:
            from data_access.adapters.data_adapter_pandas import DataAdapterPandas
            return DataAdapterPandas(path_to_csv_data=path_to_csv_data)
        elif adapter_type == DataAdapterSelector.MYSQL:
            from data_access.adapters.data_adapter_mysql import MySQLAdapter
            return MySQLAdapter()
        elif adapter_type == DataAdapterSelector.SQLITE:
            from data_access.adapters.data_adapter_sqlite import SQLiteAdapter
            return SQLiteAdapter()
        else:
            raise ValueError(f"Unknown adapter type: {adapter_type}") 