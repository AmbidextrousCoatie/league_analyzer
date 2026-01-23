"""
Create Team Handler.

Handler for CreateTeamCommand that creates a new team.
"""

from uuid import UUID
from domain.repositories.team_repository import TeamRepository
from domain.repositories.club_repository import ClubRepository
from domain.entities.team import Team
from application.commands.league.create_team_command import CreateTeamCommand
from application.dto.command_result_dto import CreateTeamResultDTO
from application.exceptions import EntityNotFoundError, ValidationError
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class CreateTeamHandler:
    """
    Handler for CreateTeamCommand.
    
    Creates a new team within a club.
    """
    
    def __init__(
        self,
        team_repository: TeamRepository,
        club_repository: ClubRepository
    ):
        """
        Initialize handler with required repositories.
        
        Args:
            team_repository: Repository for Team entities
            club_repository: Repository for Club entities
        """
        self._team_repo = team_repository
        self._club_repo = club_repository
    
    async def handle(self, command: CreateTeamCommand) -> CreateTeamResultDTO:
        """
        Handle CreateTeamCommand.
        
        Args:
            command: The command containing team data
        
        Returns:
            CreateTeamResultDTO with the created team ID
        
        Raises:
            EntityNotFoundError: If club not found
            ValidationError: If command data is invalid
        """
        # 1. Validate club exists
        club = await self._club_repo.get_by_id(command.club_id)
        if not club:
            raise EntityNotFoundError(f"Club {command.club_id} not found")
        
        # 2. Validate team name is not empty
        if not command.name or not command.name.strip():
            raise ValidationError("Team name cannot be empty")
        
        # 3. Validate team number is positive
        if command.team_number < 1:
            raise ValidationError(
                f"Team number must be positive, got: {command.team_number}"
            )
        
        # 4. Check for duplicate team (same club + team number)
        existing_teams = await self._team_repo.get_by_club(command.club_id)
        for existing_team in existing_teams:
            if existing_team.team_number == command.team_number:
                raise ValidationError(
                    f"Team with number {command.team_number} already exists "
                    f"for club {command.club_id}"
                )
        
        # 5. Create Team entity
        team = Team(
            name=command.name.strip(),
            club_id=command.club_id,
            team_number=command.team_number
        )
        
        # 6. Save via repository
        created_team = await self._team_repo.add(team)
        
        logger.info(
            f"Created team {created_team.id} '{created_team.name}' "
            f"for club {command.club_id}, team number {command.team_number}"
        )
        
        # 7. Return result DTO
        return CreateTeamResultDTO(
            success=True,
            message=f"Team '{created_team.name}' created successfully",
            command_id=command.command_id,
            timestamp=command.timestamp,
            team_id=created_team.id
        )
