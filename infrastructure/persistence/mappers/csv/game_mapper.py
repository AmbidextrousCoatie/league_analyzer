"""
Game CSV Mapper

Converts between Game domain entity and Pandas DataFrame rows.
"""

import pandas as pd
from uuid import UUID
from typing import Optional
from domain.entities.game import Game


class PandasGameMapper:
    """
    Mapper for Game entity ↔ Pandas DataFrame.
    
    Handles bidirectional conversion between domain entities and CSV storage.
    """
    
    @staticmethod
    def to_domain(row: pd.Series) -> Game:
        """
        Convert DataFrame row to Game entity.
        
        Args:
            row: Pandas Series representing a row from game.csv
        
        Returns:
            Game domain entity
        """
        # Handle UUID conversion
        game_id = UUID(row['id']) if isinstance(row['id'], str) and len(row['id']) > 10 else row['id']
        event_id = UUID(row['event_id']) if pd.notna(row.get('event_id')) and isinstance(row['event_id'], str) and len(str(row['event_id'])) > 10 else (row.get('event_id') if pd.notna(row.get('event_id')) else None)
        
        # Handle team IDs - CSV may have team_season_id, but Game entity uses team_id/opponent_team_id
        # For now, use team_season_id as team_id (simplified mapping)
        team_id = UUID(row['team_season_id']) if pd.notna(row.get('team_season_id')) and isinstance(row['team_season_id'], str) and len(str(row['team_season_id'])) > 10 else (UUID(row['team_season_id']) if pd.notna(row.get('team_season_id')) else None)
        opponent_team_id = None  # CSV doesn't have opponent_team_id directly
        
        # Handle optional fields
        match_number = int(row['match_number']) if pd.notna(row.get('match_number')) else 1
        round_number = int(row['round_number']) if pd.notna(row.get('round_number')) else 1
        
        return Game(
            id=game_id,
            event_id=event_id,
            team_id=team_id,
            opponent_team_id=opponent_team_id,
            match_number=match_number,
            round_number=round_number
        )
    
    @staticmethod
    def to_dataframe(game: Game) -> pd.Series:
        """
        Convert Game entity to DataFrame row.
        
        Args:
            game: Game domain entity
        
        Returns:
            Pandas Series representing a row for game.csv
        """
        return pd.Series({
            'id': str(game.id),
            'event_id': str(game.event_id) if game.event_id else None,
            'team_season_id': str(game.team_id) if game.team_id else None,  # Map team_id to team_season_id for CSV
            'match_number': game.match_number,
            'round_number': game.round_number
        })

