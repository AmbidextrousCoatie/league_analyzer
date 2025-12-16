"""
Team Entity

Domain entity representing a bowling team.
Teams have identity and contain business logic for managing players.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import List, Optional
from domain.exceptions.domain_exception import InvalidTeamOperation


@dataclass
class Team:
    """
    Team entity with business logic.
    
    Teams have identity (id) and can contain players.
    Teams belong to a league.
    """
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    league_id: UUID = field(default=None)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate team invariants."""
        if not self.name or not self.name.strip():
            raise ValueError("Team name cannot be empty")
    
    def assign_to_league(self, league_id: UUID) -> None:
        """
        Assign team to a league.
        
        Args:
            league_id: UUID of the league
        
        Raises:
            InvalidTeamOperation: If team is already assigned to a different league
        """
        if self.league_id is not None and self.league_id != league_id:
            raise InvalidTeamOperation(
                f"Team {self.name} is already assigned to league {self.league_id}"
            )
        self.league_id = league_id
        self.updated_at = datetime.utcnow()
    
    def remove_from_league(self) -> None:
        """Remove team from its current league."""
        self.league_id = None
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
        return f"Team(id={self.id}, name='{self.name}', league_id={self.league_id})"

