"""
Club CSV Mapper

Converts between Club domain entity and Pandas DataFrame rows.
"""

import pandas as pd
from uuid import UUID
from typing import Optional
from domain.entities.club import Club


class PandasClubMapper:
    """
    Mapper for Club entity ↔ Pandas DataFrame.
    
    Handles bidirectional conversion between domain entities and CSV storage.
    """
    
    @staticmethod
    def to_domain(row: pd.Series) -> Club:
        """
        Convert DataFrame row to Club entity.
        
        Args:
            row: Pandas Series representing a row from club.csv
        
        Returns:
            Club domain entity
        """
        # Handle UUID conversion
        club_id_str = str(row['id'])
        try:
            club_id = UUID(club_id_str) if len(club_id_str) > 10 else UUID(int(club_id_str))
        except (ValueError, AttributeError):
            from uuid import uuid4
            club_id = uuid4()
        
        # Handle name - required
        name = row.get('name', '')
        if not name or not name.strip():
            raise ValueError(f"Club {club_id} must have a name")
        
        # Handle optional fields
        short_name = row.get('short_name', None)
        if pd.notna(short_name):
            short_name = str(short_name).strip() if short_name else None
        
        # Handle home_alley_id - optional UUID
        home_alley_id = None
        if pd.notna(row.get('home_alley_id')):
            home_alley_str = str(row['home_alley_id'])
            try:
                home_alley_id = UUID(home_alley_str) if len(home_alley_str) > 10 else UUID(int(home_alley_str))
            except (ValueError, AttributeError):
                home_alley_id = None
        
        # Handle address - optional string
        address = row.get('address', None)
        if pd.notna(address):
            address = str(address).strip() if address else None
        
        return Club(
            id=club_id,
            name=name.strip(),
            short_name=short_name,
            home_alley_id=home_alley_id,
            address=address
        )
    
    @staticmethod
    def to_dataframe(club: Club) -> pd.Series:
        """
        Convert Club entity to DataFrame row.
        
        Args:
            club: Club domain entity
        
        Returns:
            Pandas Series representing a row for club.csv
        """
        return pd.Series({
            'id': str(club.id),
            'name': club.name,
            'short_name': club.short_name if club.short_name else None,
            'home_alley_id': str(club.home_alley_id) if club.home_alley_id else None,
            'address': club.address if club.address else None
        })

