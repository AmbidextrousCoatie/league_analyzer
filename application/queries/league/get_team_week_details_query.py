"""
Get Team Week Details Query.

Query to retrieve team performance summary for a specific week.
"""

from dataclasses import dataclass
from uuid import UUID
from application.queries.base_query import Query


@dataclass(frozen=True)
class GetTeamWeekDetailsQuery(Query):
    """
    Query to get team week details.
    
    Attributes:
        team_season_id: UUID of the team season (required)
        week: Week number (required)
        query_id: Unique identifier for this query instance (inherited from base, auto-generated)
        timestamp: When the query was created (inherited from base, auto-generated)
    """
    team_season_id: UUID
    week: int
