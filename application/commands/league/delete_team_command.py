"""
Delete Team Command.

Command to delete an existing team.
"""

from dataclasses import dataclass, field
from uuid import UUID
from application.commands.base_command import Command


@dataclass(frozen=True)
class DeleteTeamCommand(Command):
    """
    Command to delete an existing team.
    
    Attributes:
        team_id: UUID of the team to delete (required)
        force: If True, delete even if team has related data (team seasons).
               If False, raise error if related data exists. Default: False
        command_id: Unique identifier for this command instance (inherited from base, auto-generated)
        timestamp: When the command was created (inherited from base, auto-generated)
    """
    team_id: UUID
    force: bool = field(default=False)
