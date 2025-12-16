"""
Score Value Object

Immutable value object representing a bowling score.
Validates that scores are within acceptable range (0-300).
"""

from dataclasses import dataclass
from typing import Union
from domain.exceptions.domain_exception import InvalidScore


@dataclass(frozen=True)
class Score:
    """
    Immutable value object representing a bowling score.
    
    Bowling scores must be between 0 and 300 (perfect game).
    """
    value: float
    
    def __post_init__(self):
        """
        Validate score invariants.
        
        Scratch scores must be between 0 and 300 (perfect game).
        Handicap scores can exceed 300 if handicap is applied.
        """
        if self.value < 0:
            raise InvalidScore(f"Score cannot be negative: {self.value}")
        # Note: We allow scores > 300 for handicap scores
        # Validation for scratch scores should be done at creation time
        # This allows handicap to push scores above 300
    
    def __add__(self, other: 'Score') -> 'Score':
        """Add two scores together."""
        return Score(self.value + other.value)
    
    def __sub__(self, other: 'Score') -> 'Score':
        """Subtract one score from another."""
        result = self.value - other.value
        if result < 0:
            raise InvalidScore(f"Score subtraction result cannot be negative: {result}")
        return Score(result)
    
    def __truediv__(self, divisor: Union[int, float]) -> 'Score':
        """Divide score by a number."""
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        return Score(self.value / divisor)
    
    def __mul__(self, multiplier: Union[int, float]) -> 'Score':
        """Multiply score by a number."""
        return Score(self.value * multiplier)
    
    def __lt__(self, other: 'Score') -> bool:
        """Less than comparison."""
        return self.value < other.value
    
    def __le__(self, other: 'Score') -> bool:
        """Less than or equal comparison."""
        return self.value <= other.value
    
    def __gt__(self, other: 'Score') -> bool:
        """Greater than comparison."""
        return self.value > other.value
    
    def __ge__(self, other: 'Score') -> bool:
        """Greater than or equal comparison."""
        return self.value >= other.value
    
    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if not isinstance(other, Score):
            return False
        return self.value == other.value
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Score({self.value})"
    
    def __float__(self) -> float:
        """Convert to float."""
        return float(self.value)
    
    def __int__(self) -> int:
        """Convert to int."""
        return int(self.value)

