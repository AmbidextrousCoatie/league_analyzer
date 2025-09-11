from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from itertools import accumulate

@dataclass
class SeriesData:
    """Data structure for series data."""
    label_x_axis: str
    label_y_axis: str
    name: str
    length: int = 0
    query_params: Dict[str, Any] = field(default_factory=dict)  # Store query parameters like season, league, etc.
    data: Dict[str, List[Union[float, None]]] = field(default_factory=dict)
    data_accumulated: Dict[str, List[Union[float, None]]] = field(default_factory=dict)
    total: Dict[str, float] = field(default_factory=dict)
    average: Dict[str, float] = field(default_factory=dict)
    counts: Dict[str, int] = field(default_factory=dict)  # Store generic counts for each key
    
    def to_dict(self) -> Dict[str, Any]:    
        """Convert to a dictionary suitable for JSON serialization"""
        
        sorted_by_alphabet = sorted(self.data.keys())
        sorted_by_total = sorted(self.data.keys(), key=lambda x: self.total[x], reverse=True)
        sorted_by_average = sorted(self.data.keys(), key=lambda x: self.average[x], reverse=True)

        return {    
            "name": self.name,
            "label_x_axis": self.label_x_axis,
            "label_y_axis": self.label_y_axis,
            "query_params": self.query_params,
            "data": self.data,   
            "data_accumulated": self.data_accumulated,
            "total": self.total,
            "average": self.average,
            "counts": self.counts,
            "length": self.length,
            "sorted_by_alphabet": sorted_by_alphabet,
            "sorted_by_total": sorted_by_total,
            "sorted_by_average": sorted_by_average

        }
    
    def add_data(self, key: str, data: List[Union[float, None]]):
        """Add data to the series."""
        # add / replace data
        self.data[key] = data

        # Filter out None values for calculations
        valid_data = [x for x in data if x is not None]
        
        # add / replace data_cumulated (only for valid data)
        if valid_data:
            self.data_accumulated[key] = list(accumulate(valid_data))
        else:
            self.data_accumulated[key] = []

        # add average (only for valid data)
        self.average[key] = sum(valid_data) / len(valid_data) if valid_data else 0

        # add total (only for valid data)
        self.total[key] = sum(valid_data)

        # Store count of valid (non-None) data points
        self.counts[key] = len(valid_data)

        self.length = len(data)
    
    def update_query_params(self, **kwargs):
        """Update query parameters."""
        self.query_params.update(kwargs)
        
        
            

