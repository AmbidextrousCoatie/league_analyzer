"""
EventStatus Value Object

Represents the lifecycle state of an event.
"""

from enum import Enum


class EventStatus(Enum):
    """
    Event lifecycle states.
    
    - SCHEDULED: Event is scheduled but not yet started
    - PREPARING: Event is being prepared (rosters, etc.)
    - IN_PROGRESS: Event is currently happening
    - COMPLETED: Event has finished
    - CANCELLED: Event was cancelled
    - DISPUTED: Event results are under dispute
    """
    SCHEDULED = "scheduled"
    PREPARING = "preparing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
    
    def __str__(self) -> str:
        """String representation."""
        return self.value
    
    def is_active(self) -> bool:
        """Check if event is in an active state."""
        return self in (EventStatus.PREPARING, EventStatus.IN_PROGRESS)
    
    def is_finished(self) -> bool:
        """Check if event is finished."""
        return self in (EventStatus.COMPLETED, EventStatus.CANCELLED, EventStatus.DISPUTED)
    
    def can_modify_results(self) -> bool:
        """Check if results can be modified in this state."""
        return self in (EventStatus.IN_PROGRESS, EventStatus.COMPLETED)

