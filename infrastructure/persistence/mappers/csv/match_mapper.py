"""
Match CSV Mapper

Converts between Match domain entity and Pandas DataFrame rows.
"""

import pandas as pd
from uuid import UUID, uuid4
from datetime import datetime
from domain.entities.match import Match, MatchStatus


class PandasMatchMapper:
    """
    Mapper for Match entity ↔ Pandas DataFrame.
    
    Handles bidirectional conversion between domain entities and CSV storage.
    """
    
    @staticmethod
    def to_domain(row: pd.Series) -> Match:
        """
        Convert DataFrame row to Match entity.
        
        Args:
            row: Pandas Series representing a row from match.csv
        
        Returns:
            Match domain entity
        """
        # Handle ID conversion
        raw_id = row.get('id')
        try:
            match_id = UUID(str(raw_id)) if pd.notna(raw_id) else uuid4()
        except (ValueError, AttributeError, TypeError):
            match_id = uuid4()
        
        # Handle UUID fields
        event_id = None
        if pd.notna(row.get('event_id')):
            try:
                event_id = UUID(str(row['event_id']))
            except (ValueError, AttributeError, TypeError):
                event_id = None
        
        team1_team_season_id = None
        if pd.notna(row.get('team1_team_season_id')):
            try:
                team1_team_season_id = UUID(str(row['team1_team_season_id']))
            except (ValueError, AttributeError, TypeError):
                team1_team_season_id = None
        
        team2_team_season_id = None
        if pd.notna(row.get('team2_team_season_id')):
            try:
                team2_team_season_id = UUID(str(row['team2_team_season_id']))
            except (ValueError, AttributeError, TypeError):
                team2_team_season_id = None
        
        # Handle numeric fields
        round_number = int(row['round_number']) if pd.notna(row.get('round_number')) else 1
        match_number = int(row['match_number']) if pd.notna(row.get('match_number')) else 0
        team1_total_score = float(row['team1_total_score']) if pd.notna(row.get('team1_total_score')) else 0.0
        team2_total_score = float(row['team2_total_score']) if pd.notna(row.get('team2_total_score')) else 0.0
        
        # Handle status
        status_str = row.get('status', 'scheduled')
        if pd.isna(status_str):
            status_str = 'scheduled'
        try:
            status = MatchStatus(status_str)
        except ValueError:
            status = MatchStatus.SCHEDULED
        
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
        
        return Match(
            id=match_id,
            event_id=event_id,
            round_number=round_number,
            match_number=match_number,
            team1_team_season_id=team1_team_season_id,
            team2_team_season_id=team2_team_season_id,
            team1_total_score=team1_total_score,
            team2_total_score=team2_total_score,
            status=status,
            created_at=created_at,
            updated_at=updated_at
        )
    
    @staticmethod
    def to_dataframe(match: Match) -> pd.Series:
        """
        Convert Match entity to DataFrame row.
        
        Args:
            match: Match domain entity
        
        Returns:
            Pandas Series representing a row for match.csv
        """
        return pd.Series({
            'id': str(match.id),
            'event_id': str(match.event_id) if match.event_id else '',
            'round_number': match.round_number,
            'match_number': match.match_number,
            'team1_team_season_id': str(match.team1_team_season_id) if match.team1_team_season_id else '',
            'team2_team_season_id': str(match.team2_team_season_id) if match.team2_team_season_id else '',
            'team1_total_score': int(match.team1_total_score),
            'team2_total_score': int(match.team2_total_score),
            'status': match.status.value,
            'created_at': match.created_at.isoformat() if isinstance(match.created_at, datetime) else str(match.created_at),
            'updated_at': match.updated_at.isoformat() if isinstance(match.updated_at, datetime) else str(match.updated_at)
        })

