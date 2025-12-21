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
        club_id = UUID(row['club_id']) if isinstance(row['club_id'], str) and len(row['club_id']) > 10 else row['club_id']
        
        # Handle optional fields
        team_number = int(row['team_number']) if pd.notna(row.get('team_number')) else 1
        
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
            club_id=club_id,
            team_number=team_number,
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
            'club_id': str(team_season.club_id),
            'team_number': team_season.team_number,
            'vacancy_status': team_season.vacancy_status.value
        })

