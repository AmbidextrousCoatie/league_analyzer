"""
ClubPlayer CSV Repository Implementation

Pandas-based implementation of ClubPlayerRepository using CSV files.
"""

import pandas as pd
from typing import List, Optional
from uuid import UUID
from domain.entities.club_player import ClubPlayer
from domain.repositories.club_player_repository import ClubPlayerRepository
from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
from infrastructure.persistence.mappers.csv.club_player_mapper import PandasClubPlayerMapper
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class PandasClubPlayerRepository(ClubPlayerRepository):
    """
    CSV-based repository for ClubPlayer entities.
    
    Uses PandasDataAdapter for CSV file operations.
    """
    
    def __init__(self, adapter: PandasDataAdapter, mapper: PandasClubPlayerMapper):
        """
        Initialize repository.
        
        Args:
            adapter: PandasDataAdapter for CSV operations
            mapper: PandasClubPlayerMapper for entity conversion
        """
        self._adapter = adapter
        self._mapper = mapper
    
    def _load_data(self):
        """Load club player data from CSV."""
        return self._adapter.get_club_player_data()
    
    def _save_data(self, df):
        """Save club player data to CSV."""
        self._adapter.save_club_player_data(df)
    
    async def get_by_id(self, club_player_id: UUID) -> Optional[ClubPlayer]:
        """Get club player by ID."""
        df = self._load_data()
        if df.empty:
            return None
        
        matches = df[df['id'] == str(club_player_id)]
        if matches.empty:
            return None
        
        return self._mapper.to_domain(matches.iloc[0])
    
    async def get_all(self) -> List[ClubPlayer]:
        """Get all club player relationships from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        return [self._mapper.to_domain(row) for _, row in df.iterrows()]
    
    async def get_by_player(self, player_id: UUID) -> List[ClubPlayer]:
        """Get all club memberships for a player."""
        df = self._load_data()
        if df.empty:
            return []
        
        matches = df[df['player_id'] == str(player_id)]
        return [self._mapper.to_domain(row) for _, row in matches.iterrows()]
    
    async def get_by_club(self, club_id: UUID) -> List[ClubPlayer]:
        """Get all players for a club."""
        df = self._load_data()
        if df.empty:
            return []
        
        matches = df[df['club_id'] == str(club_id)]
        return [self._mapper.to_domain(row) for _, row in matches.iterrows()]
    
    async def add(self, club_player: ClubPlayer) -> ClubPlayer:
        """Add a new club player relationship."""
        df = self._load_data()
        
        # Check if already exists
        if not df.empty:
            existing = df[
                (df['club_id'] == str(club_player.club_id)) &
                (df['player_id'] == str(club_player.player_id))
            ]
            if not existing.empty:
                logger.warning(f"ClubPlayer relationship already exists for club {club_player.club_id} and player {club_player.player_id}, updating instead")
                return await self.update(club_player)
        
        # Add new row
        new_row = self._mapper.to_dataframe(club_player)
        df = pd.concat([df, new_row.to_frame().T], ignore_index=True)
        self._save_data(df)
        
        logger.debug(f"Added club player relationship: club {club_player.club_id} <-> player {club_player.player_id}")
        return club_player
    
    async def update(self, club_player: ClubPlayer) -> ClubPlayer:
        """Update an existing club player relationship."""
        df = self._load_data()
        
        if df.empty:
            raise ValueError(f"ClubPlayer {club_player.id} not found")
        
        # Find and update row
        mask = (
            (df['club_id'] == str(club_player.club_id)) &
            (df['player_id'] == str(club_player.player_id))
        )
        if not mask.any():
            raise ValueError(f"ClubPlayer relationship not found")
        
        updated_row = self._mapper.to_dataframe(club_player)
        df.loc[mask] = updated_row
        self._save_data(df)
        
        logger.debug(f"Updated club player relationship: club {club_player.club_id} <-> player {club_player.player_id}")
        return club_player
    
    async def delete(self, club_player_id: UUID) -> bool:
        """Delete a club player relationship."""
        df = self._load_data()
        
        if df.empty:
            return False
        
        mask = df['id'] == str(club_player_id)
        if not mask.any():
            return False
        
        df = df[~mask]
        self._save_data(df)
        
        logger.debug(f"Deleted club player relationship {club_player_id}")
        return True
    
    async def exists(self, club_player_id: UUID) -> bool:
        """Check if club player relationship exists."""
        df = self._load_data()
        if df.empty:
            return False
        
        return (df['id'] == str(club_player_id)).any()

