"""
Update Game Handler.

Handler for UpdateGameCommand that updates an existing match/game.
"""

from uuid import UUID
from domain.repositories.match_repository import MatchRepository
from domain.repositories.event_repository import EventRepository
from domain.repositories.team_season_repository import TeamSeasonRepository
from domain.entities.match import Match, MatchStatus
from application.commands.league.update_game_command import UpdateGameCommand
from application.dto.command_result_dto import UpdateGameResultDTO
from application.exceptions import EntityNotFoundError, ValidationError
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class UpdateGameHandler:
    """
    Handler for UpdateGameCommand.
    
    Updates an existing match/game.
    """
    
    def __init__(
        self,
        match_repository: MatchRepository,
        event_repository: EventRepository,
        team_season_repository: TeamSeasonRepository
    ):
        """
        Initialize handler with required repositories.
        
        Args:
            match_repository: Repository for Match entities
            event_repository: Repository for Event entities
            team_season_repository: Repository for TeamSeason entities
        """
        self._match_repo = match_repository
        self._event_repo = event_repository
        self._team_season_repo = team_season_repository
    
    async def handle(self, command: UpdateGameCommand) -> UpdateGameResultDTO:
        """
        Handle UpdateGameCommand.
        
        Args:
            command: The command containing match updates
        
        Returns:
            UpdateGameResultDTO with the updated match ID
        
        Raises:
            EntityNotFoundError: If match, event, or team seasons not found
            ValidationError: If command data is invalid
        """
        # 1. Load existing match
        match = await self._match_repo.get_by_id(command.match_id)
        if not match:
            raise EntityNotFoundError(f"Match {command.match_id} not found")
        
        # 2. Validate event if provided
        if command.event_id is not None:
            event = await self._event_repo.get_by_id(command.event_id)
            if not event:
                raise EntityNotFoundError(f"Event {command.event_id} not found")
        
        # 3. Validate team seasons if provided
        if command.team1_team_season_id is not None:
            team1_season = await self._team_season_repo.get_by_id(command.team1_team_season_id)
            if not team1_season:
                raise EntityNotFoundError(f"TeamSeason {command.team1_team_season_id} not found")
        
        if command.team2_team_season_id is not None:
            team2_season = await self._team_season_repo.get_by_id(command.team2_team_season_id)
            if not team2_season:
                raise EntityNotFoundError(f"TeamSeason {command.team2_team_season_id} not found")
        
        # 4. Validate teams are different if both provided
        team1_id = command.team1_team_season_id if command.team1_team_season_id is not None else match.team1_team_season_id
        team2_id = command.team2_team_season_id if command.team2_team_season_id is not None else match.team2_team_season_id
        if team1_id == team2_id:
            raise ValidationError("Team1 and Team2 must be different")
        
        # 5. Validate round number if provided
        if command.round_number is not None and command.round_number < 1:
            raise ValidationError(f"Round number must be positive, got: {command.round_number}")
        
        # 6. Validate match number if provided
        if command.match_number is not None and command.match_number < 0:
            raise ValidationError(f"Match number must be non-negative, got: {command.match_number}")
        
        # 7. Validate scores if provided
        if command.team1_total_score is not None and command.team1_total_score < 0:
            raise ValidationError(f"Team1 total score must be non-negative, got: {command.team1_total_score}")
        if command.team2_total_score is not None and command.team2_total_score < 0:
            raise ValidationError(f"Team2 total score must be non-negative, got: {command.team2_total_score}")
        
        # 8. Update match fields
        # Use update methods where available, otherwise create new instance
        updated_event_id = command.event_id if command.event_id is not None else match.event_id
        updated_team1_id = command.team1_team_season_id if command.team1_team_season_id is not None else match.team1_team_season_id
        updated_team2_id = command.team2_team_season_id if command.team2_team_season_id is not None else match.team2_team_season_id
        updated_round = command.round_number if command.round_number is not None else match.round_number
        updated_match_num = command.match_number if command.match_number is not None else match.match_number
        updated_team1_score = command.team1_total_score if command.team1_total_score is not None else match.team1_total_score
        updated_team2_score = command.team2_total_score if command.team2_total_score is not None else match.team2_total_score
        updated_status = command.status if command.status is not None else match.status
        
        # Create updated match instance
        updated_match = Match(
            id=match.id,
            event_id=updated_event_id,
            round_number=updated_round,
            match_number=updated_match_num,
            team1_team_season_id=updated_team1_id,
            team2_team_season_id=updated_team2_id,
            team1_total_score=updated_team1_score,
            team2_total_score=updated_team2_score,
            status=updated_status,
            created_at=match.created_at,
            updated_at=match.updated_at
        )
        
        # 9. Save updated match
        saved_match = await self._match_repo.update(updated_match)
        
        logger.info(f"Updated match {saved_match.id}")
        
        # 10. Return result
        return UpdateGameResultDTO(
            success=True,
            message=f"Match updated successfully",
            command_id=command.command_id,
            timestamp=command.timestamp,
            match_id=saved_match.id
        )
