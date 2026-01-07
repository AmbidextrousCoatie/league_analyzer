"""
Position Comparison CSV Mapper

Converts between PositionComparison domain entity and Pandas DataFrame rows.
"""

import pandas as pd
from uuid import UUID, uuid4
from datetime import datetime
from domain.entities.position_comparison import PositionComparison, ComparisonOutcome


class PandasPositionComparisonMapper:
    """
    Mapper for PositionComparison entity ↔ Pandas DataFrame.
    
    Handles bidirectional conversion between domain entities and CSV storage.
    """
    
    @staticmethod
    def to_domain(row: pd.Series) -> PositionComparison:
        """
        Convert DataFrame row to PositionComparison entity.
        
        Args:
            row: Pandas Series representing a row from position_comparison.csv
        
        Returns:
            PositionComparison domain entity
        """
        # Handle ID conversion
        raw_id = row.get('id')
        try:
            comparison_id = UUID(str(raw_id)) if pd.notna(raw_id) else uuid4()
        except (ValueError, AttributeError, TypeError):
            comparison_id = uuid4()
        
        # Handle UUID fields
        match_id = None
        if pd.notna(row.get('match_id')):
            try:
                match_id = UUID(str(row['match_id']))
            except (ValueError, AttributeError, TypeError):
                match_id = None
        
        team1_player_id = None
        if pd.notna(row.get('team1_player_id')):
            try:
                team1_player_id = UUID(str(row['team1_player_id']))
            except (ValueError, AttributeError, TypeError):
                team1_player_id = None
        
        team2_player_id = None
        if pd.notna(row.get('team2_player_id')):
            try:
                team2_player_id = UUID(str(row['team2_player_id']))
            except (ValueError, AttributeError, TypeError):
                team2_player_id = None
        
        # Handle numeric fields
        position = int(row['position']) if pd.notna(row.get('position')) else 0
        team1_score = float(row['team1_score']) if pd.notna(row.get('team1_score')) else 0.0
        team2_score = float(row['team2_score']) if pd.notna(row.get('team2_score')) else 0.0
        
        # Handle outcome enum
        outcome_str = row.get('outcome', 'tie')
        if pd.isna(outcome_str):
            outcome_str = 'tie'
        try:
            outcome = ComparisonOutcome(outcome_str)
        except ValueError:
            outcome = ComparisonOutcome.TIE
        
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
        
        return PositionComparison(
            id=comparison_id,
            match_id=match_id,
            position=position,
            team1_player_id=team1_player_id,
            team2_player_id=team2_player_id,
            team1_score=team1_score,
            team2_score=team2_score,
            outcome=outcome,
            created_at=created_at,
            updated_at=updated_at
        )
    
    @staticmethod
    def to_dataframe(comparison: PositionComparison) -> pd.Series:
        """
        Convert PositionComparison entity to DataFrame row.
        
        Args:
            comparison: PositionComparison domain entity
        
        Returns:
            Pandas Series representing a row for position_comparison.csv
        """
        return pd.Series({
            'id': str(comparison.id),
            'match_id': str(comparison.match_id) if comparison.match_id else '',
            'position': comparison.position,
            'team1_player_id': str(comparison.team1_player_id) if comparison.team1_player_id else '',
            'team2_player_id': str(comparison.team2_player_id) if comparison.team2_player_id else '',
            'team1_score': int(comparison.team1_score),
            'team2_score': int(comparison.team2_score),
            'outcome': comparison.outcome.value,
            'created_at': comparison.created_at.isoformat() if isinstance(comparison.created_at, datetime) else str(comparison.created_at),
            'updated_at': comparison.updated_at.isoformat() if isinstance(comparison.updated_at, datetime) else str(comparison.updated_at)
        })

