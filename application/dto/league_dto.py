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


@dataclass
class TopThreeDTO:
    """Top three teams for a season."""
    first_place: Optional[TeamStandingDTO]  # Winner
    second_place: Optional[TeamStandingDTO]  # Runner-up
    third_place: Optional[TeamStandingDTO]  # Third place


@dataclass
class SeasonSummaryDTO:
    """Summary for a single season."""
    season: str
    year: int  # Start year of the season
    league_season_id: UUID
    top_three: TopThreeDTO
    league_average: float  # League-wide average score for the season
    number_of_teams: int
    number_of_weeks: int
    number_of_games: int


@dataclass
class AllTimeRecordDTO:
    """All-time record holder."""
    record_type: str  # "team_season_avg", "team_game", "individual_season_avg", "individual_week_avg", "individual_game"
    value: float
    holder_id: UUID  # team_id or player_id
    holder_name: str
    season: str
    league_season_id: UUID
    date: Optional[datetime]  # For game/week records
    week: Optional[int]  # For week records
    average_score: Optional[float] = None  # For team_game records: average score per player


@dataclass
class LeagueHistoryDTO:
    """Complete league history response DTO."""
    league_id: UUID
    league_name: str
    first_season: Optional[str]  # First season string (e.g., "2020-21")
    most_recent_season: Optional[str]  # Most recent season string
    total_seasons: int
    season_summaries: List[SeasonSummaryDTO]  # Ordered by season (oldest first)
    league_average_trend: List[float]  # League-wide average per season (ordered same as season_summaries)
    all_time_records: List[AllTimeRecordDTO]
    calculated_at: datetime
