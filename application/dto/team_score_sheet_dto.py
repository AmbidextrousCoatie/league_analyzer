"""
Team Score Sheet Data Transfer Objects.

DTOs for team score sheet data transfer between application and presentation layers.
"""

from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID


@dataclass
class PositionScoreDTO:
    """Score and points for a specific position in a match."""
    position: int
    player_id: UUID
    player_name: str
    score: int
    opponent_player_id: UUID
    opponent_player_name: str
    opponent_score: int
    points: float  # Individual points awarded for this position


@dataclass
class MatchScoreSheetDTO:
    """Score sheet for a single match."""
    match_id: UUID
    event_id: UUID
    week: int
    round_number: int
    match_number: int  # NOTE: Unreliable in data - only for display/reference. Match identification uses (event_id, round_number, team1, team2)
    opponent_team_season_id: UUID
    opponent_team_name: str
    team_total_score: int
    opponent_total_score: int
    team_match_points: float  # Team match points (2 or 3)
    opponent_match_points: float
    position_scores: List[PositionScoreDTO]  # Scores for each position (0-3)


@dataclass
class PositionSummaryDTO:
    """Summary of points per position across all matches."""
    position: int
    total_points: float
    matches_played: int


@dataclass
class TeamScoreSheetDTO:
    """Complete team score sheet."""
    league_season_id: UUID
    league_name: str
    season: str
    team_season_id: UUID
    team_name: str
    week: Optional[int]  # If set, shows only this week; if None, shows all weeks
    matches: List[MatchScoreSheetDTO]  # Matches for the specified week(s)
    position_summaries: List[PositionSummaryDTO]  # Summary per position
    total_team_match_points: float  # Sum of all team match points
    total_individual_points: float  # Sum of all individual position points
    total_points: float  # Total points (team + individual)
    wins: int
    losses: int
    ties: int
