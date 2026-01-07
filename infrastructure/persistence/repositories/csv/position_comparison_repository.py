"""
Pandas Position Comparison Repository

CSV-based implementation of PositionComparisonRepository using Pandas DataFrames.
"""

import pandas as pd
from uuid import UUID
from typing import List, Optional
from domain.entities.position_comparison import PositionComparison
from domain.repositories.position_comparison_repository import PositionComparisonRepository
from domain.exceptions.domain_exception import EntityNotFoundError
from infrastructure.persistence.adapters.data_adapter import DataAdapter
from infrastructure.persistence.mappers.csv.position_comparison_mapper import PandasPositionComparisonMapper
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class PandasPositionComparisonRepository(PositionComparisonRepository):
    """
    CSV-based PositionComparison repository using Pandas DataFrames.
    
    This implementation reads/writes CSV files using Pandas DataFrames.
    """
    
    def __init__(
        self,
        data_adapter: DataAdapter,
        mapper: PandasPositionComparisonMapper
    ):
        """
        Initialize Pandas PositionComparison repository.
        
        Args:
            data_adapter: DataAdapter for accessing CSV files
            mapper: Mapper for converting between domain and DataFrame
        """
        self._adapter = data_adapter
        self._mapper = mapper
        logger.debug("Initialized PandasPositionComparisonRepository")
    
    def _load_data(self) -> pd.DataFrame:
        """Load position comparison data from CSV."""
        return self._adapter.get_position_comparison_data()
    
    def _save_data(self, df: pd.DataFrame) -> None:
        """Save position comparison data to CSV."""
        self._adapter.save_position_comparison_data(df)
    
    async def get_by_id(self, comparison_id: UUID) -> Optional[PositionComparison]:
        """Get position comparison by ID from CSV."""
        df = self._load_data()
        if df.empty:
            return None
        
        row = df[df['id'] == str(comparison_id)]
        if row.empty:
            return None
        
        return self._mapper.to_domain(row.iloc[0])
    
    async def get_all(self) -> List[PositionComparison]:
        """Get all position comparisons from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        return [self._mapper.to_domain(row) for _, row in df.iterrows()]
    
    async def get_by_match(self, match_id: UUID) -> List[PositionComparison]:
        """Get all position comparisons for a match from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['match_id'] == str(match_id)]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def get_by_match_and_position(
        self,
        match_id: UUID,
        position: int
    ) -> Optional[PositionComparison]:
        """Get position comparison for a specific match and position from CSV."""
        df = self._load_data()
        if df.empty:
            return None
        
        filtered = df[
            (df['match_id'] == str(match_id)) &
            (df['position'] == position)
        ]
        
        if filtered.empty:
            return None
        
        return self._mapper.to_domain(filtered.iloc[0])
    
    async def get_by_player(self, player_id: UUID) -> List[PositionComparison]:
        """Get all position comparisons involving a player from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[
            (df['team1_player_id'] == str(player_id)) |
            (df['team2_player_id'] == str(player_id))
        ]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def add(self, comparison: PositionComparison) -> PositionComparison:
        """Add position comparison to CSV file."""
        df = self._load_data()
        new_row = self._mapper.to_dataframe(comparison)
        
        # Check if position comparison already exists
        if not df.empty and str(comparison.id) in df['id'].values:
            logger.warning(f"PositionComparison {comparison.id} already exists, updating instead")
            return await self.update(comparison)
        
        # Append new row
        df = pd.concat([df, new_row.to_frame().T], ignore_index=True)
        self._save_data(df)
        logger.debug(f"Added position comparison {comparison.id} to CSV")
        return comparison
    
    async def update(self, comparison: PositionComparison) -> PositionComparison:
        """Update existing position comparison in CSV file."""
        df = self._load_data()
        if df.empty:
            raise EntityNotFoundError(f"PositionComparison {comparison.id} not found")
        
        # Find and update row
        mask = df['id'] == str(comparison.id)
        if not mask.any():
            raise EntityNotFoundError(f"PositionComparison {comparison.id} not found")
        
        # Update row
        updated_row = self._mapper.to_dataframe(comparison)
        for col in df.columns:
            if col in updated_row.index:
                df.loc[mask, col] = updated_row[col]
        self._save_data(df)
        logger.info(f"Updated position comparison {comparison.id} in CSV")
        return comparison
    
    async def delete(self, comparison_id: UUID) -> None:
        """Delete position comparison from CSV file."""
        df = self._load_data()
        if df.empty:
            raise EntityNotFoundError(f"PositionComparison {comparison_id} not found")
        
        # Find and remove row
        mask = df['id'] == str(comparison_id)
        if not mask.any():
            raise EntityNotFoundError(f"PositionComparison {comparison_id} not found")
        
        df = df[~mask]
        self._save_data(df)
        logger.info(f"Deleted position comparison {comparison_id} from CSV")
    
    async def exists(self, comparison_id: UUID) -> bool:
        """Check if position comparison exists in CSV."""
        df = self._load_data()
        if df.empty:
            return False
        
        return str(comparison_id) in df['id'].values

