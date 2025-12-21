"""
League Entity

Domain entity representing a bowling league.
Leagues contain teams and organize games.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import List, Set, Optional
from domain.value_objects.handicap_settings import HandicapSettings
from domain.entities.team import Team
from domain.domain_events.domain_event import TeamAddedToLeague
from domain.domain_events.event_bus import DomainEventBus
from domain.exceptions.domain_exception import InvalidTeamOperation


# League level mapping based on legacy implementation
# Note: Levels 1-2 (1. BL, 2. BL) are federal leagues not in this dataset.
# Bayernliga (BayL) at level 3 is the highest level league in this dataset.
LEAGUE_LEVELS = {
    "1. BL": 1,      # Federal league (not in dataset)
    "2. BL": 2,      # Federal league (not in dataset)
    "BayL": 3,       # Highest level in dataset
    "LL N1": 4,
    "LL N2": 4,
    "LL S": 4,
    "BZOL N1": 5,
    "BZOL N2": 5,
    "BZOL S1": 5,
    "BZOL S2": 5,
    "BZL N1": 6,
    "BZL N2": 6,
    "BZL S1": 6,
    "BZL S2": 6,
    "KL N1": 7,
    "KL N2": 7,
    "KL S1": 7,
    "KL S2": 7
}

LEAGUE_LONG_NAMES = {
    "1. BL": "1. Bundesliga",
    "2. BL": "2. Bundesliga",
    "BayL": "Bayernliga",
    "LL N1": "Landesliga Nord 1",
    "LL N2": "Landesliga Nord 2",
    "LL S": "Landesliga Süd",
    "BZOL N1": "Bezirksoberliga Nord 1",
    "BZOL N2": "Bezirksoberliga Nord 2",
    "BZOL S1": "Bezirksoberliga Süd 1",
    "BZOL S2": "Bezirksoberliga Süd 2",
    "BZL N1": "Bezirksliga Nord 1",
    "BZL N2": "Bezirksliga Nord 2",
    "BZL S1": "Bezirksliga Süd 1",
    "BZL S2": "Bezirksliga Süd 2",
    "KL N1": "Kreisliga Nord 1",
    "KL N2": "Kreisliga Nord 2",
    "KL S1": "Kreisliga Süd 1",
    "KL S2": "Kreisliga Süd 2",
}


def get_league_level(league_name: str) -> int:
    """
    Get the level (skill tier) for a league based on its name.
    
    Args:
        league_name: Short name of the league (e.g., "1. BL", "BayL")
    
    Returns:
        Level as integer (1-7), defaults to 7 if not found
    """
    return LEAGUE_LEVELS.get(league_name, 7)


def get_league_long_name(league_name: str) -> str:
    """
    Get the long name for a league based on its short name.
    
    Args:
        league_name: Short name of the league (e.g., "1. BL", "BayL")
    
    Returns:
        Long name if found, otherwise returns the input name
    """
    return LEAGUE_LONG_NAMES.get(league_name, league_name)


@dataclass
class League:
    """
    League entity with business logic.
    
    Leagues have identity (id) and contain teams.
    Leagues have a level (skill tier) from 1-7, where 1 is the highest level.
    Leagues have an abbreviation (short name like "BayL", "1. BL").
    """
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    abbreviation: str = ""
    level: int = field(default=7)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    handicap_settings: Optional[HandicapSettings] = field(default=None)
    _teams: Set[UUID] = field(default_factory=set, init=False, repr=False)
    
    def __post_init__(self):
        """Validate league invariants."""
        if not self.name or not self.name.strip():
            raise ValueError("League name cannot be empty")
        
        if not (1 <= self.level <= 7):
            raise ValueError(f"League level must be between 1 and 7, got: {self.level}")
        
        # Auto-set level from abbreviation if not explicitly set and abbreviation matches known league
        if self.level == 7 and self.abbreviation and self.abbreviation in LEAGUE_LEVELS:
            self.level = get_league_level(self.abbreviation)
        
        # Auto-set name from abbreviation if name not set but abbreviation matches known league
        if not self.name and self.abbreviation and self.abbreviation in LEAGUE_LONG_NAMES:
            self.name = get_league_long_name(self.abbreviation)
    
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
    
    def set_level(self, level: int) -> None:
        """
        Set the level (skill tier) for this league.
        
        Args:
            level: Level as integer (1-7)
        
        Raises:
            ValueError: If level is not between 1 and 7
        """
        if not (1 <= level <= 7):
            raise ValueError(f"League level must be between 1 and 7, got: {level}")
        self.level = level
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
            f"abbreviation='{self.abbreviation}', level={self.level}, teams={len(self._teams)})"
        )

