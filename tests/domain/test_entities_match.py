"""
Tests for Match entity.

Covers:
- Constructor invariants (required fields, non-negative scores, valid round/match numbers, different teams)
- Behavior methods for updating scores and status flags.
"""

import pytest
from uuid import uuid4
from datetime import datetime

from domain.entities.match import Match, MatchStatus, InvalidMatchData


class TestMatch:
    """Test cases for Match entity."""

    def _valid_match_kwargs(self) -> dict:
        return {
            "event_id": uuid4(),
            "round_number": 1,
            "match_number": 0,
            "team1_team_season_id": uuid4(),
            "team2_team_season_id": uuid4(),
            "team1_total_score": 0.0,
            "team2_total_score": 0.0,
        }

    def test_create_valid_match(self):
        """Match with all required fields and non-negative scores is valid."""
        m = Match(**self._valid_match_kwargs())
        assert m.event_id is not None
        assert m.team1_team_season_id != m.team2_team_season_id
        assert m.status == MatchStatus.SCHEDULED

    @pytest.mark.parametrize(
        "field",
        ["event_id", "team1_team_season_id", "team2_team_season_id"],
    )
    def test_missing_required_fields_raise_error(self, field: str):
        """Missing required IDs should raise InvalidMatchData."""
        kwargs = self._valid_match_kwargs()
        kwargs[field] = None
        with pytest.raises(InvalidMatchData):
            Match(**kwargs)

    def test_round_number_must_be_positive(self):
        kwargs = self._valid_match_kwargs()
        kwargs["round_number"] = 0
        with pytest.raises(InvalidMatchData):
            Match(**kwargs)

    def test_match_number_must_be_non_negative(self):
        kwargs = self._valid_match_kwargs()
        kwargs["match_number"] = -1
        with pytest.raises(InvalidMatchData):
            Match(**kwargs)

    def test_teams_must_be_different(self):
        team_id = uuid4()
        kwargs = self._valid_match_kwargs()
        kwargs["team1_team_season_id"] = team_id
        kwargs["team2_team_season_id"] = team_id
        with pytest.raises(InvalidMatchData):
            Match(**kwargs)

    def test_scores_must_be_non_negative(self):
        kwargs = self._valid_match_kwargs()
        kwargs["team1_total_score"] = -10
        with pytest.raises(InvalidMatchData):
            Match(**kwargs)

    def test_update_team_scores_positive_path(self):
        m = Match(**self._valid_match_kwargs())
        before = m.updated_at

        m.update_team1_score(700.0)
        m.update_team2_score(690.0)

        assert m.team1_total_score == 700.0
        assert m.team2_total_score == 690.0
        assert m.updated_at >= before

    def test_update_team_scores_negative_raises(self):
        m = Match(**self._valid_match_kwargs())
        with pytest.raises(InvalidMatchData):
            m.update_team1_score(-1.0)
        with pytest.raises(InvalidMatchData):
            m.update_team2_score(-1.0)

    def test_update_scores_both_teams(self):
        m = Match(**self._valid_match_kwargs())
        m.update_scores(720.0, 710.0)

        assert m.team1_total_score == 720.0
        assert m.team2_total_score == 710.0

    def test_update_scores_negative_raises(self):
        m = Match(**self._valid_match_kwargs())
        with pytest.raises(InvalidMatchData):
            m.update_scores(-5.0, 700.0)
        with pytest.raises(InvalidMatchData):
            m.update_scores(700.0, -5.0)

    def test_status_helpers_and_flags(self):
        m = Match(**self._valid_match_kwargs())
        assert not m.is_completed()
        assert not m.is_cancelled()

        m.mark_in_progress()
        assert m.status == MatchStatus.IN_PROGRESS

        m.mark_completed()
        assert m.status == MatchStatus.COMPLETED
        assert m.is_completed()

        m.mark_cancelled()
        assert m.status == MatchStatus.CANCELLED
        assert m.is_cancelled()

    def test_winner_and_tie_detection(self):
        kwargs = self._valid_match_kwargs()
        kwargs["team1_total_score"] = 750
        kwargs["team2_total_score"] = 700
        m = Match(**kwargs)

        assert m.get_winner() == m.team1_team_season_id
        assert not m.is_tie()

        m.update_scores(700, 750)
        assert m.get_winner() == m.team2_team_season_id
        assert not m.is_tie()

        m.update_scores(720, 720)
        assert m.get_winner() is None
        assert m.is_tie()

