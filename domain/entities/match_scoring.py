"""
Match Scoring Entity

Domain entity representing computed scoring results for a match under a specific scoring system.
Stores both individual points (from position comparisons) and team match points.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from domain.exceptions.domain_exception import DomainException


class InvalidMatchScoringData(DomainException):
    """Raised when match scoring data is invalid."""
    pass


@dataclass
class MatchScoring:
    """
    Match scoring entity representing computed points for a match.
    
    Stores the results of applying a scoring system to a match:
    - Individual points: Sum of position-by-position wins (from PositionComparison)
    - Team match points: Points awarded based on team total comparison (2 or 3 points)
    
    Multiple MatchScoring records can exist for the same match (one per scoring system),
    allowing historical comparison and "what-if" scenarios.
    """
    id: UUID = field(default_factory=uuid4)
    match_id: UUID = field(default=None)  # Link to Match entity (required)
    scoring_system_id: str = field(default="")  # Link to ScoringSystem (required)
    team1_individual_points: float = field(default=0.0)  # Sum of team1 position wins
    team2_individual_points: float = field(default=0.0)  # Sum of team2 position wins
    team1_match_points: float = field(default=0.0)  # Team match points for team1 (2 or 3)
    team2_match_points: float = field(default=0.0)  # Team match points for team2 (2 or 3)
    computed_at: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate match scoring invariants."""
        self._validate_required_fields()
        self._validate_points()
    
    def _validate_required_fields(self) -> None:
        """Validate that required fields are present."""
        if self.match_id is None:
            raise InvalidMatchScoringData("MatchScoring must have a match_id")
        # scoring_system_id can be UUID or string
        if not self.scoring_system_id:
            raise InvalidMatchScoringData("MatchScoring must have a scoring_system_id")
        # If it's a string, check it's not empty
        if isinstance(self.scoring_system_id, str) and not self.scoring_system_id.strip():
            raise InvalidMatchScoringData("MatchScoring must have a non-empty scoring_system_id")
    
    def _validate_points(self) -> None:
        """Validate that points are non-negative."""
        if self.team1_individual_points < 0:
            raise InvalidMatchScoringData(
                f"Team1 individual points must be non-negative, got: {self.team1_individual_points}"
            )
        if self.team2_individual_points < 0:
            raise InvalidMatchScoringData(
                f"Team2 individual points must be non-negative, got: {self.team2_individual_points}"
            )
        if self.team1_match_points < 0:
            raise InvalidMatchScoringData(
                f"Team1 match points must be non-negative, got: {self.team1_match_points}"
            )
        if self.team2_match_points < 0:
            raise InvalidMatchScoringData(
                f"Team2 match points must be non-negative, got: {self.team2_match_points}"
            )
    
    def update_individual_points(self, team1_points: float, team2_points: float) -> None:
        """
        Update individual points for both teams.
        
        Args:
            team1_points: Team1's individual points (must be non-negative)
            team2_points: Team2's individual points (must be non-negative)
        
        Raises:
            InvalidMatchScoringData: If any points are negative
        """
        if team1_points < 0:
            raise InvalidMatchScoringData(
                f"Team1 individual points must be non-negative, got: {team1_points}"
            )
        if team2_points < 0:
            raise InvalidMatchScoringData(
                f"Team2 individual points must be non-negative, got: {team2_points}"
            )
        self.team1_individual_points = team1_points
        self.team2_individual_points = team2_points
        self.updated_at = datetime.utcnow()
    
    def update_match_points(self, team1_points: float, team2_points: float) -> None:
        """
        Update team match points for both teams.
        
        Args:
            team1_points: Team1's match points (must be non-negative)
            team2_points: Team2's match points (must be non-negative)
        
        Raises:
            InvalidMatchScoringData: If any points are negative
        """
        if team1_points < 0:
            raise InvalidMatchScoringData(
                f"Team1 match points must be non-negative, got: {team1_points}"
            )
        if team2_points < 0:
            raise InvalidMatchScoringData(
                f"Team2 match points must be non-negative, got: {team2_points}"
            )
        self.team1_match_points = team1_points
        self.team2_match_points = team2_points
        self.updated_at = datetime.utcnow()
    
    def update_all_points(
        self,
        team1_individual: float,
        team2_individual: float,
        team1_match: float,
        team2_match: float
    ) -> None:
        """
        Update all points at once.
        
        Args:
            team1_individual: Team1's individual points
            team2_individual: Team2's individual points
            team1_match: Team1's match points
            team2_match: Team2's match points
        """
        self.update_individual_points(team1_individual, team2_individual)
        self.update_match_points(team1_match, team2_match)
    
    def get_team1_total_points(self) -> float:
        """Get team1's total points (individual + match)."""
        return self.team1_individual_points + self.team1_match_points
    
    def get_team2_total_points(self) -> float:
        """Get team2's total points (individual + match)."""
        return self.team2_individual_points + self.team2_match_points
    
    def __eq__(self, other: object) -> bool:
        """Equality based on ID."""
        if not isinstance(other, MatchScoring):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"MatchScoring(id={self.id}, match_id={self.match_id}, "
            f"scoring_system='{self.scoring_system_id}', "
            f"team1_individual={self.team1_individual_points}, "
            f"team2_individual={self.team2_individual_points}, "
            f"team1_match={self.team1_match_points}, "
            f"team2_match={self.team2_match_points})"
        )

