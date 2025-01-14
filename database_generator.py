import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.generator.league import DataGeneratorLeague
from business_logic.lib import calculate_points
from database.generator.seed import create_league_roster, simulate_season
from data_access.schema import Columns


if __name__ == "__main__":

    col_names = Columns().get_column_names()

 
    league_ll = DataGeneratorLeague(league_name="LL1 Nord", number_of_teams=4, number_of_players_per_team=4, skill_level=7)
    league_bzl = DataGeneratorLeague(league_name="BZL 2 Nord", number_of_teams=4, number_of_players_per_team=4, skill_level=5)

    league_ll = create_league_roster(league_ll)
    league_bzl = create_league_roster(league_bzl)

    print(league_ll)
    print(league_bzl)

    df_results = pd.DataFrame(columns=col_names)

    all_seasons = ["18/19", "19/20"] #, "20/21", "21/22", "22/23", "23/24", "24/25"]
    all_leagues = [league_ll, league_bzl]


    if 1:
        for league in all_leagues:
            for season in all_seasons:
                print(f"Simulating season {season} for {league.name}")
                df_results_season = simulate_season(league.teams, league.weeks,
                                                                league.number_of_players_per_team, league.name,
                                                                season=season)

                df_results = pd.concat([df_results, df_results_season], ignore_index=True)

        df_results.to_csv('.\\database\\data\\bowling_ergebnisse_ohne_punkte.csv', index=False, sep=";")
    df_results = pd.read_csv('.\\database\\data\\bowling_ergebnisse_ohne_punkte.csv', sep=";")
    df_results_with_points = calculate_points(df_results)
    df_results_with_points.to_csv('.\\database\\data\\bowling_ergebnisse.csv', index=False, sep=";")
    # calculate_averages(df_results, league_name=league_name, season=league_season)
