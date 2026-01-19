"""
Team vs Team Comparison Data Transfer Objects.

DTOs for team vs team comparison data transfer between application and presentation layers.
"""

from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID
from datetime import datetime


@dataclass
class MatchComparisonDTO:
    """Details of a single match between the two teams."""
    match_id: UUID
    event_id: UUID
    league_week: Optional[int]
    round_number: int
    match_number: int
    team1_total_score: int
    team2_total_score: int
    team1_match_points: float
    team2_match_points: float
    team1_individual_points: float
    team2_individual_points: float
    team1_total_points: float
    team2_total_points: float
    result: str  # "team1_win", "team2_win", "tie"
    date: Optional[datetime] = None


@dataclass
class PositionComparisonDTO:
    """Position-by-position comparison across all matches."""
    position: int
    team1_wins: int
    team2_wins: int
    ties: int
    team1_total_score: int
    team2_total_score: int
    team1_average_score: float
    team2_average_score: float
    team1_total_points: float
    team2_total_points: float


@dataclass
class TeamVsTeamComparisonDTO:
    """Complete head-to-head comparison between two teams."""
    team1_season_id: UUID
    team1_name: str
    team2_season_id: UUID
    team2_name: str
    league_season_id: UUID
    league_name: str
    season: str
    
    # Overall statistics
    matches_played: int
    team1_wins: int
    team2_wins: int
    ties: int
    
    # Total scores
    team1_total_score: int
    team2_total_score: int
    team1_average_score: float
    team2_average_score: float
    
    # Total points
    team1_total_match_points: float
    team2_total_match_points: float
    team1_total_individual_points: float
    team2_total_individual_points: float
    team1_total_points: float
    team2_total_points: float
    
    # Match-by-match breakdown
    matches: List[MatchComparisonDTO]
    
    # Position-by-position statistics
    position_comparisons: List[PositionComparisonDTO]
    
    calculated_at: datetime
