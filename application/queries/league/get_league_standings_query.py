"""
Get League Standings Query.

Query to retrieve league standings for a specific league, optionally filtered by season and week.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from application.queries.base_query import Query


@dataclass(frozen=True)
class GetLeagueStandingsQuery(Query):
    """
    Query to get league standings.
    
    Attributes:
        league_id: UUID of the league (required)
        league_season_id: Optional UUID of the league season (if None, uses current/latest)
        week: Optional week number to filter standings up to (None = all weeks)
        query_id: Unique identifier for this query instance (inherited from base, auto-generated)
        timestamp: When the query was created (inherited from base, auto-generated)
    """
    league_id: UUID
    league_season_id: Optional[UUID] = None
    week: Optional[int] = None
