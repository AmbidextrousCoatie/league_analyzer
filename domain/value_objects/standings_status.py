"""
StandingsStatus Value Object

Represents the publication status of standings.
"""

from enum import Enum


class StandingsStatus(Enum):
    """
    Standings publication status.
    
    - PROVISIONAL: Standings are provisional (may change)
    - FINAL: Standings are final (official)
    - DISPUTED: Standings are under dispute
    """
    PROVISIONAL = "provisional"
    FINAL = "final"
    DISPUTED = "disputed"
    
    def __str__(self) -> str:
        """String representation."""
        return self.value
    
    def is_official(self) -> bool:
        """Check if standings are official."""
        return self == StandingsStatus.FINAL
    
    def can_be_modified(self) -> bool:
        """Check if standings can be modified."""
        return self != StandingsStatus.FINAL

