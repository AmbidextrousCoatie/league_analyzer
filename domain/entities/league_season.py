"""
LeagueSeason Entity

Domain entity representing a league in a specific season.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from domain.value_objects.season import Season
from domain.value_objects.handicap_settings import HandicapSettings
from domain.exceptions.domain_exception import DomainException


class InvalidLeagueSeasonData(DomainException):
    """Raised when league season data is invalid."""
    pass


@dataclass
class LeagueSeason:
    """
    LeagueSeason entity with business logic.
    
    Represents a league in a specific season with configuration:
    - Scoring system
    - Handicap settings (optional)
    - Number of teams
    - Players per team
    """
    id: UUID = field(default_factory=uuid4)
    league_id: UUID = field(default=None)
    season: Season = field(default=None)
    scoring_system_id: str = field(default="")
    number_of_teams: Optional[int] = field(default=None)
    players_per_team: Optional[int] = field(default=None)
    handicap_settings: Optional[HandicapSettings] = field(default=None)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate league season invariants."""
        if self.league_id is None:
            raise InvalidLeagueSeasonData("LeagueSeason must have a league_id")
        
        if self.season is None:
            raise InvalidLeagueSeasonData("LeagueSeason must have a season")
        
        if not self.scoring_system_id or not self.scoring_system_id.strip():
            raise InvalidLeagueSeasonData("LeagueSeason must have a scoring_system_id")
        
        if self.number_of_teams is not None and self.number_of_teams < 1:
            raise InvalidLeagueSeasonData(
                f"Number of teams must be positive, got: {self.number_of_teams}"
            )
        
        if self.players_per_team is not None and self.players_per_team < 1:
            raise InvalidLeagueSeasonData(
                f"Players per team must be positive, got: {self.players_per_team}"
            )
    
    def set_handicap_settings(self, settings: HandicapSettings) -> None:
        """
        Set handicap settings for this league season.
        
        Args:
            settings: HandicapSettings value object
        """
        self.handicap_settings = settings
        self.updated_at = datetime.utcnow()
    
    def remove_handicap_settings(self) -> None:
        """Remove handicap settings (scratch league)."""
        self.handicap_settings = None
        self.updated_at = datetime.utcnow()
    
    def has_handicap_enabled(self) -> bool:
        """
        Check if handicap is enabled for this league season.
        
        Returns:
            True if handicap settings are configured, False otherwise
        """
        return (
            self.handicap_settings is not None and
            self.handicap_settings.enabled
        )
    
    def update_scoring_system(self, scoring_system_id: str) -> None:
        """
        Update scoring system.
        
        Args:
            scoring_system_id: ID of the scoring system
        
        Raises:
            InvalidLeagueSeasonData: If scoring system ID is empty
        """
        if not scoring_system_id or not scoring_system_id.strip():
            raise InvalidLeagueSeasonData("Scoring system ID cannot be empty")
        self.scoring_system_id = scoring_system_id.strip()
        self.updated_at = datetime.utcnow()
    
    def update_team_config(self, number_of_teams: Optional[int], players_per_team: Optional[int]) -> None:
        """
        Update team configuration.
        
        Args:
            number_of_teams: Number of teams in league (optional)
            players_per_team: Number of players per team (optional)
        
        Raises:
            InvalidLeagueSeasonData: If values are invalid
        """
        if number_of_teams is not None and number_of_teams < 1:
            raise InvalidLeagueSeasonData(
                f"Number of teams must be positive, got: {number_of_teams}"
            )
        
        if players_per_team is not None and players_per_team < 1:
            raise InvalidLeagueSeasonData(
                f"Players per team must be positive, got: {players_per_team}"
            )
        
        self.number_of_teams = number_of_teams
        self.players_per_team = players_per_team
        self.updated_at = datetime.utcnow()
    
    def __eq__(self, other: object) -> bool:
        """Equality based on ID."""
        if not isinstance(other, LeagueSeason):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)
    
    def __repr__(self) -> str:
        """String representation."""
        handicap_str = ", handicap_enabled" if self.has_handicap_enabled() else ""
        return (
            f"LeagueSeason(id={self.id}, league_id={self.league_id}, "
            f"season={self.season}, scoring_system='{self.scoring_system_id}'{handicap_str})"
        )

