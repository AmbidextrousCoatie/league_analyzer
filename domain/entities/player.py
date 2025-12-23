"""
Player Entity

Domain entity representing a bowling player.
Players have identity and can be assigned to teams.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, Dict
from domain.value_objects.season import Season
from domain.value_objects.handicap import Handicap
from domain.exceptions.domain_exception import InvalidTeamOperation


@dataclass
class Player:
    """
    Player entity with business logic.
    
    Players have identity (id) and can be assigned to teams.
    Players belong to a club (for eligibility checking).
    Legacy players from external DB have their original ID stored in dbu_id.
    """
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    dbu_id: Optional[str] = field(default=None)  # Legacy ID from external DB (DBU)
    club_id: Optional[UUID] = field(default=None)  # Club association (from external DB)
    team_id: Optional[UUID] = field(default=None)  # Current team assignment
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    _handicaps: Dict[str, Handicap] = field(default_factory=dict, init=False, repr=False)
    
    def __post_init__(self):
        """Validate player invariants."""
        if not self.name or not self.name.strip():
            raise ValueError("Player name cannot be empty")
    
    def assign_to_team(self, team_id: UUID) -> None:
        """
        Assign player to a team.
        
        Args:
            team_id: UUID of the team
        
        Raises:
            InvalidTeamOperation: If player is already assigned to a different team
        """
        if self.team_id is not None and self.team_id != team_id:
            raise InvalidTeamOperation(
                f"Player {self.name} is already assigned to team {self.team_id}"
            )
        self.team_id = team_id
        self.updated_at = datetime.utcnow()
    
    def remove_from_team(self) -> None:
        """Remove player from their current team."""
        self.team_id = None
        self.updated_at = datetime.utcnow()
    
    def update_name(self, new_name: str) -> None:
        """
        Update player name.
        
        Args:
            new_name: New name for the player
        
        Raises:
            ValueError: If new name is empty
        """
        if not new_name or not new_name.strip():
            raise ValueError("Player name cannot be empty")
        self.name = new_name.strip()
        self.updated_at = datetime.utcnow()
    
    def is_on_team(self) -> bool:
        """Check if player is currently assigned to a team."""
        return self.team_id is not None
    
    def set_handicap(self, season: Season, handicap: Handicap) -> None:
        """
        Set handicap for a specific season.
        
        Handicap can change during a season, so this updates the current handicap.
        
        Args:
            season: Season value object
            handicap: Handicap value object
        """
        season_key = str(season)
        self._handicaps[season_key] = handicap
        self.updated_at = datetime.utcnow()
    
    def get_handicap(self, season: Season) -> Optional[Handicap]:
        """
        Get handicap for a specific season.
        
        Args:
            season: Season value object
        
        Returns:
            Handicap if set for this season, None otherwise
        """
        season_key = str(season)
        return self._handicaps.get(season_key)
    
    def has_handicap(self, season: Season) -> bool:
        """Check if player has handicap set for a season."""
        return self.get_handicap(season) is not None
    
    def remove_handicap(self, season: Season) -> None:
        """
        Remove handicap for a specific season.
        
        Args:
            season: Season value object
        """
        season_key = str(season)
        if season_key in self._handicaps:
            del self._handicaps[season_key]
            self.updated_at = datetime.utcnow()
    
    def __eq__(self, other: object) -> bool:
        """Equality based on ID."""
        if not isinstance(other, Player):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)
    
    def assign_to_club(self, club_id: UUID) -> None:
        """
        Assign player to a club.
        
        Args:
            club_id: UUID of the club
        """
        self.club_id = club_id
        self.updated_at = datetime.utcnow()
    
    def remove_from_club(self) -> None:
        """Remove player from their current club."""
        self.club_id = None
        self.updated_at = datetime.utcnow()
    
    def belongs_to_club(self) -> bool:
        """Check if player belongs to a club."""
        return self.club_id is not None
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Player(id={self.id}, name='{self.name}', "
            f"dbu_id={self.dbu_id}, club_id={self.club_id}, team_id={self.team_id})"
        )

