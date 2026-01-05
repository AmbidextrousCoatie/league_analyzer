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
    Each row represents a single player's game result.
    """
    
    @staticmethod
    def to_domain(row: pd.Series) -> Optional[Game]:
        """
        Convert DataFrame row to Game entity.
        
        Args:
            row: Pandas Series representing a row from game.csv
        
        Returns:
            Game domain entity, or None if data is invalid
        """
        try:
            # Handle UUID conversion for required fields
            game_id_str = str(row['id'])
            try:
                game_id = UUID(game_id_str)
            except (ValueError, AttributeError):
                from uuid import uuid4
                game_id = uuid4()
            
            # Required: event_id
            event_id_str = str(row['event_id'])
            try:
                event_id = UUID(event_id_str)
            except (ValueError, AttributeError):
                return None  # Cannot create game without event_id
            
            # Required: player_id
            player_id_str = str(row['player_id'])
            try:
                player_id = UUID(player_id_str)
            except (ValueError, AttributeError):
                return None  # Cannot create game without player_id
            
            # Required: team_season_id
            team_season_id_str = str(row['team_season_id'])
            try:
                team_season_id = UUID(team_season_id_str)
            except (ValueError, AttributeError):
                return None  # Cannot create game without team_season_id
            
            # Required: position
            position = int(row['position']) if pd.notna(row.get('position')) else 0
            
            # Required: match_number
            match_number = int(row['match_number']) if pd.notna(row.get('match_number')) else 0
            
            # Required: round_number
            round_number = int(row['round_number']) if pd.notna(row.get('round_number')) else 1
            
            # Required: score
            score = float(row['score']) if pd.notna(row.get('score')) else 0.0
            
            # Required: points
            points = float(row['points']) if pd.notna(row.get('points')) else 0.0
            
            # Optional: opponent_id
            opponent_id = None
            if pd.notna(row.get('opponent_id')):
                try:
                    opponent_id = UUID(str(row['opponent_id']))
                except (ValueError, AttributeError):
                    opponent_id = None
            
            # Optional: opponent_team_season_id
            opponent_team_season_id = None
            if pd.notna(row.get('opponent_team_season_id')):
                try:
                    opponent_team_season_id = UUID(str(row['opponent_team_season_id']))
                except (ValueError, AttributeError):
                    opponent_team_season_id = None
            
            # Optional: handicap
            handicap = None
            if pd.notna(row.get('handicap')):
                try:
                    handicap = float(row['handicap'])
                except (ValueError, TypeError):
                    handicap = None
            
            # Optional: is_disqualified
            is_disqualified = bool(row.get('is_disqualified', False)) if pd.notna(row.get('is_disqualified')) else False
            
            return Game(
                id=game_id,
                event_id=event_id,
                player_id=player_id,
                team_season_id=team_season_id,
                position=position,
                match_number=match_number,
                round_number=round_number,
                score=score,
                points=points,
                opponent_id=opponent_id,
                opponent_team_season_id=opponent_team_season_id,
                handicap=handicap,
                is_disqualified=is_disqualified
            )
        except Exception as e:
            # Log error and return None for invalid rows
            import logging
            logging.warning(f"Failed to parse game row: {e}")
            return None
    
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
            'event_id': str(game.event_id),
            'player_id': str(game.player_id),
            'team_season_id': str(game.team_season_id),
            'position': game.position,
            'match_number': game.match_number,
            'round_number': game.round_number,
            'score': game.score,
            'points': game.points,
            'opponent_id': str(game.opponent_id) if game.opponent_id else None,
            'opponent_team_season_id': str(game.opponent_team_season_id) if game.opponent_team_season_id else None,
            'handicap': game.handicap,
            'is_disqualified': game.is_disqualified
        })
