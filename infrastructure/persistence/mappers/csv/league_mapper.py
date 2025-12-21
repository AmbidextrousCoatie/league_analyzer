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
        # Handle UUID conversion - CSV may have string IDs
        # CSV has 'id' as string like "BayL", need to handle both UUID and string IDs
        league_id_str = str(row['id'])
        abbreviation = league_id_str  # CSV 'id' column contains the abbreviation
        
        try:
            league_id = UUID(league_id_str) if len(league_id_str) > 10 else None
            if league_id is None:
                # Generate deterministic UUID from string ID (abbreviation)
                import hashlib
                namespace = UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
                league_id = UUID(namespace.hex[:12] + hashlib.md5(league_id_str.encode()).hexdigest()[:20])
        except (ValueError, AttributeError):
            import hashlib
            namespace = UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
            league_id = UUID(namespace.hex[:12] + hashlib.md5(league_id_str.encode()).hexdigest()[:20])
        
        # CSV has 'long_name', map to 'name'
        name = row.get('long_name', row.get('name', ''))
        
        # Always derive level from abbreviation to ensure correctness
        # (CSV may have incorrect level values, so we override with correct mapping)
        from domain.entities.league import get_league_level, LEAGUE_LEVELS
        if abbreviation in LEAGUE_LEVELS:
            # Known abbreviation - use correct level from mapping
            level = get_league_level(abbreviation)
        else:
            # Unknown abbreviation - fall back to CSV level if available
            csv_level = row.get('level', None)
            if csv_level is not None and not pd.isna(csv_level):
                level = int(csv_level)
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
            'id': league.abbreviation if league.abbreviation else str(league.id),  # Use abbreviation as CSV id
            'long_name': league.name,  # Map name to long_name for CSV
            'name': league.name,  # Also include name for compatibility
            'level': league.level  # Include level
        })

