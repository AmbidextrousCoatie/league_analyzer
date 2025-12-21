"""
DEPRECATED: Base repository interface moved to domain/repositories/base_repository.py

This file is kept for backward compatibility.
Import from domain.repositories instead.
"""

# Re-export from domain layer for backward compatibility
from domain.repositories.base_repository import BaseRepository

__all__ = ['BaseRepository']

