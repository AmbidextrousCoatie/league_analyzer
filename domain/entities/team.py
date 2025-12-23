"""
Team Entity

Domain entity representing a bowling team squad.
A team represents a specific squad (team number) within a club.
Teams participate in league seasons via TeamSeason entity.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import List, Optional
from domain.exceptions.domain_exception import InvalidTeamOperation, DomainException


class InvalidTeamData(DomainException):
    """Raised when team data is invalid."""
    pass


@dataclass
class Team:
    """
    Team entity with business logic.
    
    Represents a specific squad (team number) within a club.
    A club can have multiple teams (Team 1, Team 2, Team 3, etc.).
    Teams participate in league seasons via TeamSeason entity.
    Teams can ascend/descend between league levels over time.
    """
    id: UUID = field(default_factory=uuid4)
    name: str = ""  # Display name (e.g., "Munich Team 2")
    club_id: UUID = field(default=None)  # Reference to Club entity
    team_number: int = field(default=1)  # Squad number within the club (1, 2, 3, ...)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate team invariants."""
        if not self.name or not self.name.strip():
            raise InvalidTeamData("Team name cannot be empty")
        if self.club_id is None:
            raise InvalidTeamData("Team must belong to a club")
        if self.team_number < 1:
            raise InvalidTeamData(f"Team number must be positive, got: {self.team_number}")
    
    def assign_to_club(self, club_id: UUID, team_number: int = 1) -> None:
        """
        Assign team to a club with a squad number.
        
        Args:
            club_id: UUID of the club
            team_number: Squad number within the club (must be >= 1)
        
        Raises:
            InvalidTeamOperation: If team number is invalid
        """
        if team_number < 1:
            raise InvalidTeamOperation(f"Team number must be positive, got: {team_number}")
        self.club_id = club_id
        self.team_number = team_number
        self.updated_at = datetime.utcnow()
    
    def update_team_number(self, team_number: int) -> None:
        """
        Update team squad number.
        
        Args:
            team_number: New squad number (must be >= 1)
        
        Raises:
            InvalidTeamOperation: If team number is invalid
        """
        if team_number < 1:
            raise InvalidTeamOperation(f"Team number must be positive, got: {team_number}")
        self.team_number = team_number
        self.updated_at = datetime.utcnow()
    
    def update_name(self, new_name: str) -> None:
        """
        Update team name.
        
        Args:
            new_name: New name for the team
        
        Raises:
            ValueError: If new name is empty
        """
        if not new_name or not new_name.strip():
            raise ValueError("Team name cannot be empty")
        self.name = new_name.strip()
        self.updated_at = datetime.utcnow()
    
    def __eq__(self, other: object) -> bool:
        """Equality based on ID."""
        if not isinstance(other, Team):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Team(id={self.id}, name='{self.name}', "
            f"club_id={self.club_id}, team_number={self.team_number})"
        )

