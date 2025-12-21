"""
Pytest fixtures for infrastructure layer tests.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, MagicMock
from pathlib import Path
from infrastructure.persistence.adapters.data_adapter import DataAdapter
from infrastructure.persistence.mappers.csv.event_mapper import PandasEventMapper


@pytest.fixture
def event_csv_path(tmp_path):
    """Create a temporary event.csv file for testing."""
    csv_file = tmp_path / "event.csv"
    # Create empty CSV with headers
    df = pd.DataFrame(columns=[
        'id', 'league_season_id', 'event_type', 'league_week', 'tournament_stage',
        'date', 'venue_id', 'oil_pattern_id', 'status', 'disqualification_reason', 'notes'
    ])
    df.to_csv(csv_file, index=False)
    return csv_file


@pytest.fixture
def mock_data_adapter(event_csv_path):
    """Mock DataAdapter for testing with real CSV file."""
    from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
    # Use the event.csv path directly
    adapter = PandasDataAdapter(event_csv_path)
    return adapter


@pytest.fixture
def event_mapper():
    """Event mapper for testing."""
    return PandasEventMapper()

