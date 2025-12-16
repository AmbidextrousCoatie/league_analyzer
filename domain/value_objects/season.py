"""
Season Value Object

Immutable value object representing a bowling season.
Seasons are typically in format "YYYY-YY" (e.g., "2024-25").
"""

from dataclasses import dataclass
import re
from typing import Optional


@dataclass(frozen=True)
class Season:
    """
    Immutable value object representing a bowling season.
    
    Seasons are typically in format "YYYY-YY" (e.g., "2024-25")
    or can be special values like "all" or "latest".
    """
    value: str
    
    def __post_init__(self):
        """Validate season format."""
        if not self.value:
            raise ValueError("Season value cannot be empty")
        
        # Allow special values
        if self.value.lower() in ('all', 'latest', 'current'):
            return
        
        # Validate format: YYYY-YY or YYYY/YY
        pattern = r'^\d{4}[-/]\d{2}$'
        if not re.match(pattern, self.value):
            raise ValueError(
                f"Season must be in format YYYY-YY or YYYY/YY (e.g., '2024-25'), "
                f"or special value ('all', 'latest', 'current'). Got: {self.value}"
            )
        
        # Validate year range (e.g., 2024-25 means 2024 to 2025)
        parts = re.split(r'[-/]', self.value)
        if len(parts) == 2:
            start_year = int(parts[0])
            end_year_short = int(parts[1])
            end_year = 2000 + end_year_short if end_year_short < 100 else end_year_short
            
            if end_year != start_year + 1:
                raise ValueError(
                    f"Season end year must be start year + 1. "
                    f"Got: {self.value} (start: {start_year}, end: {end_year})"
                )
    
    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if not isinstance(other, Season):
            return False
        return self.value.lower() == other.value.lower()
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries."""
        return hash(self.value.lower())
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Season('{self.value}')"
    
    def __str__(self) -> str:
        """String conversion."""
        return self.value
    
    def is_special(self) -> bool:
        """Check if this is a special season value (all, latest, current)."""
        return self.value.lower() in ('all', 'latest', 'current')
    
    def get_start_year(self) -> Optional[int]:
        """Get the start year of the season, or None if special value."""
        if self.is_special():
            return None
        
        parts = re.split(r'[-/]', self.value)
        if len(parts) == 2:
            return int(parts[0])
        return None
    
    def get_end_year(self) -> Optional[int]:
        """Get the end year of the season, or None if special value."""
        if self.is_special():
            return None
        
        parts = re.split(r'[-/]', self.value)
        if len(parts) == 2:
            start_year = int(parts[0])
            return start_year + 1
        return None

