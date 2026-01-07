"""
Match Scoring CSV Mapper

Converts between MatchScoring domain entity and Pandas DataFrame rows.
"""

import pandas as pd
from uuid import UUID, uuid4
from datetime import datetime
from domain.entities.match_scoring import MatchScoring


class PandasMatchScoringMapper:
    """
    Mapper for MatchScoring entity ↔ Pandas DataFrame.
    
    Handles bidirectional conversion between domain entities and CSV storage.
    """
    
    @staticmethod
    def to_domain(row: pd.Series) -> MatchScoring:
        """
        Convert DataFrame row to MatchScoring entity.
        
        Args:
            row: Pandas Series representing a row from match_scoring.csv
        
        Returns:
            MatchScoring domain entity
        """
        # Handle ID conversion
        raw_id = row.get('id')
        try:
            scoring_id = UUID(str(raw_id)) if pd.notna(raw_id) else uuid4()
        except (ValueError, AttributeError, TypeError):
            scoring_id = uuid4()
        
        # Handle UUID fields
        match_id = None
        if pd.notna(row.get('match_id')):
            try:
                match_id = UUID(str(row['match_id']))
            except (ValueError, AttributeError, TypeError):
                match_id = None
        
        # Handle scoring_system_id (can be UUID string or string ID)
        scoring_system_id = str(row['scoring_system_id']).strip() if pd.notna(row.get('scoring_system_id')) else ''
        
        # Handle numeric fields
        team1_individual_points = float(row['team1_individual_points']) if pd.notna(row.get('team1_individual_points')) else 0.0
        team2_individual_points = float(row['team2_individual_points']) if pd.notna(row.get('team2_individual_points')) else 0.0
        team1_match_points = float(row['team1_match_points']) if pd.notna(row.get('team1_match_points')) else 0.0
        team2_match_points = float(row['team2_match_points']) if pd.notna(row.get('team2_match_points')) else 0.0
        
        # Handle datetime fields
        computed_at = datetime.utcnow()
        if pd.notna(row.get('computed_at')):
            try:
                if isinstance(row['computed_at'], str):
                    computed_at = pd.to_datetime(row['computed_at']).to_pydatetime()
                else:
                    computed_at = row['computed_at'] if isinstance(row['computed_at'], datetime) else pd.to_datetime(row['computed_at']).to_pydatetime()
            except (ValueError, TypeError):
                computed_at = datetime.utcnow()
        
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
        
        return MatchScoring(
            id=scoring_id,
            match_id=match_id,
            scoring_system_id=scoring_system_id,
            team1_individual_points=team1_individual_points,
            team2_individual_points=team2_individual_points,
            team1_match_points=team1_match_points,
            team2_match_points=team2_match_points,
            computed_at=computed_at,
            created_at=created_at,
            updated_at=updated_at
        )
    
    @staticmethod
    def to_dataframe(scoring: MatchScoring) -> pd.Series:
        """
        Convert MatchScoring entity to DataFrame row.
        
        Args:
            scoring: MatchScoring domain entity
        
        Returns:
            Pandas Series representing a row for match_scoring.csv
        """
        return pd.Series({
            'id': str(scoring.id),
            'match_id': str(scoring.match_id) if scoring.match_id else '',
            'scoring_system_id': str(scoring.scoring_system_id),
            'team1_individual_points': scoring.team1_individual_points,
            'team2_individual_points': scoring.team2_individual_points,
            'team1_match_points': scoring.team1_match_points,
            'team2_match_points': scoring.team2_match_points,
            'computed_at': scoring.computed_at.isoformat() if isinstance(scoring.computed_at, datetime) else str(scoring.computed_at),
            'created_at': scoring.created_at.isoformat() if isinstance(scoring.created_at, datetime) else str(scoring.created_at),
            'updated_at': scoring.updated_at.isoformat() if isinstance(scoring.updated_at, datetime) else str(scoring.updated_at)
        })

