"""
Pandas Player Repository

CSV-based implementation of PlayerRepository using Pandas DataFrames.
"""

import pandas as pd
from uuid import UUID
from typing import List, Optional
from domain.entities.player import Player
from domain.repositories.player_repository import PlayerRepository
from domain.exceptions.domain_exception import EntityNotFoundError
from infrastructure.persistence.adapters.data_adapter import DataAdapter
from infrastructure.persistence.mappers.csv.player_mapper import PandasPlayerMapper
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class PandasPlayerRepository(PlayerRepository):
    """
    CSV-based Player repository using Pandas DataFrames.
    
    This implementation reads/writes CSV files using Pandas DataFrames.
    """
    
    def __init__(
        self,
        data_adapter: DataAdapter,
        mapper: PandasPlayerMapper
    ):
        """
        Initialize Pandas Player repository.
        
        Args:
            data_adapter: DataAdapter for accessing CSV files
            mapper: Mapper for converting between domain and DataFrame
        """
        self._adapter = data_adapter
        self._mapper = mapper
        logger.debug("Initialized PandasPlayerRepository")
    
    def _load_data(self) -> pd.DataFrame:
        """Load player data from CSV."""
        return self._adapter.get_player_data()
    
    def _save_data(self, df: pd.DataFrame) -> None:
        """Save player data to CSV."""
        self._adapter.save_player_data(df)
    
    async def get_by_id(self, player_id: UUID) -> Optional[Player]:
        """Get player by ID from CSV."""
        df = self._load_data()
        if df.empty:
            return None
        
        row = df[df['id'] == str(player_id)]
        if row.empty:
            return None
        
        return self._mapper.to_domain(row.iloc[0])
    
    async def get_all(self) -> List[Player]:
        """Get all players from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        return [self._mapper.to_domain(row) for _, row in df.iterrows()]
    
    async def get_by_club(
        self,
        club_id: UUID
    ) -> List[Player]:
        """Get players for a club from CSV via ClubPlayer relationship."""
        # Get club_player relationships for this club
        club_player_df = self._adapter.get_club_player_data()
        if club_player_df.empty:
            return []
        
        # Filter by club_id and get player_ids
        club_players = club_player_df[club_player_df['club_id'] == str(club_id)]
        if club_players.empty:
            return []
        
        player_ids = set(club_players['player_id'].astype(str))
        
        # Get all players and filter by player_ids
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['id'].astype(str).isin(player_ids)]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def get_by_name(
        self,
        given_name: str,
        family_name: str
    ) -> List[Player]:
        """Get players by name from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[
            (df['given_name'] == given_name) &
            (df['family_name'] == family_name)
        ]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def get_by_team(
        self,
        team_id: UUID
    ) -> List[Player]:
        """Get players for a team from CSV."""
        # Note: CSV doesn't have team_id directly, would need to join with TeamSeason
        # For now, return empty list - this would require joining with team_season table
        logger.warning("get_by_team not fully implemented for CSV - requires join with TeamSeason")
        return []
    
    async def find_by_name(
        self,
        name: str
    ) -> List[Player]:
        """Find players by name (partial match) from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        # Search in full_name, given_name, and family_name
        filtered = df[
            df['full_name'].str.contains(name, case=False, na=False) |
            df['given_name'].str.contains(name, case=False, na=False) |
            df['family_name'].str.contains(name, case=False, na=False)
        ]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def add(self, player: Player) -> Player:
        """Add player to CSV file."""
        df = self._load_data()
        new_row = self._mapper.to_dataframe(player)
        
        # Check if player already exists
        if not df.empty and str(player.id) in df['id'].values:
            logger.warning(f"Player {player.id} already exists, updating instead")
            return await self.update(player)
        
        # Append new row
        df = pd.concat([df, new_row.to_frame().T], ignore_index=True)
        self._save_data(df)
        logger.debug(f"Added player {player.id} to CSV")
        return player
    
    async def update(self, player: Player) -> Player:
        """Update existing player in CSV file."""
        df = self._load_data()
        if df.empty:
            raise EntityNotFoundError(f"Player {player.id} not found")
        
        # Find and update row
        mask = df['id'] == str(player.id)
        if not mask.any():
            raise EntityNotFoundError(f"Player {player.id} not found")
        
        # Update each column individually to preserve dtypes
        updated_row = self._mapper.to_dataframe(player)
        for col in df.columns:
            if col in updated_row.index:
                df.loc[mask, col] = updated_row[col]
        self._save_data(df)
        logger.info(f"Updated player {player.id} in CSV")
        return player
    
    async def delete(self, player_id: UUID) -> None:
        """Delete player from CSV file."""
        df = self._load_data()
        if df.empty:
            raise EntityNotFoundError(f"Player {player_id} not found")
        
        # Find and remove row
        mask = df['id'] == str(player_id)
        if not mask.any():
            raise EntityNotFoundError(f"Player {player_id} not found")
        
        df = df[~mask]
        self._save_data(df)
        logger.info(f"Deleted player {player_id} from CSV")
    
    async def exists(self, player_id: UUID) -> bool:
        """Check if player exists in CSV."""
        df = self._load_data()
        if df.empty:
            return False
        
        return str(player_id) in df['id'].values

