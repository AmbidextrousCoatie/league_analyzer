import pandas as pd
from tqdm import tqdm

from database.definitions import Columns


def fetch_matchday(data, season, league_name, matchday):
    return data[(data[Columns.season] == season) &
                (data[Columns.week] == matchday) &
                (data[Columns.league_name] == league_name)]


def fetch_match(data, team, match_number):
    return data[(
                        (data[Columns.team_name] == team)
                        | (data[Columns.team_name_opponent] == team)
                )
                & (data[Columns.match_number] == match_number)]


def calculate_match_outcome(df):

    # validation: all players eligible? --> warning
    # validation: 4 players on each team? --> warning

    # add col if missing

    col_pos = Columns.position
    col_score = Columns.score
    col_points = Columns.points
    col_team = Columns.team_name

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
        row_total[Columns.player_name] = 'Total'
        row_total[Columns.player_id] = None
        row_total[Columns.match_number] = None

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


def depr_calculate_points(df_season_results, league_name, league_season):
    # filter for league and season

    print("hi there")
    print(df_season_results.size)

    df_filtered = df_season_results[(df_season_results[Columns.league_name] == league_name)
                                    & (df_season_results[Columns.season] == league_season)]

    print(df_filtered.size)

    # go week by week
    for (week, df_per_week) in df_filtered.groupby(Columns.week):
        # is a tuple --> unpack

        #print(df_per_week)
        for (game, df_per_week_per_game) in df_per_week.groupby(Columns.match_number):
            print(df_per_week_per_game)
            df_per_week_per_game.to_csv('tmp.csv', index=False, sep=";")

            pairings = [set([tmp_team, tmp_opponent]) for tmp_team, tmp_opponent in
                        zip(df_per_week_per_game[Columns.team_name],
                            df_per_week_per_game[Columns.team_name_opponent])
                       ]
            pairings = list(set(frozenset(s) for s in pairings))
            for pairing in pairings:
                lala = 0

    print(df_filtered.size)
    return df_filtered

def calculate_points(df):
    """Calculate points according to German Minor League rules"""
    # Create a copy to avoid modifying original
    df_with_points = df.copy()
    
    # Initialize points column
    df_with_points['Points'] = 0.0
    
    # Group by match identifiers
    match_groups = df_with_points.groupby([Columns.season, Columns.league_name, Columns.week, Columns.match_number])
    #print(match_groups)
    total_groups = len(match_groups)
    with tqdm(total=total_groups, desc="Calculating points") as pbar:
        for (season, league, week, match), match_df in match_groups:
            # Calculate individual points
            
            # iterate over all teams
            for team in match_df[Columns.team_name].unique():
                # for each team find the opponent for this match:
                individual_match_groups = match_df[(match_df[Columns.team_name] == team) | (match_df[Columns.team_name_opponent] == team)].groupby(Columns.position)
                # filter for team_name == team 
                for position, individual_match in individual_match_groups:
                    #print(individual_match)
                    if individual_match.iloc[0][Columns.score] > individual_match.iloc[1][Columns.score]:
                        df_with_points.loc[individual_match.index[0], Columns.points] = 1
                    elif individual_match.iloc[0][Columns.score] < individual_match.iloc[1][Columns.score]:
                        df_with_points.loc[individual_match.index[0], Columns.points] = 0
                        df_with_points.loc[individual_match.index[1], Columns.points] = 1
                    else:
                        df_with_points.loc[individual_match.index, Columns.points] = 0.5 
                    df_with_points.loc[individual_match.index, Columns.input_data] = True
                    df_with_points.loc[individual_match.index, Columns.computed_data] = False
    
                #print(df_with_points)
            pbar.update(1)

                        
            lala = 0
        
        # Calculate team totals and add new rows
        team_totals = match_df.groupby(Columns.team_name)[Columns.score].sum().reset_index()
        team1_score = team_totals.iloc[0][Columns.score]
        team2_score = team_totals.iloc[1][Columns.score]
        
        # Create team total rows
        team_total_rows = []
        for _, team_row in team_totals.iterrows():
            team_points = 0
            if team1_score > team2_score:
                team_points = 2 if team_row[Columns.team_name] == team_totals.iloc[0][Columns.team_name] else 0
            elif team1_score < team2_score:
                team_points = 2 if team_row[Columns.team_name] == team_totals.iloc[1][Columns.team_name] else 0
            else:
                team_points = 1  # Tie
                
            team_total_rows.append({
                Columns.season: season,
                Columns.week: week,
                Columns.date: match_df[Columns.date].iloc[0],
                Columns.league_name: league,
                Columns.location: match_df[Columns.location].iloc[0],
                Columns.team_name: team_row[Columns.team_name],
                Columns.player_name: 'Team Total',
                Columns.player_id: None,
                Columns.match_number: match,
                Columns.team_name_opponent: match_df[match_df[Columns.team_name] != team_row[Columns.team_name]].iloc[0][Columns.team_name],
                Columns.position: None,
                Columns.score: team_row[Columns.score],
                Columns.points: team_points,
                Columns.input_data: False,
                Columns.computed_data: True
            })
            
        # Add team total rows to DataFrame
        df_with_points = pd.concat([df_with_points, pd.DataFrame(team_total_rows)], ignore_index=True)
    
    return df_with_points


def calculate_averages(df: pd.DataFrame, league_name=None, season=None, player=None):

    if league_name is not None:
        df = df[df[Columns.league_name] == league_name]

    if season is not None:
        df = df[(df[Columns.season] == season)]

    if player is not None:
        df = df[df[Columns.player_name] == player]

    result = df.groupby(Columns.player_name)[Columns.score].mean()

    print(result)
