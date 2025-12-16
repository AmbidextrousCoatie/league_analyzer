"""
Base command classes.

Commands represent write operations (intent to change state).
"""

from abc import ABC
from dataclasses import dataclass
from uuid import UUID, uuid4
from datetime import datetime


@dataclass(frozen=True)
class Command(ABC):
    """
    Base class for all commands.
    
    Commands are immutable and represent an intent to perform an action.
    """
    command_id: UUID = uuid4()
    timestamp: datetime = datetime.utcnow()

