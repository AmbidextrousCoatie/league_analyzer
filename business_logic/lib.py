import pandas as pd
from tqdm import tqdm

from data_access.schema import Columns


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
