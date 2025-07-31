#!/usr/bin/env python3
"""
Script to extract data from BYL_Maenner-5-6.xlsx and map it to the existing CSV format.
Based on correct understanding: 9 teams, 30 rows each, 4 positions, up to 3 players per position.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re

def extract_excel_data():
    """Extract data from Excel file and map to CSV format."""
    
    print("Reading Excel file - Erfassung6 sheet...")
    try:
        # Read the specific sheet without header
        df = pd.read_excel('BYL_Maenner-5-6.xlsx', sheet_name='Erfassung6', header=None)
        print(f"Excel file shape: {df.shape}")
        
        # Slice from column Z onwards (index 25)
        start_col_idx = 25
        end_col_idx = min(start_col_idx + 24, len(df.columns))
        df = df.iloc[:, start_col_idx:end_col_idx]
        print(f"After slicing - shape: {df.shape}")
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None
    
    def parse_teams(excel_df):
        """Parse all teams in the Excel file."""
        
        csv_data = []
        season = "24/25"
        league = "BayL"
        players_per_team = 4
        date = "2024-12-01"
        
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
            'week': '6',
            'opponent': 'Unknown'
        }
        
        # Row 1 (index 0): League info
        # Row 2 (index 1): Location and Week
        info_row = team_data.iloc[1]
        for col, value in info_row.items():
            if pd.notna(value) and isinstance(value, str):
                if "Ort:" in str(value):
                    location_match = re.search(r'Ort:\s*(.+)', str(value))
                    if location_match:
                        team_info['location'] = location_match.group(1).strip()
                if "Spieltag:" in str(value):
                    week_match = re.search(r'Spieltag:\s*(\d+)', str(value))
                    if week_match:
                        team_info['week'] = week_match.group(1)
        
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
        
        # Find column headers (row 6, index 5) - CORRECTED
        header_row = team_data.iloc[5]
        
        # Debug: Print all header values
        print(f"\nHeader row values:")
        for col_idx, value in header_row.items():
            if pd.notna(value):
                print(f"  Col {col_idx}: '{value}'")
        
        # Find important columns
        name_col = None
        id_col = None
        score_cols = []
        points_cols = []
        opponent_cols = []
        
        # First pass: Find Name and ID columns
        for col_idx, value in header_row.items():
            if pd.notna(value):
                value_str = str(value).lower()
                if "name" in value_str:
                    name_col = col_idx
                elif "rl" in value_str:
                    id_col = col_idx
        
        # Second pass: Find individual round columns (exclude totals)
        for col_idx, value in header_row.items():
            if pd.notna(value):
                value_str = str(value).lower()
                # Look for "Pins" columns that are not "Gesamt"
                if "pins" in value_str and "gesamt" not in value_str:
                    score_cols.append(col_idx)
                elif "pkt" in value_str and "gesamt" not in value_str:
                    points_cols.append(col_idx)
        
        # Remove the last column if it's "Gesamt" (total)
        if len(score_cols) > 9:
            score_cols = score_cols[:9]  # Take only first 9
        if len(points_cols) > 9:
            points_cols = points_cols[:9]  # Take only first 9
        
        # Find opponent columns - they should be in the same pattern as score columns
        # Row 23 (index 22) contains opponent names for each round
        opponent_row = team_data.iloc[22]
        print(f"\nOpponent row (row 23) values:")
        for col_idx, value in opponent_row.items():
            if pd.notna(value):
                print(f"  Col {col_idx}: '{value}'")
                # Opponent columns are the same as score columns
                if col_idx in score_cols:
                    opponent_cols.append(col_idx)
        
        # Find team total scores and points
        # Row 19 (index 18) contains team totals
        team_total_row = team_data.iloc[18]
        print(f"\nTeam total row (row 19) values:")
        team_total_scores = {}
        team_total_points = {}
        
        for col_idx, value in team_total_row.items():
            if pd.notna(value):
                print(f"  Col {col_idx}: '{value}'")
                # Team total scores should be in the same columns as individual scores
                if col_idx in score_cols:
                    round_idx = score_cols.index(col_idx)
                    try:
                        team_total_scores[round_idx] = int(value)
                        # Team points are in the next column (points column)
                        points_col = points_cols[round_idx]
                        if pd.notna(team_total_row[points_col]):
                            team_total_points[round_idx] = float(team_total_row[points_col])
                        else:
                            team_total_points[round_idx] = 0.0
                    except (ValueError, TypeError):
                        print(f"    Invalid team total for round {round_idx + 1}: {value}")
        
        print(f"Found columns: Name={name_col}, ID={id_col}")
        print(f"Score columns (rounds): {score_cols}")
        print(f"Points columns (rounds): {points_cols}")
        print(f"Opponent columns (rounds): {opponent_cols}")
        print(f"Team total scores: {team_total_scores}")
        print(f"Team total points: {team_total_points}")
        
        # Verify we have 9 rounds
        if len(score_cols) != 9:
            print(f"WARNING: Expected 9 rounds, found {len(score_cols)}")
            print("This might be because we're not correctly identifying individual round columns")
        
        # Define position ranges (each position has up to 3 players)
        positions = [
            (6, 8),   # Position 1: rows 7-9 (index 6-8) - CORRECTED
            (9, 11),  # Position 2: rows 10-12 (index 9-11) - CORRECTED
            (12, 14), # Position 3: rows 13-15 (index 12-14) - CORRECTED
            (15, 17)  # Position 4: rows 16-18 (index 15-17) - CORRECTED
        ]
        
        for pos_idx, (start_row, end_row) in enumerate(positions):
            print(f"\nProcessing Position {pos_idx + 1} (rows {start_row+1}-{end_row+1})")
            
            # Get rows for this position
            pos_rows = team_data.iloc[start_row:end_row+1]
            
            for player_row_idx, row in pos_rows.iterrows():
                # Check if this row has a player name
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
                        # Check if player participated in this round
                        if pd.notna(row[score_col]):
                            try:
                                score = int(row[score_col])
                                
                                # Find points - check all 3 rows of this position for merged cell
                                points = ""
                                for check_row_idx in range(start_row, end_row + 1):
                                    check_row = team_data.iloc[check_row_idx]
                                    if pd.notna(check_row[points_col]):
                                        points = str(check_row[points_col])
                                        break
                                
                                # Find opponent for this specific round
                                opponent = "Unknown"
                                if round_idx < len(opponent_cols):
                                    opponent_col = opponent_cols[round_idx]
                                    if pd.notna(opponent_row[opponent_col]):
                                        opponent = str(opponent_row[opponent_col]).strip()
                                
                                # Create CSV row
                                csv_row = {
                                    'Season': season,
                                    'Week': team_info['week'],
                                    'Date': date,
                                    'League': league,
                                    'Players per Team': players_per_team,
                                    'Location': team_info['location'],
                                    'Round Number': round_idx + 1,  # Spiel 1-9
                                    'Match Number': pos_idx + 1,    # Position 1-4
                                    'Team': team_info['team_name'],
                                    'Position': pos_idx,
                                    'Player': player_name,
                                    'Player ID': player_id,
                                    'Opponent': opponent,
                                    'Score': score,
                                    'Points': points,
                                    'Input Data': 'True',
                                    'Computed Data': 'False'
                                }
                                
                                players.append(csv_row)
                                print(f"    Round {round_idx + 1}: Score={score}, Points={points}, Opponent={opponent}")
                                
                            except (ValueError, TypeError):
                                print(f"    Round {round_idx + 1}: Invalid score data")
        
        # Add team total rows for each round
        for round_idx in range(9):
            if round_idx in team_total_scores:
                # Find opponent for this round
                opponent = "Unknown"
                if round_idx < len(opponent_cols):
                    opponent_col = opponent_cols[round_idx]
                    if pd.notna(opponent_row[opponent_col]):
                        opponent = str(opponent_row[opponent_col]).strip()
                
                # Create team total CSV row
                csv_row = {
                    'Season': season,
                    'Week': team_info['week'],
                    'Date': date,
                    'League': league,
                    'Players per Team': players_per_team,
                    'Location': team_info['location'],
                    'Round Number': round_idx + 1,  # Spiel 1-9
                    'Match Number': 0,               # 0 for team total
                    'Team': team_info['team_name'],
                    'Position': 0,                   # 0 for team total
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
    
    # Parse the data
    print("\nParsing teams...")
    mapped_data = parse_teams(df)
    
    if mapped_data:
        # Create DataFrame and save to CSV
        result_df = pd.DataFrame(mapped_data)
        result_df.to_csv('database/data/bowling_ergebnisse_real.csv', index=False, sep=';')
        print(f"\nExtracted {len(mapped_data)} rows to database/data/bowling_ergebnisse_real.csv")
        print("\nSample extracted data:")
        print(result_df.head(10))
        
        # Show summary statistics
        print(f"\nSummary:")
        print(f"Teams found: {result_df['Team'].nunique()}")
        print(f"Players found: {result_df['Player'].nunique()}")
        print(f"Total matches: {len(result_df)}")
        print(f"Score range: {result_df['Score'].min()} - {result_df['Score'].max()}")
        
        # Verify we have 9 rounds per position
        rounds_per_position = result_df.groupby(['Team', 'Position'])['Round Number'].nunique()
        print(f"\nRounds per position:")
        print(rounds_per_position.value_counts())
        
    else:
        print("No data could be extracted.")
    
    return mapped_data

if __name__ == "__main__":
    print("Starting Excel data extraction...")
    extracted_data = extract_excel_data()
    print("Extraction complete!") 