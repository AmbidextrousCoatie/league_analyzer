"""
Get Team vs Team Comparison Query.

Query to retrieve head-to-head comparison between two teams.
"""

from dataclasses import dataclass
from uuid import UUID
from application.queries.base_query import Query


@dataclass(frozen=True)
class GetTeamVsTeamComparisonQuery(Query):
    """
    Query to get head-to-head comparison between two teams.
    
    Attributes:
        team1_season_id: UUID of the first team season (required)
        team2_season_id: UUID of the second team season (required)
        query_id: Unique identifier for this query instance (inherited from base, auto-generated)
        timestamp: When the query was created (inherited from base, auto-generated)
    """
    team1_season_id: UUID
    team2_season_id: UUID
