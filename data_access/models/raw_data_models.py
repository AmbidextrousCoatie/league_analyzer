from dataclasses import dataclass
from typing import Dict, List, Any, Optional

@dataclass
class RawPlayerData:
    """Raw player performance data"""
    player_name: str
    team_name: str
    week: int
    round_number: int
    score: int
    points: float
    calculated_score: bool = False

@dataclass
class RawTeamData:
    """Raw team performance data"""
    team_name: str
    season: str
    players: List[RawPlayerData]

@dataclass
class RawLeagueData:
    """Raw league performance data"""
    league_name: str
    season: str
    teams: List[RawTeamData] 