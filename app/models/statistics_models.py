from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

@dataclass
class PlayerWeekPerformance:
    """Performance data for a player in a specific week"""
    player_id: str
    player_name: str
    week: int
    score: float
    points: float
    games_played: int = 4
    details: Optional[Dict[str, Any]] = None

@dataclass
class PlayerSeasonSummary:
    """Summary of a player's performance for a season"""
    total_score: float
    total_points: float
    average_score: float
    games_played: int
    best_score: float
    worst_score: float
    details: Optional[Dict[str, Any]] = None

@dataclass
class PlayerStatistics:
    """Complete statistics for a player"""
    name: str
    season: str
    weekly_performances: Dict[int, PlayerWeekPerformance]
    season_summary: PlayerSeasonSummary
    team_contribution: float  # percentage of team's total score
    details: Optional[Dict[str, Any]] = None

@dataclass
class TeamWeekPerformance:
    """Performance data for a team in a specific week"""
    team_id: str
    team_name: str
    week: int
    total_score: float
    points: float
    number_of_games: int
    player_scores: Dict[str, float]  # player_name -> score
    details: Optional[Dict[str, Any]] = None

@dataclass
class TeamSeasonSummary:
    """Summary of a team's performance for a season"""
    total_score: float
    total_points: float
    average_score: float
    games_played: int
    best_score: float
    worst_score: float
    details: Optional[Dict[str, Any]] = None

@dataclass
class TeamStatistics:
    """Complete statistics for a team"""
    team_name: str
    season: str
    weekly_performances: Dict[int, TeamWeekPerformance]
    season_summary: TeamSeasonSummary
    player_contributions: Dict[str, float]  # player_name -> contribution percentage
    details: Optional[Dict[str, Any]] = None

@dataclass
class LeagueWeekSummary:
    """Summary of league performance for a specific week"""
    data: Dict[str, List[float]]  # team_name -> [pins, points, average]
    description: List[str] = field(default_factory=lambda: ["Pins", "Points", "Average"])
    details: Optional[Dict[str, Any]] = None

@dataclass
class LeagueSeasonSummary:
    """Summary of league performance for the entire season"""
    data: Dict[str, List[float]]  # team_name -> [total_pins, total_points, season_average]
    description: List[str] = field(default_factory=lambda: ["Total Pins", "Total Points", "Season Average"])
    details: Optional[Dict[str, Any]] = None

@dataclass
class LeagueStatistics:
    """Complete statistics for a league"""
    name: str
    season: str
    team_stats: Dict[str, TeamStatistics]
    player_stats: Dict[str, PlayerStatistics]
    weekly_summaries: Dict[int, LeagueWeekSummary]
    season_summary: LeagueSeasonSummary
    details: Optional[Dict[str, Any]] = None

@dataclass
class LeagueResults:
    """Results data for a league including weekly and season summaries"""
    name: str
    level: int
    weeks: Dict[int, LeagueWeekSummary]
    ranking: List[str]  # team names in order of ranking
    data: LeagueSeasonSummary
    details: Optional[Dict[str, Any]] = None 