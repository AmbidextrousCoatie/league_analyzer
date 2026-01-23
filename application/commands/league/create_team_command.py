"""
Create Team Command.

Command to create a new team within a club.
"""

from dataclasses import dataclass, field
from uuid import UUID
from application.commands.base_command import Command


@dataclass(frozen=True)
class CreateTeamCommand(Command):
    """
    Command to create a new team.
    
    Attributes:
        name: Team name (required)
        club_id: UUID of the club this team belongs to (required)
        team_number: Squad number within the club (optional, default 1)
        command_id: Unique identifier for this command instance (inherited from base, auto-generated)
        timestamp: When the command was created (inherited from base, auto-generated)
    """
    name: str
    club_id: UUID
    team_number: int = field(default=1)
