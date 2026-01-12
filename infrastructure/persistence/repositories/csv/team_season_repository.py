"""
Pandas TeamSeason Repository

CSV-based implementation of TeamSeasonRepository using Pandas DataFrames.
"""

import pandas as pd
from uuid import UUID
from typing import List, Optional
from domain.entities.team_season import TeamSeason
from domain.repositories.team_season_repository import TeamSeasonRepository
from domain.value_objects.vacancy_status import VacancyStatus
from domain.exceptions.domain_exception import EntityNotFoundError
from infrastructure.persistence.adapters.data_adapter import DataAdapter
from infrastructure.persistence.mappers.csv.team_season_mapper import PandasTeamSeasonMapper
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class PandasTeamSeasonRepository(TeamSeasonRepository):
    """
    CSV-based TeamSeason repository using Pandas DataFrames.
    
    This implementation reads/writes CSV files using Pandas DataFrames.
    """
    
    def __init__(
        self,
        data_adapter: DataAdapter,
        mapper: PandasTeamSeasonMapper
    ):
        """
        Initialize Pandas TeamSeason repository.
        
        Args:
            data_adapter: DataAdapter for accessing CSV files
            mapper: Mapper for converting between domain and DataFrame
        """
        self._adapter = data_adapter
        self._mapper = mapper
        logger.debug("Initialized PandasTeamSeasonRepository")
    
    def _load_data(self) -> pd.DataFrame:
        """Load team season data from CSV."""
        return self._adapter.get_team_season_data()
    
    def _save_data(self, df: pd.DataFrame) -> None:
        """Save team season data to CSV."""
        self._adapter.save_team_season_data(df)
    
    async def get_by_id(self, team_season_id: UUID) -> Optional[TeamSeason]:
        """Get team season by ID from CSV."""
        df = self._load_data()
        if df.empty:
            return None
        
        row = df[df['id'] == str(team_season_id)]
        if row.empty:
            return None
        
        return self._mapper.to_domain(row.iloc[0])
    
    async def get_all(self) -> List[TeamSeason]:
        """Get all team seasons from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        return [self._mapper.to_domain(row) for _, row in df.iterrows()]
    
    async def get_by_league_season(
        self,
        league_season_id: UUID
    ) -> List[TeamSeason]:
        """Get team seasons for a league season from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['league_season_id'] == str(league_season_id)]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def get_by_team(
        self,
        team_id: UUID
    ) -> List[TeamSeason]:
        """Get team seasons for a team from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['team_id'] == str(team_id)]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def get_by_vacancy_status(
        self,
        vacancy_status: VacancyStatus
    ) -> List[TeamSeason]:
        """Get team seasons by vacancy status from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['vacancy_status'] == vacancy_status.value]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def add(self, team_season: TeamSeason) -> TeamSeason:
        """Add team season to CSV file."""
        df = self._load_data()
        new_row = self._mapper.to_dataframe(team_season)
        
        # Check if team season already exists
        if not df.empty and str(team_season.id) in df['id'].values:
            logger.warning(f"TeamSeason {team_season.id} already exists, updating instead")
            return await self.update(team_season)
        
        # Append new row
        df = pd.concat([df, new_row.to_frame().T], ignore_index=True)
        self._save_data(df)
        logger.debug(f"Added team season {team_season.id} to CSV")
        return team_season
    
    async def update(self, team_season: TeamSeason) -> TeamSeason:
        """Update existing team season in CSV file."""
        df = self._load_data()
        if df.empty:
            raise EntityNotFoundError(f"TeamSeason {team_season.id} not found")
        
        # Find and update row
        mask = df['id'] == str(team_season.id)
        if not mask.any():
            raise EntityNotFoundError(f"TeamSeason {team_season.id} not found")
        
        # Update each column individually to preserve dtypes
        updated_row = self._mapper.to_dataframe(team_season)
        for col in df.columns:
            if col in updated_row.index:
                df.loc[mask, col] = updated_row[col]
        self._save_data(df)
        logger.info(f"Updated team season {team_season.id} in CSV")
        return team_season
    
    async def delete(self, team_season_id: UUID) -> None:
        """Delete team season from CSV file."""
        df = self._load_data()
        if df.empty:
            raise EntityNotFoundError(f"TeamSeason {team_season_id} not found")
        
        # Find and remove row
        mask = df['id'] == str(team_season_id)
        if not mask.any():
            raise EntityNotFoundError(f"TeamSeason {team_season_id} not found")
        
        df = df[~mask]
        self._save_data(df)
        logger.info(f"Deleted team season {team_season_id} from CSV")
    
    async def exists(self, team_season_id: UUID) -> bool:
        """Check if team season exists in CSV."""
        df = self._load_data()
        if df.empty:
            return False
        
        return str(team_season_id) in df['id'].values

