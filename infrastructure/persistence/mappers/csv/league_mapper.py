"""
League CSV Mapper

Converts between League domain entity and Pandas DataFrame rows.
"""

import pandas as pd
from uuid import UUID
from domain.entities.league import League


class PandasLeagueMapper:
    """
    Mapper for League entity ↔ Pandas DataFrame.
    
    Handles bidirectional conversion between domain entities and CSV storage.
    """
    
    @staticmethod
    def to_domain(row: pd.Series) -> League:
        """
        Convert DataFrame row to League entity.
        
        Args:
            row: Pandas Series representing a row from league.csv
        
        Returns:
            League domain entity
        """
        # Handle UUID conversion - CSV should have UUID in 'id' column
        league_id_str = str(row['id'])
        
        try:
            league_id = UUID(league_id_str)
        except (ValueError, AttributeError):
            # Legacy data: if id is not a UUID (e.g., abbreviation), generate UUID
            # This handles migration from old format
            import hashlib
            namespace = UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
            league_id = UUID(namespace.hex[:12] + hashlib.md5(league_id_str.encode()).hexdigest()[:20])
        
        # Get name (full name)
        name = str(row.get('name', '')).strip()
        if not name:
            # Fallback to long_name for legacy data
            name = str(row.get('long_name', '')).strip()
        
        # Get abbreviation (short name)
        abbreviation = str(row.get('abbreviation', '')).strip()
        if not abbreviation:
            # Legacy data: if abbreviation not found, try using id (if it's not a UUID)
            if len(league_id_str) <= 10:
                abbreviation = league_id_str
        
        # Get level
        csv_level = row.get('level', None)
        if csv_level is not None and not pd.isna(csv_level):
            level = int(csv_level)
        else:
            # Derive level from abbreviation if available
            from domain.entities.league import get_league_level
            if abbreviation:
                level = get_league_level(abbreviation)
            else:
                level = 7  # Default to lowest level
        
        return League(
            id=league_id,
            name=name,
            abbreviation=abbreviation,
            level=level
        )
    
    @staticmethod
    def to_dataframe(league: League) -> pd.Series:
        """
        Convert League entity to DataFrame row.
        
        Args:
            league: League domain entity
        
        Returns:
            Pandas Series representing a row for league.csv
        """
        return pd.Series({
            'id': str(league.id),  # UUID as id
            'name': league.name,  # Full name
            'abbreviation': league.abbreviation if league.abbreviation else '',  # Abbreviation (short name)
            'level': league.level  # Level
        })

