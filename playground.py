import pandas as pd


from data_access.pd_dataframes import fetch_data, filter_data, fetch_column
from database.definitions import Columns
from business_logic.statistics import calculate_score_average_player, calculate_score_min_player, calculate_score_max_player, calculate_games_count_player, calculate_score_average_team, calculate_score_average_league, calculate_score_average

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