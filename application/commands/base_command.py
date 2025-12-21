"""
Base command classes.

Commands represent write operations (intent to change state) in the CQRS pattern.
All commands inherit from the Command base class and are immutable data structures
that represent user intent to perform an action.

See Also:
    application.command_handlers.base_handler.CommandHandler - Command handlers
    docs/architecture/application_layer.md - Application layer documentation
    docs/guides/cqrs.md - CQRS pattern guide
"""

from abc import ABC
from dataclasses import dataclass
from uuid import UUID, uuid4
from datetime import datetime


@dataclass(frozen=True)
class Command(ABC):
    """
    Base class for all commands.
    
    Commands are immutable data structures that represent an intent to perform
    a write operation (change state) in the system. They are processed by
    command handlers which orchestrate the domain logic.
    
    All commands must be immutable (frozen dataclass) and contain all data
    needed to execute the operation. Commands are validated before being
    processed by handlers.
    
    Attributes:
        command_id: Unique identifier for this command instance
        timestamp: When the command was created
    
    Example:
        >>> from uuid import uuid4
        >>> class CreateGame(Command):
        ...     league_id: UUID
        ...     week: int
        >>> command = CreateGame(
        ...     command_id=uuid4(),
        ...     timestamp=datetime.utcnow(),
        ...     league_id=uuid4(),
        ...     week=1
        ... )
        >>> print(command.command_id)
        uuid
    
    See Also:
        application.queries.base_query.Query - Base class for queries (read operations)
        docs/architecture/application_layer.md - Application layer documentation
        docs/guides/cqrs.md - CQRS pattern guide
    
    Note:
        Commands should not contain business logic. Business logic belongs
        in domain entities and domain services.
    """
    command_id: UUID = uuid4()
    timestamp: datetime = datetime.utcnow()

