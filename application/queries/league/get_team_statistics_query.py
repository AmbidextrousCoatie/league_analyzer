"""
Get Team Statistics Query.

Query to retrieve comprehensive statistics for a team.
"""

from dataclasses import dataclass, field
from uuid import UUID
from typing import Optional
from application.queries.base_query import Query


@dataclass(frozen=True)
class GetTeamStatisticsQuery(Query):
    """
    Query to retrieve comprehensive statistics for a team.
    
    Attributes:
        team_id: UUID of the team (required)
        filter_type: Type of filter to apply - "all_time", "season", or "season_week" (default: "all_time")
        season: Season string (required if filter_type is "season" or "season_week")
        week: Week number (required if filter_type is "season_week")
        league_id: Optional UUID to filter by specific league
        best_worst_count: Number of best/worst games to return (default: 5)
        clutch_threshold: Score difference threshold for "clutch" matches in pins (default: 50)
        query_id: Unique identifier for this query instance (inherited from base, auto-generated)
        timestamp: When the query was created (inherited from base, auto-generated)
    """
    team_id: UUID
    filter_type: str = field(default="all_time")
    season: Optional[str] = None
    week: Optional[int] = None
    league_id: Optional[UUID] = None
    best_worst_count: int = field(default=5)
    clutch_threshold: int = field(default=50)
