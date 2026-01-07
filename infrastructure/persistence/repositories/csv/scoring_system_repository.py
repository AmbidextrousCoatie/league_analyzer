"""
ScoringSystem CSV Repository Implementation

Pandas-based implementation of ScoringSystemRepository using CSV files.
"""

import pandas as pd
from typing import List, Optional
from uuid import UUID
from domain.entities.scoring_system import ScoringSystem
from domain.repositories.scoring_system_repository import ScoringSystemRepository
from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
from infrastructure.persistence.mappers.csv.scoring_system_mapper import PandasScoringSystemMapper
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class PandasScoringSystemRepository(ScoringSystemRepository):
    """
    CSV-based repository for ScoringSystem entities.
    
    Uses PandasDataAdapter for CSV file operations.
    """
    
    def __init__(self, adapter: PandasDataAdapter, mapper: PandasScoringSystemMapper):
        """
        Initialize repository.
        
        Args:
            adapter: PandasDataAdapter for CSV operations
            mapper: PandasScoringSystemMapper for entity conversion
        """
        self._adapter = adapter
        self._mapper = mapper
    
    def _load_data(self):
        """Load scoring system data from CSV."""
        return self._adapter.get_scoring_system_data()
    
    def _save_data(self, df):
        """Save scoring system data to CSV."""
        self._adapter.save_scoring_system_data(df)
    
    async def get_by_id(self, scoring_system_id: UUID) -> Optional[ScoringSystem]:
        """Get scoring system by ID."""
        df = self._load_data()
        if df.empty:
            return None
        
        matches = df[df['id'] == str(scoring_system_id)]
        if matches.empty:
            return None
        
        return self._mapper.to_domain(matches.iloc[0])
    
    async def get_all(self) -> List[ScoringSystem]:
        """Get all scoring systems from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        return [self._mapper.to_domain(row) for _, row in df.iterrows()]
    
    async def find_by_name(self, name: str) -> Optional[ScoringSystem]:
        """Find scoring system by name."""
        df = self._load_data()
        if df.empty:
            return None
        
        matches = df[df['name'].str.strip().str.lower() == name.strip().lower()]
        if matches.empty:
            return None
        
        return self._mapper.to_domain(matches.iloc[0])
    
    async def add(self, scoring_system: ScoringSystem) -> ScoringSystem:
        """Add a new scoring system."""
        df = self._load_data()
        
        # Check if already exists
        if not df.empty:
            existing = df[df['id'] == str(scoring_system.id)]
            if not existing.empty:
                logger.warning(f"Scoring system {scoring_system.id} already exists, updating instead")
                return await self.update(scoring_system)
        
        # Add new row
        new_row = self._mapper.to_dataframe(scoring_system)
        df = pd.concat([df, new_row.to_frame().T], ignore_index=True)
        self._save_data(df)
        
        logger.debug(f"Added scoring system: {scoring_system.name} ({scoring_system.id})")
        return scoring_system
    
    async def update(self, scoring_system: ScoringSystem) -> ScoringSystem:
        """Update an existing scoring system."""
        df = self._load_data()

        if df.empty:
            raise ValueError(f"Scoring system {scoring_system.id} not found")

        # Find and update row
        mask = df["id"] == str(scoring_system.id)
        if not mask.any():
            raise ValueError(f"Scoring system {scoring_system.id} not found")

        updated_row = self._mapper.to_dataframe(scoring_system)
        # Assign column-by-column to avoid dtype and length issues
        for col in df.columns:
            if col in updated_row.index:
                df.loc[mask, col] = updated_row[col]

        self._save_data(df)

        logger.info(
            f"Updated scoring system: {scoring_system.name} ({scoring_system.id})"
        )
        return scoring_system
    
    async def delete(self, scoring_system_id: UUID) -> bool:
        """Delete a scoring system."""
        df = self._load_data()
        
        if df.empty:
            return False
        
        mask = df['id'] == str(scoring_system_id)
        if not mask.any():
            return False
        
        df = df[~mask]
        self._save_data(df)
        
        logger.info(f"Deleted scoring system: {scoring_system_id}")
        return True
    
    async def exists(self, scoring_system_id: UUID) -> bool:
        """Check if scoring system exists."""
        df = self._load_data()
        if df.empty:
            return False
        
        return (df['id'] == str(scoring_system_id)).any()

