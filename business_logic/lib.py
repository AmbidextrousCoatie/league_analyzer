import pandas as pd

from database.definitions import col_names_league_table


def fetch_matchday(data, season, league_name, matchday):
    return data[(data[col_names_league_table.season] == season) &
                (data[col_names_league_table.week] == matchday) &
                (data[col_names_league_table.league_name] == league_name)]


def fetch_match(data, team, match_number):
    return data[(
                        (data[col_names_league_table.team_name] == team)
                        | (data[col_names_league_table.team_name_opponent] == team)
                )
                & (data[col_names_league_table.match_number] == match_number)]


def calculate_match_outcome(df):

    # validation: all players eligible? --> warning
    # validation: 4 players on each team? --> warning

    # add col if missing

    col_pos = col_names_league_table.position
    col_score = col_names_league_table.score
    col_points = col_names_league_table.points
    col_team = col_names_league_table.team_name

    lala = 0

    # calculate outcome of each duel
    for position in range(1, 5):
        print(position)
        data_duel = df[df[col_pos] == position]

        idx_0 = data_duel.index[0]
        idx_1 = data_duel.index[1]

        if df.loc[idx_0, col_score] > df.loc[idx_1, col_score]:
            df.loc[idx_0, col_points] = 1
            df.loc[idx_1, col_points] = 0
        elif df.loc[idx_0, col_score] < df.loc[idx_1, col_score]:
            df.loc[idx_0, col_points] = 0
            df.loc[idx_1, col_points] = 1
        else:
            df.loc[idx_0, col_points] = 0.5
            df.loc[idx_1, col_points] = 0.5

    pins_per_team = df.groupby(col_team)[col_score].sum().reset_index()

    # Neue Zeilen im ursprünglichen DataFrame hinzufügen
    rows_team_result = []
    for index, row in pins_per_team.iterrows():
        # Eine bestehende Zeile mit demselben Team-Namen kopieren
        row_total = df[df[col_team] == row[col_team]].iloc[0].copy()

        # Neue Werte in der kopierten Zeile setzen
        row_total[col_score] = row[col_score]
        row_total[col_names_league_table.player_name] = 'Total'
        row_total[col_names_league_table.player_id] = None
        row_total[col_names_league_table.match_number] = None

        rows_team_result.append(row_total)

    if rows_team_result[0][col_score] > rows_team_result[1][col_score]:
        rows_team_result[0][col_points] = 2
        rows_team_result[1][col_points] = 0
    elif rows_team_result[0][col_score] < rows_team_result[1][col_score]:
        rows_team_result[0][col_points] = 0
        rows_team_result[1][col_points] = 2
    else:
        rows_team_result[0][col_points] = 1
        rows_team_result[1][col_points] = 1

        # Kopierte Zeile in den DataFrame einfügen
    df = pd.concat([df, pd.DataFrame(rows_team_result)], ignore_index=True)

    points_per_team = df.groupby(col_team)[col_points].sum().reset_index()

    print(pins_per_team)
    print(points_per_team)

    # find player
    print(df)
    return df
    # find opponent


def get_round_robin_pairings(teams):

    # Wenn die Anzahl der Teams ungerade ist, fügen wir ein Freilos hinzu
    if len(teams) % 2 != 0:
        teams.append('Freilos')

    n = len(teams)
    pairings = []

    for play_round in range(n - 1):
        pairs = []
        for i in range(n // 2):
            home = teams[i]
            away = teams[n - 1 - i]
            if play_round % 2 == 0:
                pairs.append((home, away))
            else:
                pairs.append((away, home))
        pairings.append(pairs)
        # Die Rotation der Teams für die nächste Runde, ohne das erste Team zu bewegen
        teams = [teams[0]] + [teams[-1]] + teams[1:-1]

    return pairings


def calculate_points(df_season_results, league_name, league_season):
    # filter for league and season

    print("hi there")
    print(df_season_results.size)

    df_filtered = df_season_results[(df_season_results[col_names_league_table.league_name] == league_name)
                                    & (df_season_results[col_names_league_table.season] == league_season)]

    print(df_filtered.size)

    # go week by week
    for (week, df_per_week) in df_filtered.groupby(col_names_league_table.week):
        # is a tuple --> unpack

        print(df_per_week)
        for (game, df_per_week_per_game) in df_per_week.groupby(col_names_league_table.match_number):
            print(df_per_week_per_game)
            df_per_week_per_game.to_csv('tmp.csv', index=False, sep=";")

            pairings = [set([tmp_team, tmp_opponent]) for tmp_team, tmp_opponent in
                        zip(df_per_week_per_game[col_names_league_table.team_name],
                            df_per_week_per_game[col_names_league_table.team_name_opponent])
                       ]
            pairings = list(set(frozenset(s) for s in pairings))
            for pairing in pairings:
                lala = 0

    print(df_filtered.size)


def calculate_averages(df: pd.DataFrame, league_name=None, season=None, player=None):

    if league_name is not None:
        df = df[df[col_names_league_table.league_name] == league_name]

    if season is not None:
        df = df[(df[col_names_league_table.season] == season)]

    if player is not None:
        df = df[df[col_names_league_table.player_name] == player]

    result = df.groupby(col_names_league_table.player_name)[col_names_league_table.score].mean()

    print(result)
