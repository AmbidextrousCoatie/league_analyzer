import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.generator.league import DataGeneratorLeague
from business_logic.lib import calculate_point3
from database.generator.seed import create_league_roster, simulate_season, transfer_teams_after_season
from data_access.schema import Columns



if __name__ == "__main__":

    col_names = Columns().get_column_names()

 
    league_bayl = DataGeneratorLeague(league_name="BayL", league_level=3, number_of_teams=10, number_of_players_per_team=4)
    league_ll = DataGeneratorLeague(league_name="LL 1 Nord", league_level=4, number_of_teams=6, number_of_players_per_team=4)
    league_bzol = DataGeneratorLeague(league_name="BZOL 2 Nord", league_level=5, number_of_teams=6, number_of_players_per_team=4)
    league_bzl = DataGeneratorLeague(league_name="BZL 2 Nord", league_level=6, number_of_teams=6, number_of_players_per_team=4)
    league_kl = DataGeneratorLeague(league_name="KL 1 Nord", league_level=7, number_of_teams=6, number_of_players_per_team=4)

        
    league_bayl = create_league_roster(league_bayl)
    league_ll = create_league_roster(league_ll)  
    league_bzol = create_league_roster(league_bzol)
    league_bzl = create_league_roster(league_bzl)
    league_kl = create_league_roster(league_kl,)

    print(league_bayl)
    print(league_ll)
    print(league_bzol)
    print(league_bzl)
    print(league_kl)




    #for league in [league_bayl, league_ll, league_bzl]:
    #    league.teams[0].simulate_n_games(100)
    #    league.simulate_player_development()


    #exit(1)

    df_results = pd.DataFrame(columns=col_names)
    df_results_with_points = pd.DataFrame()

    all_seasons = ["19/20" , "20/21", "21/22", "22/23", "23/24"]
    all_leagues = [league_bayl, league_ll, league_bzol, league_bzl, league_kl]



    if 1:
        for season in all_seasons:
            for league in all_leagues:
                print(f"Simulating season {season} for {league.name}")
                df_results_season = simulate_season(league.teams, league.weeks,
                                                                league.number_of_players_per_team, league.name,
                                                                season=season)
                df_results = pd.concat([df_results, df_results_season], ignore_index=True)
                df_results_season = calculate_point3(df_results_season)
                df_results_with_points = pd.concat([df_results_with_points, df_results_season], ignore_index=True)
                #print(df_results_season.groupby(Columns.team_name)[Columns.points].sum().to_string())
                sorted_teams = df_results_season.groupby(Columns.team_name)[Columns.points].sum().sort_values(ascending=False).index.tolist()
                league.set_last_seasons_order(sorted_teams)
                
                league.simulate_player_development()

            transfer_teams_after_season(league_bayl, league_ll, 2)
            transfer_teams_after_season(league_ll, league_bzol, 1)
            transfer_teams_after_season(league_bzol, league_bzl, 1)
            transfer_teams_after_season(league_bzl, league_kl, 1)



        df_results.to_csv('.\\database\\data\\bowling_ergebnisse_ohne_punkte.csv', index=False, sep=";")
    df_results = pd.read_csv('.\\database\\data\\bowling_ergebnisse_ohne_punkte.csv', sep=";")
    #df_results_with_points = calculate_point3(df_results)

    df_results_with_points.to_csv('.\\database\\data\\bowling_ergebnisse.csv', index=False, sep=";")
    # calculate_averages(df_results, league_name=league_name, season=league_season)
