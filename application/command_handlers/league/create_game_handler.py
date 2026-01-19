"""
Create Game Handler.

Handler for CreateGameCommand that creates a new match/game.
"""

from uuid import UUID
from domain.repositories.match_repository import MatchRepository
from domain.repositories.event_repository import EventRepository
from domain.repositories.team_season_repository import TeamSeasonRepository
from domain.entities.match import Match, MatchStatus
from application.commands.league.create_game_command import CreateGameCommand
from application.dto.command_result_dto import CreateGameResultDTO
from application.exceptions import EntityNotFoundError, ValidationError
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class CreateGameHandler:
    """
    Handler for CreateGameCommand.
    
    Creates a new match/game between two teams.
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
    
    async def handle(self, command: CreateGameCommand) -> CreateGameResultDTO:
        """
        Handle CreateGameCommand.
        
        Args:
            command: The command containing match data
        
        Returns:
            CreateGameResultDTO with the created match ID
        
        Raises:
            EntityNotFoundError: If event or team seasons not found
            ValidationError: If command data is invalid
        """
        # 1. Validate event exists
        event = await self._event_repo.get_by_id(command.event_id)
        if not event:
            raise EntityNotFoundError(f"Event {command.event_id} not found")
        
        # 2. Validate team seasons exist
        team1_season = await self._team_season_repo.get_by_id(command.team1_team_season_id)
        if not team1_season:
            raise EntityNotFoundError(f"TeamSeason {command.team1_team_season_id} not found")
        
        team2_season = await self._team_season_repo.get_by_id(command.team2_team_season_id)
        if not team2_season:
            raise EntityNotFoundError(f"TeamSeason {command.team2_team_season_id} not found")
        
        # 3. Validate teams are different
        if command.team1_team_season_id == command.team2_team_season_id:
            raise ValidationError("Team1 and Team2 must be different")
        
        # 4. Validate round number
        if command.round_number < 1:
            raise ValidationError(f"Round number must be positive, got: {command.round_number}")
        
        # 5. Validate match number
        if command.match_number < 0:
            raise ValidationError(f"Match number must be non-negative, got: {command.match_number}")
        
        # 6. Validate scores are non-negative
        if command.team1_total_score < 0:
            raise ValidationError(f"Team1 total score must be non-negative, got: {command.team1_total_score}")
        if command.team2_total_score < 0:
            raise ValidationError(f"Team2 total score must be non-negative, got: {command.team2_total_score}")
        
        # 7. Check if match already exists (same event, round, teams)
        existing_matches = await self._match_repo.get_by_event(command.event_id)
        for existing_match in existing_matches:
            if (existing_match.round_number == command.round_number and
                ((existing_match.team1_team_season_id == command.team1_team_season_id and
                  existing_match.team2_team_season_id == command.team2_team_season_id) or
                 (existing_match.team1_team_season_id == command.team2_team_season_id and
                  existing_match.team2_team_season_id == command.team1_team_season_id))):
                raise ValidationError(
                    f"Match already exists between these teams in event {command.event_id}, "
                    f"round {command.round_number}"
                )
        
        # 8. Create match entity
        match = Match(
            event_id=command.event_id,
            round_number=command.round_number,
            match_number=command.match_number,
            team1_team_season_id=command.team1_team_season_id,
            team2_team_season_id=command.team2_team_season_id,
            team1_total_score=command.team1_total_score,
            team2_total_score=command.team2_total_score,
            status=command.status
        )
        
        # 9. Save match
        created_match = await self._match_repo.add(match)
        
        logger.info(
            f"Created match {created_match.id} between teams "
            f"{command.team1_team_season_id} and {command.team2_team_season_id} "
            f"in event {command.event_id}, round {command.round_number}"
        )
        
        # 10. Return result
        return CreateGameResultDTO(
            success=True,
            message=f"Match created successfully",
            command_id=command.command_id,
            timestamp=command.timestamp,
            match_id=created_match.id
        )
