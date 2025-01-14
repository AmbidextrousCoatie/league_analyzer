import pandas as pd
from data_access.pd_dataframes import fetch_column

class DataManager:
    _instance = None
    _df = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance._load_data()
        return cls._instance

    def _load_data(self):
        self._df = pd.read_csv('database/data/bowling_ergebnisse.csv', sep=';')

    def reload_data(self):
        self._load_data()

    @property
    def df(self):
        return self._df 