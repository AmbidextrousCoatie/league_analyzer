"""
Pandas Match Repository

CSV-based implementation of MatchRepository using Pandas DataFrames.
"""

import pandas as pd
from uuid import UUID
from typing import List, Optional
from domain.entities.match import Match, MatchStatus
from domain.repositories.match_repository import MatchRepository
from domain.exceptions.domain_exception import EntityNotFoundError
from infrastructure.persistence.adapters.data_adapter import DataAdapter
from infrastructure.persistence.mappers.csv.match_mapper import PandasMatchMapper
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class PandasMatchRepository(MatchRepository):
    """
    CSV-based Match repository using Pandas DataFrames.
    
    This implementation reads/writes CSV files using Pandas DataFrames.
    """
    
    def __init__(
        self,
        data_adapter: DataAdapter,
        mapper: PandasMatchMapper
    ):
        """
        Initialize Pandas Match repository.
        
        Args:
            data_adapter: DataAdapter for accessing CSV files
            mapper: Mapper for converting between domain and DataFrame
        """
        self._adapter = data_adapter
        self._mapper = mapper
        logger.debug("Initialized PandasMatchRepository")
    
    def _load_data(self) -> pd.DataFrame:
        """Load match data from CSV."""
        return self._adapter.get_match_data()
    
    def _save_data(self, df: pd.DataFrame) -> None:
        """Save match data to CSV."""
        self._adapter.save_match_data(df)
    
    async def get_by_id(self, match_id: UUID) -> Optional[Match]:
        """Get match by ID from CSV."""
        df = self._load_data()
        if df.empty:
            return None
        
        row = df[df['id'] == str(match_id)]
        if row.empty:
            return None
        
        return self._mapper.to_domain(row.iloc[0])
    
    async def get_all(self) -> List[Match]:
        """Get all matches from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        return [self._mapper.to_domain(row) for _, row in df.iterrows()]
    
    async def get_by_event(self, event_id: UUID) -> List[Match]:
        """Get all matches for an event from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['event_id'] == str(event_id)]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def get_by_event_and_round(
        self,
        event_id: UUID,
        round_number: int
    ) -> List[Match]:
        """Get all matches for a specific event and round from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[
            (df['event_id'] == str(event_id)) &
            (df['round_number'] == round_number)
        ]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def get_by_team(self, team_season_id: UUID) -> List[Match]:
        """Get all matches for a team from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[
            (df['team1_team_season_id'] == str(team_season_id)) |
            (df['team2_team_season_id'] == str(team_season_id))
        ]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def find_match(
        self,
        event_id: UUID,
        round_number: int,
        team1_team_season_id: UUID,
        team2_team_season_id: UUID
    ) -> Optional[Match]:
        """Find a match by event, round, and teams from CSV."""
        df = self._load_data()
        if df.empty:
            return None
        
        filtered = df[
            (df['event_id'] == str(event_id)) &
            (df['round_number'] == round_number) &
            (
                ((df['team1_team_season_id'] == str(team1_team_season_id)) &
                 (df['team2_team_season_id'] == str(team2_team_season_id))) |
                ((df['team1_team_season_id'] == str(team2_team_season_id)) &
                 (df['team2_team_season_id'] == str(team1_team_season_id)))
            )
        ]
        
        if filtered.empty:
            return None
        
        return self._mapper.to_domain(filtered.iloc[0])
    
    async def get_by_status(self, status: MatchStatus) -> List[Match]:
        """Get all matches with a specific status from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['status'] == status.value]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def add(self, match: Match) -> Match:
        """Add match to CSV file."""
        df = self._load_data()
        new_row = self._mapper.to_dataframe(match)
        
        # Check if match already exists
        if not df.empty and str(match.id) in df['id'].values:
            logger.warning(f"Match {match.id} already exists, updating instead")
            return await self.update(match)
        
        # Append new row
        df = pd.concat([df, new_row.to_frame().T], ignore_index=True)
        self._save_data(df)
        logger.debug(f"Added match {match.id} to CSV")
        return match
    
    async def update(self, match: Match) -> Match:
        """Update existing match in CSV file."""
        df = self._load_data()
        if df.empty:
            raise EntityNotFoundError(f"Match {match.id} not found")
        
        # Find and update row
        mask = df['id'] == str(match.id)
        if not mask.any():
            raise EntityNotFoundError(f"Match {match.id} not found")
        
        # Update row
        updated_row = self._mapper.to_dataframe(match)
        for col in df.columns:
            if col in updated_row.index:
                df.loc[mask, col] = updated_row[col]
        self._save_data(df)
        logger.info(f"Updated match {match.id} in CSV")
        return match
    
    async def delete(self, match_id: UUID) -> None:
        """Delete match from CSV file."""
        df = self._load_data()
        if df.empty:
            raise EntityNotFoundError(f"Match {match_id} not found")
        
        # Find and remove row
        mask = df['id'] == str(match_id)
        if not mask.any():
            raise EntityNotFoundError(f"Match {match_id} not found")
        
        df = df[~mask]
        self._save_data(df)
        logger.info(f"Deleted match {match_id} from CSV")
    
    async def exists(self, match_id: UUID) -> bool:
        """Check if match exists in CSV."""
        df = self._load_data()
        if df.empty:
            return False
        
        return str(match_id) in df['id'].values

