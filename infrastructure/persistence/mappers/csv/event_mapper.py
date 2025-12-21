"""
Event CSV Mapper

Converts between Event domain entity and Pandas DataFrame rows.
"""

import pandas as pd
from uuid import UUID
from datetime import datetime
from typing import Optional
from domain.entities.event import Event
from domain.value_objects.event_status import EventStatus


class PandasEventMapper:
    """
    Mapper for Event entity ↔ Pandas DataFrame.
    
    Handles bidirectional conversion between domain entities and CSV storage.
    """
    
    @staticmethod
    def to_domain(row: pd.Series) -> Event:
        """
        Convert DataFrame row to Event entity.
        
        Args:
            row: Pandas Series representing a row from event.csv
        
        Returns:
            Event domain entity
        """
        # Handle UUID conversion
        event_id = UUID(row['id']) if isinstance(row['id'], str) else row['id']
        league_season_id = UUID(row['league_season_id']) if isinstance(row['league_season_id'], str) else row['league_season_id']
        
        # Handle date conversion
        if isinstance(row['date'], str):
            date = pd.to_datetime(row['date']).to_pydatetime()
        else:
            date = row['date'] if isinstance(row['date'], datetime) else pd.to_datetime(row['date']).to_pydatetime()
        
        # Handle optional fields
        league_week = int(row['league_week']) if pd.notna(row.get('league_week')) else None
        tournament_stage = row.get('tournament_stage') if pd.notna(row.get('tournament_stage')) else None
        venue_id = row.get('venue_id') if pd.notna(row.get('venue_id')) else None
        oil_pattern_id = int(row['oil_pattern_id']) if pd.notna(row.get('oil_pattern_id')) else None
        disqualification_reason = row.get('disqualification_reason') if pd.notna(row.get('disqualification_reason')) else None
        notes = row.get('notes') if pd.notna(row.get('notes')) else None
        
        # Handle status - default to SCHEDULED if not present
        status_str = row.get('status', 'scheduled')
        if pd.isna(status_str):
            status_str = 'scheduled'
        try:
            status = EventStatus(status_str)
        except ValueError:
            # Default to SCHEDULED if invalid status
            status = EventStatus.SCHEDULED
        
        return Event(
            id=event_id,
            league_season_id=league_season_id,
            event_type=row['event_type'],
            league_week=league_week,
            tournament_stage=tournament_stage,
            date=date,
            venue_id=venue_id,
            oil_pattern_id=oil_pattern_id,
            status=status,
            disqualification_reason=disqualification_reason,
            notes=notes
        )
    
    @staticmethod
    def to_dataframe(event: Event) -> pd.Series:
        """
        Convert Event entity to DataFrame row.
        
        Args:
            event: Event domain entity
        
        Returns:
            Pandas Series representing a row for event.csv
        """
        return pd.Series({
            'id': str(event.id),
            'league_season_id': str(event.league_season_id),
            'event_type': event.event_type,
            'league_week': event.league_week,
            'tournament_stage': event.tournament_stage,
            'date': event.date.isoformat() if isinstance(event.date, datetime) else str(event.date),
            'venue_id': event.venue_id,
            'oil_pattern_id': event.oil_pattern_id,
            'status': event.status.value,
            'disqualification_reason': event.disqualification_reason,
            'notes': event.notes
        })

