"""
Pandas League Repository

CSV-based implementation of LeagueRepository using Pandas DataFrames.
"""

import pandas as pd
from uuid import UUID
from typing import List, Optional
from domain.entities.league import League
from domain.repositories.league_repository import LeagueRepository
from domain.value_objects.season import Season
from domain.exceptions.domain_exception import EntityNotFoundError
from infrastructure.persistence.adapters.data_adapter import DataAdapter
from infrastructure.persistence.mappers.csv.league_mapper import PandasLeagueMapper
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class PandasLeagueRepository(LeagueRepository):
    """
    CSV-based League repository using Pandas DataFrames.
    
    This implementation reads/writes CSV files using Pandas DataFrames.
    """
    
    def __init__(
        self,
        data_adapter: DataAdapter,
        mapper: PandasLeagueMapper
    ):
        """
        Initialize Pandas League repository.
        
        Args:
            data_adapter: DataAdapter for accessing CSV files
            mapper: Mapper for converting between domain and DataFrame
        """
        self._adapter = data_adapter
        self._mapper = mapper
        logger.debug("Initialized PandasLeagueRepository")
    
    def _load_data(self) -> pd.DataFrame:
        """Load league data from CSV."""
        return self._adapter.get_league_data()
    
    def _save_data(self, df: pd.DataFrame) -> None:
        """Save league data to CSV."""
        self._adapter.save_league_data(df)
    
    async def get_by_id(self, league_id: UUID) -> Optional[League]:
        """Get league by ID from CSV."""
        df = self._load_data()
        if df.empty:
            return None
        
        row = df[df['id'] == str(league_id)]
        if row.empty:
            return None
        
        return self._mapper.to_domain(row.iloc[0])
    
    async def get_all(self) -> List[League]:
        """Get all leagues from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        return [self._mapper.to_domain(row) for _, row in df.iterrows()]
    
    async def get_by_name(
        self,
        name: str
    ) -> List[League]:
        """Get leagues by name from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['name'] == name]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def get_by_season(
        self,
        season
    ) -> List[League]:
        """Get leagues by season from CSV."""
        # Note: CSV doesn't have season directly, would need to join with LeagueSeason
        # For now, return empty list - this would require joining with league_season table
        logger.warning("get_by_season not fully implemented for CSV - requires join with LeagueSeason")
        return []
    
    async def find_by_name(
        self,
        name: str
    ) -> List[League]:
        """Find leagues by name (partial match) from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['name'].str.contains(name, case=False, na=False)]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def add(self, league: League) -> League:
        """Add league to CSV file."""
        df = self._load_data()
        new_row = self._mapper.to_dataframe(league)
        
        # Check if league already exists
        if not df.empty and str(league.id) in df['id'].values:
            logger.warning(f"League {league.id} already exists, updating instead")
            return await self.update(league)
        
        # Append new row
        df = pd.concat([df, new_row.to_frame().T], ignore_index=True)
        self._save_data(df)
        logger.info(f"Added league {league.id} to CSV")
        return league
    
    async def update(self, league: League) -> League:
        """Update existing league in CSV file."""
        df = self._load_data()
        if df.empty:
            raise EntityNotFoundError(f"League {league.id} not found")
        
        # Find and update row
        mask = df['id'] == str(league.id)
        if not mask.any():
            raise EntityNotFoundError(f"League {league.id} not found")
        
        # Update each column individually to preserve dtypes
        updated_row = self._mapper.to_dataframe(league)
        for col in df.columns:
            if col in updated_row.index:
                df.loc[mask, col] = updated_row[col]
        self._save_data(df)
        logger.info(f"Updated league {league.id} in CSV")
        return league
    
    async def delete(self, league_id: UUID) -> None:
        """Delete league from CSV file."""
        df = self._load_data()
        if df.empty:
            raise EntityNotFoundError(f"League {league_id} not found")
        
        # Find and remove row
        mask = df['id'] == str(league_id)
        if not mask.any():
            raise EntityNotFoundError(f"League {league_id} not found")
        
        df = df[~mask]
        self._save_data(df)
        logger.info(f"Deleted league {league_id} from CSV")
    
    async def exists(self, league_id: UUID) -> bool:
        """Check if league exists in CSV."""
        df = self._load_data()
        if df.empty:
            return False
        
        return str(league_id) in df['id'].values

