"""
Update Game Command.

Command to update an existing match/game.
"""

from dataclasses import dataclass
from uuid import UUID
from typing import Optional
from application.commands.base_command import Command
from domain.entities.match import MatchStatus


@dataclass(frozen=True)
class UpdateGameCommand(Command):
    """
    Command to update an existing match/game.
    
    Attributes:
        match_id: UUID of the match to update (required)
        event_id: UUID of the event (optional)
        team1_team_season_id: UUID of the first team season (optional)
        team2_team_season_id: UUID of the second team season (optional)
        round_number: Round number within event (optional)
        match_number: Concurrent match identifier within round (optional)
        team1_total_score: Total score for team1 (optional)
        team2_total_score: Total score for team2 (optional)
        status: Match status (optional)
        command_id: Unique identifier for this command instance (inherited from base, auto-generated)
        timestamp: When the command was created (inherited from base, auto-generated)
    """
    match_id: UUID
    event_id: Optional[UUID] = None
    team1_team_season_id: Optional[UUID] = None
    team2_team_season_id: Optional[UUID] = None
    round_number: Optional[int] = None
    match_number: Optional[int] = None
    team1_total_score: Optional[float] = None
    team2_total_score: Optional[float] = None
    status: Optional[MatchStatus] = None
