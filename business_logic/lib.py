import pandas as pd
from tqdm import tqdm
import numpy as np

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


def assign_points(match_df, team, opponent_team):
    """
    Assign points to teams based on their scores.

    Args:
        match_df (pd.DataFrame): The full DataFrame containing match data.
        team (str): The name of the team.
        opponent_team (str): The name of the opponent team.
        Columns (object): An object or namespace containing column names.

    Returns:
        None: The function updates the 'points' column in-place.
    """
    print(f"{team} : {opponent_team}")
    
    # Slice the DataFrame for both teams
    results_team = match_df[
        (match_df[Columns.team_name] == team) & 
        (match_df[Columns.team_name_opponent] == opponent_team)
    ].copy()
    
    results_opponent = match_df[
        (match_df[Columns.team_name] == opponent_team) & 
        (match_df[Columns.team_name_opponent] == team)
    ].copy()
    
    # Print scores for debugging
    print("Team Scores:")
    print(results_team[Columns.score])
    print("Opponent Scores:")
    print(results_opponent[Columns.score])
    
    # Ensure both DataFrames have the same number of rows
    if len(results_team) != len(results_opponent):
        raise ValueError("Mismatch in the number of matches between team and opponent.")
    
    # Convert scores to NumPy arrays for element-wise comparison
    team_scores = results_team[Columns.score].to_numpy()
    opponent_scores = results_opponent[Columns.score].to_numpy()
    
    # Perform comparisons
    team_wins = team_scores > opponent_scores
    opponent_wins = team_scores < opponent_scores
    ties = team_scores == opponent_scores
    
    # Debug prints for comparison masks
    print("Team Wins Mask:")
    print(team_wins)
    print("Opponent Wins Mask:")
    print(opponent_wins)
    print("Ties Mask:")
    print(ties)
    
    # Assign points based on comparisons
    results_team.loc[:, Columns.points] = np.where(team_wins, 1.0, np.where(ties, 0.5, 0.0))
    results_opponent.loc[:, Columns.points] = np.where(opponent_wins, 1.0, np.where(ties, 0.5, 0.0))
    
    # Update the original match_df with the new points
    match_df.loc[results_team.index, Columns.points] = results_team[Columns.points]
    match_df.loc[results_opponent.index, Columns.points] = results_opponent[Columns.points]

    return match_df

def calculate_point3(df):
    """Calculate points according to German Minor League rules"""
    # Create a copy to avoid modifying original
    df_with_points = df.copy()
    
    # Initialize points column
    df_with_points['Points'] = 0.0
    
    # Group by match identifiers
    match_groups = df_with_points.groupby([Columns.season, Columns.league_name, Columns.week, Columns.round_number, Columns.match_number])
    total_groups = len(match_groups)
    
    team_total_rows = []

    with tqdm(total=total_groups, desc="Calculating points") as pbar:
        for (season, league, week, round_number, match), match_df in match_groups:
            # Extract unique team-opponent pairs to avoid duplicate processing
            match_dfs = match_df.groupby(Columns.team_name)
            team_names = list(match_dfs.groups.keys())    
            if len(team_names) != 2:
                print(f"Unexpected number of teams in match {match}" + " | " + str(len(team_names)))
                continue
            team_name = team_names[0]
            opponent_name = team_names[1]
            players_per_team = match_dfs.get_group(team_name)[Columns.players_per_team].values[0]
            team_positions = match_dfs.get_group(team_name)[Columns.position].values
            opponent_positions = match_dfs.get_group(opponent_name)[Columns.position].values

            location = match_df[Columns.location].iloc[0]
            date = match_df[Columns.date].iloc[0]

            if not set(team_positions) == set(opponent_positions):
                print(f"Unexpected positions in match {match}" + " | " + str(team_positions) + " | " + str(opponent_positions))
                continue    

            team_data = match_dfs.get_group(team_name)
            opponent_data = match_dfs.get_group(opponent_name)

            
            score_team_total = 0
            score_opponent_total = 0    

            for position in team_positions:
                score_team = team_data[Columns.score].values[position]
                score_opponent = opponent_data[Columns.score].values[position]

                score_team_total += score_team
                score_opponent_total += score_opponent

                condition_team = (match_df[Columns.team_name] == team_name) & (match_df[Columns.position] == position)
                condition_opponent = (match_df[Columns.team_name] == opponent_name) & (match_df[Columns.position] == position)

                if score_team > score_opponent:
                    match_df.loc[condition_team, Columns.points] = 1.0
                    match_df.loc[condition_opponent, Columns.points] = 0.0
                elif score_team < score_opponent:
                    match_df.loc[condition_team, Columns.points] = 0.0
                    match_df.loc[condition_opponent, Columns.points] = 1.0
                else:
                    match_df.loc[condition_team, Columns.points] = 0.5
                    match_df.loc[condition_opponent, Columns.points] = 0.5
            
            #print(match_df)
            df_with_points.update(match_df)
            #print(df_with_points.head(8))

            #print(str(score_team_total) + " : " + str(score_opponent_total))
            points_team = 0 
            points_opponent = 0
            if score_team_total > score_opponent_total:
                points_team = 2
            elif score_team_total < score_opponent_total:
                points_opponent = 2
            else:
                points_team = 1
                points_opponent = 1
            #print(str(points_team) + ": " + str(points_opponent)    )
            
            lala = 0

            team_total_rows.append({
                Columns.season: season,
                Columns.week: week,
                Columns.date: date,
                Columns.league_name: league,
                Columns.players_per_team: players_per_team,
                Columns.location: location,
                Columns.round_number: round_number,
                Columns.match_number: match,
                Columns.team_name: team_name,
                Columns.position: None,
                Columns.player_name: 'Team Total',
                Columns.player_id: None,

                Columns.team_name_opponent: opponent_name,
                Columns.score: score_team_total,
                Columns.points: points_team,

                Columns.input_data: False,
                Columns.computed_data: True
            })

            team_total_rows.append({
                Columns.season: season,
                Columns.week: week,
                Columns.date: date,
                Columns.league_name: league,
                Columns.players_per_team: players_per_team,
                Columns.location: location,
                Columns.round_number: round_number,
                Columns.match_number: match,
                Columns.team_name: opponent_name,
                Columns.position: None,
                Columns.player_name: 'Team Total',
                Columns.player_id: None,

                Columns.team_name_opponent: team_name,
                Columns.score: score_opponent_total,
                Columns.points: points_opponent,

                Columns.input_data: False,
                Columns.computed_data: True
            })
            
            pbar.update(1)
    
    df_with_points = pd.concat([df_with_points, pd.DataFrame(team_total_rows)], ignore_index=True)

    return df_with_points
    
            

def calculate_point2(df):
    """Calculate points according to German Minor League rules"""
    # Create a copy to avoid modifying original
    df_with_points = df.copy()
    
    # Initialize points column
    df_with_points['Points'] = 0.0
    
    # Group by match identifiers
    match_groups = df_with_points.groupby([Columns.season, Columns.league_name, Columns.week, Columns.round_number, Columns.match_number])
    total_groups = len(match_groups)

    with tqdm(total=total_groups, desc="Calculating points") as pbar:
        for (season, league, week, round_number, match), match_df in match_groups:
            # Extract unique team-opponent pairs to avoid duplicate processing
            processed_pairs = set()
            
            for idx, row in match_df.iterrows():
                team = row[Columns.team_name]
                opponent = row[Columns.team_name_opponent]
                print(match_df)
                # Create a sorted tuple to ensure each pair is processed only once
                pair = tuple(sorted([team, opponent]))
                
                if pair in processed_pairs:
                    continue  # Skip already processed pairs
                
                processed_pairs.add(pair)
                
                # Retrieve both team rows
                team_row = match_df[
                    (match_df[Columns.team_name] == pair[0]) & 
                    (match_df[Columns.team_name_opponent] == pair[1])
                ]
                opponent_row = match_df[
                    (match_df[Columns.team_name] == pair[1]) & 
                    (match_df[Columns.team_name_opponent] == pair[0])
                ]
                
                # Ensure each pair has exactly one team and one opponent
                if len(team_row) != len(opponent_row):
                    print(f"Unexpected number ASD of rows for pair {pair} in match {match}" + " | " + str(len(team_row)) + " | " + str(len(opponent_row)))
                    continue  # Skip this pair
                
                if set(team_row.index) != set(opponent_row.index):
                    print(f"Unexpected indices for pair {pair} in match {match}" + " | " + str(set(team_row.index)) + " | " + str(set(opponent_row.index)))
                    continue  # Skip this pair
                
                # Extract indices and scores
                team_idx = team_row.index[0]
                opponent_idx = opponent_row.index[0]
                
                team_score = team_row.iloc[0][Columns.score]
                opponent_score = opponent_row.iloc[0][Columns.score]
                
                # Assign points based on score comparison
                if team_score > opponent_score:
                    df_with_points.loc[team_idx, Columns.points] = 1.0
                    df_with_points.loc[opponent_idx, Columns.points] = 0.0
                elif team_score < opponent_score:
                    df_with_points.loc[team_idx, Columns.points] = 0.0
                    df_with_points.loc[opponent_idx, Columns.points] = 1.0
                else:
                    df_with_points.loc[team_idx, Columns.points] = 0.5
                    df_with_points.loc[opponent_idx, Columns.points] = 0.5
                
            pbar.update(1)
    
    return df_with_points


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
    team_total_rows = []


    with tqdm(total=total_groups, desc="Calculating points") as pbar:
        for (season, league, week, match), match_df in match_groups:
            all_teams = match_df[Columns.team_name].unique()
            # Calculate individual points
            date = match_df[Columns.date].iloc[0]
            location = match_df[Columns.location].iloc[0]
            # iterate over all teams
            for team in all_teams:
                for opponent_team in all_teams:
                    if team == opponent_team:
                        continue
                    print(match_df)

                    match_df = assign_points(match_df, team, opponent_team)


                    if False:
                        print(team + " : " + opponent_team)
                        results_team = match_df[(match_df[Columns.team_name] == team) & (match_df[Columns.team_name_opponent] == opponent_team)]
                        results_opponent = match_df[(match_df[Columns.team_name] == opponent_team) & (match_df[Columns.team_name_opponent] == team)]
                        print(results_team[Columns.score])
                        print(results_opponent[Columns.score])
                        print (results_team[Columns.score].gt(results_opponent[Columns.score]))
                        print (results_opponent[Columns.score].gt(results_team[Columns.score]))
                        results_team.loc[results_team[Columns.score].gt(results_opponent[Columns.score]), Columns.points] = 1.0
                        results_opponent.loc[results_opponent[Columns.score].gt(results_team[Columns.score]), Columns.points] = 1.0

                        # Handle ties using index-aligned comparison
                        ties = results_team[Columns.score].eq(results_opponent[Columns.score])
                        results_team.loc[ties, Columns.points] = 0.5
                        results_opponent.loc[ties, Columns.points] = 0.5
                    #results_team[Columns.points] += 1 if results_team[Columns.score].gt(results_opponent[Columns.score]) else 0
                    #results_team[Columns.points] += 0.5 if results_team[Columns.score].eq(results_opponent[Columns.score]) else 0
                    #results_opponent[Columns.points] = 1 - results_team[Columns.points]
                    
                    if False:
                    
                        print(team + " : " + opponent_team)
                        results_team = match_df[(match_df[Columns.team_name] == team) & 
                                            (match_df[Columns.team_name_opponent] == opponent_team)]
                        results_opponent = match_df[(match_df[Columns.team_name] == opponent_team) & 
                                                (match_df[Columns.team_name_opponent] == team)]

                        # Reset indices for comparison
                        results_team_scores = results_team[Columns.score].reset_index(drop=True)
                        results_opponent_scores = results_opponent[Columns.score].reset_index(drop=True)

                        # Compare aligned scores
                        team_wins = results_team_scores.gt(results_opponent_scores)
                        opponent_wins = results_opponent_scores.gt(results_team_scores)
                        ties = results_team_scores.eq(results_opponent_scores)

                        # Update points using original indices
                        results_team.loc[results_team.index[team_wins], Columns.points] = 1.0
                        results_opponent.loc[results_opponent.index[opponent_wins], Columns.points] = 1.0
                        results_team.loc[results_team.index[ties], Columns.points] = 0.5
                        results_opponent.loc[results_opponent.index[ties], Columns.points] = 0.5
                        print(results_team)
                        print(results_opponent)
                
                        score_team = results_team[Columns.score].sum()
                        score_opponent = results_opponent[Columns.score].sum()  

                        print(str(score_team) + " : " + str(score_opponent))
                        points_team = 0 
                        points_opponent = 0
                        if score_team > score_opponent:
                            points_team = 2
                        elif score_team < score_opponent:
                            points_opponent = 2
                        else:
                            points_team = 1
                            points_opponent = 1
                        print(str(points_team) + ": " + str(points_opponent)    )
                        
                        lala = 0

                        team_total_rows.append({
                            Columns.season: season,
                            Columns.week: week,
                            Columns.date: date,
                            Columns.league_name: league,
                            Columns.location: location,
                            Columns.team_name: team,
                            Columns.player_name: 'Team Total',
                            Columns.player_id: None,
                            Columns.match_number: match,
                            Columns.team_name_opponent: opponent_team,
                            Columns.position: None,
                            Columns.score: score_team,
                            Columns.points: points_team,
                            Columns.input_data: False,
                            Columns.computed_data: True
                        })

                


                #print(df_with_points)
            pbar.update(1)
                
            # Add team total rows to DataFrame
        #df_with_points = pd.concat([df_with_points, pd.DataFrame(team_total_rows)], ignore_index=True)
    
    return df_with_points.sort_values(by=[Columns.league_name, Columns.season, Columns.week, Columns.match_number, Columns.team_name, Columns.position])


def calculate_averages(df: pd.DataFrame, league_name=None, season=None, player=None):

    if league_name is not None:
        df = df[df[Columns.league_name] == league_name]

    if season is not None:
        df = df[(df[Columns.season] == season)]

    if player is not None:
        df = df[df[Columns.player_name] == player]

    result = df.groupby(Columns.player_name)[Columns.score].mean()

    print(result)
