"""
Pandas Event Repository

CSV-based implementation of EventRepository using Pandas DataFrames.
"""

import pandas as pd
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from domain.entities.event import Event
from domain.repositories.event_repository import EventRepository
from domain.value_objects.event_status import EventStatus
from domain.exceptions.domain_exception import EntityNotFoundError
from infrastructure.persistence.adapters.data_adapter import DataAdapter
from infrastructure.persistence.mappers.csv.event_mapper import PandasEventMapper
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class PandasEventRepository(EventRepository):
    """
    CSV-based Event repository using Pandas DataFrames.
    
    This implementation reads/writes CSV files using Pandas DataFrames.
    """
    
    def __init__(
        self,
        data_adapter: DataAdapter,
        mapper: PandasEventMapper
    ):
        """
        Initialize Pandas Event repository.
        
        Args:
            data_adapter: DataAdapter for accessing CSV files
            mapper: Mapper for converting between domain and DataFrame
        """
        self._adapter = data_adapter
        self._mapper = mapper
        logger.debug("Initialized PandasEventRepository")
    
    def _load_data(self) -> pd.DataFrame:
        """Load event data from CSV."""
        return self._adapter.get_event_data()
    
    def _save_data(self, df: pd.DataFrame) -> None:
        """Save event data to CSV."""
        self._adapter.save_event_data(df)
    
    async def get_by_id(self, event_id: UUID) -> Optional[Event]:
        """Get event by ID from CSV."""
        df = self._load_data()
        if df.empty:
            return None
        
        row = df[df['id'] == str(event_id)]
        if row.empty:
            return None
        
        return self._mapper.to_domain(row.iloc[0])
    
    async def get_all(self) -> List[Event]:
        """Get all events from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        return [self._mapper.to_domain(row) for _, row in df.iterrows()]
    
    async def get_by_league_season(
        self, 
        league_season_id: UUID
    ) -> List[Event]:
        """Get events for league season from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['league_season_id'] == str(league_season_id)]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def get_by_week(
        self,
        league_season_id: UUID,
        week: int
    ) -> List[Event]:
        """Get events for specific week from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[
            (df['league_season_id'] == str(league_season_id)) &
            (df['league_week'] == week)
        ]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def get_by_status(
        self,
        status: EventStatus
    ) -> List[Event]:
        """Get events by status from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['status'] == status.value]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Event]:
        """Get events within date range from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        # Convert date column to datetime if needed
        df['date'] = pd.to_datetime(df['date'])
        
        filtered = df[
            (df['date'] >= start_date) &
            (df['date'] <= end_date)
        ]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def add(self, event: Event) -> Event:
        """Add event to CSV file."""
        df = self._load_data()
        new_row = self._mapper.to_dataframe(event)
        
        # Check if event already exists
        if not df.empty and str(event.id) in df['id'].values:
            logger.warning(f"Event {event.id} already exists, updating instead")
            return await self.update(event)
        
        # Append new row
        df = pd.concat([df, new_row.to_frame().T], ignore_index=True)
        self._save_data(df)
        logger.debug(f"Added event {event.id} to CSV")
        return event
    
    async def update(self, event: Event) -> Event:
        """Update existing event in CSV file."""
        df = self._load_data()
        if df.empty:
            raise EntityNotFoundError(f"Event {event.id} not found")
        
        # Find and update row
        mask = df['id'] == str(event.id)
        if not mask.any():
            raise EntityNotFoundError(f"Event {event.id} not found")
        
        # Update row - convert to dict first to avoid dtype issues
        updated_row = self._mapper.to_dataframe(event)
        # Update each column individually to preserve dtypes
        for col in df.columns:
            if col in updated_row.index:
                df.loc[mask, col] = updated_row[col]
        self._save_data(df)
        logger.info(f"Updated event {event.id} in CSV")
        return event
    
    async def delete(self, event_id: UUID) -> None:
        """Delete event from CSV file."""
        df = self._load_data()
        if df.empty:
            raise EntityNotFoundError(f"Event {event_id} not found")
        
        # Find and remove row
        mask = df['id'] == str(event_id)
        if not mask.any():
            raise EntityNotFoundError(f"Event {event_id} not found")
        
        df = df[~mask]
        self._save_data(df)
        logger.info(f"Deleted event {event_id} from CSV")
    
    async def exists(self, event_id: UUID) -> bool:
        """Check if event exists in CSV."""
        df = self._load_data()
        if df.empty:
            return False
        
        return str(event_id) in df['id'].values

