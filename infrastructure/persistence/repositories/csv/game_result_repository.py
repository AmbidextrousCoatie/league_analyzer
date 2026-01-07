"""
Pandas Game Result Repository

CSV-based implementation of GameResultRepository using Pandas DataFrames.
"""

import pandas as pd
from uuid import UUID
from typing import List, Optional
from domain.entities.game_result import GameResult
from domain.repositories.game_result_repository import GameResultRepository
from domain.exceptions.domain_exception import EntityNotFoundError
from infrastructure.persistence.adapters.data_adapter import DataAdapter
from infrastructure.persistence.mappers.csv.game_result_mapper import PandasGameResultMapper
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class PandasGameResultRepository(GameResultRepository):
    """
    CSV-based GameResult repository using Pandas DataFrames.
    
    This implementation reads/writes CSV files using Pandas DataFrames.
    """
    
    def __init__(
        self,
        data_adapter: DataAdapter,
        mapper: PandasGameResultMapper
    ):
        """
        Initialize Pandas GameResult repository.
        
        Args:
            data_adapter: DataAdapter for accessing CSV files
            mapper: Mapper for converting between domain and DataFrame
        """
        self._adapter = data_adapter
        self._mapper = mapper
        logger.debug("Initialized PandasGameResultRepository")
    
    def _load_data(self) -> pd.DataFrame:
        """Load game result data from CSV."""
        return self._adapter.get_game_result_data()
    
    def _save_data(self, df: pd.DataFrame) -> None:
        """Save game result data to CSV."""
        self._adapter.save_game_result_data(df)
    
    async def get_by_id(self, game_result_id: UUID) -> Optional[GameResult]:
        """Get game result by ID from CSV."""
        df = self._load_data()
        if df.empty:
            return None
        
        row = df[df['id'] == str(game_result_id)]
        if row.empty:
            return None
        
        return self._mapper.to_domain(row.iloc[0])
    
    async def get_all(self) -> List[GameResult]:
        """Get all game results from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        return [self._mapper.to_domain(row) for _, row in df.iterrows()]
    
    async def get_by_match(self, match_id: UUID) -> List[GameResult]:
        """Get all game results for a match from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['match_id'] == str(match_id)]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def get_by_match_and_team(
        self,
        match_id: UUID,
        team_season_id: UUID
    ) -> List[GameResult]:
        """Get all game results for a match and team from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[
            (df['match_id'] == str(match_id)) &
            (df['team_season_id'] == str(team_season_id))
        ]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def get_by_player(self, player_id: UUID) -> List[GameResult]:
        """Get all game results for a player from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['player_id'] == str(player_id)]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def get_by_team(self, team_season_id: UUID) -> List[GameResult]:
        """Get all game results for a team from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['team_season_id'] == str(team_season_id)]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def find_by_match_and_position(
        self,
        match_id: UUID,
        team_season_id: UUID,
        position: int
    ) -> Optional[GameResult]:
        """Find a game result by match, team, and position from CSV."""
        df = self._load_data()
        if df.empty:
            return None
        
        filtered = df[
            (df['match_id'] == str(match_id)) &
            (df['team_season_id'] == str(team_season_id)) &
            (df['position'] == position)
        ]
        
        if filtered.empty:
            return None
        
        return self._mapper.to_domain(filtered.iloc[0])
    
    async def add(self, game_result: GameResult) -> GameResult:
        """Add game result to CSV file."""
        df = self._load_data()
        new_row = self._mapper.to_dataframe(game_result)
        
        # Check if game result already exists
        if not df.empty and str(game_result.id) in df['id'].values:
            logger.warning(f"GameResult {game_result.id} already exists, updating instead")
            return await self.update(game_result)
        
        # Append new row
        df = pd.concat([df, new_row.to_frame().T], ignore_index=True)
        self._save_data(df)
        logger.debug(f"Added game result {game_result.id} to CSV")
        return game_result
    
    async def update(self, game_result: GameResult) -> GameResult:
        """Update existing game result in CSV file."""
        df = self._load_data()
        if df.empty:
            raise EntityNotFoundError(f"GameResult {game_result.id} not found")
        
        # Find and update row
        mask = df['id'] == str(game_result.id)
        if not mask.any():
            raise EntityNotFoundError(f"GameResult {game_result.id} not found")
        
        # Update row
        updated_row = self._mapper.to_dataframe(game_result)
        for col in df.columns:
            if col in updated_row.index:
                df.loc[mask, col] = updated_row[col]
        self._save_data(df)
        logger.info(f"Updated game result {game_result.id} in CSV")
        return game_result
    
    async def delete(self, game_result_id: UUID) -> None:
        """Delete game result from CSV file."""
        df = self._load_data()
        if df.empty:
            raise EntityNotFoundError(f"GameResult {game_result_id} not found")
        
        # Find and remove row
        mask = df['id'] == str(game_result_id)
        if not mask.any():
            raise EntityNotFoundError(f"GameResult {game_result_id} not found")
        
        df = df[~mask]
        self._save_data(df)
        logger.info(f"Deleted game result {game_result_id} from CSV")
    
    async def exists(self, game_result_id: UUID) -> bool:
        """Check if game result exists in CSV."""
        df = self._load_data()
        if df.empty:
            return False
        
        return str(game_result_id) in df['id'].values

