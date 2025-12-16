"""
Tests for HandicapCalculator domain service.
"""

import pytest
from uuid import uuid4
from domain.domain_services.handicap_calculator import (
    HandicapCalculator,
    InvalidHandicapCalculation
)
from domain.value_objects import (
    Score, Points, GameResult, HandicapSettings, HandicapCalculationMethod,
    Handicap
)
from tests.conftest import create_game_results


class TestHandicapCalculator:
    """Test cases for HandicapCalculator domain service."""
    
    def test_calculate_handicap_cumulative_average(self, sample_handicap_settings):
        """Test calculating handicap using cumulative average."""
        player_id = uuid4()
        scores = [180, 190, 185, 195, 200]  # Average = 190
        results = create_game_results(player_id, scores)
        
        handicap = HandicapCalculator.calculate_handicap(results, sample_handicap_settings)
        
        assert handicap is not None
        # (200 - 190) * 0.9 = 9.0
        assert handicap.value == 9.0
    
    def test_calculate_handicap_moving_window(self, sample_handicap_settings_moving_window):
        """Test calculating handicap using moving window."""
        player_id = uuid4()
        scores = [150, 160, 170, 180, 190]  # Last 5 (window_size=5): [150, 160, 170, 180, 190], Average = 170
        results = create_game_results(player_id, scores)
        
        handicap = HandicapCalculator.calculate_handicap(
            results, 
            sample_handicap_settings_moving_window
        )
        
        assert handicap is not None
        # (200 - 170) * 0.9 = 27.0
        assert handicap.value == 27.0
    
    def test_calculate_handicap_disabled(self):
        """Test that disabled handicap returns None."""
        settings = HandicapSettings(enabled=False)
        player_id = uuid4()
        results = create_game_results(player_id, [180, 190, 200])
        
        handicap = HandicapCalculator.calculate_handicap(results, settings)
        assert handicap is None
    
    def test_calculate_handicap_no_results(self, sample_handicap_settings):
        """Test that no results returns None."""
        handicap = HandicapCalculator.calculate_handicap([], sample_handicap_settings)
        assert handicap is None
    
    def test_calculate_handicap_max_cap(self, sample_handicap_settings):
        """Test that handicap is capped at max_handicap."""
        player_id = uuid4()
        # Very low average to trigger max cap
        scores = [100, 110, 120]  # Average = 110, handicap would be (200-110)*0.9 = 81
        results = create_game_results(player_id, scores)
        
        handicap = HandicapCalculator.calculate_handicap(results, sample_handicap_settings)
        
        assert handicap is not None
        # Should be capped at 50.0 (max_handicap)
        assert handicap.value == 50.0
    
    def test_apply_handicap_with_capping(self, sample_handicap_settings):
        """Test applying handicap with score capping."""
        scratch = Score(280.0)
        handicap = Handicap(30.0)
        
        result = HandicapCalculator.apply_handicap_with_capping(
            scratch, handicap, sample_handicap_settings
        )
        
        # Should be capped at 300
        assert result.value == 300.0
    
    def test_apply_handicap_without_capping(self):
        """Test applying handicap without capping."""
        settings = HandicapSettings(
            enabled=True,
            cap_handicap_score=False
        )
        scratch = Score(280.0)
        handicap = Handicap(30.0)
        
        result = HandicapCalculator.apply_handicap_with_capping(
            scratch, handicap, settings
        )
        
        # Should not be capped
        assert result.value == 310.0
    
    def test_recalculate_handicap_for_season(self, sample_handicap_settings):
        """Test recalculating handicap when new games are played."""
        player_id = uuid4()
        initial_scores = [180, 190, 200]  # Average = 190
        initial_results = create_game_results(player_id, initial_scores)
        
        initial_handicap = HandicapCalculator.calculate_handicap(
            initial_results, 
            sample_handicap_settings
        )
        
        # Add more games
        new_scores = [200, 210]  # New average = 196.67
        new_results = initial_results + create_game_results(player_id, new_scores)
        
        updated_handicap = HandicapCalculator.recalculate_handicap_for_season(
            new_results,
            sample_handicap_settings,
            initial_handicap
        )
        
        assert updated_handicap is not None
        # New handicap should be different (lower, since average increased)
        assert updated_handicap.value < initial_handicap.value
    
    def test_recalculate_handicap_no_change(self, sample_handicap_settings):
        """Test that recalculation returns None if handicap unchanged."""
        player_id = uuid4()
        scores = [180, 190, 200]
        results = create_game_results(player_id, scores)
        
        initial_handicap = HandicapCalculator.calculate_handicap(
            results, 
            sample_handicap_settings
        )
        
        # Recalculate with same results
        updated = HandicapCalculator.recalculate_handicap_for_season(
            results,
            sample_handicap_settings,
            initial_handicap
        )
        
        # Should return None (no change)
        assert updated is None
    
    @pytest.mark.parametrize("scores,expected_avg", [
        ([180, 190, 200], 190.0),
        ([150, 160, 170, 180, 190], 170.0),
        ([200, 200, 200], 200.0),
    ])
    def test_cumulative_average_calculation(self, scores, expected_avg, sample_handicap_settings):
        """Test cumulative average calculation with various scores."""
        player_id = uuid4()
        results = create_game_results(player_id, scores)
        
        handicap = HandicapCalculator.calculate_handicap(results, sample_handicap_settings)
        
        # Verify calculation: (200 - expected_avg) * 0.9
        expected_handicap = (200.0 - expected_avg) * 0.9
        expected_handicap = min(expected_handicap, 50.0)  # Apply max cap
        expected_handicap = max(expected_handicap, 0.0)  # Cannot be negative
        
        assert handicap.value == pytest.approx(expected_handicap, rel=0.01)

