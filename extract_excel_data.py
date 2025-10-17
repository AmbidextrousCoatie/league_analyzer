#!/usr/bin/env python3
"""
Script to extract data from BYL_Maenner-5-6.xlsx and map it to the existing CSV format.
Based on correct understanding: 9 teams, 30 rows each, 4 positions, up to 3 players per position.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re


dict_of_match_numbers = {}
def get_match_number(round_idx, team_name, team_name_opponent):
    """Get the match number for a given round, team name, and opponent."""
    
    my_team_tuple = frozenset([team_name, team_name_opponent])

    if round_idx not in dict_of_match_numbers:
        dict_of_match_numbers[round_idx] = {my_team_tuple: 0}

    elif my_team_tuple not in dict_of_match_numbers[round_idx]:
        max_match_number = max(dict_of_match_numbers[round_idx].values())
        dict_of_match_numbers[round_idx][my_team_tuple] = max_match_number + 1

    return dict_of_match_numbers[round_idx][my_team_tuple]


def extract_season_info(excel_file, sheet_name):
    """Extract season information from specified sheet."""
    try:
        # Read the specified sheet
        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
        
        # Look for season information in the first row
        first_row = df.iloc[0]
        for col, value in first_row.items():
            if pd.notna(value) and isinstance(value, str):
                # Look for pattern like "Saison 2025/2026"
                season_match = re.search(r'Saison\s+(\d{4})/(\d{4})', str(value))
                if season_match:
                    year1 = season_match.group(1)
                    year2 = season_match.group(2)
                    # Convert YYYY/YYYY to YY/YY format
                    season_short = f"{year1[-2:]}/{year2[-2:]}"
                    return {
                        'season_short': season_short,
                        'year1': year1,
                        'year2': year2
                    }
        
        print("Warning: Could not find season information in Schiedsrichterinfos sheet")
        return {'season_short': '??/??', 'year1': '????', 'year2': '????'}  # Default fallback
        
    except Exception as e:
        print(f"Error reading Schiedsrichterinfos sheet: {e}")
        return {'season_short': '??/??', 'year1': '????', 'year2': '????'}  # Default fallback


def extract_date_info(df):
    """Extract date information from first row of team sheet."""
    try:
        # Look in the first row for date pattern like "04.10. / 05.10." or "12.11."
        first_row = df.iloc[0]
        for col, value in first_row.items():
            if pd.notna(value) and isinstance(value, str):
                # Look for DD.MM. pattern (with optional slash and more)
                date_match = re.search(r'(\d{2})\.(\d{2})\.', str(value))
                if date_match:
                    day = date_match.group(1)
                    month = date_match.group(2)
                    return {
                        'day': day,
                        'month': month
                    }
        
        print("Warning: Could not find date information in first row")
        return {'day': '04', 'month': '10'}  # Default fallback
        
    except Exception as e:
        print(f"Error extracting date info: {e}")
        return {'day': 'n/a', 'month': 'n/a'}  # Default fallback


def combine_season_and_date(season_info, date_info):
    """Combine season and date information to create full date."""
    try:
        day = date_info['day']
        month = int(date_info['month'])
        year1 = season_info['year1']
        year2 = season_info['year2']
        
        # Determine which year to use based on month
        if month >= 9:
            year = year1  # Use first year for months 9-12
        else:
            year = year2  # Use second year for months 1-8
        
        # Create full date in YYYY-MM-DD format
        full_date = f"{year}-{month:02d}-{day}"
        return full_date
        
    except Exception as e:
        print(f"Error combining season and date: {e}")
        return "could not extract date"  # Default fallback


def extract_excel_data(excel_file='2025_BYL_M-1.xlsx', team_sheet='Erfassung1', season_sheet='Schiedsrichterinfos'):
    """Extract data from Excel file and map to CSV format."""
    
    print(f"Reading Excel file - {team_sheet} sheet...")
    try:
        # Read the specific sheet without header
        df = pd.read_excel(excel_file, sheet_name=team_sheet, header=None)
        print(f"Excel file shape: {df.shape}")
        
        # Slice from column Z onwards (index 25)
        start_col_idx = 25
        end_col_idx = min(start_col_idx + 24, len(df.columns))
        df = df.iloc[:, start_col_idx:end_col_idx]
        print(f"After slicing - shape: {df.shape}")
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None
    
    # Extract season information from specified sheet
    season_info = extract_season_info(excel_file, season_sheet)
    print(f"Extracted season info: {season_info}")
    
    # Extract date information from first row of team sheet
    date_info = extract_date_info(df)
    print(f"Extracted date info: {date_info}")
    
    # Combine season and date to get full date
    full_date = combine_season_and_date(season_info, date_info)
    print(f"Combined full date: {full_date}")
    
    return df, season_info, full_date


def parse_teams(excel_df, season_info, full_date):
    """Parse all teams in the Excel file."""
    
    csv_data = []
    season = season_info['season_short']
    league = "BayL"
    players_per_team = 4
    date = full_date
    
    # Find team sections (rows containing "Team-Nr.")
    team_start_rows = []
    for idx, row in excel_df.iterrows():
        for col, value in row.items():
            if pd.notna(value) and "Team-Nr." in str(value):
                team_start_rows.append(idx)
                break
    
    print(f"Found {len(team_start_rows)} team sections starting at rows: {team_start_rows}")
    
    for team_idx, start_row in enumerate(team_start_rows):
        print(f"\n=== Processing Team {team_idx + 1} ===")
        
        # Extract 30 rows for this team
        end_row = start_row + 30
        team_data = excel_df.iloc[start_row:end_row]
        
        # Extract team information
        team_info = extract_team_info(team_data)
        print(f"Team: {team_info['team_name']}")
        print(f"Location: {team_info['location']}")
        print(f"Week: {team_info['week']}")
        
        # Extract player data for this team
        team_players = extract_team_players(team_data, team_info, season, league, players_per_team, date)
        
        # Add to CSV data
        csv_data.extend(team_players)
    
    return csv_data


def extract_team_info(team_data):
    """Extract basic team information from the first few rows."""
    
    team_info = {
        'team_name': 'Unknown Team',
        'location': 'Unknown',
        'week': '1',
        'opponent': 'Unknown'
    }
    
    # Debug: Print the actual row 2 (index 1) to see what's there
    if len(team_data) > 1:
        print(f"Row 2 (index 1) contents:")
        row_2 = team_data.iloc[1]
        for i, value in enumerate(row_2):
            if pd.notna(value):
                print(f"  Col {i}: '{value}'")
    
    # Location is always in column 30 (index 29) of row 2 (index 1)
    if len(team_data) > 1 and len(team_data.columns) > 5:
        location_value = team_data.iloc[1, 5]  # Row 2, Column 30 (index 29)
        print(f"Location value at col 30: '{location_value}' (type: {type(location_value)})")
        if pd.notna(location_value):
            team_info['location'] = str(location_value).strip()
            print(f"Location (col 30): {team_info['location']}")

    # Week is always in column 44 (index 43) of row 2 (index 1)
    if len(team_data) > 1 and len(team_data.columns) > 19:
        week_value = team_data.iloc[1, 19]  # Row 2, Column 44 (index 43)
        print(f"Week value at col 44: '{week_value}' (type: {type(week_value)})")
        if pd.notna(week_value):
            if isinstance(week_value, (int, float)) or (isinstance(week_value, str) and week_value.isdigit()):
                team_info['week'] = str(int(float(week_value)))
                print(f"Week (col 44): {team_info['week']}")
    
    # Row 3 (index 2): Team name
    team_name_row = team_data.iloc[2]
    for col, value in team_name_row.items():
        if pd.notna(value) and isinstance(value, str) and len(str(value).strip()) > 0:
            team_info['team_name'] = str(value).strip()
            break
    
    # Row 23 (index 22): Opponent team name
    opponent_row = team_data.iloc[22]
    print(f"\nOpponent row (row 23) values:")
    for col_idx, value in opponent_row.items():
        if pd.notna(value):
            print(f"  Col {col_idx}: '{value}'")
            # Look for team name patterns
            if isinstance(value, str) and len(str(value).strip()) > 0 and "Team" not in str(value):
                team_info['opponent'] = str(value).strip()
                break
        
        # Also check rows 25-29 for opponent info
        print(f"\nOpponent verification rows (25-29):")
        for row_idx in range(24, 29):
            row = team_data.iloc[row_idx]
            print(f"  Row {row_idx+1}: {[str(v) for v in row.values if pd.notna(v)]}")
        
        return team_info

def extract_team_players(team_data, team_info, season, league, players_per_team, date):
    """Extract all player data for a team."""
    
    players = []
    
    # Find column headers (row 6, index 5)
    header_row = team_data.iloc[5]
    
    # Find important columns
    name_col = None
    id_col = None
    score_cols = []
    points_cols = []
    
    # Find Name and ID columns
    for col_idx, value in header_row.items():
        if pd.notna(value):
            value_str = str(value).lower()
            if "name" in value_str:
                name_col = col_idx
            elif "rl" in value_str:
                id_col = col_idx
    
    # Find individual round columns
    for col_idx, value in header_row.items():
        if pd.notna(value):
            value_str = str(value).lower()
            if "pins" in value_str and "gesamt" not in value_str:
                score_cols.append(col_idx)
            elif "pkt" in value_str and "gesamt" not in value_str:
                points_cols.append(col_idx)
    
    # Limit to 9 rounds
    if len(score_cols) > 9:
        score_cols = score_cols[:9]
    if len(points_cols) > 9:
        points_cols = points_cols[:9]
    
    # Find opponent columns (same as score columns)
    opponent_row = team_data.iloc[22]
    opponent_cols = [col for col in score_cols if col in opponent_row.index and pd.notna(opponent_row[col])]
    
    # Find team total scores and points
    team_total_row = team_data.iloc[18]
    team_total_scores = {}
    team_total_points = {}
    
    for col_idx, value in team_total_row.items():
        if pd.notna(value) and col_idx in score_cols:
            round_idx = score_cols.index(col_idx)
            try:
                team_total_scores[round_idx] = int(value)
                points_col = points_cols[round_idx]
                if pd.notna(team_total_row[points_col]):
                    team_total_points[round_idx] = float(team_total_row[points_col])
                else:
                    team_total_points[round_idx] = 0.0
            except (ValueError, TypeError):
                pass
    
    print(f"Found columns: Name={name_col}, ID={id_col}")
    print(f"Score columns (rounds): {score_cols}")
    print(f"Points columns (rounds): {points_cols}")
    print(f"Opponent columns (rounds): {opponent_cols}")
    print(f"Team total scores: {team_total_scores}")
    print(f"Team total points: {team_total_points}")
    
    # Define position ranges
    positions = [
        (6, 8),   # Position 1: rows 7-9
        (9, 11),  # Position 2: rows 10-12
        (12, 14), # Position 3: rows 13-15
        (15, 17)  # Position 4: rows 16-18
    ]
    
    for pos_idx, (start_row, end_row) in enumerate(positions):
        print(f"\nProcessing Position {pos_idx + 1} (rows {start_row+1}-{end_row+1})")
        
        pos_rows = team_data.iloc[start_row:end_row+1]
        
        for player_row_idx, row in pos_rows.iterrows():
            if name_col and pd.notna(row[name_col]):
                player_name = str(row[name_col]).strip()
                
                # Get player ID
                player_id = 0
                if id_col and pd.notna(row[id_col]):
                    try:
                        player_id = int(row[id_col])
                    except (ValueError, TypeError):
                        player_id = hash(f"{team_info['team_name']}_{player_name}_{pos_idx}") % 100000
                    
                print(f"  Player: {player_name} (ID: {player_id})")
                
                # Process each round (Spiel 1-9) - only individual rounds, not totals
                for round_idx, (score_col, points_col) in enumerate(zip(score_cols, points_cols)):
                    if pd.notna(row[score_col]):
                        try:
                            score = int(row[score_col])

                            points = float(pos_rows[points_col].sum()) if pd.notna(pos_rows[points_col].sum()) else 0.0
                            
                            # Get opponent
                            opponent = "Unknown"
                            if round_idx < len(opponent_cols):
                                opponent_col = opponent_cols[round_idx]
                                if pd.notna(opponent_row[opponent_col]):
                                    opponent = str(opponent_row[opponent_col]).strip()
                            
                            match_number = get_match_number(round_idx, team_info['team_name'], opponent)
                            
                            # Create CSV row
                            csv_row = {
                                'Season': season,
                                'Week': team_info['week'],
                                'Date': date,
                                'League': league,
                                'Players per Team': players_per_team,
                                'Location': team_info['location'],
                                'Round Number': round_idx + 1,
                                'Match Number': match_number,
                                'Team': team_info['team_name'],
                                'Position': pos_idx,
                                'Player': player_name,
                                'Player ID': player_id,
                                'Opponent': opponent,
                                'Score': score,
                                'Points': str(points),
                                'Input Data': 'True',
                                'Computed Data': 'False'
                            }
                            
                            players.append(csv_row)
                            print(f"    Round {round_idx + 1}: Score={score}, Points={points}, Opponent={opponent}")
                            
                        except (ValueError, TypeError) as e:
                            print(f"    Invalid data for round {round_idx + 1}: {e}")
    
    # Add team total rows
    for round_idx in range(len(score_cols)):
        if round_idx in team_total_scores:
            # Get opponent
            opponent = "Unknown"
            if round_idx < len(opponent_cols):
                opponent_col = opponent_cols[round_idx]
                if pd.notna(opponent_row[opponent_col]):
                    opponent = str(opponent_row[opponent_col]).strip()
            
            match_number = get_match_number(round_idx, team_info['team_name'], opponent)
            
            # Create CSV row for team total
            csv_row = {
                'Season': season,
                'Week': team_info['week'],
                'Date': date,
                'League': league,
                'Players per Team': players_per_team,
                'Location': team_info['location'],
                'Round Number': round_idx + 1,
                'Match Number': match_number,
                'Team': team_info['team_name'],
                'Position': 0,  # Team total
                'Player': 'Team Total',
                'Player ID': 0,
                'Opponent': opponent,
                'Score': team_total_scores[round_idx],
                'Points': str(team_total_points[round_idx]),
                'Input Data': 'False',
                'Computed Data': 'True'
            }
            
            players.append(csv_row)
            print(f"  Team Total Round {round_idx + 1}: Score={team_total_scores[round_idx]}, Points={team_total_points[round_idx]}, Opponent={opponent}")

    return players


if __name__ == "__main__":
    print("Starting Excel data extraction...")
    
    # Configuration - can be easily changed
   
    team_sheet = 'Erfassung'
    season_sheet = 'Schiedsrichterinfos'
    
    setup = {'BYL_Maenner-5-6.xlsx': [1, 2, 3, 4, 5, 6],
             '2025_BYL_M-1.xlsx': [1]}
   
   
    output_df = pd.DataFrame()
    for input_file in setup.keys():
        for week in setup[input_file]:
            dict_of_match_numbers = {} # reset the dict of match numbers for each week
            result = extract_excel_data(input_file, team_sheet+str(week), season_sheet)
    
            if result is not None:
                df, season_info, full_date = result
                
                # Parse teams with extracted season and date info
                csv_data = parse_teams(df, season_info, full_date)
                
                if csv_data:
                    temp_df = pd.DataFrame(csv_data)
                    output_df = pd.concat([output_df, temp_df], ignore_index=True)


    # Save to CSV
    if output_df.empty:
        print("No data extracted")
    else:
        output_df = output_df.sort_values(by=['Season', 'League', 'Week', 'Round Number', 'Match Number', 'Team', 'Position'])
        output_file = 'database/data/bowling_ergebnisse_real_2025_new.csv'
        output_df.to_csv(output_file, sep=';', index=False)
        print(f"Extracted {len(csv_data)} rows to {output_file}")
        
        # Show sample data
        print(f"\nSample extracted data:")
        print(output_df[['Season', 'Week', 'Date', 'League', 'Team', 'Player', 'Score', 'Points']].head(10))
        
        # Show summary
        print(f"\nSummary:")
        print(f"Teams found: {len(output_df['Team'].unique())}")
        print(f"Players found: {len(output_df[output_df['Player'] != 'Team Total']['Player'].unique())}")
        print(f"Total matches: {len(csv_data)}")
        print(f"Score range: {output_df['Score'].min()} - {output_df['Score'].max()}")
        
        # Show rounds per position
        print(f"\nRounds per position:")
        print(output_df['Round Number'].value_counts().sort_index())
    
    print("Extraction complete!") 
    # pretty print the dict_of_match_numbers
    for round_idx, match_numbers in dict_of_match_numbers.items():
        print(f"Round {round_idx}:")
        for team_tuple, match_number in match_numbers.items():
            print(f"  {team_tuple}: {match_number}")
    