"""
Pandas LeagueSeason Repository

CSV-based implementation of LeagueSeasonRepository using Pandas DataFrames.
"""

import pandas as pd
from uuid import UUID
from typing import List, Optional
from domain.entities.league_season import LeagueSeason
from domain.repositories.league_season_repository import LeagueSeasonRepository
from domain.value_objects.season import Season
from domain.exceptions.domain_exception import EntityNotFoundError
from infrastructure.persistence.adapters.data_adapter import DataAdapter
from infrastructure.persistence.mappers.csv.league_season_mapper import PandasLeagueSeasonMapper
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class PandasLeagueSeasonRepository(LeagueSeasonRepository):
    """
    CSV-based LeagueSeason repository using Pandas DataFrames.
    
    This implementation reads/writes CSV files using Pandas DataFrames.
    """
    
    def __init__(
        self,
        data_adapter: DataAdapter,
        mapper: PandasLeagueSeasonMapper
    ):
        """
        Initialize Pandas LeagueSeason repository.
        
        Args:
            data_adapter: DataAdapter for accessing CSV files
            mapper: Mapper for converting between domain and DataFrame
        """
        self._adapter = data_adapter
        self._mapper = mapper
        logger.debug("Initialized PandasLeagueSeasonRepository")
    
    def _load_data(self) -> pd.DataFrame:
        """Load league season data from CSV."""
        return self._adapter.get_league_season_data()
    
    def _save_data(self, df: pd.DataFrame) -> None:
        """Save league season data to CSV."""
        self._adapter.save_league_season_data(df)
    
    async def get_by_id(self, league_season_id: UUID) -> Optional[LeagueSeason]:
        """Get league season by ID from CSV."""
        df = self._load_data()
        if df.empty:
            return None
        
        row = df[df['id'] == str(league_season_id)]
        if row.empty:
            return None
        
        return self._mapper.to_domain(row.iloc[0])
    
    async def get_all(self) -> List[LeagueSeason]:
        """Get all league seasons from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        return [self._mapper.to_domain(row) for _, row in df.iterrows()]
    
    async def get_by_league(
        self,
        league_id: UUID
    ) -> List[LeagueSeason]:
        """Get league seasons for a league from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['league_id'] == str(league_id)]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def get_by_season(
        self,
        season: Season
    ) -> List[LeagueSeason]:
        """Get league seasons for a season from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['season'] == str(season)]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def get_by_league_and_season(
        self,
        league_id: UUID,
        season: Season
    ) -> Optional[LeagueSeason]:
        """Get league season by league and season from CSV."""
        df = self._load_data()
        if df.empty:
            return None
        
        filtered = df[
            (df['league_id'] == str(league_id)) &
            (df['season'] == str(season))
        ]
        if filtered.empty:
            return None
        
        return self._mapper.to_domain(filtered.iloc[0])
    
    async def add(self, league_season: LeagueSeason) -> LeagueSeason:
        """Add league season to CSV file."""
        df = self._load_data()
        new_row = self._mapper.to_dataframe(league_season)
        
        # Check if league season already exists
        if not df.empty and str(league_season.id) in df['id'].values:
            logger.warning(f"LeagueSeason {league_season.id} already exists, updating instead")
            return await self.update(league_season)
        
        # Append new row
        df = pd.concat([df, new_row.to_frame().T], ignore_index=True)
        self._save_data(df)
        logger.info(f"Added league season {league_season.id} to CSV")
        return league_season
    
    async def update(self, league_season: LeagueSeason) -> LeagueSeason:
        """Update existing league season in CSV file."""
        df = self._load_data()
        if df.empty:
            raise EntityNotFoundError(f"LeagueSeason {league_season.id} not found")
        
        # Find and update row
        mask = df['id'] == str(league_season.id)
        if not mask.any():
            raise EntityNotFoundError(f"LeagueSeason {league_season.id} not found")
        
        # Update each column individually to preserve dtypes
        updated_row = self._mapper.to_dataframe(league_season)
        for col in df.columns:
            if col in updated_row.index:
                df.loc[mask, col] = updated_row[col]
        self._save_data(df)
        logger.info(f"Updated league season {league_season.id} in CSV")
        return league_season
    
    async def delete(self, league_season_id: UUID) -> None:
        """Delete league season from CSV file."""
        df = self._load_data()
        if df.empty:
            raise EntityNotFoundError(f"LeagueSeason {league_season_id} not found")
        
        # Find and remove row
        mask = df['id'] == str(league_season_id)
        if not mask.any():
            raise EntityNotFoundError(f"LeagueSeason {league_season_id} not found")
        
        df = df[~mask]
        self._save_data(df)
        logger.info(f"Deleted league season {league_season_id} from CSV")
    
    async def exists(self, league_season_id: UUID) -> bool:
        """Check if league season exists in CSV."""
        df = self._load_data()
        if df.empty:
            return False
        
        return str(league_season_id) in df['id'].values

