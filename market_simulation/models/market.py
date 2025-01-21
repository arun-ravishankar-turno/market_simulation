from typing import List, Dict, Optional
from dataclasses import dataclass
import numpy as np
from market_simulation.models.geo import PostalCode
from market_simulation.data.schemas import GeoMappingSchema, CleanerSchema
from market_simulation.utils.geo_utils import calculate_haversine_distance


@dataclass
class Market:
    """
    Represents a market composed of multiple postal codes and their cleaners.
    
    This class manages the geographic organization of postal codes within a market
    and handles the initialization and distribution of cleaners and searches.
    
    Attributes:
        market_id: str
            Unique identifier for the market
        postal_codes: Dict[str, PostalCode]
            Dictionary of postal codes in the market, keyed by postal code
        cleaners: Dict[str, CleanerSchema]
            Dictionary of cleaners in the market, keyed by contractor_id
    """
    market_id: str
    postal_codes: Dict[str, PostalCode]
    cleaners: Dict[str, CleanerSchema] = None
    
    @property
    def total_str_tam(self) -> int:
        """Calculate total STR TAM for the market."""
        return sum(pc.str_tam for pc in self.postal_codes.values())
    
    def initialize_cleaners(self, cleaners: Dict[str, CleanerSchema]) -> None:
        """
        Initialize cleaners in the market.
        
        Args:
            cleaners: Dictionary of cleaner schemas
        """
        # Filter cleaners to only those in market's postal codes
        self.cleaners = {
            cid: cleaner for cid, cleaner in cleaners.items()
            if cleaner.postal_code in self.postal_codes
        }
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the distance in kilometers between two points.
        
        Args:
            lat1: Latitude of first point
            lon1: Longitude of first point
            lat2: Latitude of second point
            lon2: Longitude of second point
            
        Returns:
            float: Distance in kilometers
        """
        return calculate_haversine_distance(lat1, lon1, lat2, lon2)

    def get_postal_code_neighbors(self, postal_code: str, 
                                threshold_km: float) -> List[PostalCode]:
        """
        Get neighboring postal codes within threshold distance.
        
        Args:
            postal_code: Postal code to find neighbors for
            threshold_km: Maximum distance in kilometers
            
        Returns:
            List of neighboring PostalCode objects
        """
        if postal_code not in self.postal_codes:
            raise ValueError(f"Postal code {postal_code} not in market")
            
        origin = self.postal_codes[postal_code]
        return origin.find_neighbors(list(self.postal_codes.values()), threshold_km)
    
    def get_cleaners_in_range(self, lat: float, lon: float, 
                             radius_km: float) -> List[CleanerSchema]:
        """
        Find all cleaners within specified radius of a point.
        
        Args:
            lat: Latitude of point
            lon: Longitude of point
            radius_km: Search radius in kilometers
            
        Returns:
            List of cleaners within range
        """
        if self.cleaners is None:
            raise ValueError("Cleaners not initialized")
            
        # Create temporary PostalCode for distance calculation
        point = PostalCode("temp", self.market_id, lat, lon, 0)
        
        in_range = []
        for cleaner in self.cleaners.values():
            cleaner_point = PostalCode("temp", self.market_id, 
                                     cleaner.latitude, cleaner.longitude, 0)
            if point.calculate_distance(cleaner_point) <= radius_km:
                in_range.append(cleaner)
                
        return in_range
    
    def sample_location_by_tam(self) -> tuple[float, float, str]:
        """
        Sample a random location within the market, weighted by STR TAM.
        
        Returns:
            Tuple of (latitude, longitude, postal_code)
        """
        # Select postal code weighted by TAM
        weights = [pc.str_tam for pc in self.postal_codes.values()]
        total_tam = sum(weights)
        weights = [w/total_tam for w in weights]
        
        selected_pc = np.random.choice(list(self.postal_codes.values()), p=weights)
        
        # Sample location around postal code center
        # Using a simplified circular normal distribution
        std_dev_km = 1.0  # Can be configured as needed
        
        # Convert km to degrees (approximate)
        lat_std = std_dev_km / 111  # 1 degree lat ≈ 111 km
        lon_std = std_dev_km / (111 * np.cos(np.radians(selected_pc.latitude)))
        
        sampled_lat = np.random.normal(selected_pc.latitude, lat_std)
        sampled_lon = np.random.normal(selected_pc.longitude, lon_std)
        
        return sampled_lat, sampled_lon, selected_pc.postal_code

    def add_cleaner(self, cleaner: CleanerSchema) -> None:
        """
        Add a new cleaner to the market.
        
        Args:
            cleaner: CleanerSchema instance representing the new cleaner
            
        Raises:
            ValueError: If cleaner's postal code is not in this market
        """
        if cleaner.postal_code not in self.postal_codes:
            raise ValueError(f"Cleaner postal code {cleaner.postal_code} not in market")
            
        if self.cleaners is None:
            self.cleaners = {}
        
        self.cleaners[cleaner.contractor_id] = cleaner