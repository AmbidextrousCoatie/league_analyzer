"""
Tests for Query Validators.

Tests validation functions for query objects.
"""

import pytest
from uuid import UUID, uuid4
from application.validators import (
    validate_uuid,
    validate_optional_uuid,
    validate_season_string,
    validate_week_number,
    validate_league_abbreviation,
    validate_club_slug,
    validate_team_number
)
from application.exceptions import ValidationError


class TestValidateUUID:
    """Tests for validate_uuid function."""
    
    def test_valid_uuid_object(self):
        """Test validation with UUID object."""
        uuid = uuid4()
        result = validate_uuid(uuid, "test_field")
        assert result == uuid
    
    def test_valid_uuid_string(self):
        """Test validation with UUID string."""
        uuid = uuid4()
        result = validate_uuid(str(uuid), "test_field")
        assert result == uuid
    
    def test_none_raises_error(self):
        """Test that None raises ValidationError."""
        with pytest.raises(ValidationError, match="test_field is required"):
            validate_uuid(None, "test_field")
    
    def test_invalid_string_raises_error(self):
        """Test that invalid UUID string raises ValidationError."""
        with pytest.raises(ValidationError, match="test_field must be a valid UUID"):
            validate_uuid("not-a-uuid", "test_field")
    
    def test_invalid_type_raises_error(self):
        """Test that invalid type raises ValidationError."""
        with pytest.raises(ValidationError, match="test_field must be a UUID"):
            validate_uuid(123, "test_field")


class TestValidateOptionalUUID:
    """Tests for validate_optional_uuid function."""
    
    def test_none_returns_none(self):
        """Test that None returns None."""
        result = validate_optional_uuid(None, "test_field")
        assert result is None
    
    def test_valid_uuid_object(self):
        """Test validation with UUID object."""
        uuid = uuid4()
        result = validate_optional_uuid(uuid, "test_field")
        assert result == uuid
    
    def test_valid_uuid_string(self):
        """Test validation with UUID string."""
        uuid = uuid4()
        result = validate_optional_uuid(str(uuid), "test_field")
        assert result == uuid
    
    def test_invalid_string_raises_error(self):
        """Test that invalid UUID string raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_optional_uuid("not-a-uuid", "test_field")


class TestValidateSeasonString:
    """Tests for validate_season_string function."""
    
    def test_valid_season_format_1(self):
        """Test validation with format '2025-26'."""
        result = validate_season_string("2025-26", "season")
        assert result == "2025-26"
    
    def test_valid_season_format_2(self):
        """Test validation with format '25/26'."""
        result = validate_season_string("25/26", "season")
        assert result == "2025-26"  # Normalized and expanded to full year format
    
    def test_empty_string_raises_error(self):
        """Test that empty string raises ValidationError."""
        with pytest.raises(ValidationError, match="season cannot be empty"):
            validate_season_string("", "season")
    
    def test_none_raises_error(self):
        """Test that None raises ValidationError."""
        with pytest.raises(ValidationError, match="season must be a non-empty string"):
            validate_season_string(None, "season")
    
    def test_invalid_format_raises_error(self):
        """Test that invalid format raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_season_string("invalid", "season")


class TestValidateWeekNumber:
    """Tests for validate_week_number function."""
    
    def test_valid_week_number(self):
        """Test validation with valid week number."""
        result = validate_week_number(5, "week")
        assert result == 5
    
    def test_none_returns_none(self):
        """Test that None returns None."""
        result = validate_week_number(None, "week")
        assert result is None
    
    def test_string_number_converts(self):
        """Test that string number converts to int."""
        result = validate_week_number("5", "week")
        assert result == 5
    
    def test_zero_raises_error(self):
        """Test that zero raises ValidationError."""
        with pytest.raises(ValidationError, match="week must be a positive integer"):
            validate_week_number(0, "week")
    
    def test_negative_raises_error(self):
        """Test that negative number raises ValidationError."""
        with pytest.raises(ValidationError, match="week must be a positive integer"):
            validate_week_number(-1, "week")
    
    def test_invalid_type_raises_error(self):
        """Test that invalid type raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_week_number("not-a-number", "week")


class TestValidateLeagueAbbreviation:
    """Tests for validate_league_abbreviation function."""
    
    def test_valid_abbreviation(self):
        """Test validation with valid abbreviation."""
        result = validate_league_abbreviation("bayl", "league_abbreviation")
        assert result == "bayl"
    
    def test_uppercase_normalized(self):
        """Test that uppercase is normalized to lowercase."""
        result = validate_league_abbreviation("BAYL", "league_abbreviation")
        assert result == "bayl"
    
    def test_with_hyphen(self):
        """Test abbreviation with hyphen."""
        result = validate_league_abbreviation("bay-l", "league_abbreviation")
        assert result == "bay-l"
    
    def test_empty_string_raises_error(self):
        """Test that empty string raises ValidationError."""
        with pytest.raises(ValidationError, match="league_abbreviation cannot be empty"):
            validate_league_abbreviation("", "league_abbreviation")
    
    def test_none_raises_error(self):
        """Test that None raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_league_abbreviation(None, "league_abbreviation")


class TestValidateClubSlug:
    """Tests for validate_club_slug function."""
    
    def test_valid_slug(self):
        """Test validation with valid slug."""
        result = validate_club_slug("bk-muenchen", "club_slug")
        assert result == "bk-muenchen"
    
    def test_uppercase_normalized(self):
        """Test that uppercase is normalized to lowercase."""
        result = validate_club_slug("BK-MUENCHEN", "club_slug")
        assert result == "bk-muenchen"
    
    def test_empty_string_raises_error(self):
        """Test that empty string raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_club_slug("", "club_slug")


class TestValidateTeamNumber:
    """Tests for validate_team_number function."""
    
    def test_valid_team_number(self):
        """Test validation with valid team number."""
        result = validate_team_number(3, "team_number")
        assert result == 3
    
    def test_string_number_converts(self):
        """Test that string number converts to int."""
        result = validate_team_number("3", "team_number")
        assert result == 3
    
    def test_zero_raises_error(self):
        """Test that zero raises ValidationError."""
        with pytest.raises(ValidationError, match="team_number must be a positive integer"):
            validate_team_number(0, "team_number")
    
    def test_none_raises_error(self):
        """Test that None raises ValidationError."""
        with pytest.raises(ValidationError, match="team_number is required"):
            validate_team_number(None, "team_number")
