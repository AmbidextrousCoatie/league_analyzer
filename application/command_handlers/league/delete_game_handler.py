"""
Delete Game Handler.

Handler for DeleteGameCommand that deletes a match/game.
"""

from uuid import UUID
from domain.repositories.match_repository import MatchRepository
from application.commands.league.delete_game_command import DeleteGameCommand
from application.dto.command_result_dto import DeleteGameResultDTO
from application.exceptions import EntityNotFoundError
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class DeleteGameHandler:
    """
    Handler for DeleteGameCommand.
    
    Deletes an existing match/game.
    """
    
    def __init__(
        self,
        match_repository: MatchRepository
    ):
        """
        Initialize handler with required repositories.
        
        Args:
            match_repository: Repository for Match entities
        """
        self._match_repo = match_repository
    
    async def handle(self, command: DeleteGameCommand) -> DeleteGameResultDTO:
        """
        Handle DeleteGameCommand.
        
        Args:
            command: The command containing match ID to delete
        
        Returns:
            DeleteGameResultDTO with the deleted match ID
        
        Raises:
            EntityNotFoundError: If match not found
        """
        # 1. Check if match exists
        match = await self._match_repo.get_by_id(command.match_id)
        if not match:
            raise EntityNotFoundError(f"Match {command.match_id} not found")
        
        # 2. Delete match
        await self._match_repo.delete(command.match_id)
        
        logger.info(f"Deleted match {command.match_id}")
        
        # 3. Return result
        return DeleteGameResultDTO(
            success=True,
            message=f"Match deleted successfully",
            command_id=command.command_id,
            timestamp=command.timestamp,
            match_id=command.match_id
        )
