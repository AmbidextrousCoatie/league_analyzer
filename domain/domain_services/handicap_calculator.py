"""
HandicapCalculator Domain Service

Calculates handicap for players based on their performance history.
Supports different calculation methods: moving window and cumulative average.
"""

from typing import List, Optional
from domain.value_objects.score import Score
from domain.value_objects.handicap import Handicap
from domain.value_objects.handicap_settings import (
    HandicapSettings,
    HandicapCalculationMethod
)
from domain.value_objects.game_result import GameResult
from domain.exceptions.domain_exception import DomainException


class InvalidHandicapCalculation(DomainException):
    """Raised when handicap calculation fails."""
    pass


class HandicapCalculator:
    """
    Domain service for calculating player handicap.
    
    Handicap is calculated based on a player's average score and
    can use different methods (moving window or cumulative average).
    """
    
    @staticmethod
    def calculate_handicap(
        game_results: List[GameResult],
        settings: HandicapSettings
    ) -> Optional[Handicap]:
        """
        Calculate handicap for a player based on their game results.
        
        Args:
            game_results: List of GameResult objects (scratch scores)
            settings: HandicapSettings configuration
        
        Returns:
            Handicap value object, or None if not enough data or disabled
        
        Raises:
            InvalidHandicapCalculation: If calculation fails
        """
        if not settings.enabled:
            return None
        
        if not game_results:
            return None
        
        # Get scratch scores (not handicap scores)
        scratch_scores = [
            float(result.scratch_score) for result in game_results
            if not result.is_team_total
        ]
        
        if not scratch_scores:
            return None
        
        # Calculate average based on method
        if settings.calculation_method == HandicapCalculationMethod.MOVING_WINDOW:
            average = HandicapCalculator._calculate_moving_window_average(
                scratch_scores,
                settings.moving_window_size
            )
        elif settings.calculation_method == HandicapCalculationMethod.CUMULATIVE_AVERAGE:
            average = HandicapCalculator._calculate_cumulative_average(scratch_scores)
        elif settings.calculation_method == HandicapCalculationMethod.FIXED:
            # Fixed handicap - not calculated from scores
            return None
        else:
            raise InvalidHandicapCalculation(
                f"Unknown calculation method: {settings.calculation_method}"
            )
        
        # Calculate handicap using settings
        handicap_value = settings.calculate_handicap(average)
        
        # Create Handicap value object
        return Handicap(
            value=handicap_value,
            max_handicap=settings.max_handicap if settings.max_handicap else 0.0
        )
    
    @staticmethod
    def _calculate_moving_window_average(
        scores: List[float],
        window_size: Optional[int]
    ) -> float:
        """
        Calculate average using moving window.
        
        Args:
            scores: List of scratch scores (most recent first)
            window_size: Number of games to include (None = all games)
        
        Returns:
            Average score
        """
        if not scores:
            raise InvalidHandicapCalculation("No scores provided for moving window")
        
        # If window_size is None, use all scores
        if window_size is None:
            window_size = len(scores)
        
        # Take the most recent N games
        recent_scores = scores[:window_size]
        
        if not recent_scores:
            raise InvalidHandicapCalculation("No scores in moving window")
        
        return sum(recent_scores) / len(recent_scores)
    
    @staticmethod
    def _calculate_cumulative_average(scores: List[float]) -> float:
        """
        Calculate cumulative average (all games in season).
        
        Args:
            scores: List of all scratch scores
        
        Returns:
            Average score
        """
        if not scores:
            raise InvalidHandicapCalculation("No scores provided for cumulative average")
        
        return sum(scores) / len(scores)
    
    @staticmethod
    def apply_handicap_with_capping(
        scratch_score: Score,
        handicap: Handicap,
        settings: HandicapSettings
    ) -> Score:
        """
        Apply handicap to scratch score with capping based on settings.
        
        Args:
            scratch_score: The scratch score
            handicap: The handicap to apply
            settings: HandicapSettings with capping configuration
        
        Returns:
            Score with handicap applied (optionally capped)
        """
        # Validate scratch score doesn't exceed maximum
        if float(scratch_score) > settings.scratch_score_max:
            raise InvalidHandicapCalculation(
                f"Scratch score {scratch_score} exceeds maximum {settings.scratch_score_max}"
            )
        
        # Apply handicap with capping
        final_score = settings.apply_handicap_to_score(
            float(scratch_score),
            float(handicap)
        )
        
        return Score(final_score)
    
    @staticmethod
    def recalculate_handicap_for_season(
        game_results: List[GameResult],
        settings: HandicapSettings,
        current_handicap: Optional[Handicap] = None
    ) -> Optional[Handicap]:
        """
        Recalculate handicap based on updated game results.
        
        This is called when new games are played and handicap needs updating.
        
        Args:
            game_results: All game results for the player in the season
            settings: HandicapSettings configuration
            current_handicap: Current handicap (for comparison)
        
        Returns:
            Updated Handicap, or None if unchanged or disabled
        """
        new_handicap = HandicapCalculator.calculate_handicap(game_results, settings)
        
        # Return None if handicap hasn't changed
        if current_handicap is not None and new_handicap is not None:
            if new_handicap == current_handicap:
                return None  # No change
        
        return new_handicap

