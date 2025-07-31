import pandas as pd
from data_access.pd_dataframes import fetch_column

class DataManager:
    _instance = None
    _df = None
    _current_source = 'bowling_ergebnisse.csv'
    _server_instances = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance._load_data()
        return cls._instance

    def _load_data(self, source=None):
        if source:
            self._current_source = source
        self._df = pd.read_csv(f'database/data/{self._current_source}', sep=';')

    def reload_data(self, source=None):
        # Force reload even if singleton exists
        if source:
            self._current_source = source
        print(f"DEBUG: DataManager reloading data from: {self._current_source}")
        self._df = pd.read_csv(f'database/data/{self._current_source}', sep=';')
        print(f"✅ DATA SOURCE SWITCHED: {self._current_source}")
        print(f"📊 Table dimensions: {len(self._df)} rows × {len(self._df.columns)} columns")
        print(f"📋 Columns: {list(self._df.columns)}")
        # Refresh all server instances
        print(f"DEBUG: DataManager refreshing {len(self._server_instances)} server instances")
        self._refresh_server_instances()

    def register_server_instance(self, server_instance):
        """Register a server instance to be refreshed when data source changes"""
        if server_instance not in self._server_instances:
            self._server_instances.append(server_instance)
            print(f"DEBUG: DataManager registered server instance, total: {len(self._server_instances)}")

    def _refresh_server_instances(self):
        """Refresh all registered server instances"""
        for server in self._server_instances:
            if hasattr(server, 'refresh_data_adapter'):
                print(f"DEBUG: DataManager refreshing server instance")
                server.refresh_data_adapter()

    @property
    def df(self):
        return self._df
    
    @property
    def current_source(self):
        return self._current_source 