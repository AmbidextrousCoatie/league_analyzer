"""
Base query handler interface.

Query handlers execute queries and return data.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from application.queries.base_query import Query

Q = TypeVar('Q', bound=Query)
R = TypeVar('R')


class QueryHandler(ABC, Generic[Q, R]):
    """
    Base interface for query handlers.
    
    Handlers execute queries and return results.
    """
    
    @abstractmethod
    async def handle(self, query: Q) -> R:
        """
        Handle a query.
        
        Args:
            query: The query to execute
        
        Returns:
            Query result
        """
        pass

