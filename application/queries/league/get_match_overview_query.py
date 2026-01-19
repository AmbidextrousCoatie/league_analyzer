"""
Get Match Overview Query.

Query to retrieve detailed overview of a specific match including
position-by-position comparisons and team totals.
"""

from dataclasses import dataclass
from uuid import UUID
from application.queries.base_query import Query


@dataclass(frozen=True)
class GetMatchOverviewQuery(Query):
    """
    Query to get match overview.
    
    Attributes:
        match_id: UUID of the match (required)
        query_id: Unique identifier for this query instance (inherited from base, auto-generated)
        timestamp: When the query was created (inherited from base, auto-generated)
    """
    match_id: UUID
