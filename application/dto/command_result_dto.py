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
