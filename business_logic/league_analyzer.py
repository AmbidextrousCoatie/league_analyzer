import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import database.definitions
from business_logic.league import League
from business_logic.lib import fetch_matchday, fetch_match, calculate_match_outcome, calculate_averages, calculate_points
from data_access.seed import create_team, create_league_roster, simulate_season
from database.definitions import Columns

def playground():

    # for consistency checks: player database
    # 'Player ID', 'Player Name', 'Player Surname',

    # for consistency checks: club database
    # 'Season', 'Club Name', 'Team Name', 'EDV'

    columns = Columns()
    col_names = columns.get_column_names()

    league_cols = ['League Name', 'Season', 'Team Name', 'Week', 'Date', 'Loation']
    league_teams = ['Donaubowler 1', 'Comet 1', 'Bayreuth 1', 'Ratisbona 2']
    league_content = ['LL1_N', "22/23", 'Donaubowler 1', 1, '01.01.23', 'Regensburg']

    data_dummy = [
        ['22/23', 1, '01.01.23', 'LL1_N', 'Regensburg', 'Donaubowler 1', 'Feller, Christian', 16007, 1, 'Comet 1', 1, 220],
        ['22/23', 1, '01.01.23', 'LL1_N', 'Regensburg', 'Donaubowler 1', 'Hartfeil, Volkmar', 123, 1, 'Comet 1', 2, 210],
        ['22/23', 1, '01.01.23', 'LL1_N', 'Regensburg', 'Donaubowler 1', 'Hürdler, Marco', 456, 1, 'Comet 1', 3, 200],
        ['22/23', 1, '01.01.23', 'LL1_N', 'Regensburg', 'Donaubowler 1', 'Obermeier, Kurt', 789, 1, 'Comet 1', 4, 190],
        ['22/23', 1, '01.01.23', 'LL1_N', 'Regensburg', 'Comet 1', 'Comet #1', 67, 1, 'Donaubowler 1', 1, 200],
        ['22/23', 1, '01.01.23', 'LL1_N', 'Regensburg', 'Comet 1', 'Comet #2', 23, 1, 'Donaubowler 1', 2, 205],
        ['22/23', 1, '01.01.23', 'LL1_N', 'Regensburg', 'Comet 1', 'Comet #3', 56, 1, 'Donaubowler 1', 3, 205],
        ['22/23', 1, '01.01.23', 'LL1_N', 'Regensburg', 'Comet 1', 'Comet #4', 89, 1, 'Donaubowler 1', 4, 195],
        ['23/24', 2, '03.01.24', 'LL1_N', 'Regensburg', 'Donaubowler 1', 'Feller, Christian', 16007, 1, 'Comet 1', 1, 220],
        ['23/24', 2, '03.01.24', 'LL1_N', 'Regensburg', 'Donaubowler 1', 'Hartfeil, Volkmar', 123, 1, 'Comet 1', 2, 200],
        ['23/24', 2, '03.01.24', 'LL1_N', 'Regensburg', 'Donaubowler 1', 'Hürdler, Marco', 456, 1, 'Comet 1', 3, 200],
        ['23/24', 2, '03.01.24', 'LL1_N', 'Regensburg', 'Donaubowler 1', 'Obermeier, Kurt', 789, 1, 'Comet 1', 4, 190]
    ]

    # DataFrame erstellen
    data_league = pd.DataFrame(data_dummy, columns=col_names)
    data_league['Points'] = None

    # DataFrame anzeigen

    data_matchday = fetch_matchday(data_league, '22/23', 'LL1_N', 1)

    data_match = fetch_match(data_matchday, 'Donaubowler 1', 1)

    data_match_processed = calculate_match_outcome(data_match)

    if 0:
        for df in [data_league, data_matchday, data_match, data_match_processed]:
            print(df)
            print()

    # DataFrame in eine CSV-Datei speichern

    team = create_team(7)
    print(team)


if __name__ == "__main__":

    columns = Columns()
    col_names = columns.get_column_names()

 
    league_ll = League(league_name="LL1 Nord", number_of_teams=8, number_of_players_per_team=4, skill_level=7)
    league_bzl = League(league_name="BZL 2 Nord", number_of_teams=6, number_of_players_per_team=4, skill_level=5)

    league_ll = create_league_roster(league_ll)
    league_bzl = create_league_roster(league_bzl)

    print(league_ll)
    print(league_bzl)

    df_results = pd.DataFrame(columns=col_names)

    if 0:
        for league in [league_ll, league_bzl]:
            for season in ["18/19", "19/20", "20/21", "21/22", "22/23", "23/24", "24/25"]:
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
