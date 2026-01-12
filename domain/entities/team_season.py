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
    
    Note: TeamSeason references a Team entity (via team_id), which represents
    a stable team identity (club + team_number) across all seasons.
    """
    id: UUID = field(default_factory=uuid4)
    league_season_id: UUID = field(default=None)
    team_id: UUID = field(default=None)
    vacancy_status: VacancyStatus = field(default=VacancyStatus.ACTIVE)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate team season invariants."""
        if self.league_season_id is None:
            raise InvalidTeamSeasonData("TeamSeason must have a league_season_id")
        
        if self.team_id is None:
            raise InvalidTeamSeasonData("TeamSeason must have a team_id")
    
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
            f"team_id={self.team_id}, vacancy_status={self.vacancy_status})"
        )

