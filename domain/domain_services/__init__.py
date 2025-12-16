"""
Domain Services

Domain services contain business logic that doesn't naturally fit
within a single entity or value object.
"""

from domain.domain_services.handicap_calculator import HandicapCalculator

__all__ = [
    'HandicapCalculator',
]

