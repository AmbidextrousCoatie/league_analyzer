from business_logic.statistics import query_database
from app.services.data_manager import DataManager
from data_access.schema import Columns, ColumnsExtra
from data_access.adapters.data_adapter import DataAdapter
from data_access.adapters.data_adapter_factory import DataAdapterFactory, DataAdapterSelector
import pandas as pd
from typing import List
from business_logic.server import Server
from flask import jsonify, Response

class TeamService:
    # fetches dataframes from server
    # converts dataframes to dicts
    # jsonifies dicts   
    # forwards JSON dict to app routes
    def __init__(self):
        self.server = Server()

    def get_all_teams(self, league_name: str=None, season: str=None):
        """Returns all teams for a given league and season"""
        print(f"Team Service: Get All Teams - Received request with: league_name={league_name}, season={season}")
        return self.server.get_teams_in_league_season(league_name=league_name, season=season, debug_output=True)
        
    def get_available_seasons(self, team_name: str=None):
        """Returns all possible seasons"""
        return self.server.get_seasons(team_name=team_name)
    
    def get_available_weeks(self, team_name: str=None, season: str=None):
        """Returns all possible weeks for a given team and season"""
        return self.server.get_weeks(team_name=team_name, season=season)    
