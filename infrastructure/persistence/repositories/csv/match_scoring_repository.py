"""
Pandas Match Scoring Repository

CSV-based implementation of MatchScoringRepository using Pandas DataFrames.
"""

import pandas as pd
from uuid import UUID
from typing import List, Optional
from domain.entities.match_scoring import MatchScoring
from domain.repositories.match_scoring_repository import MatchScoringRepository
from domain.exceptions.domain_exception import EntityNotFoundError
from infrastructure.persistence.adapters.data_adapter import DataAdapter
from infrastructure.persistence.mappers.csv.match_scoring_mapper import PandasMatchScoringMapper
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class PandasMatchScoringRepository(MatchScoringRepository):
    """
    CSV-based MatchScoring repository using Pandas DataFrames.
    
    This implementation reads/writes CSV files using Pandas DataFrames.
    """
    
    def __init__(
        self,
        data_adapter: DataAdapter,
        mapper: PandasMatchScoringMapper
    ):
        """
        Initialize Pandas MatchScoring repository.
        
        Args:
            data_adapter: DataAdapter for accessing CSV files
            mapper: Mapper for converting between domain and DataFrame
        """
        self._adapter = data_adapter
        self._mapper = mapper
        logger.debug("Initialized PandasMatchScoringRepository")
    
    def _load_data(self) -> pd.DataFrame:
        """Load match scoring data from CSV."""
        return self._adapter.get_match_scoring_data()
    
    def _save_data(self, df: pd.DataFrame) -> None:
        """Save match scoring data to CSV."""
        self._adapter.save_match_scoring_data(df)
    
    async def get_by_id(self, scoring_id: UUID) -> Optional[MatchScoring]:
        """Get match scoring by ID from CSV."""
        df = self._load_data()
        if df.empty:
            return None
        
        row = df[df['id'] == str(scoring_id)]
        if row.empty:
            return None
        
        return self._mapper.to_domain(row.iloc[0])
    
    async def get_all(self) -> List[MatchScoring]:
        """Get all match scorings from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        return [self._mapper.to_domain(row) for _, row in df.iterrows()]
    
    async def get_by_match(self, match_id: UUID) -> List[MatchScoring]:
        """Get all match scorings for a match from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['match_id'] == str(match_id)]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def get_by_match_and_system(
        self,
        match_id: UUID,
        scoring_system_id: str
    ) -> Optional[MatchScoring]:
        """Get match scoring for a specific match and scoring system from CSV."""
        df = self._load_data()
        if df.empty:
            return None
        
        filtered = df[
            (df['match_id'] == str(match_id)) &
            (df['scoring_system_id'] == str(scoring_system_id))
        ]
        
        if filtered.empty:
            return None
        
        return self._mapper.to_domain(filtered.iloc[0])
    
    async def get_by_scoring_system(self, scoring_system_id: str) -> List[MatchScoring]:
        """Get all match scorings for a scoring system from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['scoring_system_id'] == str(scoring_system_id)]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def add(self, scoring: MatchScoring) -> MatchScoring:
        """Add match scoring to CSV file."""
        df = self._load_data()
        new_row = self._mapper.to_dataframe(scoring)
        
        # Check if match scoring already exists
        if not df.empty and str(scoring.id) in df['id'].values:
            logger.warning(f"MatchScoring {scoring.id} already exists, updating instead")
            return await self.update(scoring)
        
        # Append new row
        df = pd.concat([df, new_row.to_frame().T], ignore_index=True)
        self._save_data(df)
        logger.debug(f"Added match scoring {scoring.id} to CSV")
        return scoring
    
    async def update(self, scoring: MatchScoring) -> MatchScoring:
        """Update existing match scoring in CSV file."""
        df = self._load_data()
        if df.empty:
            raise EntityNotFoundError(f"MatchScoring {scoring.id} not found")
        
        # Find and update row
        mask = df['id'] == str(scoring.id)
        if not mask.any():
            raise EntityNotFoundError(f"MatchScoring {scoring.id} not found")
        
        # Update row
        updated_row = self._mapper.to_dataframe(scoring)
        for col in df.columns:
            if col in updated_row.index:
                df.loc[mask, col] = updated_row[col]
        self._save_data(df)
        logger.info(f"Updated match scoring {scoring.id} in CSV")
        return scoring
    
    async def delete(self, scoring_id: UUID) -> None:
        """Delete match scoring from CSV file."""
        df = self._load_data()
        if df.empty:
            raise EntityNotFoundError(f"MatchScoring {scoring_id} not found")
        
        # Find and remove row
        mask = df['id'] == str(scoring_id)
        if not mask.any():
            raise EntityNotFoundError(f"MatchScoring {scoring_id} not found")
        
        df = df[~mask]
        self._save_data(df)
        logger.info(f"Deleted match scoring {scoring_id} from CSV")
    
    async def exists(self, scoring_id: UUID) -> bool:
        """Check if match scoring exists in CSV."""
        df = self._load_data()
        if df.empty:
            return False
        
        return str(scoring_id) in df['id'].values

