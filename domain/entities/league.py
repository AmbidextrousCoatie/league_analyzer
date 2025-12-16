"""
League Entity

Domain entity representing a bowling league.
Leagues contain teams and organize games.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import List, Set, Optional
from domain.value_objects.season import Season
from domain.value_objects.handicap_settings import HandicapSettings
from domain.entities.team import Team
from domain.domain_events.domain_event import TeamAddedToLeague
from domain.domain_events.event_bus import DomainEventBus
from domain.exceptions.domain_exception import InvalidTeamOperation


@dataclass
class League:
    """
    League entity with business logic.
    
    Leagues have identity (id) and contain teams.
    Leagues are associated with a season.
    """
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    season: Season = field(default=None)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    handicap_settings: Optional[HandicapSettings] = field(default=None)
    _teams: Set[UUID] = field(default_factory=set, init=False, repr=False)
    
    def __post_init__(self):
        """Validate league invariants."""
        if not self.name or not self.name.strip():
            raise ValueError("League name cannot be empty")
        
        if self.season is None:
            raise ValueError("League must have a season")
    
    def add_team(self, team: Team) -> None:
        """
        Add a team to the league.
        
        Args:
            team: Team entity to add
        
        Raises:
            InvalidTeamOperation: If team is already in the league
        """
        if team.id in self._teams:
            raise InvalidTeamOperation(
                f"Team {team.name} (id: {team.id}) is already in league {self.name}"
            )
        
        # Assign team to this league
        team.assign_to_league(self.id)
        
        # Add team to league
        self._teams.add(team.id)
        self.updated_at = datetime.utcnow()
        
        # Publish domain event
        DomainEventBus.publish(
            TeamAddedToLeague(league_id=self.id, team_id=team.id)
        )
    
    def remove_team(self, team: Team) -> None:
        """
        Remove a team from the league.
        
        Args:
            team: Team entity to remove
        
        Raises:
            InvalidTeamOperation: If team is not in the league
        """
        if team.id not in self._teams:
            raise InvalidTeamOperation(
                f"Team {team.name} (id: {team.id}) is not in league {self.name}"
            )
        
        # Remove team from league
        self._teams.remove(team.id)
        team.remove_from_league()
        self.updated_at = datetime.utcnow()
    
    def has_team(self, team_id: UUID) -> bool:
        """Check if a team is in this league."""
        return team_id in self._teams
    
    def get_team_count(self) -> int:
        """Get the number of teams in the league."""
        return len(self._teams)
    
    def update_name(self, new_name: str) -> None:
        """
        Update league name.
        
        Args:
            new_name: New name for the league
        
        Raises:
            ValueError: If new name is empty
        """
        if not new_name or not new_name.strip():
            raise ValueError("League name cannot be empty")
        self.name = new_name.strip()
        self.updated_at = datetime.utcnow()
    
    def set_season(self, season: Season) -> None:
        """
        Set the season for this league.
        
        Args:
            season: Season value object
        """
        self.season = season
        self.updated_at = datetime.utcnow()
    
    def set_handicap_settings(self, settings: HandicapSettings) -> None:
        """
        Set handicap settings for this league.
        
        Args:
            settings: HandicapSettings value object
        """
        self.handicap_settings = settings
        self.updated_at = datetime.utcnow()
    
    def has_handicap_enabled(self) -> bool:
        """Check if handicap is enabled for this league."""
        return (
            self.handicap_settings is not None and 
            self.handicap_settings.enabled
        )
    
    def __eq__(self, other: object) -> bool:
        """Equality based on ID."""
        if not isinstance(other, League):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"League(id={self.id}, name='{self.name}', "
            f"season={self.season}, teams={len(self._teams)})"
        )

