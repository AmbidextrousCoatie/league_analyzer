"""
Pandas Team Repository

CSV-based implementation of TeamRepository using Pandas DataFrames.
"""

import pandas as pd
from uuid import UUID
from typing import List, Optional
from domain.entities.team import Team
from domain.repositories.team_repository import TeamRepository
from domain.exceptions.domain_exception import EntityNotFoundError
from infrastructure.persistence.adapters.data_adapter import DataAdapter
from infrastructure.persistence.mappers.csv.team_mapper import PandasTeamMapper
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class PandasTeamRepository(TeamRepository):
    """
    CSV-based Team repository using Pandas DataFrames.
    
    This implementation reads/writes CSV files using Pandas DataFrames.
    """
    
    def __init__(
        self,
        data_adapter: DataAdapter,
        mapper: PandasTeamMapper
    ):
        """
        Initialize Pandas Team repository.
        
        Args:
            data_adapter: DataAdapter for accessing CSV files
            mapper: Mapper for converting between domain and DataFrame
        """
        self._adapter = data_adapter
        self._mapper = mapper
        logger.debug("Initialized PandasTeamRepository")
    
    def _load_data(self) -> pd.DataFrame:
        """Load team data from CSV."""
        return self._adapter.get_team_data()
    
    def _save_data(self, df: pd.DataFrame) -> None:
        """Save team data to CSV."""
        self._adapter.save_team_data(df)
    
    async def get_by_id(self, team_id: UUID) -> Optional[Team]:
        """Get team by ID from CSV."""
        df = self._load_data()
        if df.empty:
            return None
        
        row = df[df['id'] == str(team_id)]
        if row.empty:
            return None
        
        return self._mapper.to_domain(row.iloc[0])
    
    async def get_all(self) -> List[Team]:
        """Get all teams from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        return [self._mapper.to_domain(row) for _, row in df.iterrows()]
    
    async def get_by_club(
        self,
        club_id: UUID
    ) -> List[Team]:
        """Get teams for a club from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['club_id'] == str(club_id)]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def get_by_league(
        self,
        league_id: UUID
    ) -> List[Team]:
        """Get teams for a league from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['league_id'] == str(league_id)]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def find_by_name(
        self,
        name: str
    ) -> List[Team]:
        """Find teams by name (partial match) from CSV."""
        df = self._load_data()
        if df.empty:
            return []
        
        filtered = df[df['name'].str.contains(name, case=False, na=False)]
        return [self._mapper.to_domain(row) for _, row in filtered.iterrows()]
    
    async def add(self, team: Team) -> Team:
        """Add team to CSV file."""
        df = self._load_data()
        new_row = self._mapper.to_dataframe(team)
        
        # Check if team already exists
        if not df.empty and str(team.id) in df['id'].values:
            logger.warning(f"Team {team.id} already exists, updating instead")
            return await self.update(team)
        
        # Append new row
        df = pd.concat([df, new_row.to_frame().T], ignore_index=True)
        self._save_data(df)
        logger.info(f"Added team {team.id} to CSV")
        return team
    
    async def update(self, team: Team) -> Team:
        """Update existing team in CSV file."""
        df = self._load_data()
        if df.empty:
            raise EntityNotFoundError(f"Team {team.id} not found")
        
        # Find and update row
        mask = df['id'] == str(team.id)
        if not mask.any():
            raise EntityNotFoundError(f"Team {team.id} not found")
        
        # Update each column individually to preserve dtypes
        updated_row = self._mapper.to_dataframe(team)
        for col in df.columns:
            if col in updated_row.index:
                df.loc[mask, col] = updated_row[col]
        self._save_data(df)
        logger.info(f"Updated team {team.id} in CSV")
        return team
    
    async def delete(self, team_id: UUID) -> None:
        """Delete team from CSV file."""
        df = self._load_data()
        if df.empty:
            raise EntityNotFoundError(f"Team {team_id} not found")
        
        # Find and remove row
        mask = df['id'] == str(team_id)
        if not mask.any():
            raise EntityNotFoundError(f"Team {team_id} not found")
        
        df = df[~mask]
        self._save_data(df)
        logger.info(f"Deleted team {team_id} from CSV")
    
    async def exists(self, team_id: UUID) -> bool:
        """Check if team exists in CSV."""
        df = self._load_data()
        if df.empty:
            return False
        
        return str(team_id) in df['id'].values

