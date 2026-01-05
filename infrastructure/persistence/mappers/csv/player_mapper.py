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
        from uuid import uuid4
        
        # Handle ID conversion
        # Legacy CSV files have numeric DBU IDs in the 'id' column (e.g., 16896, 7724)
        # New format has UUIDs in 'id' and DBU IDs in 'dbu_id'
        raw_id = row.get('id')
        dbu_id = None
        
        # Check if dbu_id column exists (new format)
        if pd.notna(row.get('dbu_id')):
            # New format: id is UUID, dbu_id contains legacy ID
            dbu_id = str(row.get('dbu_id')).strip()
            try:
                player_id = UUID(str(raw_id))
            except (ValueError, AttributeError, TypeError):
                # Fallback: generate new UUID if id is invalid
                player_id = uuid4()
        else:
            # Legacy format: id column contains DBU ID (numeric string)
            # Check if it's a numeric string (legacy DBU ID)
            raw_id_str = str(raw_id).strip() if pd.notna(raw_id) else ''
            is_legacy_id = raw_id_str.isdigit() or (len(raw_id_str) < 10 and raw_id_str and not '-' in raw_id_str)
            
            if is_legacy_id:
                # Legacy ID found - store in dbu_id and generate new UUID
                dbu_id = raw_id_str
                player_id = uuid4()
            else:
                # Try to parse as UUID (might be already migrated)
                try:
                    player_id = UUID(raw_id_str) if len(raw_id_str) > 10 else uuid4()
                except (ValueError, AttributeError, TypeError):
                    # Generate new UUID if parsing fails
                    player_id = uuid4()
        
        # Build name from CSV fields (given_name, family_name, full_name)
        full_name = row.get('full_name', '')
        if not full_name and (row.get('given_name') or row.get('family_name')):
            given = row.get('given_name', '')
            family = row.get('family_name', '')
            full_name = f"{given} {family}".strip()
        
        return Player(
            id=player_id,
            name=full_name or 'Unknown',
            dbu_id=dbu_id
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
            'id': str(player.id),  # UUID
            'dbu_id': player.dbu_id,  # Legacy DBU ID (if exists)
            'given_name': given_name,
            'family_name': family_name,
            'full_name': player.name
        })

