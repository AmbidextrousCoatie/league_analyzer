"""
Base query classes.

Queries represent read operations (no state changes).
"""

from abc import ABC
from dataclasses import dataclass
from uuid import UUID, uuid4
from datetime import datetime


@dataclass(frozen=True)
class Query(ABC):
    """
    Base class for all queries.
    
    Queries are immutable and represent a request for data.
    """
    query_id: UUID = uuid4()
    timestamp: datetime = datetime.utcnow()

