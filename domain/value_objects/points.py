"""
Points Value Object

Immutable value object representing league points.
Points are always non-negative.
"""

from dataclasses import dataclass
from typing import Union
from domain.exceptions.domain_exception import DomainException


class InvalidPoints(DomainException):
    """Raised when points value is invalid."""
    pass


@dataclass(frozen=True)
class Points:
    """
    Immutable value object representing league points.
    
    Points are always non-negative and can be fractional.
    """
    value: float
    
    def __post_init__(self):
        """Validate points invariants."""
        if self.value < 0:
            raise InvalidPoints(f"Points cannot be negative: {self.value}")
    
    def __add__(self, other: 'Points') -> 'Points':
        """Add two points values together."""
        return Points(self.value + other.value)
    
    def __sub__(self, other: 'Points') -> 'Points':
        """Subtract one points value from another."""
        result = self.value - other.value
        if result < 0:
            raise InvalidPoints(f"Points subtraction result cannot be negative: {result}")
        return Points(result)
    
    def __truediv__(self, divisor: Union[int, float]) -> 'Points':
        """Divide points by a number."""
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        return Points(self.value / divisor)
    
    def __mul__(self, multiplier: Union[int, float]) -> 'Points':
        """Multiply points by a number."""
        return Points(self.value * multiplier)
    
    def __lt__(self, other: 'Points') -> bool:
        """Less than comparison."""
        return self.value < other.value
    
    def __le__(self, other: 'Points') -> bool:
        """Less than or equal comparison."""
        return self.value <= other.value
    
    def __gt__(self, other: 'Points') -> bool:
        """Greater than comparison."""
        return self.value > other.value
    
    def __ge__(self, other: 'Points') -> bool:
        """Greater than or equal comparison."""
        return self.value >= other.value
    
    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if not isinstance(other, Points):
            return False
        return self.value == other.value
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Points({self.value})"
    
    def __float__(self) -> float:
        """Convert to float."""
        return float(self.value)
    
    def __int__(self) -> int:
        """Convert to int."""
        return int(self.value)

