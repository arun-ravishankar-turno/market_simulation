from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import numpy as np
from market_simulation.models.geo import PostalCode, GeoLocation
from market_simulation.models.cleaner import Cleaner
from market_simulation.utils.geo_utils import calculate_haversine_distance

@dataclass
class Market:
    """
    Represents a market with either postal code or location-based definition.
    
    The market can be defined either by:
    1. A collection of postal codes (postal code-based market)
    2. A center point and radius (location-based market)
    
    This class handles:
    - Geographic organization of service areas
    - Cleaner management and queries
    - Location sampling for searches
    - Distance calculations
    
    Attributes:
        market_id: Unique identifier for the market
        postal_codes: Optional dictionary of postal codes in the market
        center_lat: Optional center latitude for location-based market
        center_lon: Optional center longitude for location-based market
        radius_km: Optional radius in km for location-based market
        cleaners: Dictionary of cleaners in the market
    """
    market_id: str
    postal_codes: Optional[Dict[str, PostalCode]] = None
    center_lat: Optional[float] = None
    center_lon: Optional[float] = None
    radius_km: Optional[float] = None
    cleaners: Dict[str, Cleaner] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate market configuration."""
        if self.postal_codes is None and (
            self.center_lat is None or
            self.center_lon is None or
            self.radius_km is None
        ):
            raise ValueError(
                "Must provide either postal_codes or (center_lat, center_lon, radius_km)"
            )
            
        if self.postal_codes is not None and (
            self.center_lat is not None or
            self.center_lon is not None or
            self.radius_km is not None
        ):
            raise ValueError(
                "Cannot provide both postal_codes and location-based parameters"
            )
            
        if self.center_lat is not None:
            if not -90 <= self.center_lat <= 90:
                raise ValueError("center_lat must be between -90 and 90")
                
        if self.center_lon is not None:
            if not -180 <= self.center_lon <= 180:
                raise ValueError("center_lon must be between -180 and 180")
                
        if self.radius_km is not None:
            if self.radius_km <= 0:
                raise ValueError("radius_km must be positive")

    @property
    def total_str_tam(self) -> int:
        """Calculate total STR TAM for the market."""
        if self.postal_codes is None:
            raise ValueError("TAM only available for postal code-based markets")
        return sum(pc.str_tam for pc in self.postal_codes.values())

    def add_cleaner(self, cleaner: Cleaner) -> None:
        """
        Add a cleaner to the market.
        
        For postal code-based markets, validates postal code.
        For location-based markets, validates location within radius.
        
        Args:
            cleaner: Cleaner instance to add
            
        Raises:
            ValueError: If cleaner location invalid for market type
        """
        if self.postal_codes is not None:
            if cleaner.postal_code not in self.postal_codes:
                raise ValueError(
                    f"Cleaner postal code {cleaner.postal_code} not in market"
                )
        else:
            distance = calculate_haversine_distance(
                self.center_lat, self.center_lon,
                cleaner.latitude, cleaner.longitude
            )
            if distance > self.radius_km:
                raise ValueError(
                    f"Cleaner location {distance:.1f}km from market center, "
                    f"exceeds radius of {self.radius_km}km"
                )
        
        self.cleaners[cleaner.contractor_id] = cleaner

    def get_cleaners_in_range(self, lat: float, lon: float, 
                             radius_km: float) -> List[Cleaner]:
        """
        Find all cleaners within radius of a point.
        
        Args:
            lat: Latitude of point
            lon: Longitude of point
            radius_km: Search radius in kilometers
            
        Returns:
            List of cleaners within range
            
        Raises:
            ValueError: If radius is not positive
        """
        if radius_km <= 0:
            raise ValueError("Search radius must be positive")

        in_range = []
        for cleaner in self.cleaners.values():
            distance = cleaner.calculate_distance_to(lat, lon)
            if distance <= radius_km:
                in_range.append(cleaner)
                
        return in_range
    
    def sample_location_by_tam(self) -> Tuple[float, float, Optional[str]]:
        """
        Sample a random location within the market.
        
        For postal code-based markets:
            - Samples postal code weighted by TAM
            - Samples location around postal code center
            
        For location-based markets:
            - Samples uniformly within radius
        
        Returns:
            Tuple of (latitude, longitude, postal_code)
            postal_code will be None for location-based markets
        """
        if self.postal_codes is not None:
            # Sample postal code weighted by TAM
            weights = [pc.str_tam for pc in self.postal_codes.values()]
            total_tam = sum(weights)
            weights = [w/total_tam for w in weights]
            
            selected_pc = np.random.choice(
                list(self.postal_codes.values()),
                p=weights
            )
            
            # Sample location around postal code center
            std_dev_km = 1.0  # Could make configurable
            lat_std = std_dev_km / 111  # 1 degree ≈ 111 km
            lon_std = std_dev_km / (111 * np.cos(np.radians(selected_pc.latitude)))
            
            lat = np.random.normal(selected_pc.latitude, lat_std)
            lon = np.random.normal(selected_pc.longitude, lon_std)
            
            return lat, lon, selected_pc.postal_code
            
        else:
            # Sample uniformly within radius
            angle = np.random.uniform(0, 2 * np.pi)
            r = np.random.uniform(0, self.radius_km)
            
            lat_offset = r * np.cos(angle) / 111.0
            lon_offset = r * np.sin(angle) / (111.0 * np.cos(np.radians(self.center_lat)))
            
            lat = self.center_lat + lat_offset
            lon = self.center_lon + lon_offset
            
            return lat, lon, None