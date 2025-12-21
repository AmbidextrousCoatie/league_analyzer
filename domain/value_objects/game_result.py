"""
GameResult Value Object

Immutable value object representing a single player's result in a game.
"""

from dataclasses import dataclass
from uuid import UUID
from typing import Optional
from domain.value_objects.score import Score
from domain.value_objects.points import Points
from domain.value_objects.handicap import Handicap
from domain.exceptions.domain_exception import DomainException


class InvalidGameResult(DomainException):
    """Raised when game result data is invalid."""
    pass


@dataclass(frozen=True)
class GameResult:
    """
    Immutable value object representing a player's result in a game.
    
    A game result contains:
    - player_id: The player who achieved this result
    - position: Position in the team (1-4)
    - scratch_score: The player's actual score (pins knocked down)
    - handicap: The handicap applied (optional, can be None)
    - handicap_score: The total score with handicap applied (scratch + handicap)
    - points: Points earned for the team
    - is_team_total: Whether this is a team total row
    - is_disqualified: Whether this result is disqualified
    
    Note: handicap_score is calculated from scratch_score + handicap if handicap is provided.
    If handicap is None, handicap_score equals scratch_score.
    """
    player_id: UUID
    position: int
    scratch_score: Score
    points: Points
    handicap: Optional[Handicap] = None
    is_team_total: bool = False
    is_disqualified: bool = False
    
    def __post_init__(self):
        """Validate game result invariants."""
        if self.position < 1 or self.position > 4:
            raise InvalidGameResult(
                f"Position must be between 1 and 4, got: {self.position}"
            )
        
        if self.is_team_total and self.position != 0:
            # Team totals might have position 0 or a special marker
            # This is a business rule that can be adjusted
            pass
    
    @property
    def handicap_score(self) -> Score:
        """
        Get the handicap score (scratch score + handicap).
        
        If no handicap is applied, returns the scratch score.
        By default, does not cap at 300 (handicap can push above 300).
        """
        if self.handicap is None:
            return self.scratch_score
        return self.handicap.apply_to_score(self.scratch_score, cap_at_300=False)
    
    def get_handicap_score_capped(self, cap_at_300: bool = True) -> Score:
        """
        Get the handicap score with optional capping.
        
        Args:
            cap_at_300: Whether to cap the score at 300 (default: True)
        
        Returns:
            Score with handicap applied, optionally capped at 300
        """
        if self.handicap is None:
            return self.scratch_score
        return self.handicap.apply_to_score(self.scratch_score, cap_at_300=cap_at_300)
    
    @property
    def score(self) -> Score:
        """
        Get the score (for backward compatibility).
        Returns handicap_score if handicap exists, otherwise scratch_score.
        """
        return self.handicap_score
    
    def has_handicap(self) -> bool:
        """Check if this result has handicap applied."""
        return self.handicap is not None
    
    def __post_init__(self):
        """Validate game result invariants."""
        if self.position < 1 or self.position > 4:
            raise InvalidGameResult(
                f"Position must be between 1 and 4, got: {self.position}"
            )
        
        if self.is_team_total and self.position != 0:
            # Team totals might have position 0 or a special marker
            # This is a business rule that can be adjusted
            pass
    
    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if not isinstance(other, GameResult):
            return False
        return (
            self.player_id == other.player_id and
            self.position == other.position and
            self.scratch_score == other.scratch_score and
            self.handicap == other.handicap and
            self.points == other.points and
            self.is_team_total == other.is_team_total and
            self.is_disqualified == other.is_disqualified
        )
    
    def __repr__(self) -> str:
        """String representation."""
        handicap_str = f", handicap={self.handicap}" if self.handicap else ""
        disqualified_str = ", DISQUALIFIED" if self.is_disqualified else ""
        return (
            f"GameResult(player_id={self.player_id}, position={self.position}, "
            f"scratch_score={self.scratch_score}{handicap_str}, "
            f"handicap_score={self.handicap_score}, points={self.points}, "
            f"is_team_total={self.is_team_total}{disqualified_str})"
        )

