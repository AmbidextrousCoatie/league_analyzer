import pandas as pd
from data_access.pd_dataframes import fetch_column, fetch_data
from data_access.schema import Columns
from app.services.data_manager import DataManager
from business_logic.statistics import calculate_score_average_player, calculate_games_count_player
from business_logic.server import Server
from app.services.statistics_service import StatisticsService
from app.models.statistics_models import PlayerStatistics
from typing import Dict, List, Any, Optional

class PlayerService:
    def __init__(self):
        self.data_manager = DataManager()
        self.server = Server()
        self.stats_service = StatisticsService()

    def get_all_players(self):
        """Get list of all players for selection"""
        players = fetch_column(
            database_df=self.data_manager.df,
            column_name=Columns.player_name,
            unique=True,
            as_list=True
        )
        return [{'id': name, 'name': name} for name in sorted(players)]

    def get_player_statistics(self, player_name: str, season: str) -> PlayerStatistics:
        """Get comprehensive player statistics"""
        return self.stats_service.get_player_statistics(player_name, season)

    def get_personal_stats(self, player_name: str, season: str = 'all') -> Dict[str, Any]:
        """Get personal statistics for a player"""
        if season == 'all':
            # Get all seasons the player participated in
            player_data = self.data_manager.df[self.data_manager.df[Columns.player_name] == player_name]
            seasons = sorted(player_data[Columns.season].unique())
            
            # Get statistics for each season
            season_stats = []
            for season in seasons:
                stats = self.get_player_statistics(player_name, season)
                if stats:
                    season_stats.append({
                        'season': season,
                        'statistics': {
                            'total_score': stats.season_summary.total_score,
                            'total_points': stats.season_summary.total_points,
                            'average_score': stats.season_summary.average_score,
                            'games_played': stats.season_summary.games_played,
                            'best_score': stats.season_summary.best_score,
                            'worst_score': stats.season_summary.worst_score,
                            'team_contribution': stats.team_contribution
                        }
                    })
            
            return {
                'name': player_name,
                'seasons': season_stats
            }
        else:
            # Get statistics for specific season
            stats = self.get_player_statistics(player_name, season)
            if not stats:
                return None
                
            return {
                'name': player_name,
                'season': season,
                'statistics': {
                    'total_score': stats.season_summary.total_score,
                    'total_points': stats.season_summary.total_points,
                    'average_score': stats.season_summary.average_score,
                    'games_played': stats.season_summary.games_played,
                    'best_score': stats.season_summary.best_score,
                    'worst_score': stats.season_summary.worst_score,
                    'team_contribution': stats.team_contribution
                }
            }

    def get_team_comparison(self, player_name: str, season: str) -> Dict[str, Any]:
        """Compare player stats with team averages"""
        player_stats = self.get_player_statistics(player_name, season)
        if not player_stats:
            return None
            
        # Get team data
        team_data = self.data_manager.df[
            (self.data_manager.df[Columns.team_name] == player_stats.team_name) &
            (self.data_manager.df[Columns.season] == season)
        ]
        
        # Calculate team averages
        team_avg = team_data[Columns.score].mean()
        team_total = team_data[Columns.score].sum()
        
        return {
            'player': {
                'name': player_name,
                'average': player_stats.season_summary.average_score,
                'total_score': player_stats.season_summary.total_score,
                'contribution': player_stats.team_contribution
            },
            'team': {
                'name': player_stats.team_name,
                'average': team_avg,
                'total_score': team_total
            },
            'comparison': {
                'vs_team_avg': player_stats.season_summary.average_score - team_avg,
                'contribution_percentage': player_stats.team_contribution
            }
        }

    def search_players(self, search_term: str) -> List[Dict[str, str]]:
        """Search players by name"""
        # Get all players first
        all_players = self.get_all_players()
        
        # Filter players based on search term
        if search_term:
            search_term = search_term.lower()
            filtered_players = [
                player for player in all_players 
                if search_term in player['name'].lower()
            ]
            return filtered_players
        
        return all_players

    def get_historical_data(self, player_id: str):
        """Get historical performance data"""
        pass

    def get_lifetime_stats(self, player_name):
        """Get lifetime statistics for a player."""
        # Get all games for the player
               
        games_df = self.server.get_games_for_player(player_name)
        
        if games_df.empty:
            return None
 
        overall_average = games_df[Columns.score].mean()

        # first handle the seasons stats
        data_grouped = games_df.groupby(Columns.season)
        season_stats = []
        last_seasons_average = None
        for i, (season, data) in enumerate(data_grouped):
            
            total_games = len(data)
            total_pins = data[Columns.score].sum()
            average = total_pins / total_games
            
            # Calculate deviation from overall average
            dev_from_avg = average - overall_average
            
            # Calculate change from previous season
            if last_seasons_average is not None:
                vs_last_season = average - last_seasons_average
            else:
                vs_last_season = None  # Use None instead of 0.0 for first season
            
            last_seasons_average = average

            # Find best and worst games
            best_game = data[data[Columns.score] == data[Columns.score].max()].iloc[0]   
            worst_game = data[data[Columns.score] == data[Columns.score].min()].iloc[0]
            
            season_stats.append({
                'season': season,
                'games': int(total_games),
                'total_pins': int(total_pins),
                'average': float(round(average, 2)),
                'dev_from_avg': float(round(dev_from_avg, 2)),
                'vs_last_season': float(round(vs_last_season, 2)) if vs_last_season is not None else None,

                'best_game': {
                    'score': int(best_game.at[Columns.score]),
                    'date': 'tbd',
                    'event': f"{best_game.at[Columns.league_name]} Week {best_game.at[Columns.week]}"
                },

                'worst_game': {
                    'score': int(worst_game.at[Columns.score]),
                    'date': 'tbd',
                    'event': f"{best_game.at[Columns.league_name]} Week {best_game.at[Columns.week]}"       
                }
            })

        collected_data = dict(seasons=season_stats)

        # calculate the lifetime stats
        
        # Calculate basic stats
        total_games = len(games_df)
        total_pins = games_df[Columns.score].sum()
        avg_score = total_pins / total_games if total_games > 0 else 0
        
        # Find best and worst games
        best_game = games_df[games_df[Columns.score] == games_df[Columns.score].max()].iloc[0]
        worst_game = games_df[games_df[Columns.score] == games_df[Columns.score].min()].iloc[0]
        
        season_means = data_grouped[Columns.score].mean()

        # Find season with best mean
        best_season = season_means.idxmax()  # Gets the season name
        best_season_avg = season_means.max()  # Gets the actual average

        # For most improved, calculate differences between consecutive seasons
        season_improvements = season_means.diff()  # Calculates difference to previous season
        
        # Handle NaN values in improvements
        if season_improvements.empty or season_improvements.isna().all():
            most_improved_season = None
            most_improved_improvement = None
        else:
            # Filter out NaN values and find the maximum improvement
            valid_improvements = season_improvements.dropna()
            if valid_improvements.empty:
                most_improved_season = None
                most_improved_improvement = None
            else:
                most_improved_season = valid_improvements.idxmax()  # Gets the season name
                most_improved_improvement = valid_improvements.max()

        collected_data['lifetime'] = {
            'total_games': int(total_games),
            'total_pins': int(total_pins),
            'average_score': float(round(avg_score, 2)),

            'best_game': {
                'score': int(best_game.at[Columns.score]),
                'date': 'tbd',
                'event': f"{best_game.at[Columns.season]} {best_game.at[Columns.league_name]} Week {best_game.at[Columns.week]}"
            },
            'worst_game': {
                'score': int(worst_game.at[Columns.score]),
                'date': 'tbd',
                'event': f"{worst_game.at[Columns.season]} {worst_game.at[Columns.league_name]} Week {worst_game.at[Columns.week]}"
            },
            'best_season': {
                'season': best_season,
                'average': float(round(best_season_avg, 2))    
            },
            'most_improved': {
                'season': most_improved_season,
                'improvement': float(round(most_improved_improvement, 2)) if most_improved_improvement is not None else None
            }
        }

        return collected_data
