"""
Tests for MatchScoring entity.

Covers:
- Constructor invariants (required match_id and scoring_system_id, non-negative points)
- Behavior methods: update_individual_points, update_match_points, update_all_points,
  and total points helpers.
"""

import pytest
from uuid import uuid4

from domain.entities.match_scoring import MatchScoring, InvalidMatchScoringData


class TestMatchScoring:
    """Test cases for MatchScoring entity."""

    def _valid_kwargs(self) -> dict:
        return {
            "match_id": uuid4(),
            "scoring_system_id": "system-1",
            "team1_individual_points": 2.0,
            "team2_individual_points": 1.0,
            "team1_match_points": 2.0,
            "team2_match_points": 0.0,
        }

    def test_create_valid_match_scoring(self):
        ms = MatchScoring(**self._valid_kwargs())
        assert ms.match_id is not None
        assert ms.scoring_system_id
        assert ms.get_team1_total_points() == 4.0
        assert ms.get_team2_total_points() == 1.0

    def test_missing_match_id_raises_error(self):
        kwargs = self._valid_kwargs()
        kwargs["match_id"] = None
        with pytest.raises(InvalidMatchScoringData):
            MatchScoring(**kwargs)

    @pytest.mark.parametrize("scoring_system_id", ["", "   "])
    def test_empty_scoring_system_id_raises_error(self, scoring_system_id: str):
        kwargs = self._valid_kwargs()
        kwargs["scoring_system_id"] = scoring_system_id
        with pytest.raises(InvalidMatchScoringData):
            MatchScoring(**kwargs)

    @pytest.mark.parametrize(
        "fields",
        [
            {"team1_individual_points": -1.0},
            {"team2_individual_points": -1.0},
            {"team1_match_points": -1.0},
            {"team2_match_points": -1.0},
        ],
    )
    def test_negative_points_in_constructor_raise_error(self, fields: dict):
        kwargs = self._valid_kwargs()
        kwargs.update(fields)
        with pytest.raises(InvalidMatchScoringData):
            MatchScoring(**kwargs)

    def test_update_individual_points_positive_path(self):
        ms = MatchScoring(**self._valid_kwargs())
        ms.update_individual_points(3.0, 0.5)
        assert ms.team1_individual_points == 3.0
        assert ms.team2_individual_points == 0.5

    def test_update_individual_points_negative_raises(self):
        ms = MatchScoring(**self._valid_kwargs())
        with pytest.raises(InvalidMatchScoringData):
            ms.update_individual_points(-1.0, 0.5)
        with pytest.raises(InvalidMatchScoringData):
            ms.update_individual_points(1.0, -0.5)

    def test_update_match_points_positive_path(self):
        ms = MatchScoring(**self._valid_kwargs())
        ms.update_match_points(3.0, 1.0)
        assert ms.team1_match_points == 3.0
        assert ms.team2_match_points == 1.0

    def test_update_match_points_negative_raises(self):
        ms = MatchScoring(**self._valid_kwargs())
        with pytest.raises(InvalidMatchScoringData):
            ms.update_match_points(-1.0, 1.0)
        with pytest.raises(InvalidMatchScoringData):
            ms.update_match_points(1.0, -1.0)

    def test_update_all_points_updates_both_kinds(self):
        ms = MatchScoring(**self._valid_kwargs())
        ms.update_all_points(2.5, 1.5, 3.0, 0.0)

        assert ms.team1_individual_points == 2.5
        assert ms.team2_individual_points == 1.5
        assert ms.team1_match_points == 3.0
        assert ms.team2_match_points == 0.0

        assert ms.get_team1_total_points() == 5.5
        assert ms.get_team2_total_points() == 1.5

