from business_logic.statistics import query_database
from app.services.data_manager import DataManager
from data_access.schema import Columns, ColumnsExtra
from data_access.adapters.data_adapter import DataAdapter
from data_access.adapters.data_adapter_factory import DataAdapterFactory, DataAdapterSelector
import pandas as pd
from typing import List
from business_logic.server import Server
from flask import jsonify, Response
from business_logic.league import levels

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

    def get_average_per_season(self, team_name: str=None):
        """Returns the average position per season for a given team"""
        return self.server.get_average_per_season(team_name=team_name)

    def get_team_history(self, team_name: str=None):
        """Returns the history of a team for a given season"""

        if team_name is None:
            return {}
        
        seasons = self.server.get_seasons(team_name=team_name)
        if seasons is None:
            return {}
        
        history = {}

        for season in seasons:
            league_name = self.server.get_leagues(team_name=team_name, season=season)
            if isinstance(league_name, list):
                league_name = league_name[0]
            else:
                return {}
            final_position = self.server.get_final_position_in_league(team_name=team_name, league_name=league_name, season=season)

            history[season] = {"league_name": league_name, "final_position": final_position, 'league_level': levels[league_name]}

        return history
