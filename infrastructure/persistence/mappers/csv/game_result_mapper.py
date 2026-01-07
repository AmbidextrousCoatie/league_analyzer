"""
Game Result CSV Mapper

Converts between GameResult domain entity and Pandas DataFrame rows.
"""

import pandas as pd
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from domain.entities.game_result import GameResult


class PandasGameResultMapper:
    """
    Mapper for GameResult entity ↔ Pandas DataFrame.
    
    Handles bidirectional conversion between domain entities and CSV storage.
    """
    
    @staticmethod
    def to_domain(row: pd.Series) -> GameResult:
        """
        Convert DataFrame row to GameResult entity.
        
        Args:
            row: Pandas Series representing a row from game_result.csv
        
        Returns:
            GameResult domain entity
        """
        # Handle ID conversion
        raw_id = row.get('id')
        try:
            game_result_id = UUID(str(raw_id)) if pd.notna(raw_id) else uuid4()
        except (ValueError, AttributeError, TypeError):
            game_result_id = uuid4()
        
        # Handle UUID fields
        match_id = None
        if pd.notna(row.get('match_id')):
            try:
                match_id = UUID(str(row['match_id']))
            except (ValueError, AttributeError, TypeError):
                match_id = None
        
        player_id = None
        if pd.notna(row.get('player_id')):
            try:
                player_id = UUID(str(row['player_id']))
            except (ValueError, AttributeError, TypeError):
                player_id = None
        
        team_season_id = None
        if pd.notna(row.get('team_season_id')):
            try:
                team_season_id = UUID(str(row['team_season_id']))
            except (ValueError, AttributeError, TypeError):
                team_season_id = None
        
        # Handle numeric fields
        position = int(row['position']) if pd.notna(row.get('position')) else 0
        score = float(row['score']) if pd.notna(row.get('score')) else 0.0
        
        # Handle optional handicap
        handicap = None
        if pd.notna(row.get('handicap')) and str(row['handicap']).strip():
            try:
                handicap = float(row['handicap'])
            except (ValueError, TypeError):
                handicap = None
        
        # Handle boolean field
        is_disqualified = bool(row['is_disqualified']) if pd.notna(row.get('is_disqualified')) else False
        
        # Handle datetime fields
        created_at = datetime.utcnow()
        if pd.notna(row.get('created_at')):
            try:
                if isinstance(row['created_at'], str):
                    created_at = pd.to_datetime(row['created_at']).to_pydatetime()
                else:
                    created_at = row['created_at'] if isinstance(row['created_at'], datetime) else pd.to_datetime(row['created_at']).to_pydatetime()
            except (ValueError, TypeError):
                created_at = datetime.utcnow()
        
        updated_at = datetime.utcnow()
        if pd.notna(row.get('updated_at')):
            try:
                if isinstance(row['updated_at'], str):
                    updated_at = pd.to_datetime(row['updated_at']).to_pydatetime()
                else:
                    updated_at = row['updated_at'] if isinstance(row['updated_at'], datetime) else pd.to_datetime(row['updated_at']).to_pydatetime()
            except (ValueError, TypeError):
                updated_at = datetime.utcnow()
        
        return GameResult(
            id=game_result_id,
            match_id=match_id,
            player_id=player_id,
            team_season_id=team_season_id,
            position=position,
            score=score,
            handicap=handicap,
            is_disqualified=is_disqualified,
            created_at=created_at,
            updated_at=updated_at
        )
    
    @staticmethod
    def to_dataframe(game_result: GameResult) -> pd.Series:
        """
        Convert GameResult entity to DataFrame row.
        
        Args:
            game_result: GameResult domain entity
        
        Returns:
            Pandas Series representing a row for game_result.csv
        """
        return pd.Series({
            'id': str(game_result.id),
            'match_id': str(game_result.match_id) if game_result.match_id else '',
            'player_id': str(game_result.player_id) if game_result.player_id else '',
            'team_season_id': str(game_result.team_season_id) if game_result.team_season_id else '',
            'position': game_result.position,
            'score': int(game_result.score),
            'handicap': game_result.handicap if game_result.handicap is not None else '',
            'is_disqualified': game_result.is_disqualified,
            'created_at': game_result.created_at.isoformat() if isinstance(game_result.created_at, datetime) else str(game_result.created_at),
            'updated_at': game_result.updated_at.isoformat() if isinstance(game_result.updated_at, datetime) else str(game_result.updated_at)
        })

