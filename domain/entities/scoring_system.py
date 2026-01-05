"""
ScoringSystem Entity

Domain entity representing a scoring system configuration.
Scoring systems define how points are awarded for individual and team matches.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from domain.exceptions.domain_exception import DomainException


class InvalidScoringSystemData(DomainException):
    """Raised when scoring system data is invalid."""
    pass


@dataclass
class ScoringSystem:
    """
    ScoringSystem entity with business logic.
    
    Represents a scoring system configuration that defines:
    - Points for individual match outcomes (win, tie, loss)
    - Points for team match outcomes (win, tie, loss)
    - Whether ties are allowed
    """
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    points_per_individual_match_win: float = field(default=1.0)
    points_per_individual_match_tie: float = field(default=0.5)
    points_per_individual_match_loss: float = field(default=0.0)
    points_per_team_match_win: float = field(default=2.0)
    points_per_team_match_tie: float = field(default=1.0)
    points_per_team_match_loss: float = field(default=0.0)
    allow_ties: bool = field(default=True)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate scoring system invariants."""
        if not self.name or not self.name.strip():
            raise InvalidScoringSystemData("Scoring system name cannot be empty")
        
        if self.points_per_individual_match_win < 0:
            raise InvalidScoringSystemData("Individual match win points cannot be negative")
        
        if self.points_per_individual_match_tie < 0:
            raise InvalidScoringSystemData("Individual match tie points cannot be negative")
        
        if self.points_per_team_match_win < 0:
            raise InvalidScoringSystemData("Team match win points cannot be negative")
        
        if self.points_per_team_match_tie < 0:
            raise InvalidScoringSystemData("Team match tie points cannot be negative")
    
    def update_name(self, new_name: str) -> None:
        """
        Update scoring system name.
        
        Args:
            new_name: New name for the scoring system
            
        Raises:
            InvalidScoringSystemData: If new name is empty
        """
        if not new_name or not new_name.strip():
            raise InvalidScoringSystemData("Scoring system name cannot be empty")
        self.name = new_name.strip()
        self.updated_at = datetime.utcnow()
    
    def update_individual_points(self, win: float, tie: float, loss: float) -> None:
        """
        Update points for individual matches.
        
        Args:
            win: Points for individual match win
            tie: Points for individual match tie
            loss: Points for individual match loss
            
        Raises:
            InvalidScoringSystemData: If any points are negative
        """
        if win < 0 or tie < 0 or loss < 0:
            raise InvalidScoringSystemData("Individual match points cannot be negative")
        self.points_per_individual_match_win = win
        self.points_per_individual_match_tie = tie
        self.points_per_individual_match_loss = loss
        self.updated_at = datetime.utcnow()
    
    def update_team_points(self, win: float, tie: float, loss: float) -> None:
        """
        Update points for team matches.
        
        Args:
            win: Points for team match win
            tie: Points for team match tie
            loss: Points for team match loss
            
        Raises:
            InvalidScoringSystemData: If any points are negative
        """
        if win < 0 or tie < 0 or loss < 0:
            raise InvalidScoringSystemData("Team match points cannot be negative")
        self.points_per_team_match_win = win
        self.points_per_team_match_tie = tie
        self.points_per_team_match_loss = loss
        self.updated_at = datetime.utcnow()
    
    def set_allow_ties(self, allow: bool) -> None:
        """
        Set whether ties are allowed.
        
        Args:
            allow: Whether ties are allowed
        """
        self.allow_ties = allow
        self.updated_at = datetime.utcnow()
    
    def __eq__(self, other: object) -> bool:
        """Equality based on ID."""
        if not isinstance(other, ScoringSystem):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ScoringSystem(id={self.id}, name='{self.name}', "
            f"individual_win={self.points_per_individual_match_win}, "
            f"team_win={self.points_per_team_match_win}, allow_ties={self.allow_ties})"
        )

