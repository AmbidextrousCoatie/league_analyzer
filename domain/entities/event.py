"""
Event Entity

Domain entity representing a bowling event (league week/day).
Events contain multiple games/matches.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from domain.value_objects.season import Season
from domain.value_objects.event_status import EventStatus
from domain.exceptions.domain_exception import DomainException


class InvalidEventData(DomainException):
    """Raised when event data is invalid."""
    pass


@dataclass
class Event:
    """
    Event entity with business logic.
    
    Events represent a league week/day where multiple matches occur.
    Events have a lifecycle state and can contain multiple games.
    """
    id: UUID = field(default_factory=uuid4)
    league_season_id: UUID = field(default=None)
    event_type: str = "league"  # "league", "tournament", etc.
    league_week: Optional[int] = field(default=None)
    tournament_stage: Optional[str] = field(default=None)
    date: datetime = field(default_factory=datetime.utcnow)
    venue_id: Optional[str] = field(default=None)
    oil_pattern_id: Optional[int] = field(default=None)
    status: EventStatus = field(default=EventStatus.SCHEDULED)
    disqualification_reason: Optional[str] = field(default=None)
    notes: Optional[str] = field(default=None)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate event invariants."""
        if not self.event_type or not self.event_type.strip():
            raise InvalidEventData("Event type cannot be empty")
        
        if self.league_week is not None and self.league_week < 0:
            raise InvalidEventData(f"League week must be non-negative, got: {self.league_week}")
    
    def update_status(self, new_status: EventStatus) -> None:
        """
        Update event status.
        
        Args:
            new_status: New status for the event
        
        Raises:
            InvalidEventData: If status transition is invalid
        """
        # Validate status transitions
        if self.status == EventStatus.COMPLETED and new_status not in (EventStatus.DISPUTED, EventStatus.COMPLETED):
            raise InvalidEventData(
                f"Cannot change status from {self.status} to {new_status}"
            )
        
        if self.status == EventStatus.CANCELLED:
            raise InvalidEventData("Cannot change status of cancelled event")
        
        self.status = new_status
        self.updated_at = datetime.utcnow()
    
    def mark_disqualified(self, reason: str) -> None:
        """
        Mark event as having disqualifications.
        
        Args:
            reason: Reason for disqualification
        """
        self.disqualification_reason = reason
        if self.status != EventStatus.COMPLETED:
            self.update_status(EventStatus.DISPUTED)
        self.updated_at = datetime.utcnow()
    
    def clear_disqualification(self) -> None:
        """Clear disqualification reason."""
        self.disqualification_reason = None
        if self.status == EventStatus.DISPUTED:
            self.update_status(EventStatus.COMPLETED)
        self.updated_at = datetime.utcnow()
    
    def update_date(self, new_date: datetime) -> None:
        """
        Update event date.
        
        Args:
            new_date: New date for the event
        """
        self.date = new_date
        self.updated_at = datetime.utcnow()
    
    def update_venue(self, venue_id: str) -> None:
        """
        Update venue for the event.
        
        Args:
            venue_id: ID of the venue
        """
        self.venue_id = venue_id
        self.updated_at = datetime.utcnow()
    
    def update_notes(self, notes: str) -> None:
        """
        Update event notes.
        
        Args:
            notes: Notes for the event
        """
        self.notes = notes
        self.updated_at = datetime.utcnow()
    
    def is_active(self) -> bool:
        """Check if event is in an active state."""
        return self.status.is_active()
    
    def is_finished(self) -> bool:
        """Check if event is finished."""
        return self.status.is_finished()
    
    def can_modify_results(self) -> bool:
        """Check if results can be modified."""
        return self.status.can_modify_results()
    
    def __eq__(self, other: object) -> bool:
        """Equality based on ID."""
        if not isinstance(other, Event):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Event(id={self.id}, league_season_id={self.league_season_id}, "
            f"event_type='{self.event_type}', league_week={self.league_week}, "
            f"date={self.date}, status={self.status})"
        )

