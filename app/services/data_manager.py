import pandas as pd
from data_access.pd_dataframes import fetch_column
from flask import session
import os
import json
from typing import Optional
from app.config.database_config import database_config

class DataManager:
    _server_instances = []
    _session_key = 'selected_database'

    def __init__(self, source=None):
        # Always load data from session, don't rely on singleton
        self._load_data(source)

    def _load_data(self, source=None):
        # Prioritize explicit source parameter over session
        if source and database_config.validate_source(source):
            self._current_source = source
        else:
            # Try to get from session
            session_source = self._get_session_source()
            if session_source and database_config.validate_source(session_source):
                self._current_source = session_source
            else:
                # Use default from config
                self._current_source = database_config.get_default_source()
        
        # Save to session for consistency
        self._save_session_source(self._current_source)
        
        try:
            config = database_config.get_source_config(self._current_source)
            file_path = config.file_path if config else f'database/data/{self._current_source}'
            
            self._df = pd.read_csv(file_path, sep=';')
            print(f"✅ Data loaded successfully from: {self._current_source}")
        except Exception as e:
            print(f"❌ Error loading data from {self._current_source}: {e}")
            # Fallback to default if current source fails
            default_source = database_config.get_default_source()
            if self._current_source != default_source:
                self._current_source = default_source
                self._save_session_source(self._current_source)
                config = database_config.get_source_config(self._current_source)
                file_path = config.file_path if config else f'database/data/{self._current_source}'
                self._df = pd.read_csv(file_path, sep=';')
                print(f"✅ Fallback to default data source: {self._current_source}")

    def reload_data(self, source=None):
        """Reload data with better error handling and state management"""
        if source and not database_config.validate_source(source):
            raise ValueError(f"Invalid data source: {source}. Available sources: {database_config.get_available_sources()}")
        
        # Store previous source for rollback if needed
        previous_source = self._current_source
        
        try:
            # Force reload even if singleton exists
            if source:
                self._current_source = source
            
            print(f"DEBUG: DataManager reloading data from: {self._current_source}")
            
            # Save to session before loading data
            self._save_session_source(self._current_source)
            
            # Load the new data
            config = database_config.get_source_config(self._current_source)
            file_path = config.file_path if config else f'database/data/{self._current_source}'
            self._df = pd.read_csv(file_path, sep=';')
            
            print(f"✅ DATA SOURCE SWITCHED: {self._current_source}")
            print(f"📊 Table dimensions: {len(self._df)} rows × {len(self._df.columns)} columns")
            print(f"📋 Columns: {list(self._df.columns)}")
            
            # Refresh all server instances
            print(f"DEBUG: DataManager refreshing {len(self._server_instances)} server instances")
            self._refresh_server_instances()
            
            return True
            
        except Exception as e:
            print(f"❌ Error switching to {self._current_source}: {e}")
            # Rollback to previous source
            self._current_source = previous_source
            self._save_session_source(self._current_source)
            try:
                config = database_config.get_source_config(self._current_source)
                file_path = config.file_path if config else f'database/data/{self._current_source}'
                self._df = pd.read_csv(file_path, sep=';')
                print(f"✅ Rolled back to: {self._current_source}")
            except Exception as rollback_error:
                print(f"❌ Critical error: Could not rollback to {self._current_source}: {rollback_error}")
                # Last resort: try default source
                self._current_source = database_config.get_default_source()
                self._save_session_source(self._current_source)
                config = database_config.get_source_config(self._current_source)
                file_path = config.file_path if config else f'database/data/{self._current_source}'
                self._df = pd.read_csv(file_path, sep=';')
            
            return False

    def _get_session_source(self) -> Optional[str]:
        """Get the selected database source from Flask session"""
        try:
            from flask import has_request_context
            if has_request_context():
                source = session.get(self._session_key)
                print(f"DEBUG: Session source: {source}")
                return source
            else:
                print("DEBUG: No request context, skipping session access")
                return None
        except Exception as e:
            print(f"Warning: Could not access session: {e}")
            return None

    def _save_session_source(self, source: str):
        """Save the selected database source to Flask session"""
        try:
            from flask import has_request_context
            if has_request_context():
                session[self._session_key] = source
                session.modified = True
                print(f"DEBUG: Saved to session: {source}")
            else:
                print("DEBUG: No request context, skipping session save")
        except Exception as e:
            print(f"Warning: Could not save to session: {e}")

    def force_reload_from_session(self):
        """Force reload data from session - useful for production with multiple workers"""
        print("DEBUG: Force reloading from session")
        # Clear any cached data
        self._df = None
        self._current_source = None
        # Reload from session
        self._load_data()
        print(f"DEBUG: Force reload complete. Current source: {self._current_source}")
        print(f"DEBUG: Data loaded: {len(self._df) if self._df is not None else 'None'} rows")

    def get_available_sources(self) -> list:
        """Get list of available data sources"""
        return database_config.get_available_sources()

    def validate_source(self, source: str) -> bool:
        """Validate if a data source exists and is accessible"""
        return database_config.validate_source(source)

    def get_source_display_name(self, source: str) -> str:
        """Get display name for a data source"""
        return database_config.get_source_display_name(source)

    def get_sources_info(self) -> dict:
        """Get detailed information about all available sources"""
        return database_config.get_sources_info()

    def register_server_instance(self, server_instance):
        """Register a server instance to be refreshed when data source changes"""
        if server_instance not in self._server_instances:
            self._server_instances.append(server_instance)
            print(f"DEBUG: DataManager registered server instance, total: {len(self._server_instances)}")

    def _refresh_server_instances(self):
        """Refresh all registered server instances"""
        for server in self._server_instances:
            if hasattr(server, 'refresh_data_adapter'):
                try:
                    print(f"DEBUG: DataManager refreshing server instance")
                    server.refresh_data_adapter()
                except Exception as e:
                    print(f"Warning: Error refreshing server instance: {e}")

    @property
    def df(self):
        return self._df
    
    @property
    def current_source(self):
        return self._current_source
    
    def force_source(self, source: str) -> bool:
        """Force a specific data source and reload data"""
        if not database_config.validate_source(source):
            print(f"❌ Invalid source: {source}")
            return False
        
        print(f"🔄 Forcing data source to: {source}")
        self._current_source = source
        self._save_session_source(source)
        
        # Reload data with the new source
        try:
            config = database_config.get_source_config(source)
            file_path = config.file_path if config else f'database/data/{source}'
            self._df = pd.read_csv(file_path, sep=';')
            print(f"✅ Successfully switched to: {source}")
            return True
        except Exception as e:
            print(f"❌ Error forcing source {source}: {e}")
            return False 