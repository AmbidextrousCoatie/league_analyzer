"""
Base query classes.

Queries represent read operations (no state changes).
"""

from abc import ABC
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime


@dataclass(frozen=True)
class Query(ABC):
    """
    Base class for all queries.
    
    Queries are immutable and represent a request for data.
    
    Attributes:
        query_id: Unique identifier for this query instance
        timestamp: When the query was created
    
    Note: Base class fields use init=False to allow subclasses to define
    required fields without field ordering issues.
    """
    query_id: UUID = field(default_factory=uuid4, init=False)
    timestamp: datetime = field(default_factory=datetime.utcnow, init=False)
    
    def __post_init__(self):
        """Initialize base class fields after subclass fields."""
        # Set query_id and timestamp if not already set
        object.__setattr__(self, 'query_id', uuid4())
        object.__setattr__(self, 'timestamp', datetime.utcnow())
