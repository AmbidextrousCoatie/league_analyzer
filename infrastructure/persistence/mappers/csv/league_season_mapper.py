"""
LeagueSeason CSV Mapper

Converts between LeagueSeason domain entity and Pandas DataFrame rows.
"""

import pandas as pd
from uuid import UUID
from typing import Optional
from domain.entities.league_season import LeagueSeason
from domain.value_objects.season import Season


class PandasLeagueSeasonMapper:
    """
    Mapper for LeagueSeason entity ↔ Pandas DataFrame.
    
    Handles bidirectional conversion between domain entities and CSV storage.
    """
    
    @staticmethod
    def to_domain(row: pd.Series) -> LeagueSeason:
        """
        Convert DataFrame row to LeagueSeason entity.
        
        Args:
            row: Pandas Series representing a row from league_season.csv
        
        Returns:
            LeagueSeason domain entity
        """
        # Handle UUID conversion - CSV may have string IDs
        league_season_id = UUID(row['id']) if isinstance(row['id'], str) and len(row['id']) > 10 else row['id']
        
        # Handle league_id - may be string or UUID
        league_id_str = str(row['league_id'])
        try:
            league_id = UUID(league_id_str)
        except (ValueError, AttributeError):
            # If not a valid UUID, treat as string (will need mapping later)
            # For now, generate a deterministic UUID from string
            import hashlib
            namespace = UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # DNS namespace
            league_id = UUID(namespace.hex[:12] + hashlib.md5(league_id_str.encode()).hexdigest()[:20])
        
        # Handle season
        season_str = str(row['season'])
        season = Season(season_str)
        
        # Handle optional fields
        number_of_teams = int(row['number_of_teams']) if pd.notna(row.get('number_of_teams')) else None
        players_per_team = int(row['players_per_team']) if pd.notna(row.get('players_per_team')) else None
        
        return LeagueSeason(
            id=league_season_id,
            league_id=league_id,
            season=season,
            scoring_system_id=row['scoring_system_id'],
            number_of_teams=number_of_teams,
            players_per_team=players_per_team
        )
    
    @staticmethod
    def to_dataframe(league_season: LeagueSeason) -> pd.Series:
        """
        Convert LeagueSeason entity to DataFrame row.
        
        Args:
            league_season: LeagueSeason domain entity
        
        Returns:
            Pandas Series representing a row for league_season.csv
        """
        return pd.Series({
            'id': str(league_season.id),
            'league_id': str(league_season.league_id),
            'season': str(league_season.season),
            'scoring_system_id': league_season.scoring_system_id,
            'number_of_teams': league_season.number_of_teams,
            'players_per_team': league_season.players_per_team
        })

