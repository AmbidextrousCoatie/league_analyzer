"""
Game Entity

Domain entity representing a bowling game/match.
Games contain results and enforce business rules.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import List, Optional
from domain.value_objects.handicap import Handicap
from domain.value_objects.season import Season
from domain.value_objects.game_result import GameResult
from domain.domain_events.domain_event import (
    GameCreated,
    GameUpdated,
    GameResultAdded,
    GameResultUpdated
)
from domain.domain_events.event_bus import DomainEventBus
from domain.exceptions.domain_exception import InvalidGameData, DuplicateGame


@dataclass
class Game:
    """
    Game entity with business logic.
    
    Games represent a match between two teams in a league.
    Games contain results for each player.
    Games belong to an Event (league week/day).
    """
    id: UUID = field(default_factory=uuid4)
    event_id: Optional[UUID] = field(default=None)  # Link to Event entity
    league_id: UUID = field(default=None)
    season: Season = field(default=None)
    week: int = field(default=0)
    round_number: int = field(default=1)
    match_number: int = field(default=0)  # Match number within event
    date: datetime = field(default_factory=datetime.utcnow)
    team_id: UUID = field(default=None)
    opponent_team_id: UUID = field(default=None)
    results: List[GameResult] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate game invariants."""
        self._validate_teams_different()
        self._validate_week_positive()
        self._validate_round_positive()
    
    def _validate_teams_different(self) -> None:
        """Validate that teams are different."""
        if self.team_id is not None and self.opponent_team_id is not None:
            if self.team_id == self.opponent_team_id:
                raise InvalidGameData("Team cannot play against itself")
    
    def _validate_week_positive(self) -> None:
        """Validate that week is positive."""
        if self.week < 0:
            raise InvalidGameData(f"Week must be positive, got: {self.week}")
    
    def _validate_round_positive(self) -> None:
        """Validate that round number is positive."""
        if self.round_number < 0:
            raise InvalidGameData(f"Round number must be positive, got: {self.round_number}")
    
    def add_result(self, result: GameResult) -> None:
        """
        Add a game result for a player.
        
        Args:
            result: GameResult value object
        
        Raises:
            InvalidGameData: If player already has a result for this game
        """
        # Check if player already has a result
        existing_result = self._find_result(result.player_id)
        if existing_result is not None:
            raise InvalidGameData(
                f"Player {result.player_id} already has a result for this game"
            )
        
        self.results.append(result)
        self.updated_at = datetime.utcnow()
        
        # Publish domain event
        DomainEventBus.publish(
            GameResultAdded(
                game_id=self.id,
                player_id=result.player_id,
                score=float(result.handicap_score)  # Use handicap_score for event
            )
        )
    
    def update_result(
        self, 
        player_id: UUID, 
        new_scratch_score: float, 
        new_points: float,
        handicap: Optional['Handicap'] = None,
        is_disqualified: Optional[bool] = None
    ) -> None:
        """
        Update a game result for a player.
        
        Args:
            player_id: UUID of the player
            new_scratch_score: New scratch score value (actual pins)
            new_points: New points value
            handicap: Optional handicap to apply (if None, keeps existing handicap)
            is_disqualified: Optional disqualification flag (if None, keeps existing)
        
        Raises:
            InvalidGameData: If result not found
        """
        result = self._find_result(player_id)
        if result is None:
            raise InvalidGameData(f"Result not found for player {player_id}")
        
        old_score = float(result.handicap_score)
        
        # Create new result with updated values
        from domain.value_objects.score import Score
        from domain.value_objects.points import Points
        
        # Use provided handicap or keep existing
        updated_handicap = handicap if handicap is not None else result.handicap
        
        # Use provided disqualification flag or keep existing
        updated_disqualified = (
            is_disqualified if is_disqualified is not None 
            else result.is_disqualified
        )
        
        new_result = GameResult(
            player_id=result.player_id,
            position=result.position,
            scratch_score=Score(new_scratch_score),
            points=Points(new_points),
            handicap=updated_handicap,
            is_team_total=result.is_team_total,
            is_disqualified=updated_disqualified
        )
        
        # Replace the result
        index = self.results.index(result)
        self.results[index] = new_result
        self.updated_at = datetime.utcnow()
        
        # Publish domain event
        DomainEventBus.publish(
            GameResultUpdated(
                game_id=self.id,
                player_id=player_id,
                old_score=old_score,
                new_score=float(new_result.handicap_score)
            )
        )
    
    def remove_result(self, player_id: UUID) -> None:
        """
        Remove a game result for a player.
        
        Args:
            player_id: UUID of the player
        
        Raises:
            InvalidGameData: If result not found
        """
        result = self._find_result(player_id)
        if result is None:
            raise InvalidGameData(f"Result not found for player {player_id}")
        
        self.results.remove(result)
        self.updated_at = datetime.utcnow()
    
    def _find_result(self, player_id: UUID) -> Optional[GameResult]:
        """Find a result for a specific player."""
        for result in self.results:
            if result.player_id == player_id:
                return result
        return None
    
    def get_team_total_score(self, team_id: UUID) -> float:
        """
        Get the total score for a team in this game.
        
        Args:
            team_id: UUID of the team
        
        Returns:
            Total score as float
        """
        # This would need to filter results by team
        # For now, return sum of all scores (simplified)
        total = 0.0
        for result in self.results:
            if not result.is_team_total:  # Exclude team totals from calculation
                total += float(result.score)
        return total
    
    def get_team_total_points(self, team_id: UUID) -> float:
        """
        Get the total points for a team in this game.
        
        Args:
            team_id: UUID of the team
        
        Returns:
            Total points as float
        """
        total = 0.0
        for result in self.results:
            if not result.is_team_total:  # Exclude team totals from calculation
                total += float(result.points)
        return total
    
    def update_teams(self, team_id: UUID, opponent_team_id: UUID) -> None:
        """
        Update the teams playing in this game.
        
        Args:
            team_id: UUID of the team
            opponent_team_id: UUID of the opponent team
        
        Raises:
            InvalidGameData: If teams are the same
        """
        if team_id == opponent_team_id:
            raise InvalidGameData("Team cannot play against itself")
        
        self.team_id = team_id
        self.opponent_team_id = opponent_team_id
        self.updated_at = datetime.utcnow()
        
        # Publish domain event
        DomainEventBus.publish(
            GameUpdated(game_id=self.id, league_id=self.league_id)
        )
    
    def update_week(self, week: int) -> None:
        """
        Update the week number.
        
        Args:
            week: Week number (must be positive)
        
        Raises:
            InvalidGameData: If week is negative
        """
        if week < 0:
            raise InvalidGameData(f"Week must be positive, got: {week}")
        
        self.week = week
        self.updated_at = datetime.utcnow()
        
        # Publish domain event
        DomainEventBus.publish(
            GameUpdated(game_id=self.id, league_id=self.league_id)
        )
    
    def __eq__(self, other: object) -> bool:
        """Equality based on ID."""
        if not isinstance(other, Game):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)
    
    def update_match_number(self, match_number: int) -> None:
        """
        Update match number.
        
        Args:
            match_number: Match number (must be non-negative)
        
        Raises:
            InvalidGameData: If match number is negative
        """
        if match_number < 0:
            raise InvalidGameData(f"Match number must be non-negative, got: {match_number}")
        self.match_number = match_number
        self.updated_at = datetime.utcnow()
    
    def assign_to_event(self, event_id: UUID) -> None:
        """
        Assign game to an event.
        
        Args:
            event_id: UUID of the event
        """
        self.event_id = event_id
        self.updated_at = datetime.utcnow()
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Game(id={self.id}, event_id={self.event_id}, league_id={self.league_id}, "
            f"season={self.season}, week={self.week}, match_number={self.match_number}, "
            f"team_id={self.team_id}, opponent_team_id={self.opponent_team_id}, "
            f"results={len(self.results)})"
        )

