"""
Update Team Handler.

Handler for UpdateTeamCommand that updates an existing team.
"""

from uuid import UUID
from domain.repositories.team_repository import TeamRepository
from domain.repositories.club_repository import ClubRepository
from domain.entities.team import Team
from application.commands.league.update_team_command import UpdateTeamCommand
from application.dto.command_result_dto import UpdateTeamResultDTO
from application.exceptions import EntityNotFoundError, ValidationError
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class UpdateTeamHandler:
    """
    Handler for UpdateTeamCommand.
    
    Updates an existing team's information. Supports partial updates.
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
    
    async def handle(self, command: UpdateTeamCommand) -> UpdateTeamResultDTO:
        """
        Handle UpdateTeamCommand.
        
        Args:
            command: The command containing team updates
        
        Returns:
            UpdateTeamResultDTO with the updated team ID
        
        Raises:
            EntityNotFoundError: If team or club not found
            ValidationError: If command data is invalid
        """
        # 1. Load existing team
        team = await self._team_repo.get_by_id(command.team_id)
        if not team:
            raise EntityNotFoundError(f"Team {command.team_id} not found")
        
        # 2. Validate club exists if provided
        new_club_id = command.club_id
        if new_club_id is not None:
            club = await self._club_repo.get_by_id(new_club_id)
            if not club:
                raise EntityNotFoundError(f"Club {new_club_id} not found")
        
        # 3. Validate team name if provided
        if command.name is not None:
            if not command.name.strip():
                raise ValidationError("Team name cannot be empty")
        
        # 4. Validate team number if provided
        if command.team_number is not None:
            if command.team_number < 1:
                raise ValidationError(
                    f"Team number must be positive, got: {command.team_number}"
                )
        
        # 5. Determine which fields are being updated
        updated_club_id = new_club_id if new_club_id is not None else team.club_id
        updated_team_number = command.team_number if command.team_number is not None else team.team_number
        
        # 6. Check for duplicate team (if club or team_number changed)
        if new_club_id is not None or command.team_number is not None:
            existing_teams = await self._team_repo.get_by_club(updated_club_id)
            for existing_team in existing_teams:
                # Skip the team being updated
                if existing_team.id == team.id:
                    continue
                if existing_team.team_number == updated_team_number:
                    raise ValidationError(
                        f"Team with number {updated_team_number} already exists "
                        f"for club {updated_club_id}"
                    )
        
        # 7. Update Team entity using entity methods
        updated_team = Team(
            id=team.id,
            name=command.name.strip() if command.name is not None else team.name,
            club_id=updated_club_id,
            team_number=updated_team_number,
            created_at=team.created_at,
            updated_at=team.updated_at
        )
        
        # 8. Save via repository
        saved_team = await self._team_repo.update(updated_team)
        
        logger.info(
            f"Updated team {saved_team.id} '{saved_team.name}' "
            f"(club: {saved_team.club_id}, team_number: {saved_team.team_number})"
        )
        
        # 9. Return result DTO
        return UpdateTeamResultDTO(
            success=True,
            message=f"Team '{saved_team.name}' updated successfully",
            command_id=command.command_id,
            timestamp=command.timestamp,
            team_id=saved_team.id
        )
