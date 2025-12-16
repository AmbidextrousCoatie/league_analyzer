"""
Unit of Work pattern.

Manages transactions and ensures atomic operations.
"""

from abc import ABC, abstractmethod
from typing import Protocol


class UnitOfWork(ABC):
    """
    Unit of Work interface.
    
    Manages transactions and provides access to repositories.
    """
    
    @abstractmethod
    async def __aenter__(self):
        """Enter async context manager."""
        pass
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager."""
        pass
    
    @abstractmethod
    async def commit(self) -> None:
        """Commit the current transaction."""
        pass
    
    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the current transaction."""
        pass


class UnitOfWorkFactory(Protocol):
    """Factory protocol for creating UnitOfWork instances."""
    
    def __call__(self) -> UnitOfWork:
        """Create a new UnitOfWork instance."""
        ...

