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
    align: Optional[str] = None  # "left", "center", "right"

@dataclass
class ColumnGroup:
    """Column group with a common header."""
    title: str
    columns: List[Column]
    frozen: Optional[str] = None  # 'left', 'right', or None

@dataclass
class TableData:
    """Complete table data structure."""
    columns: List[ColumnGroup]
    data: List[List[Any]]
    title: Optional[str] = None
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary suitable for JSON serialization"""
        return {
            "columns": [
                {
                    "title": group.title,
                    "columns": [{"title": col.title, "field": col.field} for col in group.columns],
                    **({"frozen": group.frozen} if group.frozen else {})
                }
                for group in self.columns
            ],
            "data": self.data,
            **({"title": self.title} if self.title else {}),
            **({"description": self.description} if self.description else {})
        }

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