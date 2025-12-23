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
        from uuid import uuid4
        
        # Handle ID conversion - similar to player mapper
        # Legacy CSV files have numeric DBU IDs in the 'id' column
        # New format has UUIDs in 'id' and DBU IDs in 'dbu_id'
        raw_id = row.get('id')
        dbu_id = None
        
        # Check if dbu_id column exists (new format)
        if pd.notna(row.get('dbu_id')):
            # New format: id is UUID, dbu_id contains legacy ID
            dbu_id = str(row.get('dbu_id')).strip()
            try:
                event_id = UUID(str(raw_id))
            except (ValueError, AttributeError, TypeError):
                # Fallback: generate new UUID if id is invalid
                event_id = uuid4()
        else:
            # Legacy format: id column contains DBU ID (numeric string)
            raw_id_str = str(raw_id).strip() if pd.notna(raw_id) else ''
            is_legacy_id = raw_id_str.isdigit() or (len(raw_id_str) < 10 and raw_id_str and not '-' in raw_id_str)
            
            if is_legacy_id:
                # Legacy ID found - store in dbu_id and generate new UUID
                dbu_id = raw_id_str
                event_id = uuid4()
            else:
                # Try to parse as UUID (might be already migrated)
                try:
                    event_id = UUID(raw_id_str) if len(raw_id_str) > 10 else uuid4()
                except (ValueError, AttributeError, TypeError):
                    # Generate new UUID if parsing fails
                    event_id = uuid4()
        
        # Handle league_season_id - also needs UUID conversion with legacy handling
        raw_league_season_id = row.get('league_season_id')
        if pd.notna(raw_league_season_id):
            raw_ls_id_str = str(raw_league_season_id).strip()
            try:
                league_season_id = UUID(raw_ls_id_str) if len(raw_ls_id_str) > 10 else None
            except (ValueError, AttributeError, TypeError):
                league_season_id = None
        else:
            league_season_id = None
        
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
            dbu_id=dbu_id,
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
            'id': str(event.id),  # UUID
            'dbu_id': event.dbu_id,  # Legacy DBU ID (if exists)
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

