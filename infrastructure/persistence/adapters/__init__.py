"""
Data Adapter Infrastructure

Provides data adapter interfaces and implementations.
"""

from infrastructure.persistence.adapters.data_adapter import DataAdapter
from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter

__all__ = ["DataAdapter", "PandasDataAdapter"]
