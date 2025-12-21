"""
Team CSV Mapper

Converts between Team domain entity and Pandas DataFrame rows.
"""

import pandas as pd
from uuid import UUID
from typing import Optional
from domain.entities.team import Team


class PandasTeamMapper:
    """
    Mapper for Team entity ↔ Pandas DataFrame.
    
    Handles bidirectional conversion between domain entities and CSV storage.
    """
    
    @staticmethod
    def to_domain(row: pd.Series) -> Team:
        """
        Convert DataFrame row to Team entity.
        
        Args:
            row: Pandas Series representing a row from team.csv
        
        Returns:
            Team domain entity
        """
        # Handle UUID conversion
        team_id = UUID(row['id']) if isinstance(row['id'], str) and len(row['id']) > 10 else row['id']
        club_id = UUID(row['club_id']) if pd.notna(row.get('club_id')) and isinstance(row['club_id'], str) and len(str(row['club_id'])) > 10 else (row.get('club_id') if pd.notna(row.get('club_id')) else None)
        
        # Handle optional fields
        team_number = int(row['team_number']) if pd.notna(row.get('team_number')) else 1
        name = row.get('name', '')
        if not name and team_number:
            name = f"Team {team_number}"
        if not name:
            name = "Team"
        
        # Handle league_id - CSV may not have it, but Team entity needs it
        league_id = None
        if pd.notna(row.get('league_id')):
            league_id_str = str(row['league_id'])
            try:
                league_id = UUID(league_id_str) if len(league_id_str) > 10 else None
            except (ValueError, AttributeError):
                league_id = None
        
        # Team entity has: id, name, league_id
        team = Team(
            id=team_id,
            name=name
        )
        if league_id:
            team.league_id = league_id
        
        return team
    
    @staticmethod
    def to_dataframe(team: Team) -> pd.Series:
        """
        Convert Team entity to DataFrame row.
        
        Args:
            team: Team domain entity
        
        Returns:
            Pandas Series representing a row for team.csv
        """
        # Team entity has: id, name, league_id
        # CSV has: id, club_id, team_number, name, league_id
        return pd.Series({
            'id': str(team.id),
            'club_id': None,  # Would need to be set separately
            'team_number': 1,  # Default
            'name': team.name,
            'league_id': str(team.league_id) if team.league_id else None
        })

