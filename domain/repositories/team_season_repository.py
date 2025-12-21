"""
TeamSeason Repository Interface

Abstract interface for TeamSeason entity repositories.
Storage-agnostic - works for CSV or SQL implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from domain.entities.team_season import TeamSeason
from domain.value_objects.vacancy_status import VacancyStatus


class TeamSeasonRepository(ABC):
    """
    Repository interface for TeamSeason entities.
    
    Storage-agnostic interface - works for CSV or SQL implementations.
    """
    
    @abstractmethod
    async def get_by_id(self, team_season_id: UUID) -> Optional[TeamSeason]:
        """
        Get team season by ID.
        
        Args:
            team_season_id: UUID of the team season
        
        Returns:
            TeamSeason if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(self) -> List[TeamSeason]:
        """
        Get all team seasons.
        
        Returns:
            List of all team seasons
        """
        pass
    
    @abstractmethod
    async def get_by_league_season(
        self,
        league_season_id: UUID
    ) -> List[TeamSeason]:
        """
        Get all team seasons for a league season.
        
        Args:
            league_season_id: UUID of the league season
        
        Returns:
            List of team seasons for the league season
        """
        pass
    
    @abstractmethod
    async def get_by_club(
        self,
        club_id: UUID
    ) -> List[TeamSeason]:
        """
        Get all team seasons for a club.
        
        Args:
            club_id: UUID of the club
        
        Returns:
            List of team seasons for the club
        """
        pass
    
    @abstractmethod
    async def get_by_vacancy_status(
        self,
        vacancy_status: VacancyStatus
    ) -> List[TeamSeason]:
        """
        Get team seasons by vacancy status.
        
        Args:
            vacancy_status: VacancyStatus to filter by
        
        Returns:
            List of team seasons with the vacancy status
        """
        pass
    
    @abstractmethod
    async def add(self, team_season: TeamSeason) -> TeamSeason:
        """
        Add a new team season.
        
        Args:
            team_season: TeamSeason entity to add
        
        Returns:
            Added team season
        """
        pass
    
    @abstractmethod
    async def update(self, team_season: TeamSeason) -> TeamSeason:
        """
        Update an existing team season.
        
        Args:
            team_season: TeamSeason entity to update
        
        Returns:
            Updated team season
        
        Raises:
            EntityNotFoundError: If team season doesn't exist
        """
        pass
    
    @abstractmethod
    async def delete(self, team_season_id: UUID) -> None:
        """
        Delete a team season.
        
        Args:
            team_season_id: UUID of team season to delete
        
        Raises:
            EntityNotFoundError: If team season doesn't exist
        """
        pass
    
    @abstractmethod
    async def exists(self, team_season_id: UUID) -> bool:
        """
        Check if team season exists.
        
        Args:
            team_season_id: UUID to check
        
        Returns:
            True if exists, False otherwise
        """
        pass

