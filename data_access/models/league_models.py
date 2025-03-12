# data_access/models/league_models.py
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Union

@dataclass
class LeagueQuery:
    """Query object for league data"""
    season: str
    league: str
    week: Optional[int] = None
    team: Optional[str] = None
    min_week: Optional[int] = None
    max_week: Optional[int] = None
    
    def to_filter_dict(self) -> Dict[str, Any]:
        """Convert to a filter dictionary for the adapter"""
        filters = {}
        
        if self.season:
            filters["Season"] = self.season
        
        if self.league:
            filters["League"] = self.league
        
        if self.week is not None:
            filters["Week"] = self.week
        elif self.min_week is not None or self.max_week is not None:
            # Handle week range
            if self.min_week is not None and self.max_week is not None:
                # Between min and max
                filters["Week"] = ("in", list(range(self.min_week, self.max_week + 1)))
            elif self.min_week is not None:
                # Greater than or equal to min
                filters["Week"] = ("ge", self.min_week)
            elif self.max_week is not None:
                # Less than or equal to max
                filters["Week"] = ("le", self.max_week)
        
        if self.team:
            filters["Team"] = self.team
        
        return filters

@dataclass
class TeamWeeklyPerformance:
    """Team performance for a specific week."""
    team_id: str
    team_name: str
    week: int
    score: int
    points: float
    players_per_team: int = 4  # Default to 4 if not specified
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary suitable for JSON serialization"""
        return {
            "team_id": self.team_id,
            "team_name": self.team_name,
            "week": self.week,
            "score": self.score,
            "points": self.points,
            "players_per_team": self.players_per_team
        }

@dataclass
class TeamSeasonPerformance:
    """Domain model for team performance across a season"""
    team_id: str
    team_name: str
    total_score: int  # Total pins for the season
    total_points: int  # Total league points
    average: float  # Average pins per game
    weekly_performances: List[TeamWeeklyPerformance] = field(default_factory=list)
    position: Optional[int] = None  # Season ranking
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary suitable for JSON serialization"""
        return {
            "team_id": self.team_id,
            "team_name": self.team_name,
            "total_score": self.total_score,
            "total_points": self.total_points,
            "average": self.average,
            "weekly_performances": [wp.to_dict() for wp in self.weekly_performances],
            "position": self.position
        }

@dataclass
class LeagueStandings:
    """Collection of team standings for a league"""
    season: str
    league_name: str
    week: int
    teams: List[TeamSeasonPerformance]
    last_updated: str  # ISO format date
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary suitable for JSON serialization"""
        return {
            "season": self.season,
            "league_name": self.league_name,
            "week": self.week,
            "teams": [team.to_dict() for team in self.teams],
            "last_updated": self.last_updated
        }