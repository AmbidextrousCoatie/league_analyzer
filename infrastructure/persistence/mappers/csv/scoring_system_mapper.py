"""
ScoringSystem CSV Mapper

Converts between ScoringSystem domain entity and Pandas DataFrame rows.
"""

import pandas as pd
from uuid import UUID
from typing import Optional
from domain.entities.scoring_system import ScoringSystem


class PandasScoringSystemMapper:
    """
    Mapper for ScoringSystem entity ↔ Pandas DataFrame.
    
    Handles bidirectional conversion between domain entities and CSV storage.
    """
    
    @staticmethod
    def to_domain(row: pd.Series) -> ScoringSystem:
        """
        Convert DataFrame row to ScoringSystem entity.
        
        Args:
            row: Pandas Series representing a row from scoring_system.csv
        
        Returns:
            ScoringSystem domain entity
        """
        from uuid import uuid4
        
        # Handle UUID conversion - legacy CSV has string IDs (e.g., "liga_bayern_2pt")
        # Generate new UUID for id field
        raw_id = row.get('id')
        scoring_system_id = uuid4()
        
        # Try to parse as UUID if it's already a UUID string
        if pd.notna(raw_id):
            raw_id_str = str(raw_id).strip()
            try:
                if len(raw_id_str) > 10 and '-' in raw_id_str:
                    scoring_system_id = UUID(raw_id_str)
            except (ValueError, AttributeError, TypeError):
                pass  # Use generated UUID
        
        name = str(row.get('name', '')).strip()
        points_per_individual_match_win = float(row.get('points_per_individual_match_win', 1.0)) if pd.notna(row.get('points_per_individual_match_win')) else 1.0
        points_per_individual_match_tie = float(row.get('points_per_individual_match_tie', 0.5)) if pd.notna(row.get('points_per_individual_match_tie')) else 0.5
        points_per_individual_match_loss = float(row.get('points_per_individual_match_loss', 0.0)) if pd.notna(row.get('points_per_individual_match_loss')) else 0.0
        points_per_team_match_win = float(row.get('points_per_team_match_win', 2.0)) if pd.notna(row.get('points_per_team_match_win')) else 2.0
        points_per_team_match_tie = float(row.get('points_per_team_match_tie', 1.0)) if pd.notna(row.get('points_per_team_match_tie')) else 1.0
        points_per_team_match_loss = float(row.get('points_per_team_match_loss', 0.0)) if pd.notna(row.get('points_per_team_match_loss')) else 0.0
        allow_ties = bool(row.get('allow_ties', True)) if pd.notna(row.get('allow_ties')) else True
        
        return ScoringSystem(
            id=scoring_system_id,
            name=name,
            points_per_individual_match_win=points_per_individual_match_win,
            points_per_individual_match_tie=points_per_individual_match_tie,
            points_per_individual_match_loss=points_per_individual_match_loss,
            points_per_team_match_win=points_per_team_match_win,
            points_per_team_match_tie=points_per_team_match_tie,
            points_per_team_match_loss=points_per_team_match_loss,
            allow_ties=allow_ties
        )
    
    @staticmethod
    def to_dataframe(scoring_system: ScoringSystem) -> pd.Series:
        """
        Convert ScoringSystem entity to DataFrame row.
        
        Args:
            scoring_system: ScoringSystem domain entity
        
        Returns:
            Pandas Series representing a row for scoring_system.csv
        """
        return pd.Series({
            'id': str(scoring_system.id),
            'name': scoring_system.name,
            'points_per_individual_match_win': scoring_system.points_per_individual_match_win,
            'points_per_individual_match_tie': scoring_system.points_per_individual_match_tie,
            'points_per_individual_match_loss': scoring_system.points_per_individual_match_loss,
            'points_per_team_match_win': scoring_system.points_per_team_match_win,
            'points_per_team_match_tie': scoring_system.points_per_team_match_tie,
            'points_per_team_match_loss': scoring_system.points_per_team_match_loss,
            'allow_ties': scoring_system.allow_ties
        })

