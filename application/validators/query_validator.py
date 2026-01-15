"""
Query Validation Utilities.

Provides validation functions for query objects to ensure data integrity
before processing.
"""

from uuid import UUID
from typing import Optional, List
from application.exceptions import ValidationError
from domain.value_objects.season import Season


def validate_uuid(value: any, field_name: str) -> UUID:
    """
    Validate and convert a value to UUID.
    
    Args:
        value: Value to validate (can be UUID, str, or None)
        field_name: Name of the field for error messages
    
    Returns:
        UUID object
    
    Raises:
        ValidationError: If value cannot be converted to UUID
    """
    if value is None:
        raise ValidationError(f"{field_name} is required")
    
    if isinstance(value, UUID):
        return value
    
    if isinstance(value, str):
        try:
            return UUID(value)
        except ValueError:
            raise ValidationError(f"{field_name} must be a valid UUID, got: {value}")
    
    raise ValidationError(f"{field_name} must be a UUID or UUID string, got: {type(value).__name__}")


def validate_optional_uuid(value: any, field_name: str) -> Optional[UUID]:
    """
    Validate and convert an optional value to UUID.
    
    Args:
        value: Value to validate (can be UUID, str, or None)
        field_name: Name of the field for error messages
    
    Returns:
        UUID object or None
    
    Raises:
        ValidationError: If value cannot be converted to UUID
    """
    if value is None:
        return None
    
    return validate_uuid(value, field_name)


def validate_season_string(season_str: str, field_name: str = "season") -> str:
    """
    Validate season string format.
    
    Args:
        season_str: Season string to validate (e.g., "2025-26", "25/26")
        field_name: Name of the field for error messages
    
    Returns:
        Normalized season string (YYYY-YY format)
    
    Raises:
        ValidationError: If season string is invalid
    """
    if not isinstance(season_str, str):
        raise ValidationError(f"{field_name} must be a non-empty string")
    
    season_str = season_str.strip()
    if not season_str:
        raise ValidationError(f"{field_name} cannot be empty")
    
    # Normalize format: replace '/' with '-'
    normalized = season_str.replace('/', '-')
    
    # Expand short year format (YY-YY) to full format (YYYY-YY)
    parts = normalized.split('-')
    if len(parts) == 2:
        start_part = parts[0].strip()
        end_part = parts[1].strip()
        
        # Check if start year is 2-digit (YY format)
        if len(start_part) == 2 and start_part.isdigit():
            start_year = int(start_part)
            # Assume 2000s for recent data (years 50-99 = 1950-1999, 00-49 = 2000-2049)
            if start_year >= 50:
                start_year = 1900 + start_year
            else:
                start_year = 2000 + start_year
            normalized = f"{start_year}-{end_part}"
    
    # Try to create Season value object to validate format
    try:
        Season(normalized)
        return normalized
    except ValueError as e:
        raise ValidationError(f"{field_name} has invalid format: {season_str}. {str(e)}")


def validate_week_number(week: any, field_name: str = "week") -> Optional[int]:
    """
    Validate week number.
    
    Args:
        week: Week number to validate (can be int or None)
        field_name: Name of the field for error messages
    
    Returns:
        Week number as int or None
    
    Raises:
        ValidationError: If week number is invalid
    """
    if week is None:
        return None
    
    if not isinstance(week, int):
        try:
            week = int(week)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be an integer, got: {type(week).__name__}")
    
    if week < 1:
        raise ValidationError(f"{field_name} must be a positive integer, got: {week}")
    
    return week


def validate_league_abbreviation(abbreviation: str, field_name: str = "league_abbreviation") -> str:
    """
    Validate league abbreviation.
    
    Args:
        abbreviation: League abbreviation to validate
        field_name: Name of the field for error messages
    
    Returns:
        Normalized abbreviation
    
    Raises:
        ValidationError: If abbreviation is invalid
    """
    if not isinstance(abbreviation, str):
        raise ValidationError(f"{field_name} must be a non-empty string")
    
    abbreviation_stripped = abbreviation.strip()
    if not abbreviation_stripped:
        raise ValidationError(f"{field_name} cannot be empty")
    
    abbreviation = abbreviation_stripped.lower()
    
    # Basic validation: alphanumeric and hyphens/underscores only
    if not abbreviation.replace('-', '').replace('_', '').isalnum():
        raise ValidationError(f"{field_name} contains invalid characters: {abbreviation}")
    
    return abbreviation


def validate_club_slug(slug: str, field_name: str = "club_slug") -> str:
    """
    Validate club slug.
    
    Args:
        slug: Club slug to validate
        field_name: Name of the field for error messages
    
    Returns:
        Normalized slug
    
    Raises:
        ValidationError: If slug is invalid
    """
    if not slug or not isinstance(slug, str):
        raise ValidationError(f"{field_name} must be a non-empty string")
    
    slug = slug.strip().lower()
    if not slug:
        raise ValidationError(f"{field_name} cannot be empty")
    
    return slug


def validate_team_number(team_number: any, field_name: str = "team_number") -> int:
    """
    Validate team number.
    
    Args:
        team_number: Team number to validate
        field_name: Name of the field for error messages
    
    Returns:
        Team number as int
    
    Raises:
        ValidationError: If team number is invalid
    """
    if team_number is None:
        raise ValidationError(f"{field_name} is required")
    
    if not isinstance(team_number, int):
        try:
            team_number = int(team_number)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be an integer, got: {type(team_number).__name__}")
    
    if team_number < 1:
        raise ValidationError(f"{field_name} must be a positive integer, got: {team_number}")
    
    return team_number
