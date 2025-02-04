import pandas as pd
from data_access.pd_dataframes import fetch_column, fetch_data
from data_access.schema import Columns
from app.services.data_manager import DataManager
from business_logic.statistics import calculate_score_average_player, calculate_games_count_player
from business_logic.server import Server

class PlayerService:
    def __init__(self):
        self.data_manager = DataManager()
        self.server = Server()

    def get_all_players(self):
        players = fetch_column(
            database_df=self.data_manager.df,
            column_name=Columns.player_name,
            unique=True,
            as_list=True
        )
        return [{'id': name, 'name': name} for name in sorted(players)]

    def get_personal_stats(self, player_name: str, season: str = 'all'):
        df = self.data_manager.df
        print(player_name)
        # Filter for the specific player
        player_df = fetch_data(df, values_to_filter_for={Columns.player_name: player_name})

        player_id = player_df.iloc[0][Columns.player_id]
        print(player_id)
        # Calculate all-time average
        # Calculate all-time average
        all_time_average = calculate_score_average_player(player_df, player_name)
        all_time_game_count = len(player_df)

        # Calculate per-season average
        per_season_average = calculate_score_average_player(player_df, player_name, group_by=Columns.season)
        per_season_game_count = calculate_games_count_player(player_df, player_name, group_by=Columns.season)
        print(per_season_average)
        seasons = per_season_average.index.to_list() 
        averages = per_season_average.values.tolist()
        gamecount = [30] # per_season_game_count.values.tolist()

        # TODO: Add team comparison
        stats = {
            'name': player_name,
            'id': int(player_id),
            'team': player_df.iloc[0][Columns.team_name],
            'average': [all_time_average] + averages,
            'game_count': [all_time_game_count] + gamecount,
            'season': ["all time"] + seasons,

        }

        #print(stats)
    
        return stats
    
    def get_team_comparison(self, player_id: str, season: str = 'all'):
        """Compare player stats with team averages"""
        pass
    
    def get_historical_data(self, player_id: str):
        """Get historical performance data"""
        pass
    
    def get_all_players(self):
        """Get list of all players for selection"""
        players = fetch_column(
            database_df=self.data_manager.df,
            column_name=Columns.player_name,
            unique=True,
            as_list=True
        )
        return [{'id': name, 'name': name} for name in sorted(players)]

    def search_players(self, search_term):
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
                vs_last_season = 0.0
            
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
                'vs_last_season': vs_last_season,

                'best_game': {
                    'score': int(best_game.at[Columns.score]),
                    'date': 'tbd',
                    'event': f"{best_game.at[Columns.league_name]} Week {best_game.at[Columns.week]}"
                },

                'worst_game': {
                    'score': int(worst_game.at[Columns.score]),
                    'date': 'tbd',
                    'event': f"{worst_game.at[Columns.league_name]} Week {worst_game.at[Columns.week]}"       
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
        most_improved_season = season_improvements.idxmax()  # Gets the season name
        most_improved_improvement = season_improvements.max()

        

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
                'improvement': float(round(most_improved_improvement, 2))
            }

        }

        return collected_data
