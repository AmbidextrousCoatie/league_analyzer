"""
Color constants matching ColorUtils.THEME_COLORS from color-utils.js
These should be kept in sync with the JavaScript ColorUtils definitions.
"""

# Theme colors - matching ColorUtils.THEME_COLORS
THEME_COLORS = {
    # Primary colors
    "primary": "#0a9dc7",           # Dark blue - navbar, card headers
    "secondary": "#4aa8c2",         # Light blue - buttons, interactive elements
    "accent": "#7dcfe6",             # Lightest blue - highlights, accents
    
    # Background colors
    "background": "#f8f9fa",        # Main page background
    "surface": "#ffffff",           # Card/container background
    "surface_alt": "#e9ecef",       # Alternate surface (lighter gray)
    "surface_light": "#f0f0f0",     # Light gray variant
    
    # Text colors
    "text_on_primary": "#ffffff",   # Text on primary background
    "text_on_secondary": "#ffffff",  # Text on secondary background
    "text_on_light": "#0a9dc7",     # Text on light background
    
    # Border colors
    "border": "#264653",             # Dark teal/green borders
    "border_light": "#dee2e6",      # Light borders
    
    # Table colors
    "table_header_bg": "#eef2f7",   # Table header background
    "table_header_text": "#0f172a", # Table header text
    "table_body_text": "#1f2933",   # Table body text
    "table_muted_text": "#64748b",  # Muted text
    
    # Heat map colors
    "heat_map_start": "#dddddd",    # Heat map start color
    "heat_map_end": "#1b8da7",      # Heat map end color
    "heat_map_low": "#d9596a",      # Heat map low value
    "heat_map_high": "#1b8da7",     # Heat map high value
    
    # Status colors
    "warning": "#86e1b3",            # Warning states
    "info": "#a1e8c4",              # Info states
    "success": "#d4edda",           # Success states
    "danger": "#f8d7da",            # Danger states
}


def get_theme_color(color_name: str) -> str:
    """
    Get a theme color by name.
    
    Args:
        color_name: Name of the color (e.g., 'background', 'primary', 'border')
        
    Returns:
        Hex color string, or empty string if not found
    """
    return THEME_COLORS.get(color_name, "")

