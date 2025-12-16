"""
Base repository interface.

Repositories abstract data access and provide a collection-like interface
for domain entities.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
from uuid import UUID

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Base repository interface.
    
    Provides common CRUD operations for entities.
    """
    
    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """Get an entity by its ID."""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[T]:
        """Get all entities."""
        pass
    
    @abstractmethod
    async def add(self, entity: T) -> T:
        """Add a new entity."""
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update an existing entity."""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: UUID) -> None:
        """Delete an entity by ID."""
        pass
    
    @abstractmethod
    async def exists(self, entity_id: UUID) -> bool:
        """Check if an entity exists."""
        pass

