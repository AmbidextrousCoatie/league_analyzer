"""
Base domain exception class.

All domain-specific exceptions should inherit from this.
"""


class DomainException(Exception):
    """Base exception for domain errors."""
    
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class InvalidGameData(DomainException):
    """Raised when game data violates domain rules."""
    pass


class DuplicateGame(DomainException):
    """Raised when attempting to create a duplicate game."""
    pass


class InvalidScore(DomainException):
    """Raised when a score value is invalid."""
    pass


class InvalidTeamOperation(DomainException):
    """Raised when a team operation violates business rules."""
    pass

