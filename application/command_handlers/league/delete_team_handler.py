"""
Delete Team Handler.

Handler for DeleteTeamCommand that deletes an existing team.
"""

from uuid import UUID
from domain.repositories.team_repository import TeamRepository
from domain.repositories.team_season_repository import TeamSeasonRepository
from application.commands.league.delete_team_command import DeleteTeamCommand
from application.dto.command_result_dto import DeleteTeamResultDTO
from application.exceptions import EntityNotFoundError, ValidationError
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class DeleteTeamHandler:
    """
    Handler for DeleteTeamCommand.
    
    Deletes an existing team. Checks for related data (team seasons) and
    raises ValidationError unless force=True.
    """
    
    def __init__(
        self,
        team_repository: TeamRepository,
        team_season_repository: TeamSeasonRepository
    ):
        """
        Initialize handler with required repositories.
        
        Args:
            team_repository: Repository for Team entities
            team_season_repository: Repository for TeamSeason entities
        """
        self._team_repo = team_repository
        self._team_season_repo = team_season_repository
    
    async def handle(self, command: DeleteTeamCommand) -> DeleteTeamResultDTO:
        """
        Handle DeleteTeamCommand.
        
        Args:
            command: The command containing team ID to delete
        
        Returns:
            DeleteTeamResultDTO with the deleted team ID
        
        Raises:
            EntityNotFoundError: If team not found
            ValidationError: If team has related data and force=False
        """
        # 1. Check if team exists
        team = await self._team_repo.get_by_id(command.team_id)
        if not team:
            raise EntityNotFoundError(f"Team {command.team_id} not found")
        
        # 2. Check for related data (team seasons)
        related_team_seasons = await self._team_season_repo.get_by_team(command.team_id)
        
        # 3. If related data exists and force=False, raise error
        if related_team_seasons and not command.force:
            count = len(related_team_seasons)
            raise ValidationError(
                f"Team {command.team_id} has related data ({count} team season(s)). "
                f"Set force=True to delete anyway."
            )
        
        # 4. Delete team
        await self._team_repo.delete(command.team_id)
        
        logger.info(
            f"Deleted team {command.team_id} '{team.name}' "
            f"(force={command.force}, related_team_seasons={len(related_team_seasons) if related_team_seasons else 0})"
        )
        
        # 5. Return result DTO
        return DeleteTeamResultDTO(
            success=True,
            message=f"Team '{team.name}' deleted successfully",
            command_id=command.command_id,
            timestamp=command.timestamp,
            team_id=command.team_id
        )
