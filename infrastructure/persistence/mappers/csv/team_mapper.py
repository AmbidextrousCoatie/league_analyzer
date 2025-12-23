"""
Team CSV Mapper

Converts between Team domain entity and Pandas DataFrame rows.
"""

import pandas as pd
from uuid import UUID
from typing import Optional
from domain.entities.team import Team


class PandasTeamMapper:
    """
    Mapper for Team entity ↔ Pandas DataFrame.
    
    Handles bidirectional conversion between domain entities and CSV storage.
    """
    
    @staticmethod
    def to_domain(row: pd.Series) -> Optional[Team]:
        """
        Convert DataFrame row to Team entity.
        
        Args:
            row: Pandas Series representing a row from team.csv
        
        Returns:
            Team domain entity
        """
        # Handle UUID conversion
        team_id_str = str(row['id'])
        try:
            team_id = UUID(team_id_str) if len(team_id_str) > 10 else UUID(int(team_id_str))
        except (ValueError, AttributeError):
            from uuid import uuid4
            team_id = uuid4()
        
        # Handle club_id - required for Team entity
        club_id = None
        club_id_raw = row.get('club_id')
        
        # Check if club_id exists and is not empty/NaN
        # Empty CSV fields can be read as empty strings, NaN, or None
        # Be explicit: check for None, NaN, empty string, or whitespace-only string
        if (club_id_raw is not None and 
            pd.notna(club_id_raw) and 
            str(club_id_raw).strip()):
            club_id_str = str(club_id_raw).strip()
            # Only process if string is not empty and not a special value
            if club_id_str and club_id_str.lower() not in ('nan', 'none', ''):
                try:
                    club_id = UUID(club_id_str) if len(club_id_str) > 10 else UUID(int(club_id_str))
                except (ValueError, AttributeError):
                    club_id = None
        
        # Skip teams without club_id (legacy data) - return None BEFORE creating Team entity
        # This prevents Team.__post_init__ from raising InvalidTeamData
        if club_id is None:
            from infrastructure.logging import get_logger
            logger = get_logger(__name__)
            logger.warning(f"Skipping team {team_id} - missing or invalid club_id (legacy data)")
            return None
        
        # Handle team_number - required, default to 1
        team_number = int(row['team_number']) if pd.notna(row.get('team_number')) else 1
        
        # Handle name - generate if missing
        name = row.get('name', '')
        if not name or not name.strip():
            name = f"Team {team_number}"
        
        # Team entity has: id, name, club_id, team_number
        # Wrap in try-except to catch any validation errors from Team entity
        # (e.g., if club_id is None, Team.__post_init__ will raise InvalidTeamData)
        try:
            team = Team(
                id=team_id,
                name=name.strip(),
                club_id=club_id,
                team_number=team_number
            )
            return team
        except Exception as e:
            # If Team entity validation fails (e.g., InvalidTeamData), log and return None
            from infrastructure.logging import get_logger
            logger = get_logger(__name__)
            logger.warning(f"Skipping team {team_id} - validation error: {e}")
            return None
    
    @staticmethod
    def to_dataframe(team: Team) -> pd.Series:
        """
        Convert Team entity to DataFrame row.
        
        Args:
            team: Team domain entity
        
        Returns:
            Pandas Series representing a row for team.csv
        """
        # Team entity has: id, name, club_id, team_number
        # CSV has: id, club_id, team_number, name
        return pd.Series({
            'id': str(team.id),
            'club_id': str(team.club_id) if team.club_id else None,
            'team_number': team.team_number,
            'name': team.name
        })

