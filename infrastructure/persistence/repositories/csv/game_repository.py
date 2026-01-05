"""
Pandas Game Repository

CSV-based implementation of GameRepository using Pandas DataFrames.
"""

import pandas as pd
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from domain.entities.game import Game
from domain.repositories.game_repository import GameRepository
from domain.exceptions.domain_exception import EntityNotFoundError
from infrastructure.persistence.adapters.data_adapter import DataAdapter
from infrastructure.persistence.mappers.csv.game_mapper import PandasGameMapper
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class PandasGameRepository(GameRepository):
    """
    CSV-based Game repository using Pandas DataFrames.
    
    This implementation reads/writes CSV files using Pandas DataFrames.
    """
    
    def __init__(
        self,
        data_adapter: DataAdapter,
        mapper: PandasGameMapper
    ):
        """
        Initialize Pandas Game repository.
        
        Args:
            data_adapter: DataAdapter for accessing CSV files
            mapper: Mapper for converting between domain and DataFrame
        """
        self._adapter = data_adapter
        self._mapper = mapper
        logger.debug("Initialized PandasGameRepository")
    
    def _load_data(self) -> pd.DataFrame:
        """Load game data from CSV."""
        return self._adapter.get_game_data()
    
    def _save_data(self, df: pd.DataFrame) -> None:
        """Save game data to CSV."""
        self._adapter.save_game_data(df)
    
    async def get_by_id(self, game_id: UUID) -> Optional[Game]:
        """Get game by ID from CSV."""
        df = self._load_data()
        if df.empty:
            return None
        
        row = df[df['id'] == str(game_id)]
        if row.empty:
            return None
        
        return self._mapper.to_domain(row.iloc[0])
    
    async def get_all(self) -> List[Game]:
        """Get all games from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        games = []
        for _, row in df.iterrows():
            game = self._mapper.to_domain(row)
            if game is not None:  # Filter out None values from invalid rows
                games.append(game)
        return games
    
    async def get_by_event(
        self,
        event_id: UUID
    ) -> List[Game]:
        """Get games for an event from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['event_id'] == str(event_id)]
        games = []
        for _, row in filtered.iterrows():
            game = self._mapper.to_domain(row)
            if game is not None:
                games.append(game)
        return games
    
    async def get_by_team_season(
        self,
        team_season_id: UUID
    ) -> List[Game]:
        """Get games for a team season from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['team_season_id'] == str(team_season_id)]
        games = []
        for _, row in filtered.iterrows():
            game = self._mapper.to_domain(row)
            if game is not None:
                games.append(game)
        return games
    
    async def get_by_event_and_match(
        self,
        event_id: UUID,
        match_number: int
    ) -> List[Game]:
        """Get games by event and match number from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[
            (df['event_id'] == str(event_id)) &
            (df['match_number'] == match_number)
        ]
        games = []
        for _, row in filtered.iterrows():
            game = self._mapper.to_domain(row)
            if game is not None:
                games.append(game)
        return games
    
    async def get_by_league(
        self,
        league_id: UUID
    ) -> List[Game]:
        """Get games for a league from CSV."""
        # Note: CSV doesn't have league_id directly, would need to join with Event
        # For now, return empty list - this would require joining with event table
        logger.warning("get_by_league not fully implemented for CSV - requires join with Event")
        return []
    
    async def get_by_week(
        self,
        league_id: UUID,
        week: int
    ) -> List[Game]:
        """Get games for a specific week from CSV."""
        # Note: CSV doesn't have league_id/week directly, would need to join with Event
        # For now, return empty list - this would require joining with event table
        logger.warning("get_by_week not fully implemented for CSV - requires join with Event")
        return []
    
    async def get_by_team(
        self,
        team_id: UUID
    ) -> List[Game]:
        """Get games for a team from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        # Filter by team_season_id (which represents the team in a season)
        # Note: team_id parameter is treated as team_season_id
        filtered = df[df['team_season_id'] == str(team_id)]
        games = []
        for _, row in filtered.iterrows():
            game = self._mapper.to_domain(row)
            if game is not None:
                games.append(game)
        return games
    
    async def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Game]:
        """Get games within date range from CSV."""
        # Note: CSV doesn't have date directly, would need to join with Event
        # For now, return empty list - this would require joining with event table
        logger.warning("get_by_date_range not fully implemented for CSV - requires join with Event")
        return []
    
    async def add(self, game: Game) -> Game:
        """Add game to CSV file."""
        df = self._load_data()
        new_row = self._mapper.to_dataframe(game)
        
        # Check if game already exists
        if not df.empty and str(game.id) in df['id'].values:
            logger.warning(f"Game {game.id} already exists, updating instead")
            return await self.update(game)
        
        # Append new row
        df = pd.concat([df, new_row.to_frame().T], ignore_index=True)
        self._save_data(df)
        #logger.info(f"Added game {game.id} to CSV")
        return game
    
    async def update(self, game: Game) -> Game:
        """Update existing game in CSV file."""
        df = self._load_data()
        if df.empty:
            raise EntityNotFoundError(f"Game {game.id} not found")
        
        # Find and update row
        mask = df['id'] == str(game.id)
        if not mask.any():
            raise EntityNotFoundError(f"Game {game.id} not found")
        
        # Update each column individually to preserve dtypes
        updated_row = self._mapper.to_dataframe(game)
        for col in df.columns:
            if col in updated_row.index:
                df.loc[mask, col] = updated_row[col]
        self._save_data(df)
        logger.info(f"Updated game {game.id} in CSV")
        return game
    
    async def delete(self, game_id: UUID) -> None:
        """Delete game from CSV file."""
        df = self._load_data()
        if df.empty:
            raise EntityNotFoundError(f"Game {game_id} not found")
        
        # Find and remove row
        mask = df['id'] == str(game_id)
        if not mask.any():
            raise EntityNotFoundError(f"Game {game_id} not found")
        
        df = df[~mask]
        self._save_data(df)
        logger.info(f"Deleted game {game_id} from CSV")
    
    async def exists(self, game_id: UUID) -> bool:
        """Check if game exists in CSV."""
        df = self._load_data()
        if df.empty:
            return False
        
        return str(game_id) in df['id'].values

