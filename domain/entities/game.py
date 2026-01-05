"""
Game Entity

Domain entity representing a single player's game result in a match.
Each Game represents one player's performance in one match.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from domain.exceptions.domain_exception import InvalidGameData


@dataclass
class Game:
    """
    Game entity representing a single player's game result.
    
    Each Game represents one player's performance in one match.
    Games belong to an Event (league week/day) and are part of a match
    between two teams (TeamSeasons).
    """
    id: UUID = field(default_factory=uuid4)
    event_id: UUID = field(default=None)  # Link to Event entity (required)
    player_id: UUID = field(default=None)  # Player who played (required)
    team_season_id: UUID = field(default=None)  # TeamSeason the player played for (required)
    position: int = field(default=0)  # Lineup position (0-3, required)
    match_number: int = field(default=0)  # Match number within event (required)
    round_number: int = field(default=1)  # Round number (required)
    score: float = field(default=0.0)  # Player's score (required)
    points: float = field(default=0.0)  # Points earned (required)
    opponent_id: Optional[UUID] = field(default=None)  # Player ID of opponent at same position (optional)
    opponent_team_season_id: Optional[UUID] = field(default=None)  # TeamSeason ID of opponent team (optional)
    handicap: Optional[float] = field(default=None)  # Handicap applied (optional)
    is_disqualified: bool = field(default=False)  # Disqualification flag (optional)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate game invariants."""
        self._validate_required_fields()
        self._validate_position()
        self._validate_match_number()
        self._validate_round_number()
        self._validate_score()
        self._validate_points()
    
    def _validate_required_fields(self) -> None:
        """Validate that required fields are present."""
        if self.event_id is None:
            raise InvalidGameData("Game must have an event_id")
        if self.player_id is None:
            raise InvalidGameData("Game must have a player_id")
        if self.team_season_id is None:
            raise InvalidGameData("Game must have a team_season_id")
    
    def _validate_position(self) -> None:
        """Validate that position is valid (0-3)."""
        if self.position < 0 or self.position > 3:
            raise InvalidGameData(f"Position must be between 0 and 3, got: {self.position}")
    
    def _validate_match_number(self) -> None:
        """Validate that match number is non-negative."""
        if self.match_number < 0:
            raise InvalidGameData(f"Match number must be non-negative, got: {self.match_number}")
    
    def _validate_round_number(self) -> None:
        """Validate that round number is positive."""
        if self.round_number < 1:
            raise InvalidGameData(f"Round number must be positive, got: {self.round_number}")
    
    def _validate_score(self) -> None:
        """Validate that score is non-negative."""
        if self.score < 0:
            raise InvalidGameData(f"Score must be non-negative, got: {self.score}")
    
    def _validate_points(self) -> None:
        """Validate that points is non-negative."""
        if self.points < 0:
            raise InvalidGameData(f"Points must be non-negative, got: {self.points}")
    
    def update_score(self, new_score: float) -> None:
        """
        Update the player's score.
        
        Args:
            new_score: New score value (must be non-negative)
        
        Raises:
            InvalidGameData: If score is negative
        """
        if new_score < 0:
            raise InvalidGameData(f"Score must be non-negative, got: {new_score}")
        self.score = new_score
        self.updated_at = datetime.utcnow()
    
    def update_points(self, new_points: float) -> None:
        """
        Update the points earned.
        
        Args:
            new_points: New points value (must be non-negative)
        
        Raises:
            InvalidGameData: If points is negative
        """
        if new_points < 0:
            raise InvalidGameData(f"Points must be non-negative, got: {new_points}")
        self.points = new_points
        self.updated_at = datetime.utcnow()
    
    def set_opponent(self, opponent_id: UUID, opponent_team_season_id: UUID) -> None:
        """
        Set the opponent information.
        
        Args:
            opponent_id: Player ID of the opponent at the same position
            opponent_team_season_id: TeamSeason ID of the opponent team
        """
        self.opponent_id = opponent_id
        self.opponent_team_season_id = opponent_team_season_id
        self.updated_at = datetime.utcnow()
    
    def set_handicap(self, handicap: float) -> None:
        """
        Set the handicap applied.
        
        Args:
            handicap: Handicap value (can be negative, zero, or positive)
        """
        self.handicap = handicap
        self.updated_at = datetime.utcnow()
    
    def disqualify(self) -> None:
        """Mark this game result as disqualified."""
        self.is_disqualified = True
        self.updated_at = datetime.utcnow()
    
    def clear_disqualification(self) -> None:
        """Clear the disqualification flag."""
        self.is_disqualified = False
        self.updated_at = datetime.utcnow()
    
    def __eq__(self, other: object) -> bool:
        """Equality based on ID."""
        if not isinstance(other, Game):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)
    
    def __repr__(self) -> str:
        """String representation."""
        opponent_str = f", opponent={self.opponent_id}" if self.opponent_id else ""
        handicap_str = f", handicap={self.handicap}" if self.handicap else ""
        dq_str = ", DISQUALIFIED" if self.is_disqualified else ""
        return (
            f"Game(id={self.id}, event_id={self.event_id}, player_id={self.player_id}, "
            f"team_season_id={self.team_season_id}, position={self.position}, "
            f"match={self.match_number}, round={self.round_number}, "
            f"score={self.score}, points={self.points}{opponent_str}{handicap_str}{dq_str})"
        )
