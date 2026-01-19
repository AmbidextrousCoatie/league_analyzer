"""
Delete Game Command.

Command to delete a match/game.
"""

from dataclasses import dataclass
from uuid import UUID
from application.commands.base_command import Command


@dataclass(frozen=True)
class DeleteGameCommand(Command):
    """
    Command to delete a match/game.
    
    Attributes:
        match_id: UUID of the match to delete (required)
        command_id: Unique identifier for this command instance (inherited from base, auto-generated)
        timestamp: When the command was created (inherited from base, auto-generated)
    """
    match_id: UUID
