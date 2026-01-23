"""
Update Team Command.

Command to update an existing team's information.
"""

from dataclasses import dataclass, field
from uuid import UUID
from typing import Optional
from application.commands.base_command import Command


@dataclass(frozen=True)
class UpdateTeamCommand(Command):
    """
    Command to update an existing team.
    
    Supports partial updates - only provided fields will be updated.
    
    Attributes:
        team_id: UUID of the team to update (required)
        name: New team name (optional)
        club_id: New club ID (optional)
        team_number: New team number (optional)
        command_id: Unique identifier for this command instance (inherited from base, auto-generated)
        timestamp: When the command was created (inherited from base, auto-generated)
    """
    team_id: UUID
    name: Optional[str] = None
    club_id: Optional[UUID] = None
    team_number: Optional[int] = None
