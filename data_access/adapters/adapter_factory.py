from typing import Optional
from data_access.interfaces import DataAdapter
from enum import Enum

class DataAdapterSelector(Enum):
    PANDAS = "pandas"
    MYSQL = "mysql"
    SQLITE = "sqlite"

class AdapterFactory:
    @staticmethod
    def get_adapter(adapter_type: DataAdapterSelector) -> DataAdapter:
        if adapter_type == DataAdapterSelector.PANDAS:
            from data_access.adapters.adapter_pandas import DataAdapterPandas
            return DataAdapterPandas()
        elif adapter_type == DataAdapterSelector.MYSQL:
            from data_access.adapters.adapter_mysql import MySQLAdapter
            return MySQLAdapter()
        elif adapter_type == DataAdapterSelector.SQLITE:
            from data_access.adapters.adapter_sqlite import SQLiteAdapter
            return SQLiteAdapter()
        else:
            raise ValueError(f"Unknown adapter type: {adapter_type}") 