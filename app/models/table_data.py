# app/models/table_data.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union

@dataclass
class Column:
    """Individual column definition."""
    title: str
    field: str
    sortable: bool = True
    filterable: bool = True
    width: Optional[str] = None
    align: Optional[str] = "center"  # "left", "center", "right"
    format: Optional[str] = None  # Format string for numbers, dates, etc.
    style: Optional[Dict[str, str]] = None  # Custom CSS styles
    tooltip: Optional[str] = None  # Tooltip text for column header

@dataclass
class ColumnGroup:
    """Column group with a common header."""
    title: str
    columns: List[Column]
    frozen: Optional[str] = None  # 'left', 'right', or None
    style: Optional[Dict[str, str]] = None  # Custom CSS styles for the group
    header_style: Optional[Dict[str, str]] = None  # Custom CSS for header
    width: Optional[str] = None  # Width for the entire group
    highlighted: bool = False  # Whether this group should be visually highlighted

@dataclass
class TableData:
    """Complete table data structure."""
    columns: Union[List[ColumnGroup], List[Column]]  # Accept either ColumnGroups or bare Columns
    data: List[List[Any]]
    title: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = field(default_factory=dict)  # Table-wide configuration
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)  # Additional metadata for i18n and UI
    row_metadata: Optional[List[Dict[str, Any]]] = field(default_factory=list)  # Row-level metadata for styling
    cell_metadata: Optional[Dict[str, Dict[str, Any]]] = field(default_factory=dict)  # Cell-level metadata for styling (format: "row:col")
    default_sort: Optional[Dict[str, str]] = None  # Default sort: {"field": "average", "dir": "desc"}
    
    def __post_init__(self):
        """Normalize columns: if bare Columns are provided, wrap them in a ColumnGroup with empty title."""
        if self.columns and len(self.columns) > 0 and isinstance(self.columns[0], Column):
            # Convert List[Column] to List[ColumnGroup] by wrapping in a single group
            self.columns = [ColumnGroup(title="", columns=list(self.columns))]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary suitable for JSON serialization"""
        return {
            "columns": [
                {
                    "title": group.title,
                    "columns": [
                        {
                            "title": col.title, 
                            "field": col.field,
                            **({"sortable": col.sortable} if col.sortable is not None else {}),
                            **({"filterable": col.filterable} if col.filterable is not None else {}),
                            **({"width": col.width} if col.width else {}),
                            **({"align": col.align} if col.align else {}),
                            **({"format": col.format} if col.format else {}),
                            **({"style": col.style} if col.style else {}),
                            **({"tooltip": col.tooltip} if col.tooltip else {})
                        } 
                        for col in group.columns
                    ],
                    **({"frozen": group.frozen} if group.frozen else {}),
                    **({"style": group.style} if group.style else {}),
                    **({"headerStyle": group.header_style} if group.header_style else {}),
                    **({"width": group.width} if group.width else {}),
                    **({"highlighted": group.highlighted} if group.highlighted else {})
                }
                for group in self.columns
            ],
            "data": self.data,
            **({"title": self.title} if self.title else {}),
            **({"description": self.description} if self.description else {}),
            **({"config": self.config} if self.config else {}),
            **({"metadata": self.metadata} if self.metadata else {}),
            **({"row_metadata": self.row_metadata} if self.row_metadata else {}),
            **({"cell_metadata": self.cell_metadata} if self.cell_metadata else {}),
            **({"default_sort": self.default_sort} if self.default_sort else {})
        }

#@dataclass
#class TableDataLeague(TableData):
#    """Table data for a league."""
#    league: str

@dataclass
class PlotData:
    """Data structure for chart/plot visualization."""
    title: str
    series: List[Dict[str, Any]]
    x_axis: Optional[List[Any]] = None
    y_axis_label: Optional[str] = None
    x_axis_label: Optional[str] = None
    plot_type: str = "line"  # line, bar, scatter, pie, etc.
    options: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary suitable for JSON serialization"""
        return {
            "title": self.title,
            "series": self.series,
            "xAxis": {"categories": self.x_axis} if self.x_axis else {},
            "yAxis": {"title": {"text": self.y_axis_label}} if self.y_axis_label else {},
            "plotType": self.plot_type,
            "options": self.options
        }

@dataclass
class TileData:
    """Data structure for dashboard tiles/cards."""
    title: str
    value: Any  # The primary value to display
    subtitle: Optional[str] = None
    trend: Optional[Dict[str, Any]] = None  # Trend information (value, direction, etc.)
    icon: Optional[str] = None
    color: Optional[str] = None  # Primary color
    size: str = "small"  # small, medium, large, wide
    type: str = "stat"  # stat, trend, progress, chart, info
    chart_data: Optional[List[Union[int, float]]] = None  # For mini charts
    link: Optional[str] = None  # URL to navigate to on click
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary suitable for JSON serialization"""
        result = {
            "title": self.title,
            "value": self.value,
            "size": self.size,
            "type": self.type
        }
        
        if self.subtitle:
            result["subtitle"] = self.subtitle
        
        if self.trend:
            result["trend"] = self.trend
            
        if self.icon:
            result["icon"] = self.icon
            
        if self.color:
            result["color"] = self.color
            
        if self.chart_data:
            result["chartData"] = self.chart_data
            
        if self.link:
            result["link"] = self.link
            
        return result