"""
League Data Transfer Objects.

DTOs for league-related data transfer between application and presentation layers.
"""

from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID
from datetime import datetime


@dataclass
class WeeklyPerformanceDTO:
    """Weekly performance data for a team."""
    week: int
    score: int  # Bowling scores are integers
    points: float
    number_of_games: int


@dataclass
class TeamStandingDTO:
    """Standing data for a team in the league."""
    team_id: UUID
    team_name: str
    position: int
    total_score: int  # Bowling scores are integers
    total_points: float
    average_score: float  # Rounded to 1 decimal place
    games_played: int
    wins: int
    losses: int
    ties: int
    weekly_performances: List[WeeklyPerformanceDTO]


@dataclass
class WeeklyStandingsDTO:
    """Standings for a specific week."""
    week: int
    standings: List[TeamStandingDTO]


@dataclass
class LeagueStandingsDTO:
    """League standings response DTO."""
    league_id: UUID
    league_name: str
    league_season_id: UUID
    season: str
    week: Optional[int]  # If set, shows only this week; if None, shows all weeks
    standings: List[TeamStandingDTO]  # Overall standings (or single week if week is set)
    weekly_standings: List[WeeklyStandingsDTO]  # Weekly breakdown (only when week is None)
    status: str  # "provisional", "final", "disputed"
    calculated_at: datetime
