"""
Color constants matching ColorUtils.THEME_COLORS from color-utils.js
These should be kept in sync with the JavaScript ColorUtils definitions.
"""

# Theme colors - matching ColorUtils.THEME_COLORS
THEME_COLORS = {
    # Primary colors
    "primary": "#1B8CA6",           # Dark blue - navbar, card headers
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
    "text_on_light": "#1F77B4",     # Text on light background
    
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


def hex_to_rgb(hex_color: str) -> tuple:
    """
    Convert hex color to RGB tuple.
    
    Args:
        hex_color: Hex color string (with or without #)
        
    Returns:
        Tuple of (r, g, b) values
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_heat_map_color(value: float, min_val: float, max_val: float, 
                       start_color: str = None, end_color: str = None,
                       use_low_high: bool = True) -> str:
    """
    Generate heat map color interpolating between start and end colors.
    Matches the JavaScript ColorUtils.getHeatMapColor implementation.
    
    Args:
        value: The value to map to a color
        min_val: Minimum value in the range
        max_val: Maximum value in the range
        start_color: Optional start color (low value). If None, uses theme color
        end_color: Optional end color (high value). If None, uses theme color
        use_low_high: If True (default), uses heat_map_low/high. If False, uses heat_map_start/end
        
    Returns:
        RGB color string (e.g., "rgb(123, 45, 67)")
    """
    if value == "" or value is None or min_val == max_val:
        return get_theme_color("background") or "#f8f9fa"
    
    # Use theme colors if not specified
    if start_color is None:
        if use_low_high:
            start_color = THEME_COLORS.get("heat_map_low", "#d9596a")
        else:
            start_color = THEME_COLORS.get("heat_map_start", "#dddddd")
    if end_color is None:
        if use_low_high:
            end_color = THEME_COLORS.get("heat_map_high", "#1b8da7")
        else:
            end_color = THEME_COLORS.get("heat_map_end", "#1b8da7")
    
    # Normalize value to 0-1 range, clamped between 0 and 1
    ratio = (value - min_val) / (max_val - min_val) if max_val != min_val else 0
    ratio = max(0, min(1, ratio))  # Clamp between 0 and 1
    
    # Convert hex colors to RGB
    r1, g1, b1 = hex_to_rgb(start_color)
    r2, g2, b2 = hex_to_rgb(end_color)
    
    # Interpolate between the two colors
    r = round(r1 + (r2 - r1) * ratio)
    g = round(g1 + (g2 - g1) * ratio)
    b = round(b1 + (b2 - b1) * ratio)
    
    return f"rgb({r}, {g}, {b})"

