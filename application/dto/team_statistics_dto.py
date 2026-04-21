"""
Team Statistics DTOs.

Data Transfer Objects for team statistics queries.
"""

from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID
from datetime import datetime


@dataclass
class SeasonProgressionDTO:
    """Single data point for team progression chart."""
    season: str
    league_id: UUID
    league_name: str
    league_level: int
    final_position: Optional[int]
    promotion: bool
    relegation: bool


@dataclass
class SeasonStatisticsDTO:
    """Statistics for a single season."""
    season: str
    league_id: UUID
    league_name: str
    league_level: int
    league_abbreviation: Optional[str]
    games_played: int
    total_score: int
    average_score: float
    league_average_score: float  # League average for THIS specific league in THIS season
    best_score: int
    worst_score: int
    total_points: float
    average_points: float  # Points per match
    maximum_points_per_match: float  # Based on scoring system for THIS season
    points_percentage: float  # (average_points / maximum_points_per_match) * 100
    wins: int
    losses: int
    ties: int
    final_position: Optional[int]  # If season completed


@dataclass
class WeeklyPerformanceDTO:
    """Performance for a single week."""
    week: int
    season: str
    league_name: str
    total_score: int
    total_points: float
    matches_played: int
    wins: int
    losses: int
    ties: int


@dataclass
class GameRecordDTO:
    """Record of a single game (best/worst/biggest win/loss)."""
    match_id: UUID
    score: int
    league_id: UUID
    league_name: str
    league_level: int
    season: str
    opponent_team_id: UUID
    opponent_team_name: str
    opponent_score: Optional[int] = None  # For biggest win/loss
    score_difference: Optional[int] = None  # For biggest win/loss
    date: Optional[datetime] = None
    week: Optional[int] = None


@dataclass
class OpponentClutchSummaryDTO:
    """Clutch performance summary for a specific opponent."""
    opponent_team_id: UUID
    opponent_team_name: str
    wins: int
    losses: int
    ties: int
    total_close_matches: int
    win_rate: float


@dataclass
class ClutchPerformanceDTO:
    """Clutch performance statistics."""
    total_close_matches: int
    wins_in_close_matches: int
    losses_in_close_matches: int
    ties_in_close_matches: int
    win_rate_in_close_matches: float
    threshold: int  # Score difference threshold used
    opponent_summaries: List[OpponentClutchSummaryDTO]  # Aggregated by opponent


@dataclass
class PositionPerformanceDTO:
    """Performance statistics for a specific position (0-3)."""
    position: int
    games_played: int
    average_score: float
    total_points: float
    wins: int
    losses: int
    ties: int
    win_rate: float


@dataclass
class RecentFormDTO:
    """Recent form statistics (last N matches)."""
    last_n_matches: int  # N value used
    form_string: str  # e.g., "WWLWW"
    matches: List[GameRecordDTO]  # Last N matches
    points_in_period: float
    wins_in_period: int
    losses_in_period: int
    ties_in_period: int
    win_rate_in_period: float


@dataclass
class TeamStatisticsDTO:
    """Complete team statistics."""
    team_id: UUID
    team_name: str
    club_id: UUID
    club_name: str
    filter_type: str  # "all_time", "season", "season_week"
    total_games_played: int
    total_score: int
    average_score: float
    league_average_score: float  # Overall league average (weighted average across all seasons/leagues)
    best_score: int
    worst_score: int
    total_points: float
    average_points: float  # Overall average points per match
    total_wins: int
    total_losses: int
    total_ties: int
    season_progression: List[SeasonProgressionDTO]
    season_statistics: List[SeasonStatisticsDTO]
    weekly_performances: List[WeeklyPerformanceDTO]
    best_games: List[GameRecordDTO]
    worst_games: List[GameRecordDTO]
    biggest_wins: List[GameRecordDTO]
    biggest_losses: List[GameRecordDTO]
    clutch_performance: ClutchPerformanceDTO
    position_performance: List[PositionPerformanceDTO]
    recent_form: RecentFormDTO
    calculated_at: datetime
    # Filter information (optional)
    season: Optional[str] = None
    week: Optional[int] = None
