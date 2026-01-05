"""
Game Result Entity

Domain entity representing a single player's raw game result in a match.
This is immutable raw data - no computed fields like points or opponent references.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from domain.exceptions.domain_exception import DomainException


class InvalidGameResultData(DomainException):
    """Raised when game result data is invalid."""
    pass


@dataclass
class GameResult:
    """
    Game result entity representing raw, immutable player performance data.
    
    This entity stores only raw data:
    - Player, team, position, score
    - Handicap and disqualification status
    
    Computed fields (points, opponent references) are stored in MatchScoring
    and PositionComparison entities.
    """
    id: UUID = field(default_factory=uuid4)
    match_id: UUID = field(default=None)  # Link to Match entity (required)
    player_id: UUID = field(default=None)  # Player who played (required)
    team_season_id: UUID = field(default=None)  # TeamSeason the player played for (required)
    position: int = field(default=0)  # Lineup position (0-3, required)
    score: float = field(default=0.0)  # Player's raw score (required)
    handicap: Optional[float] = field(default=None)  # Handicap applied (optional)
    is_disqualified: bool = field(default=False)  # Disqualification flag (optional)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate game result invariants."""
        self._validate_required_fields()
        self._validate_position()
        self._validate_score()
    
    def _validate_required_fields(self) -> None:
        """Validate that required fields are present."""
        if self.match_id is None:
            raise InvalidGameResultData("GameResult must have a match_id")
        if self.player_id is None:
            raise InvalidGameResultData("GameResult must have a player_id")
        if self.team_season_id is None:
            raise InvalidGameResultData("GameResult must have a team_season_id")
    
    def _validate_position(self) -> None:
        """Validate that position is valid (0-3)."""
        if self.position < 0 or self.position > 3:
            raise InvalidGameResultData(
                f"Position must be between 0 and 3, got: {self.position}"
            )
    
    def _validate_score(self) -> None:
        """Validate that score is non-negative."""
        if self.score < 0:
            raise InvalidGameResultData(f"Score must be non-negative, got: {self.score}")
    
    def update_score(self, new_score: float) -> None:
        """
        Update the player's score.
        
        Args:
            new_score: New score value (must be non-negative)
        
        Raises:
            InvalidGameResultData: If score is negative
        """
        if new_score < 0:
            raise InvalidGameResultData(f"Score must be non-negative, got: {new_score}")
        self.score = new_score
        self.updated_at = datetime.utcnow()
    
    def set_handicap(self, handicap: Optional[float]) -> None:
        """
        Set the handicap applied.
        
        Args:
            handicap: Handicap value (can be None, negative, zero, or positive)
        """
        self.handicap = handicap
        self.updated_at = datetime.utcnow()
    
    def disqualify(self) -> None:
        """Mark this game result as disqualified."""
        self.is_disqualified = True
        self.updated_at = datetime.utcnow()
    
    def clear_disqualification(self) -> None:
        """Clear the disqualification flag."""
        self.is_disqualified = False
        self.updated_at = datetime.utcnow()
    
    def __eq__(self, other: object) -> bool:
        """Equality based on ID."""
        if not isinstance(other, GameResult):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)
    
    def __repr__(self) -> str:
        """String representation."""
        handicap_str = f", handicap={self.handicap}" if self.handicap else ""
        dq_str = ", DISQUALIFIED" if self.is_disqualified else ""
        return (
            f"GameResult(id={self.id}, match_id={self.match_id}, player_id={self.player_id}, "
            f"team_season_id={self.team_season_id}, position={self.position}, "
            f"score={self.score}{handicap_str}{dq_str})"
        )

