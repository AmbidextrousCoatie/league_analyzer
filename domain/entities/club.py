"""
Club Entity

Domain entity representing a bowling club/organization.
Clubs have a home alley, address, and can have multiple teams participating in different league seasons.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from domain.exceptions.domain_exception import DomainException


class InvalidClubData(DomainException):
    """Raised when club data is invalid."""
    pass


@dataclass
class Club:
    """
    Club entity with business logic.
    
    Represents a bowling club/organization that:
    - Has a home alley (venue)
    - Has an address
    - Can have multiple teams (squads) participating in different league seasons
    - Can have players as members
    """
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    short_name: Optional[str] = field(default=None)
    home_alley_id: Optional[UUID] = field(default=None)  # Reference to Venue entity
    address: Optional[str] = field(default=None)  # Full address as string (can be enhanced later)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate club invariants."""
        if not self.name or not self.name.strip():
            raise InvalidClubData("Club name cannot be empty")
    
    def update_name(self, new_name: str) -> None:
        """
        Update club name.
        
        Args:
            new_name: New name for the club
            
        Raises:
            ValueError: If new name is empty
        """
        if not new_name or not new_name.strip():
            raise ValueError("Club name cannot be empty")
        self.name = new_name.strip()
        self.updated_at = datetime.utcnow()
    
    def update_short_name(self, short_name: Optional[str]) -> None:
        """Update club short name."""
        self.short_name = short_name.strip() if short_name else None
        self.updated_at = datetime.utcnow()
    
    def set_home_alley(self, venue_id: UUID) -> None:
        """
        Set the club's home alley.
        
        Args:
            venue_id: UUID of the venue
        """
        self.home_alley_id = venue_id
        self.updated_at = datetime.utcnow()
    
    def update_address(self, address: Optional[str]) -> None:
        """Update club address."""
        self.address = address.strip() if address else None
        self.updated_at = datetime.utcnow()
    
    def __eq__(self, other: object) -> bool:
        """Equality based on ID."""
        if not isinstance(other, Club):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Club(id={self.id}, name='{self.name}', "
            f"short_name='{self.short_name}', home_alley_id={self.home_alley_id})"
        )

