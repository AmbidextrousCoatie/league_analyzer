"""
Debug Configuration
Centralized debug settings for the application
"""

import os
from typing import Dict, Any

class DebugConfig:
    """Centralized debug configuration"""
    
    def __init__(self):
        # Global debug flag - can be set via environment variable
        self.DEBUG_ENABLED = os.getenv('DEBUG_ENABLED', 'false').lower() == 'true'
        
        # Component-specific debug flags
        self.debug_flags = {
            'routes': True,  # Always log route parameters and response sizes
            'services': False,  # Service layer debug
            'business_logic': False,  # Business logic debug
            'data_access': False,  # Data access layer debug
            'database_queries': False,  # Database query debug
            'chart_generation': False,  # Chart data generation debug
            'filter_operations': False,  # Filter operations debug
        }
    
    def is_debug_enabled(self, component: str = 'global') -> bool:
        """Check if debug is enabled for a specific component"""
        if component == 'global':
            return self.DEBUG_ENABLED
        return self.DEBUG_ENABLED and self.debug_flags.get(component, False)
    
    def enable_debug(self, component: str = 'global'):
        """Enable debug for a specific component"""
        if component == 'global':
            self.DEBUG_ENABLED = True
        else:
            self.debug_flags[component] = True
    
    def disable_debug(self, component: str = 'global'):
        """Disable debug for a specific component"""
        if component == 'global':
            self.DEBUG_ENABLED = False
        else:
            self.debug_flags[component] = False
    
    def log_route(self, route_name: str, params: Dict[str, Any], response_size: int = None):
        """Log route access with parameters and response size"""
        if self.is_debug_enabled('routes'):
            size_info = f" | Response: {response_size} bytes" if response_size else ""
            print(f"🔄 Route: {route_name} | Params: {params}{size_info}")
    
    def log_service(self, service_name: str, method: str, message: str):
        """Log service layer operations"""
        if self.is_debug_enabled('services'):
            print(f"🔧 Service: {service_name}.{method} | {message}")
    
    def log_business(self, component: str, message: str):
        """Log business logic operations"""
        if self.is_debug_enabled('business_logic'):
            print(f"⚙️ Business: {component} | {message}")
    
    def log_data_access(self, operation: str, message: str):
        """Log data access operations"""
        if self.is_debug_enabled('data_access'):
            print(f"💾 Data: {operation} | {message}")

# Global debug instance
debug_config = DebugConfig()