"""
Position Comparison Entity

Domain entity representing the comparison of two players at the same position in a match.
Used for calculating individual points in round-robin tournaments.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from domain.exceptions.domain_exception import DomainException


class InvalidPositionComparisonData(DomainException):
    """Raised when position comparison data is invalid."""
    pass


class ComparisonOutcome(str, Enum):
    """Outcome of a position comparison."""
    TEAM1_WIN = "team1_win"
    TEAM2_WIN = "team2_win"
    TIE = "tie"


@dataclass
class PositionComparison:
    """
    Position comparison entity representing a head-to-head comparison.
    
    In round-robin tournaments, players at the same position (0-3) are compared
    to determine individual points. Each position comparison contributes to the
    team's total individual points.
    """
    id: UUID = field(default_factory=uuid4)
    match_id: UUID = field(default=None)  # Link to Match entity (required)
    position: int = field(default=0)  # Lineup position (0-3, required)
    team1_player_id: UUID = field(default=None)  # Team1's player at this position (required)
    team2_player_id: UUID = field(default=None)  # Team2's player at this position (required)
    team1_score: float = field(default=0.0)  # Team1 player's score (required)
    team2_score: float = field(default=0.0)  # Team2 player's score (required)
    outcome: ComparisonOutcome = field(default=ComparisonOutcome.TIE)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate position comparison invariants."""
        self._validate_required_fields()
        self._validate_position()
        self._validate_scores()
        # Auto-determine outcome if not set
        if self.outcome == ComparisonOutcome.TIE:
            self._determine_outcome()
    
    def _validate_required_fields(self) -> None:
        """Validate that required fields are present."""
        if self.match_id is None:
            raise InvalidPositionComparisonData("PositionComparison must have a match_id")
        if self.team1_player_id is None:
            raise InvalidPositionComparisonData("PositionComparison must have a team1_player_id")
        if self.team2_player_id is None:
            raise InvalidPositionComparisonData("PositionComparison must have a team2_player_id")
    
    def _validate_position(self) -> None:
        """Validate that position is valid (0-3)."""
        if self.position < 0 or self.position > 3:
            raise InvalidPositionComparisonData(
                f"Position must be between 0 and 3, got: {self.position}"
            )
    
    def _validate_scores(self) -> None:
        """Validate that scores are non-negative."""
        if self.team1_score < 0:
            raise InvalidPositionComparisonData(
                f"Team1 score must be non-negative, got: {self.team1_score}"
            )
        if self.team2_score < 0:
            raise InvalidPositionComparisonData(
                f"Team2 score must be non-negative, got: {self.team2_score}"
            )
    
    def _determine_outcome(self) -> None:
        """Determine outcome based on scores."""
        if self.team1_score > self.team2_score:
            self.outcome = ComparisonOutcome.TEAM1_WIN
        elif self.team2_score > self.team1_score:
            self.outcome = ComparisonOutcome.TEAM2_WIN
        else:
            self.outcome = ComparisonOutcome.TIE
    
    def update_scores(self, team1_score: float, team2_score: float) -> None:
        """
        Update scores and recalculate outcome.
        
        Args:
            team1_score: Team1 player's score (must be non-negative)
            team2_score: Team2 player's score (must be non-negative)
        
        Raises:
            InvalidPositionComparisonData: If any score is negative
        """
        if team1_score < 0:
            raise InvalidPositionComparisonData(
                f"Team1 score must be non-negative, got: {team1_score}"
            )
        if team2_score < 0:
            raise InvalidPositionComparisonData(
                f"Team2 score must be non-negative, got: {team2_score}"
            )
        self.team1_score = team1_score
        self.team2_score = team2_score
        self._determine_outcome()
        self.updated_at = datetime.utcnow()
    
    def is_team1_win(self) -> bool:
        """Check if team1 won this position."""
        return self.outcome == ComparisonOutcome.TEAM1_WIN
    
    def is_team2_win(self) -> bool:
        """Check if team2 won this position."""
        return self.outcome == ComparisonOutcome.TEAM2_WIN
    
    def is_tie(self) -> bool:
        """Check if this position ended in a tie."""
        return self.outcome == ComparisonOutcome.TIE
    
    def __eq__(self, other: object) -> bool:
        """Equality based on ID."""
        if not isinstance(other, PositionComparison):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"PositionComparison(id={self.id}, match_id={self.match_id}, position={self.position}, "
            f"team1_player={self.team1_player_id}, team2_player={self.team2_player_id}, "
            f"scores={self.team1_score}:{self.team2_score}, outcome={self.outcome})"
        )

