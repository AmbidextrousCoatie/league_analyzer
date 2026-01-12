"""
Application layer exceptions.

Exceptions specific to the application layer (handlers, use cases).
"""


class EntityNotFoundError(Exception):
    """Raised when an entity is not found."""
    pass


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class BusinessRuleViolationError(Exception):
    """Raised when a business rule is violated."""
    pass
