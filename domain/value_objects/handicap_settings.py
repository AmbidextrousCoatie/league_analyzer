"""
HandicapSettings Value Object

Immutable value object representing handicap configuration for a league/tournament.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class HandicapCalculationMethod(Enum):
    """Method for calculating handicap."""
    MOVING_WINDOW = "moving_window"  # Based on last N games
    CUMULATIVE_AVERAGE = "cumulative_average"  # Based on all games in season
    FIXED = "fixed"  # Fixed handicap value


@dataclass(frozen=True)
class HandicapSettings:
    """
    Immutable value object representing handicap configuration.
    
    Defines how handicap is calculated and what limits apply.
    """
    enabled: bool = False
    calculation_method: HandicapCalculationMethod = HandicapCalculationMethod.CUMULATIVE_AVERAGE
    base_average: float = 200.0  # Base average for handicap calculation (e.g., 200)
    percentage: float = 0.9  # Percentage of difference (e.g., 90% = 0.9)
    max_handicap: Optional[float] = None  # Maximum handicap value (None = no limit)
    moving_window_size: Optional[int] = None  # Number of games for moving window (None = all games)
    cap_handicap_score: bool = True  # Cap final handicap score at 300
    scratch_score_max: float = 300.0  # Maximum scratch score (perfect game)
    
    def __post_init__(self):
        """Validate handicap settings."""
        if self.base_average < 0:
            raise ValueError(f"Base average must be non-negative, got: {self.base_average}")
        
        if not 0 <= self.percentage <= 1:
            raise ValueError(f"Percentage must be between 0 and 1, got: {self.percentage}")
        
        if self.max_handicap is not None and self.max_handicap < 0:
            raise ValueError(f"Max handicap must be non-negative, got: {self.max_handicap}")
        
        if self.moving_window_size is not None and self.moving_window_size < 1:
            raise ValueError(
                f"Moving window size must be at least 1, got: {self.moving_window_size}"
            )
        
        if self.scratch_score_max < 0:
            raise ValueError(
                f"Scratch score max must be non-negative, got: {self.scratch_score_max}"
            )
    
    def calculate_handicap(self, player_average: float) -> float:
        """
        Calculate handicap based on player average.
        
        Formula: (base_average - player_average) * percentage
        
        Args:
            player_average: Player's average score
        
        Returns:
            Calculated handicap value (before capping)
        """
        if not self.enabled:
            return 0.0
        
        handicap = (self.base_average - player_average) * self.percentage
        
        # Apply max handicap cap if set
        if self.max_handicap is not None:
            handicap = min(handicap, self.max_handicap)
        
        # Handicap cannot be negative
        return max(0.0, handicap)
    
    def apply_handicap_to_score(
        self, 
        scratch_score: float, 
        handicap_value: float
    ) -> float:
        """
        Apply handicap to scratch score with optional capping.
        
        Args:
            scratch_score: The scratch score
            handicap_value: The handicap value to apply
        
        Returns:
            Final score (scratch + handicap, optionally capped at 300)
        """
        total_score = scratch_score + handicap_value
        
        if self.cap_handicap_score:
            # Cap at perfect game (300) or scratch_score_max
            return min(total_score, self.scratch_score_max)
        
        return total_score

