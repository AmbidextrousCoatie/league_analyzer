"""
Pandas Club Repository

CSV-based implementation of ClubRepository using Pandas DataFrames.
"""

import pandas as pd
from uuid import UUID
from typing import List, Optional
from domain.entities.club import Club
from domain.repositories.club_repository import ClubRepository
from domain.exceptions.domain_exception import EntityNotFoundError
from infrastructure.persistence.adapters.data_adapter import DataAdapter
from infrastructure.persistence.mappers.csv.club_mapper import PandasClubMapper
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class PandasClubRepository(ClubRepository):
    """
    CSV-based Club repository using Pandas DataFrames.
    
    This implementation reads/writes CSV files using Pandas DataFrames.
    """
    
    def __init__(
        self,
        data_adapter: DataAdapter,
        mapper: PandasClubMapper
    ):
        """
        Initialize Pandas Club repository.
        
        Args:
            data_adapter: DataAdapter for accessing CSV files
            mapper: Mapper for converting between domain and DataFrame
        """
        self._adapter = data_adapter
        self._mapper = mapper
        logger.debug("Initialized PandasClubRepository")
    
    def _load_data(self) -> pd.DataFrame:
        """Load club data from CSV."""
        return self._adapter.get_club_data()
    
    def _save_data(self, df: pd.DataFrame) -> None:
        """Save club data to CSV."""
        self._adapter.save_club_data(df)
    
    async def get_by_id(self, club_id: UUID) -> Optional[Club]:
        """Get club by ID from CSV."""
        df = self._load_data()
        if df.empty:
            return None
        
        row = df[df['id'] == str(club_id)]
        if row.empty:
            return None
        
        return self._mapper.to_domain(row.iloc[0])
    
    async def get_all(self) -> List[Club]:
        """Get all clubs from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        return [self._mapper.to_domain(row) for _, row in df.iterrows()]
    
    async def find_by_name(
        self,
        name: str
    ) -> List[Club]:
        """Find clubs by name (partial match) from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['name'].str.contains(name, case=False, na=False)]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def add(self, club: Club) -> Club:
        """Add club to CSV file."""
        df = self._load_data()
        new_row = self._mapper.to_dataframe(club)
        
        # Check if club already exists
        if not df.empty and str(club.id) in df['id'].values:
            logger.warning(f"Club {club.id} already exists, updating instead")
            return await self.update(club)
        
        # Append new row
        df = pd.concat([df, new_row.to_frame().T], ignore_index=True)
        self._save_data(df)
        logger.info(f"Added club {club.id} to CSV")
        return club
    
    async def update(self, club: Club) -> Club:
        """Update existing club in CSV file."""
        df = self._load_data()
        if df.empty:
            raise EntityNotFoundError(f"Club {club.id} not found")
        
        # Find and update row
        mask = df['id'] == str(club.id)
        if not mask.any():
            raise EntityNotFoundError(f"Club {club.id} not found")
        
        # Update each column individually to preserve dtypes
        updated_row = self._mapper.to_dataframe(club)
        for col in df.columns:
            if col in updated_row.index:
                df.loc[mask, col] = updated_row[col]
        self._save_data(df)
        logger.info(f"Updated club {club.id} in CSV")
        return club
    
    async def delete(self, club_id: UUID) -> bool:
        """Delete club from CSV file."""
        df = self._load_data()
        if df.empty:
            return False
        
        # Find and remove row
        mask = df['id'] == str(club_id)
        if not mask.any():
            return False
        
        df = df[~mask]
        self._save_data(df)
        logger.info(f"Deleted club {club_id} from CSV")
        return True

