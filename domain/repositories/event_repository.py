"""
Event Repository Interface

Abstract interface for Event entity repositories.
Storage-agnostic - works for CSV or SQL implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from domain.entities.event import Event
from domain.value_objects.event_status import EventStatus


class EventRepository(ABC):
    """
    Repository interface for Event entities.
    
    Storage-agnostic interface - works for CSV or SQL implementations.
    """
    
    @abstractmethod
    async def get_by_id(self, event_id: UUID) -> Optional[Event]:
        """
        Get event by ID.
        
        Args:
            event_id: UUID of the event
        
        Returns:
            Event if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Event]:
        """
        Get all events.
        
        Returns:
            List of all events
        """
        pass
    
    @abstractmethod
    async def get_by_league_season(
        self, 
        league_season_id: UUID
    ) -> List[Event]:
        """
        Get all events for a league season.
        
        Args:
            league_season_id: UUID of the league season
        
        Returns:
            List of events for the season
        """
        pass
    
    @abstractmethod
    async def get_by_week(
        self,
        league_season_id: UUID,
        week: int
    ) -> List[Event]:
        """
        Get events for a specific week.
        
        Args:
            league_season_id: UUID of the league season
            week: Week number
        
        Returns:
            List of events for the week
        """
        pass
    
    @abstractmethod
    async def get_by_status(
        self,
        status: EventStatus
    ) -> List[Event]:
        """
        Get events by status.
        
        Args:
            status: EventStatus to filter by
        
        Returns:
            List of events with the status
        """
        pass
    
    @abstractmethod
    async def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Event]:
        """
        Get events within a date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
        
        Returns:
            List of events in the date range
        """
        pass
    
    @abstractmethod
    async def add(self, event: Event) -> Event:
        """
        Add a new event.
        
        Args:
            event: Event entity to add
        
        Returns:
            Added event
        """
        pass
    
    @abstractmethod
    async def update(self, event: Event) -> Event:
        """
        Update an existing event.
        
        Args:
            event: Event entity to update
        
        Returns:
            Updated event
        
        Raises:
            EntityNotFoundError: If event doesn't exist
        """
        pass
    
    @abstractmethod
    async def delete(self, event_id: UUID) -> None:
        """
        Delete an event.
        
        Args:
            event_id: UUID of event to delete
        
        Raises:
            EntityNotFoundError: If event doesn't exist
        """
        pass
    
    @abstractmethod
    async def exists(self, event_id: UUID) -> bool:
        """
        Check if event exists.
        
        Args:
            event_id: UUID to check
        
        Returns:
            True if exists, False otherwise
        """
        pass

