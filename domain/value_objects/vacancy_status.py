"""
VacancyStatus Value Object

Represents the vacancy status of a team in a season.
"""

from enum import Enum


class VacancyStatus(Enum):
    """
    Team vacancy status in a league season.
    
    - ACTIVE: Team is active and participating
    - VACANT: Team position is vacant (no team assigned)
    - FORFEIT: Team has forfeited (cannot participate)
    """
    ACTIVE = "active"
    VACANT = "vacant"
    FORFEIT = "forfeit"
    
    def __str__(self) -> str:
        """String representation."""
        return self.value
    
    def can_participate(self) -> bool:
        """Check if team can participate in events."""
        return self == VacancyStatus.ACTIVE
    
    def is_available(self) -> bool:
        """Check if team position is available."""
        return self != VacancyStatus.VACANT

