from business_logic.statistics import query_database
from app.services.data_manager import DataManager
from data_access.schema import Columns, ColumnsExtra
from data_access.adapters.data_adapter import DataAdapter
from data_access.adapters.data_adapter_factory import DataAdapterFactory, DataAdapterSelector
import pandas as pd
from typing import List, Dict, Any, Optional
from business_logic.server import Server
from flask import jsonify, Response
from business_logic.league import levels
from app.services.statistics_service import StatisticsService
from app.models.statistics_models import TeamStatistics

class TeamService:
    # fetches dataframes from server
    # converts dataframes to dicts
    # jsonifies dicts   
    # forwards JSON dict to app routes
    def __init__(self):
        self.server = Server()
        self.stats_service = StatisticsService()

    def get_all_teams(self, league_name: str=None, season: str=None):
        """Returns all teams for a given league and season"""
        print(f"Team Service: Get All Teams - Received request with: league_name={league_name}, season={season}")
        return self.server.get_teams_in_league_season(league_name=league_name, season=season, debug_output=True)
        
    def get_available_seasons(self, team_name: str=None):
        """Returns all possible seasons"""
        return self.server.get_seasons(team_name=team_name)
    
    def get_available_weeks(self, team_name: str=None, season: str=None):
        """Returns all possible weeks for a given team and season"""
        # Handle "all seasons" case (empty string, None, or "All")
        if not season or season == "" or season == "All":
            # Get all seasons for this team
            seasons = self.server.get_seasons(team_name=team_name)
            if not seasons:
                return []
            
            # Get all weeks across all seasons
            all_weeks = set()
            for s in seasons:
                # Get the league for this season
                leagues = self.server.get_leagues(team_name=team_name, season=s)
                if leagues and len(leagues) > 0:
                    league = leagues[0]  # Take the first league
                    # Call get_weeks with correct parameters (season, league)
                    weeks = self.server.get_weeks(league_name=league, season=s)
                    if weeks:
                        all_weeks.update(weeks)
            
            return sorted(list(all_weeks))
        else:
            # Get the league for this specific season
            leagues = self.server.get_leagues(team_name=team_name, season=season)
            if leagues and len(leagues) > 0:
                league = leagues[0]  # Take the first league
                return self.server.get_weeks(season=season, league=league)
            else:
                return []



    def get_team_statistics(self, team_name: str, season: str) -> TeamStatistics:
        """Get comprehensive team statistics"""
        return self.stats_service.get_team_statistics(team_name, season)

    def get_team_history(self, team_name: str=None) -> Dict[str, Any]:
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
                
            # Get team statistics for this season
            team_stats = self.get_team_statistics(team_name, season)
            if not team_stats:
                continue
                
            final_position = self.server.get_final_position_in_league(
                team_name=team_name,
                season=season,
                league_name=league_name
            )

            history[season] = {
                "league_name": league_name,
                "final_position": final_position,
                "league_level": levels[league_name],
                "statistics": {
                    "total_score": team_stats.season_summary.total_score,
                    "total_points": team_stats.season_summary.total_points,
                    "average_score": team_stats.season_summary.average_score,
                    "games_played": team_stats.season_summary.games_played,
                    "best_score": team_stats.season_summary.best_score,
                    "worst_score": team_stats.season_summary.worst_score
                }
            }

        return history

    def get_league_comparison_data(self, team_name: str) -> Dict[str, Any]:
        """Get comprehensive league comparison data for a team"""
        if team_name is None:
            return {}
        
        seasons = self.server.get_seasons(team_name=team_name)
        if not seasons:
            return {}
        
        comparison_data = {}
        
        for season in seasons:
            league_name = self.server.get_leagues(team_name=team_name, season=season)
            if isinstance(league_name, list):
                league_name = league_name[0]
            else:
                continue
            
            # Get league averages for this season
            league_averages = self.get_league_averages(league_name, season)
            if not league_averages:
                continue
            
            # Get team performance vs league
            team_vs_league = self.get_team_vs_league_performance(team_name, league_name, season)
            if not team_vs_league:
                continue
            
            comparison_data[season] = {
                "league_name": league_name,
                "league_averages": league_averages,
                "team_performance": team_vs_league,
                "performance_rank": team_vs_league.get("performance_rank", 0),
                "vs_league_average": team_vs_league.get("vs_league_average", 0)
            }
        
        return comparison_data

    def get_league_averages(self, league_name: str, season: str) -> Dict[str, Any]:
        """Calculate league averages for a given season"""
        try:
            # First, let's see what data is actually available
            print(f"Investigating data structure for {league_name} {season}")
            
            # Try to get individual player data
            individual_columns = [Columns.team_name, Columns.player_name, Columns.score, Columns.points, Columns.week, Columns.round_number, Columns.input_data]
            individual_filters = {
                Columns.league_name: {'value': league_name, 'operator': 'eq'},
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.computed_data: {'value': False, 'operator': 'eq'},
                Columns.input_data: {'value': True, 'operator': 'eq'}  # Individual scores
            }
            
            individual_data = self.server.data_adapter.get_filtered_data(columns=individual_columns, filters=individual_filters)
            print(f"Individual data found: {len(individual_data)} rows")
            
            if not individual_data.empty:
                print(f"Individual data columns: {list(individual_data.columns)}")
                print(f"Sample individual scores: {individual_data[Columns.score].head().tolist()}")
                
                # Calculate league averages from individual scores
                league_avg_score = individual_data[Columns.score].mean()
                league_avg_points = individual_data[Columns.points].mean()
                league_std_score = individual_data[Columns.score].std()
                league_std_points = individual_data[Columns.points].std()
                
                # Get number of teams and total individual games
                num_teams = individual_data[Columns.team_name].nunique()
                total_individual_games = len(individual_data)
                
                print(f"League averages (individual) for {league_name} {season}: avg_score={league_avg_score:.2f}, avg_points={league_avg_points:.2f}, teams={num_teams}, games={total_individual_games}")
                
                return {
                    "average_score": round(league_avg_score, 2),
                    "average_points": round(league_avg_points, 2),
                    "std_score": round(league_std_score, 2),
                    "std_points": round(league_std_points, 2),
                    "num_teams": num_teams,
                    "total_games": total_individual_games
                }
            else:
                print(f"No individual data found for {league_name} {season}")
                return {}
            
        except Exception as e:
            print(f"Error calculating league averages: {str(e)}")
            return {}

    def get_team_vs_league_performance(self, team_name: str, league_name: str, season: str) -> Dict[str, Any]:
        """Calculate team performance compared to league average"""
        try:
            print(f"Calculating team vs league performance for {team_name} in {league_name} {season}")
            
            # Get team statistics for this season
            try:
                team_stats = self.get_team_statistics(team_name, season)
                if not team_stats:
                    print(f"No team statistics found for {team_name} in {season}")
                    return {}
                print(f"Successfully got team statistics for {team_name}")
            except Exception as e:
                print(f"Error getting team statistics: {str(e)}")
                return {}
            
            # Get league averages
            try:
                league_averages = self.get_league_averages(league_name, season)
                if not league_averages:
                    print(f"No league averages found for {league_name} in {season}")
                    return {}
                print(f"Successfully got league averages for {league_name}")
            except Exception as e:
                print(f"Error getting league averages: {str(e)}")
                return {}
            
            # Calculate performance vs league
            try:
                # Get individual player data for this team
                team_individual_filters = {
                    Columns.team_name: {'value': team_name, 'operator': 'eq'},
                    Columns.season: {'value': season, 'operator': 'eq'},
                    Columns.computed_data: {'value': False, 'operator': 'eq'},
                    Columns.input_data: {'value': True, 'operator': 'eq'}  # Individual scores
                }
                team_individual_data = self.server.data_adapter.get_filtered_data(columns=[Columns.score, Columns.points], filters=team_individual_filters)
                
                if team_individual_data.empty:
                    print(f"No individual data found for {team_name} in {season}")
                    return {}
                
                team_avg_score = team_individual_data[Columns.score].mean()
                team_avg_points = team_individual_data[Columns.points].mean()
                print(f"Team individual average score: {team_avg_score}")
                print(f"Team individual average points: {team_avg_points}")
                
                vs_league_score = team_avg_score - league_averages["average_score"]
                vs_league_points = team_avg_points - league_averages["average_points"]
                print(f"vs league score: {vs_league_score}, vs league points: {vs_league_points}")
                
                # Calculate performance rank (how many standard deviations above/below average)
                score_z_score = vs_league_score / league_averages["std_score"] if league_averages["std_score"] > 0 else 0
                points_z_score = vs_league_points / league_averages["std_points"] if league_averages["std_points"] > 0 else 0
                print(f"Z-scores: score={score_z_score}, points={points_z_score}")
                
                # Get final position for context
                final_position = self.server.get_final_position_in_league(team_name, season, league_name)
                print(f"Final position: {final_position}")
                print(f"Successfully calculated performance metrics")
            except Exception as e:
                print(f"Error calculating performance metrics: {str(e)}")
                import traceback
                traceback.print_exc()
                return {}
            
            return {
                "team_average_score": round(team_avg_score, 2),
                "team_average_points": round(team_avg_points, 2),
                "vs_league_score": round(vs_league_score, 2),
                "vs_league_points": round(vs_league_points, 2),
                "score_z_score": round(score_z_score, 2),
                "points_z_score": round(points_z_score, 2),
                "performance_rank": final_position,
                "vs_league_average": round(vs_league_score, 2)  # Main comparison metric
            }
            
        except Exception as e:
            print(f"Error calculating team vs league performance: {str(e)}")
            return {}

    def get_special_matches(self, team_name: str=None):
        """Returns the special matches for a given team"""
        return self.server.get_special_matches(team_name=team_name)
