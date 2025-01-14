import pandas as pd

from database.generator.seed import create_team
from data_access.pd_dataframes import fetch_data, fetch_column
from data_access.schema import Columns
from business_logic.statistics import calculate_score_average_player, calculate_score_min_player, calculate_score_max_player, calculate_games_count_player, calculate_score_average_team, calculate_score_average_league, calculate_score_average
from business_logic.lib import fetch_matchday, fetch_match, calculate_points

df = pd.read_csv('database/data/bowling_ergebnisse.csv', sep=';')


# Alle möglichen Werte für Filteroptionen
all_leagues = fetch_column(df, Columns.league_name, unique=True, as_list=True)
all_seasons = fetch_column(df, Columns.season, unique=True, as_list=True)
all_teams = fetch_column(df, Columns.team_name, unique=True, as_list=True)
all_players = fetch_column(df, Columns.player_name, unique=True, as_list=True)
all_scores = fetch_column(df, Columns.score, unique=True, as_list=True)
all_scores_df = fetch_column(df, Columns.score, filters={Columns.player_name: [all_players[0]]})
average = all_scores_df.mean()
#print(average)


spieler = all_players[0]
seasons = [None, '22/23', '23/24', '24/25']

for season in seasons:
    filtered_df = fetch_data(df, values_to_filter_for={Columns.season: season})
    print(filtered_df.size)
    html_kpis = {
        'pins_im_schnitt': calculate_score_average_player(filtered_df, spieler),
        'min_pins': calculate_score_min_player(filtered_df, spieler),
        'max_pins': calculate_score_max_player(filtered_df, spieler),
        'anzahl_spiele': calculate_games_count_player(filtered_df, spieler)
    }

    print(html_kpis)

#filtered_df = df.copy()
team_avg = calculate_score_average_team(df, all_teams[0])
print("Team average of team " + all_teams[0] + ": " + str(team_avg))

#filtered_df = df.copy()
season_average = calculate_score_average(df, filters={Columns.season: [all_seasons[0]]})
print("Average of " + all_seasons[0]+ ": " + str(season_average))


#filtered_df = df.copy()
league_average = calculate_score_average(df, filters={Columns.league_name: [all_leagues[0]]})
print("Average of league " + all_leagues[0] + ": " + str(league_average))

#filtered_df = df.copy()
player_avg = calculate_score_average_player(df, spieler, group_by=Columns.week)
print("Average of player " + spieler + " in season 22/23: " + str(player_avg))

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
    ['22/23', 1, '01.01.23', 'LL1_N', 'Regensburg', 'Donaubowler 1', 'Feller, Christian', 16007, 1, 'Comet 1', 1, 220, 1, True, False],
    ['22/23', 1, '01.01.23', 'LL1_N', 'Regensburg', 'Donaubowler 1', 'Hartfeil, Volkmar', 123, 1, 'Comet 1', 2, 210, 1,True, False],
    ['22/23', 1, '01.01.23', 'LL1_N', 'Regensburg', 'Donaubowler 1', 'Hürdler, Marco', 456, 1, 'Comet 1', 3, 200, 0, True, False],
    ['22/23', 1, '01.01.23', 'LL1_N', 'Regensburg', 'Donaubowler 1', 'Obermeier, Kurt', 789, 1, 'Comet 1', 4, 190, 0, True, False],
    ['22/23', 1, '01.01.23', 'LL1_N', 'Regensburg', 'Comet 1', 'Comet #1', 67, 1, 'Donaubowler 1', 1, 200, 0, True, False],
    ['22/23', 1, '01.01.23', 'LL1_N', 'Regensburg', 'Comet 1', 'Comet #2', 23, 1, 'Donaubowler 1', 2, 205, 0,True, False],
    ['22/23', 1, '01.01.23', 'LL1_N', 'Regensburg', 'Comet 1', 'Comet #3', 56, 1, 'Donaubowler 1', 3, 205, 1,True, False],
    ['22/23', 1, '01.01.23', 'LL1_N', 'Regensburg', 'Comet 1', 'Comet #4', 89, 1, 'Donaubowler 1', 4, 195, 1,True, False],
    ['23/24', 2, '03.01.24', 'LL1_N', 'Regensburg', 'Donaubowler 1', 'Feller, Christian', 16007, 1, 'Comet 1', 1, 220, 1, True, False],
    ['23/24', 2, '03.01.24', 'LL1_N', 'Regensburg', 'Donaubowler 1', 'Hartfeil, Volkmar', 123, 1, 'Comet 1', 2, 210, 1, True, False],
    ['23/24', 2, '03.01.24', 'LL1_N', 'Regensburg', 'Donaubowler 1', 'Hürdler, Marco', 456, 1, 'Comet 1', 3, 200, 0.5, True, False],
    ['23/24', 2, '03.01.24', 'LL1_N', 'Regensburg', 'Donaubowler 1', 'Obermeier, Kurt', 789, 1, 'Comet 1', 4, 190, 0, True, False],
    ['22/23', 2, '01.01.23', 'LL1_N', 'Regensburg', 'Comet 1', 'Comet #1', 67, 1, 'Donaubowler 1', 1, 200, 0, True, False],
    ['22/23', 2, '01.01.23', 'LL1_N', 'Regensburg', 'Comet 1', 'Comet #2', 23, 1, 'Donaubowler 1', 2, 200, 0,True, False],
    ['22/23', 2, '01.01.23', 'LL1_N', 'Regensburg', 'Comet 1', 'Comet #3', 56, 1, 'Donaubowler 1', 3, 200, 0.5,True, False],
    ['22/23', 2, '01.01.23', 'LL1_N', 'Regensburg', 'Comet 1', 'Comet #4', 89, 1, 'Donaubowler 1', 4, 200, 1,True, False],
]

# DataFrame erstellen
data_league = pd.DataFrame(data_dummy, columns=col_names)
data_league['Points'] = None

# DataFrame anzeigen

data_matchday = fetch_matchday(data_league, '22/23', 'LL1_N', 1)

data_match = fetch_match(data_matchday, 'Donaubowler 1', 1)

data_match_processed = calculate_points(data_match)

if 0:
    for df in [data_league, data_matchday, data_match, data_match_processed]:
        print(df)
        print()

# DataFrame in eine CSV-Datei speichern

team = create_team(7)
print(team)