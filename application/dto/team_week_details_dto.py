"""
Team Week Details Data Transfer Objects.

DTOs for team week details data transfer between application and presentation layers.
"""

from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID


@dataclass
class PlayerWeekPerformanceDTO:
    """Player performance for a specific week."""
    player_id: UUID
    player_name: str
    position: int
    score: int
    points: float
    opponent_player_name: Optional[str] = None
    opponent_score: Optional[int] = None


@dataclass
class MatchWeekSummaryDTO:
    """Summary of a match in the week."""
    match_id: UUID
    opponent_team_season_id: UUID
    opponent_team_name: str
    team_total_score: int
    opponent_total_score: int
    team_match_points: float
    opponent_match_points: float
    result: str  # "win", "loss", "tie"


@dataclass
class TeamWeekDetailsDTO:
    """Complete team week details."""
    team_season_id: UUID
    team_name: str
    league_season_id: UUID
    league_name: str
    season: str
    week: int
    matches: List[MatchWeekSummaryDTO]  # All matches for this week
    player_performances: List[PlayerWeekPerformanceDTO]  # All player performances
    total_team_score: int  # Sum of all team scores for the week
    total_team_match_points: float  # Sum of team match points
    total_individual_points: float  # Sum of individual position points
    total_points: float  # Total points (team + individual)
    wins: int
    losses: int
    ties: int
    average_score: float  # Average team score per match
    number_of_matches: int
