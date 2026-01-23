"""
Command Result Data Transfer Objects.

DTOs for command execution results.
"""

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class CommandResultDTO:
    """Base result DTO for command execution."""
    success: bool
    message: str
    command_id: UUID
    timestamp: datetime


@dataclass
class CreateGameResultDTO(CommandResultDTO):
    """Result DTO for CreateGameCommand."""
    match_id: UUID


@dataclass
class UpdateGameResultDTO(CommandResultDTO):
    """Result DTO for UpdateGameCommand."""
    match_id: UUID


@dataclass
class DeleteGameResultDTO(CommandResultDTO):
    """Result DTO for DeleteGameCommand."""
    match_id: UUID


@dataclass
class CreateTeamResultDTO(CommandResultDTO):
    """Result DTO for CreateTeamCommand."""
    team_id: UUID


@dataclass
class UpdateTeamResultDTO(CommandResultDTO):
    """Result DTO for UpdateTeamCommand."""
    team_id: UUID


@dataclass
class DeleteTeamResultDTO(CommandResultDTO):
    """Result DTO for DeleteTeamCommand."""
    team_id: UUID
