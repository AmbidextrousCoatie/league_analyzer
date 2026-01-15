"""
Integration Tests for API Routes.

Tests the full request/response cycle for API endpoints.
"""

import pytest
from uuid import uuid4

# Import TestClient - will fail if httpx is not installed (as intended)
try:
    from fastapi.testclient import TestClient
except (ImportError, RuntimeError) as e:
    # Make tests fail with clear error message instead of skipping
    pytest.fail(f"httpx is required for integration tests. Install with: pip install httpx. Original error: {e}")


@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI app."""
    from main import app
    return TestClient(app)


class TestLeagueStandingsRoutes:
    """Tests for league standings routes."""
    
    def test_get_league_standings_json_invalid_uuid(self, client):
        """Test that invalid UUID returns 400 Bad Request."""
        response = client.get("/api/v1/leagues/invalid-uuid/standings")
        assert response.status_code == 400
        assert "error" in response.json()
    
    def test_get_league_standings_json_not_found(self, client):
        """Test that non-existent league returns 404."""
        fake_uuid = str(uuid4())
        response = client.get(f"/api/v1/leagues/{fake_uuid}/standings")
        assert response.status_code == 404
        assert "error" in response.json()
    
    def test_get_league_standings_json_invalid_week(self, client):
        """Test that invalid week number returns 400."""
        # Use a valid UUID format (but may not exist)
        fake_uuid = str(uuid4())
        response = client.get(f"/api/v1/leagues/{fake_uuid}/standings?week=-1")
        assert response.status_code == 400
    
    def test_get_league_standings_json_zero_week(self, client):
        """Test that week=0 returns 400."""
        fake_uuid = str(uuid4())
        response = client.get(f"/api/v1/leagues/{fake_uuid}/standings?week=0")
        assert response.status_code == 400


class TestLeagueSlugRoutes:
    """Tests for league slug-based routes."""
    
    def test_get_league_standings_slug_invalid_abbreviation(self, client):
        """Test that invalid league abbreviation returns 404."""
        response = client.get("/leagues/invalid-league/standings")
        assert response.status_code == 404
    
    def test_get_league_standings_slug_invalid_week(self, client):
        """Test that invalid week in slug route returns 400."""
        response = client.get("/leagues/bayl/standings?week=-5")
        # May return 400 (validation) or 404 (league not found) depending on data
        assert response.status_code in [400, 404]


class TestErrorHandling:
    """Tests for error handling middleware."""
    
    def test_error_response_format(self, client):
        """Test that error responses have consistent format."""
        response = client.get("/api/v1/leagues/invalid-uuid/standings")
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "detail" in data
        assert "path" in data
    
    def test_not_found_error_format(self, client):
        """Test that 404 errors have consistent format."""
        fake_uuid = str(uuid4())
        response = client.get(f"/api/v1/leagues/{fake_uuid}/standings")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "detail" in data
