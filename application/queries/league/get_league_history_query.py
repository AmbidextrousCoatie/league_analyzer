"""
Get League History Query.

Query to retrieve historical data for a league across all seasons.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from application.queries.base_query import Query


@dataclass(frozen=True)
class GetLeagueHistoryQuery(Query):
    """
    Query to get league history.
    
    Attributes:
        league_id: UUID of the league (required)
        query_id: Unique identifier for this query instance (inherited from base, auto-generated)
        timestamp: When the query was created (inherited from base, auto-generated)
    """
    league_id: UUID
