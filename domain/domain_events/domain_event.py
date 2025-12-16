"""
Base domain event class.

Domain events represent something important that happened in the domain.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass(frozen=True)
class DomainEvent(ABC):
    """Base class for all domain events."""
    
    event_id: UUID = field(default_factory=uuid4, kw_only=True)
    occurred_at: datetime = field(default_factory=datetime.utcnow, kw_only=True)
    
    def __post_init__(self):
        """Validate event invariants."""
        pass


@dataclass(frozen=True)
class GameCreated(DomainEvent):
    """Event raised when a game is created."""
    game_id: UUID
    league_id: UUID
    season: str
    week: int
    
    def __post_init__(self):
        super().__post_init__()


@dataclass(frozen=True)
class GameUpdated(DomainEvent):
    """Event raised when a game is updated."""
    game_id: UUID
    league_id: UUID
    
    def __post_init__(self):
        super().__post_init__()


@dataclass(frozen=True)
class GameDeleted(DomainEvent):
    """Event raised when a game is deleted."""
    game_id: UUID
    league_id: UUID
    
    def __post_init__(self):
        super().__post_init__()


@dataclass(frozen=True)
class GameResultAdded(DomainEvent):
    """Event raised when a game result is added."""
    game_id: UUID
    player_id: UUID
    score: float
    
    def __post_init__(self):
        super().__post_init__()


@dataclass(frozen=True)
class GameResultUpdated(DomainEvent):
    """Event raised when a game result is updated."""
    game_id: UUID
    player_id: UUID
    old_score: float
    new_score: float
    
    def __post_init__(self):
        super().__post_init__()


@dataclass(frozen=True)
class DataImported(DomainEvent):
    """Event raised when data is imported."""
    source: str
    record_count: int
    league_id: UUID | None = None
    
    def __post_init__(self):
        super().__post_init__()


@dataclass(frozen=True)
class TeamAddedToLeague(DomainEvent):
    """Event raised when a team is added to a league."""
    league_id: UUID
    team_id: UUID
    
    def __post_init__(self):
        super().__post_init__()

