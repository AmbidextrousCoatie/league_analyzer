"""
Base command handler interface.

Command handlers execute commands and coordinate domain objects.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from application.commands.base_command import Command

C = TypeVar('C', bound=Command)
R = TypeVar('R')


class CommandHandler(ABC, Generic[C, R]):
    """
    Base interface for command handlers.
    
    Handlers execute commands and return results.
    """
    
    @abstractmethod
    async def handle(self, command: C) -> R:
        """
        Handle a command.
        
        Args:
            command: The command to execute
        
        Returns:
            Result of command execution
        """
        pass

