"""
Handicap Value Object

Immutable value object representing a bowling handicap.
Handicap is additional pins added to a player's scratch score.
"""

from dataclasses import dataclass
from typing import Union
from domain.exceptions.domain_exception import DomainException


class InvalidHandicap(DomainException):
    """Raised when handicap value is invalid."""
    pass


@dataclass(frozen=True)
class Handicap:
    """
    Immutable value object representing a bowling handicap.
    
    Handicap is additional pins added to a player's scratch score.
    Handicap is typically calculated based on a player's average
    and can change during a season.
    
    Handicap is always non-negative and typically has a maximum value.
    """
    value: float
    max_handicap: float = 0.0  # 0 means no maximum
    
    def __post_init__(self):
        """Validate handicap invariants."""
        if self.value < 0:
            raise InvalidHandicap(f"Handicap cannot be negative: {self.value}")
        
        if self.max_handicap > 0 and self.value > self.max_handicap:
            raise InvalidHandicap(
                f"Handicap {self.value} exceeds maximum {self.max_handicap}"
            )
    
    def apply_to_score(
        self, 
        scratch_score: Union[float, 'Score'],
        cap_at_300: bool = False
    ) -> 'Score':
        """
        Apply handicap to a scratch score.
        
        Args:
            scratch_score: The scratch score (actual pins knocked down)
            cap_at_300: Whether to cap the final score at 300 (default: False)
        
        Returns:
            Score value object with handicap applied
        
        Raises:
            InvalidHandicap: If scratch score exceeds 300 or resulting score exceeds maximum
        """
        from domain.value_objects.score import Score
        
        if isinstance(scratch_score, Score):
            scratch_value = float(scratch_score)
        else:
            scratch_value = float(scratch_score)
        
        # Validate scratch score doesn't exceed 300
        if scratch_value > 300:
            raise InvalidHandicap(
                f"Scratch score {scratch_value} exceeds maximum 300 (perfect game)"
            )
        
        total_score = scratch_value + self.value
        
        # Apply capping if requested
        if cap_at_300:
            total_score = min(total_score, 300.0)
        
        # Check if total exceeds max_handicap limit (if set)
        if self.max_handicap > 0:
            max_total = 300.0 + self.max_handicap  # Max possible with handicap
            if total_score > max_total:
                # This shouldn't happen if handicap is properly capped
                total_score = min(total_score, max_total)
        
        return Score(total_score)
    
    def __add__(self, other: 'Handicap') -> 'Handicap':
        """Add two handicap values together."""
        new_value = self.value + other.value
        new_max = max(self.max_handicap, other.max_handicap) if self.max_handicap > 0 or other.max_handicap > 0 else 0.0
        return Handicap(value=new_value, max_handicap=new_max)
    
    def __sub__(self, other: 'Handicap') -> 'Handicap':
        """Subtract one handicap from another."""
        result = self.value - other.value
        if result < 0:
            raise InvalidHandicap(f"Handicap subtraction result cannot be negative: {result}")
        return Handicap(value=result, max_handicap=self.max_handicap)
    
    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if not isinstance(other, Handicap):
            return False
        return self.value == other.value and self.max_handicap == other.max_handicap
    
    def __lt__(self, other: 'Handicap') -> bool:
        """Less than comparison."""
        return self.value < other.value
    
    def __le__(self, other: 'Handicap') -> bool:
        """Less than or equal comparison."""
        return self.value <= other.value
    
    def __gt__(self, other: 'Handicap') -> bool:
        """Greater than comparison."""
        return self.value > other.value
    
    def __ge__(self, other: 'Handicap') -> bool:
        """Greater than or equal comparison."""
        return self.value >= other.value
    
    def __repr__(self) -> str:
        """String representation."""
        max_str = f", max={self.max_handicap}" if self.max_handicap > 0 else ""
        return f"Handicap({self.value}{max_str})"
    
    def __float__(self) -> float:
        """Convert to float."""
        return float(self.value)
    
    def __int__(self) -> int:
        """Convert to int."""
        return int(self.value)

