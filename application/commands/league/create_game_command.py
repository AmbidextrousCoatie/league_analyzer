"""
Create Game Command.

Command to create a new match/game between two teams.
"""

from dataclasses import dataclass, field
from uuid import UUID
from typing import Optional
from application.commands.base_command import Command
from domain.entities.match import MatchStatus


@dataclass(frozen=True)
class CreateGameCommand(Command):
    """
    Command to create a new match/game.
    
    Attributes:
        event_id: UUID of the event (required)
        team1_team_season_id: UUID of the first team season (required)
        team2_team_season_id: UUID of the second team season (required)
        round_number: Round number within event (required, default 1)
        match_number: Concurrent match identifier within round (required, default 0)
        team1_total_score: Initial total score for team1 (optional, default 0.0)
        team2_total_score: Initial total score for team2 (optional, default 0.0)
        status: Match status (optional, default SCHEDULED)
        command_id: Unique identifier for this command instance (inherited from base, auto-generated)
        timestamp: When the command was created (inherited from base, auto-generated)
    """
    event_id: UUID
    team1_team_season_id: UUID
    team2_team_season_id: UUID
    round_number: int = field(default=1)
    match_number: int = field(default=0)
    team1_total_score: float = field(default=0.0)
    team2_total_score: float = field(default=0.0)
    status: MatchStatus = field(default=MatchStatus.SCHEDULED)
