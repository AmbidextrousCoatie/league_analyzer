"""
Player CSV Mapper

Converts between Player domain entity and Pandas DataFrame rows.
"""

import pandas as pd
from uuid import UUID
from typing import Optional
from domain.entities.player import Player


class PandasPlayerMapper:
    """
    Mapper for Player entity ↔ Pandas DataFrame.
    
    Handles bidirectional conversion between domain entities and CSV storage.
    """
    
    @staticmethod
    def to_domain(row: pd.Series) -> Player:
        """
        Convert DataFrame row to Player entity.
        
        Args:
            row: Pandas Series representing a row from player.csv
        
        Returns:
            Player domain entity
        """
        # Handle UUID conversion
        player_id = UUID(row['id']) if isinstance(row['id'], str) and len(row['id']) > 10 else row['id']
        
        # Handle optional club_id
        club_id = None
        if pd.notna(row.get('club_id')):
            club_id_str = str(row['club_id'])
            try:
                club_id = UUID(club_id_str) if len(club_id_str) > 10 else None
            except (ValueError, AttributeError):
                club_id = None
        
        # Build name from CSV fields (given_name, family_name, full_name)
        full_name = row.get('full_name', '')
        if not full_name and (row.get('given_name') or row.get('family_name')):
            given = row.get('given_name', '')
            family = row.get('family_name', '')
            full_name = f"{given} {family}".strip()
        
        return Player(
            id=player_id,
            name=full_name or 'Unknown',
            club_id=club_id
        )
    
    @staticmethod
    def to_dataframe(player: Player) -> pd.Series:
        """
        Convert Player entity to DataFrame row.
        
        Args:
            player: Player domain entity
        
        Returns:
            Pandas Series representing a row for player.csv
        """
        # Split name into components for CSV (simplified)
        name_parts = player.name.split(' ', 1) if player.name else ['', '']
        given_name = name_parts[0] if len(name_parts) > 0 else ''
        family_name = name_parts[1] if len(name_parts) > 1 else ''
        
        return pd.Series({
            'id': str(player.id),
            'given_name': given_name,
            'family_name': family_name,
            'full_name': player.name,
            'club_id': str(player.club_id) if player.club_id else None
        })

