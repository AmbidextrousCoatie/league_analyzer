"""
Base Repository Interface

Abstract base interface for all repositories.
Provides common CRUD operations that work for any storage backend.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
from uuid import UUID

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Base repository interface - storage agnostic.
    
    All repositories implement these basic CRUD operations.
    Storage-specific implementations handle the details.
    """
    
    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """
        Get entity by ID.
        
        Args:
            entity_id: UUID of the entity
        
        Returns:
            Entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(self) -> List[T]:
        """
        Get all entities.
        
        Returns:
            List of all entities
        """
        pass
    
    @abstractmethod
    async def add(self, entity: T) -> T:
        """
        Add a new entity.
        
        Args:
            entity: Entity to add
        
        Returns:
            Added entity (with generated ID if applicable)
        """
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """
        Update an existing entity.
        
        Args:
            entity: Entity to update
        
        Returns:
            Updated entity
        
        Raises:
            EntityNotFoundError: If entity doesn't exist
        """
        pass
    
    @abstractmethod
    async def delete(self, entity_id: UUID) -> None:
        """
        Delete an entity by ID.
        
        Args:
            entity_id: UUID of entity to delete
        
        Raises:
            EntityNotFoundError: If entity doesn't exist
        """
        pass
    
    @abstractmethod
    async def exists(self, entity_id: UUID) -> bool:
        """
        Check if entity exists.
        
        Args:
            entity_id: UUID to check
        
        Returns:
            True if exists, False otherwise
        """
        pass

