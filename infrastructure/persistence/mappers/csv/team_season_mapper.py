"""
TeamSeason CSV Mapper

Converts between TeamSeason domain entity and Pandas DataFrame rows.
"""

import pandas as pd
from uuid import UUID
from domain.entities.team_season import TeamSeason
from domain.value_objects.vacancy_status import VacancyStatus


class PandasTeamSeasonMapper:
    """
    Mapper for TeamSeason entity ↔ Pandas DataFrame.
    
    Handles bidirectional conversion between domain entities and CSV storage.
    """
    
    @staticmethod
    def to_domain(row: pd.Series) -> TeamSeason:
        """
        Convert DataFrame row to TeamSeason entity.
        
        Args:
            row: Pandas Series representing a row from team_season.csv
        
        Returns:
            TeamSeason domain entity
        """
        # Handle UUID conversion
        team_season_id = UUID(row['id']) if isinstance(row['id'], str) and len(row['id']) > 10 else row['id']
        league_season_id = UUID(row['league_season_id']) if isinstance(row['league_season_id'], str) and len(row['league_season_id']) > 10 else row['league_season_id']
        
        # Handle team_id - support both new format (team_id) and legacy format (club_id + team_number)
        # Legacy format: if team_id is missing but club_id and team_number exist, we'll need to resolve it
        # For now, assume team_id is present in new format
        if 'team_id' in row and pd.notna(row.get('team_id')):
            team_id = UUID(row['team_id']) if isinstance(row['team_id'], str) and len(row['team_id']) > 10 else row['team_id']
        else:
            # Legacy format: try to get from club_id + team_number (will need to be resolved by repository)
            # For migration purposes, we'll raise an error if team_id is missing
            raise ValueError("team_id is required. Legacy format (club_id + team_number) is no longer supported.")
        
        # Handle vacancy_status - default to ACTIVE if not present
        vacancy_status_str = row.get('vacancy_status', 'active')
        if pd.isna(vacancy_status_str):
            vacancy_status_str = 'active'
        try:
            vacancy_status = VacancyStatus(vacancy_status_str)
        except ValueError:
            vacancy_status = VacancyStatus.ACTIVE
        
        return TeamSeason(
            id=team_season_id,
            league_season_id=league_season_id,
            team_id=team_id,
            vacancy_status=vacancy_status
        )
    
    @staticmethod
    def to_dataframe(team_season: TeamSeason) -> pd.Series:
        """
        Convert TeamSeason entity to DataFrame row.
        
        Args:
            team_season: TeamSeason domain entity
        
        Returns:
            Pandas Series representing a row for team_season.csv
        """
        return pd.Series({
            'id': str(team_season.id),
            'league_season_id': str(team_season.league_season_id),
            'team_id': str(team_season.team_id),
            'vacancy_status': team_season.vacancy_status.value
        })

