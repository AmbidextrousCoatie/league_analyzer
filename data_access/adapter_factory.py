from typing import Optional
from data_access.interfaces import DataAdapter

class AdapterFactory:
    @staticmethod
    def get_adapter(adapter_type: str) -> DataAdapter:
        if adapter_type == "pandas":
            from data_access.adapters.adapter_pandas import DataAdapterPandas
            return DataAdapterPandas()
        elif adapter_type == "mysql":
            from data_access.mysql_adapter import MySQLAdapter
            return MySQLAdapter()
        elif adapter_type == "sqlite":
            from data_access.sqlite_adapter import SQLiteAdapter
            return SQLiteAdapter()
        else:
            raise ValueError(f"Unknown adapter type: {adapter_type}") 