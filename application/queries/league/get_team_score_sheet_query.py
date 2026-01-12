"""
Get Team Score Sheet Query.

Query to retrieve detailed score sheet for a specific team in a league season.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from application.queries.base_query import Query


@dataclass(frozen=True)
class GetTeamScoreSheetQuery(Query):
    """
    Query to get team score sheet.
    
    Attributes:
        league_season_id: UUID of the league season (required)
        team_season_id: UUID of the team season (required)
        week: Optional week number to filter by (None = all weeks)
        query_id: Unique identifier for this query instance (inherited from base, auto-generated)
        timestamp: When the query was created (inherited from base, auto-generated)
    """
    league_season_id: UUID
    team_season_id: UUID
    week: Optional[int] = None
