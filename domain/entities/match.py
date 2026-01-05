"""
Match Entity

Domain entity representing a match between two teams in a round-robin tournament.
Matches occur within events (weeks/days) and are organized into rounds.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from domain.exceptions.domain_exception import DomainException


class InvalidMatchData(DomainException):
    """Raised when match data is invalid."""
    pass


class MatchStatus(str, Enum):
    """Match status enumeration."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


@dataclass
class Match:
    """
    Match entity representing a match between two teams.
    
    In round-robin tournaments:
    - Each event (week/day) contains (n-1) rounds
    - Each round contains multiple matches
    - Each team plays every other team exactly once per event
    - match_number identifies concurrent matches within a round
    
    Matches are uniquely identified by (event_id, round_number, team1, team2).
    """
    id: UUID = field(default_factory=uuid4)
    event_id: UUID = field(default=None)  # Link to Event entity (required)
    round_number: int = field(default=1)  # Round number within event (required, 1 to n-1)
    match_number: int = field(default=0)  # Concurrent match identifier within round (required)
    team1_team_season_id: UUID = field(default=None)  # First team (required)
    team2_team_season_id: UUID = field(default=None)  # Second team (required)
    team1_total_score: float = field(default=0.0)  # Sum of team1 player scores (cached)
    team2_total_score: float = field(default=0.0)  # Sum of team2 player scores (cached)
    status: MatchStatus = field(default=MatchStatus.SCHEDULED)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate match invariants."""
        self._validate_required_fields()
        self._validate_round_number()
        self._validate_match_number()
        self._validate_teams()
        self._validate_scores()
    
    def _validate_required_fields(self) -> None:
        """Validate that required fields are present."""
        if self.event_id is None:
            raise InvalidMatchData("Match must have an event_id")
        if self.team1_team_season_id is None:
            raise InvalidMatchData("Match must have a team1_team_season_id")
        if self.team2_team_season_id is None:
            raise InvalidMatchData("Match must have a team2_team_season_id")
    
    def _validate_round_number(self) -> None:
        """Validate that round number is positive."""
        if self.round_number < 1:
            raise InvalidMatchData(f"Round number must be positive, got: {self.round_number}")
    
    def _validate_match_number(self) -> None:
        """Validate that match number is non-negative."""
        if self.match_number < 0:
            raise InvalidMatchData(f"Match number must be non-negative, got: {self.match_number}")
    
    def _validate_teams(self) -> None:
        """Validate that teams are different."""
        if self.team1_team_season_id == self.team2_team_season_id:
            raise InvalidMatchData("Team1 and Team2 must be different")
    
    def _validate_scores(self) -> None:
        """Validate that scores are non-negative."""
        if self.team1_total_score < 0:
            raise InvalidMatchData(f"Team1 total score must be non-negative, got: {self.team1_total_score}")
        if self.team2_total_score < 0:
            raise InvalidMatchData(f"Team2 total score must be non-negative, got: {self.team2_total_score}")
    
    def update_team1_score(self, score: float) -> None:
        """
        Update team1's total score.
        
        Args:
            score: New total score (must be non-negative)
        
        Raises:
            InvalidMatchData: If score is negative
        """
        if score < 0:
            raise InvalidMatchData(f"Team1 total score must be non-negative, got: {score}")
        self.team1_total_score = score
        self.updated_at = datetime.utcnow()
    
    def update_team2_score(self, score: float) -> None:
        """
        Update team2's total score.
        
        Args:
            score: New total score (must be non-negative)
        
        Raises:
            InvalidMatchData: If score is negative
        """
        if score < 0:
            raise InvalidMatchData(f"Team2 total score must be non-negative, got: {score}")
        self.team2_total_score = score
        self.updated_at = datetime.utcnow()
    
    def update_scores(self, team1_score: float, team2_score: float) -> None:
        """
        Update both teams' total scores.
        
        Args:
            team1_score: Team1's total score (must be non-negative)
            team2_score: Team2's total score (must be non-negative)
        
        Raises:
            InvalidMatchData: If any score is negative
        """
        if team1_score < 0:
            raise InvalidMatchData(f"Team1 total score must be non-negative, got: {team1_score}")
        if team2_score < 0:
            raise InvalidMatchData(f"Team2 total score must be non-negative, got: {team2_score}")
        self.team1_total_score = team1_score
        self.team2_total_score = team2_score
        self.updated_at = datetime.utcnow()
    
    def update_status(self, new_status: MatchStatus) -> None:
        """
        Update match status.
        
        Args:
            new_status: New status for the match
        """
        self.status = new_status
        self.updated_at = datetime.utcnow()
    
    def mark_completed(self) -> None:
        """Mark match as completed."""
        self.update_status(MatchStatus.COMPLETED)
    
    def mark_cancelled(self) -> None:
        """Mark match as cancelled."""
        self.update_status(MatchStatus.CANCELLED)
    
    def mark_in_progress(self) -> None:
        """Mark match as in progress."""
        self.update_status(MatchStatus.IN_PROGRESS)
    
    def is_completed(self) -> bool:
        """Check if match is completed."""
        return self.status == MatchStatus.COMPLETED
    
    def is_cancelled(self) -> bool:
        """Check if match is cancelled."""
        return self.status == MatchStatus.CANCELLED
    
    def get_winner(self) -> UUID | None:
        """
        Get the winning team's ID based on total scores.
        
        Returns:
            UUID of winning team, or None if tie
        """
        if self.team1_total_score > self.team2_total_score:
            return self.team1_team_season_id
        elif self.team2_total_score > self.team1_total_score:
            return self.team2_team_season_id
        else:
            return None  # Tie
    
    def is_tie(self) -> bool:
        """Check if match ended in a tie."""
        return self.team1_total_score == self.team2_total_score
    
    def __eq__(self, other: object) -> bool:
        """Equality based on ID."""
        if not isinstance(other, Match):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Match(id={self.id}, event_id={self.event_id}, round={self.round_number}, "
            f"match={self.match_number}, team1={self.team1_team_season_id}, "
            f"team2={self.team2_team_season_id}, scores={self.team1_total_score}:{self.team2_total_score}, "
            f"status={self.status})"
        )

