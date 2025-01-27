from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import numpy as np
from market_simulation.data.schemas import GeoMappingSchema
from market_simulation.utils.geo_utils import calculate_haversine_distance

@dataclass
class GeoLocation:
    """Base class for geographic locations."""
    latitude: float
    longitude: float

    def __post_init__(self):
        """Validate geographic coordinates."""
        if not isinstance(self.latitude, (int, float)) or not isinstance(self.longitude, (int, float)):
            raise TypeError("Latitude and longitude must be numeric")
        if not -90 <= self.latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        if not -180 <= self.longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180")
    
    def calculate_distance(self, lat: float, lon: float) -> float:
        """Calculate distance to a point in kilometers."""
        return calculate_haversine_distance(
            self.latitude, self.longitude,
            lat, lon
        )

    def sample_point_in_radius(self, radius_km: float) -> Tuple[float, float]:
        """Generate random point within radius."""
        if radius_km <= 0:
            raise ValueError("Radius must be positive")
            
        # Convert radius to degrees (approximate)
        lat_radius = radius_km / 111.0
        lon_radius = radius_km / (111.0 * np.cos(np.radians(self.latitude)))
        
        # Sample random angle and distance
        angle = np.random.uniform(0, 2 * np.pi)
        r = np.random.uniform(0, radius_km)
        
        # Convert to lat/lon offset
        lat_offset = r * np.cos(angle) / 111.0
        lon_offset = r * np.sin(angle) / (111.0 * np.cos(np.radians(self.latitude)))
        
        return (
            self.latitude + lat_offset,
            self.longitude + lon_offset
        )

@dataclass
class PostalCode(GeoLocation):
    """
    Represents a postal code area with its geographic and market properties.
    """
    postal_code: str
    market: str
    str_tam: int
    area: Optional[float] = None
    latitude: float = field(init=True)  # override from parent
    longitude: float = field(init=True)  # override from parent

    def __post_init__(self):
        """Validate all fields."""
        super().__post_init__()
        if not isinstance(self.str_tam, (int)):
            raise TypeError("STR TAM must be an integer")
        if self.str_tam < 0:
            raise ValueError("STR TAM cannot be negative")
    
    @classmethod
    def from_schema(cls, schema: GeoMappingSchema) -> 'PostalCode':
        """Create from validated schema."""
        return cls(
            postal_code=schema.postal_code,
            market=schema.market,
            latitude=schema.latitude,
            longitude=schema.longitude,
            str_tam=schema.str_tam,
            area=schema.area
        )
    
    def calculate_distance_to(self, other: GeoLocation) -> float:
        """Calculate distance to another location."""
        return calculate_haversine_distance(
            self.latitude, self.longitude,
            other.latitude, other.longitude
        )
    
    def find_neighbors(self, postal_codes: List['PostalCode'], 
                      threshold_km: float) -> List['PostalCode']:
        """Find postal codes within threshold distance."""
        if threshold_km <= 0:
            raise ValueError("Threshold must be positive")
            
        return [
            pc for pc in postal_codes 
            if pc.postal_code != self.postal_code 
            and self.calculate_distance_to(pc) <= threshold_km
        ]
    
    def get_tam_weight(self, total_market_tam: int) -> float:
        """Calculate TAM weight relative to total market TAM."""
        if total_market_tam <= 0:
            raise ValueError("Total market TAM must be positive")
        return self.str_tam / total_market_tam