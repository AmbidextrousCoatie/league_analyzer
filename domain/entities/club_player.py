"""
ClubPlayer Entity

Domain entity representing a player's membership in a club over time.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from uuid import UUID, uuid4
from typing import Optional
from domain.exceptions.domain_exception import DomainException


class InvalidClubPlayerData(DomainException):
    """Raised when club player data is invalid."""
    pass


@dataclass
class ClubPlayer:
    """
    ClubPlayer entity with business logic.
    
    Represents a player's membership period in a club.
    Tracks when a player joined and left a club.
    """
    id: UUID = field(default_factory=uuid4)
    club_id: UUID = field(default=None)
    player_id: UUID = field(default=None)
    date_entry: Optional[date] = field(default=None)
    date_exit: Optional[date] = field(default=None)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate club player invariants."""
        if self.club_id is None:
            raise InvalidClubPlayerData("ClubPlayer must have a club_id")
        
        if self.player_id is None:
            raise InvalidClubPlayerData("ClubPlayer must have a player_id")
        
        if self.date_entry and self.date_exit:
            if self.date_exit < self.date_entry:
                raise InvalidClubPlayerData(
                    f"date_exit ({self.date_exit}) cannot be before date_entry ({self.date_entry})"
                )
    
    def is_active(self) -> bool:
        """
        Check if this membership is currently active.
        
        Returns:
            True if date_exit is None (still active), False otherwise
        """
        return self.date_exit is None
    
    def __eq__(self, other: object) -> bool:
        """Equality based on ID."""
        if not isinstance(other, ClubPlayer):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)
    
    def __repr__(self) -> str:
        """String representation."""
        exit_str = f" to {self.date_exit}" if self.date_exit else " (active)"
        return (
            f"ClubPlayer(id={self.id}, club_id={self.club_id}, "
            f"player_id={self.player_id}, {self.date_entry}{exit_str})"
        )

