"""
ClubPlayer CSV Mapper

Converts between ClubPlayer domain entity and Pandas DataFrame rows.
"""

import pandas as pd
from uuid import UUID
from datetime import datetime, date
from typing import Optional
from domain.entities.club_player import ClubPlayer


class PandasClubPlayerMapper:
    """
    Mapper for ClubPlayer entity ↔ Pandas DataFrame.
    
    Handles bidirectional conversion between domain entities and CSV storage.
    """
    
    @staticmethod
    def to_domain(row: pd.Series) -> ClubPlayer:
        """
        Convert DataFrame row to ClubPlayer entity.
        
        Args:
            row: Pandas Series representing a row from club_player.csv
        
        Returns:
            ClubPlayer domain entity
        """
        # Handle UUID conversion
        club_player_id_str = str(row['id'])
        try:
            club_player_id = UUID(club_player_id_str)
        except (ValueError, AttributeError):
            from uuid import uuid4
            club_player_id = uuid4()
        
        # Handle club_id - required UUID
        club_id_str = str(row['club_id'])
        try:
            club_id = UUID(club_id_str)
        except (ValueError, AttributeError):
            raise ValueError(f"Invalid club_id UUID: {club_id_str}")
        
        # Handle player_id - required UUID
        player_id_str = str(row['player_id'])
        try:
            player_id = UUID(player_id_str)
        except (ValueError, AttributeError):
            raise ValueError(f"Invalid player_id UUID: {player_id_str}")
        
        # Handle date_entry - optional date
        date_entry = None
        if pd.notna(row.get('date_entry')):
            date_entry_str = str(row['date_entry'])
            try:
                date_entry = pd.to_datetime(date_entry_str).date()
            except (ValueError, TypeError):
                date_entry = None
        
        # Handle date_exit - optional date
        date_exit = None
        if pd.notna(row.get('date_exit')):
            date_exit_str = str(row['date_exit'])
            try:
                date_exit = pd.to_datetime(date_exit_str).date()
            except (ValueError, TypeError):
                date_exit = None
        
        return ClubPlayer(
            id=club_player_id,
            club_id=club_id,
            player_id=player_id,
            date_entry=date_entry,
            date_exit=date_exit
        )
    
    @staticmethod
    def to_dataframe(club_player: ClubPlayer) -> pd.Series:
        """
        Convert ClubPlayer entity to DataFrame row.
        
        Args:
            club_player: ClubPlayer domain entity
        
        Returns:
            Pandas Series representing a row for club_player.csv
        """
        return pd.Series({
            'id': str(club_player.id),
            'club_id': str(club_player.club_id),
            'player_id': str(club_player.player_id),
            'date_entry': club_player.date_entry.isoformat() if club_player.date_entry else None,
            'date_exit': club_player.date_exit.isoformat() if club_player.date_exit else None
        })

