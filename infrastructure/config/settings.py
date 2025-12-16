"""
Application settings and configuration.

Loads configuration from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.
    
    Loads from environment variables with defaults.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = Field(default="League Analyzer API")
    app_version: str = Field(default="2.0.0")
    debug: bool = Field(default=False)
    
    # Server
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=5000)
    
    # Database
    database_url: str = Field(default="sqlite:///./league_analyzer.db")
    database_type: str = Field(default="sqlite")  # sqlite, mysql, pandas
    
    # Logging
    log_level: str = Field(default="INFO")
    log_file: Optional[str] = Field(default=None)
    
    # Data paths
    data_directory: Path = Field(
        default=Path(__file__).parent.parent.parent.parent / "database" / "data"
    )


# Global settings instance
settings = Settings()

