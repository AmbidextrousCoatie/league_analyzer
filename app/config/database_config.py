"""
Database Configuration
Manages available data sources and their settings
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class DataSourceConfig:
    """Configuration for a data source"""
    filename: str
    display_name: str
    description: str
    is_default: bool = False
    is_enabled: bool = True
    file_path: Optional[str] = None
    
    def __post_init__(self):
        if self.file_path is None:
            self.file_path = f'database/data/{self.filename}'

class DatabaseConfig:
    """Centralized database configuration management"""
    
    def __init__(self):
        self._sources = {
            'bowling_ergebnisse.csv': DataSourceConfig(
                filename='bowling_ergebnisse.csv',
                display_name='Simulated Data',
                description='Generated test data for development and testing',
                is_default=True,
                is_enabled=True
            ),
            'bowling_ergebnisse_real.csv': DataSourceConfig(
                filename='bowling_ergebnisse_real.csv',
                display_name='Real Data',
                description='Actual bowling league data',
                is_default=False,
                is_enabled=True
            )
        }
        
        # Validate sources on initialization
        self._validate_sources()
    
    def _validate_sources(self):
        """Validate that all enabled sources exist and are accessible"""
        for source_id, config in self._sources.items():
            if config.is_enabled:
                if not os.path.exists(config.file_path):
                    print(f"⚠️ Warning: Data source file not found: {config.file_path}")
                    config.is_enabled = False
    
    def get_available_sources(self) -> List[str]:
        """Get list of available (enabled) data source filenames"""
        return [source_id for source_id, config in self._sources.items() 
                if config.is_enabled]
    
    def get_source_config(self, source_id: str) -> Optional[DataSourceConfig]:
        """Get configuration for a specific data source"""
        return self._sources.get(source_id)
    
    def get_default_source(self) -> str:
        """Get the default data source filename"""
        for source_id, config in self._sources.items():
            if config.is_default and config.is_enabled:
                return source_id
        # Fallback to first available source
        available = self.get_available_sources()
        return available[0] if available else 'bowling_ergebnisse.csv'
    
    def validate_source(self, source_id: str) -> bool:
        """Validate if a data source exists and is accessible"""
        config = self.get_source_config(source_id)
        if not config or not config.is_enabled:
            return False
        
        return os.path.exists(config.file_path) and os.path.isfile(config.file_path)
    
    def get_source_display_name(self, source_id: str) -> str:
        """Get display name for a data source"""
        config = self.get_source_config(source_id)
        return config.display_name if config else 'Unknown Data Source'
    
    def get_source_description(self, source_id: str) -> str:
        """Get description for a data source"""
        config = self.get_source_config(source_id)
        return config.description if config else ''
    
    def get_sources_info(self) -> Dict:
        """Get information about all available sources"""
        return {
            source_id: {
                'filename': config.filename,
                'display_name': config.display_name,
                'description': config.description,
                'is_default': config.is_default,
                'is_enabled': config.is_enabled,
                'file_path': config.file_path
            }
            for source_id, config in self._sources.items()
            if config.is_enabled
        }

# Global instance
database_config = DatabaseConfig() 