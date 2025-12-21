"""
TeamSeason Entity

Domain entity representing a team's participation in a league season.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from domain.value_objects.vacancy_status import VacancyStatus
from domain.exceptions.domain_exception import DomainException


class InvalidTeamSeasonData(DomainException):
    """Raised when team season data is invalid."""
    pass


@dataclass
class TeamSeason:
    """
    TeamSeason entity with business logic.
    
    Represents a team's participation in a specific league season.
    Teams can have different statuses (active, vacant, forfeit).
    """
    id: UUID = field(default_factory=uuid4)
    league_season_id: UUID = field(default=None)
    club_id: UUID = field(default=None)
    team_number: int = field(default=1)
    vacancy_status: VacancyStatus = field(default=VacancyStatus.ACTIVE)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate team season invariants."""
        if self.league_season_id is None:
            raise InvalidTeamSeasonData("TeamSeason must have a league_season_id")
        
        if self.club_id is None:
            raise InvalidTeamSeasonData("TeamSeason must have a club_id")
        
        if self.team_number < 1:
            raise InvalidTeamSeasonData(
                f"Team number must be positive, got: {self.team_number}"
            )
    
    def update_vacancy_status(self, new_status: VacancyStatus) -> None:
        """
        Update vacancy status.
        
        Args:
            new_status: New vacancy status
        """
        self.vacancy_status = new_status
        self.updated_at = datetime.utcnow()
    
    def mark_vacant(self) -> None:
        """Mark team as vacant."""
        self.update_vacancy_status(VacancyStatus.VACANT)
    
    def mark_forfeit(self) -> None:
        """Mark team as forfeit."""
        self.update_vacancy_status(VacancyStatus.FORFEIT)
    
    def mark_active(self) -> None:
        """Mark team as active."""
        self.update_vacancy_status(VacancyStatus.ACTIVE)
    
    def can_participate(self) -> bool:
        """Check if team can participate in events."""
        return self.vacancy_status.can_participate()
    
    def is_available(self) -> bool:
        """Check if team position is available."""
        return self.vacancy_status.is_available()
    
    def update_team_number(self, team_number: int) -> None:
        """
        Update team number.
        
        Args:
            team_number: New team number (must be positive)
        
        Raises:
            InvalidTeamSeasonData: If team number is invalid
        """
        if team_number < 1:
            raise InvalidTeamSeasonData(
                f"Team number must be positive, got: {team_number}"
            )
        self.team_number = team_number
        self.updated_at = datetime.utcnow()
    
    def __eq__(self, other: object) -> bool:
        """Equality based on ID."""
        if not isinstance(other, TeamSeason):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"TeamSeason(id={self.id}, league_season_id={self.league_season_id}, "
            f"club_id={self.club_id}, team_number={self.team_number}, "
            f"vacancy_status={self.vacancy_status})"
        )

