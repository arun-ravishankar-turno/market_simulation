from typing import List, Dict, Optional
from dataclasses import dataclass
import numpy as np
from market_simulation.data.schemas import GeoMappingSchema

@dataclass
class PostalCode:
    """
    Represents a postal code area with its geographic and market properties.
    
    This class handles spatial relationships between postal codes and provides
    methods for calculating distances and finding neighboring postal codes.
    
    Attributes:
        postal_code (str): Unique identifier for the postal code
        market (str): Market identifier this postal code belongs to
        latitude (float): Latitude of postal code centroid
        longitude (float): Longitude of postal code centroid
        str_tam (int): Short term rental total addressable market
    """
    postal_code: str
    market: str
    latitude: float
    longitude: float
    str_tam: int
    
    @classmethod
    def from_schema(cls, schema: GeoMappingSchema) -> 'PostalCode':
        """Create a PostalCode instance from a validated schema."""
        return cls(
            postal_code=schema.postal_code,
            market=schema.market,
            latitude=schema.latitude,
            longitude=schema.longitude,
            str_tam=schema.str_tam
        )
    
    def calculate_distance(self, other: 'PostalCode') -> float:
        """
        Calculate the distance in kilometers between this postal code and another.
        
        Uses the Haversine formula for calculating great-circle distances between points.
        
        Args:
            other: Another PostalCode instance
            
        Returns:
            float: Distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1 = np.radians(self.latitude), np.radians(self.longitude)
        lat2, lon2 = np.radians(other.latitude), np.radians(other.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c
    
    def find_neighbors(self, postal_codes: List['PostalCode'], 
                      threshold_km: float) -> List['PostalCode']:
        """
        Find all postal codes within a specified distance threshold.
        
        Args:
            postal_codes: List of postal codes to check
            threshold_km: Maximum distance in kilometers to consider as neighboring
            
        Returns:
            List of PostalCode instances within the threshold distance
        """
        return [
            pc for pc in postal_codes 
            if pc.postal_code != self.postal_code 
            and self.calculate_distance(pc) <= threshold_km
        ]
    
    def get_tam_weight(self, total_market_tam: int) -> float:
        """
        Calculate this postal code's TAM weight relative to total market TAM.
        
        Args:
            total_market_tam: Total TAM across all postal codes in the market
            
        Returns:
            float: TAM weight between 0 and 1
        """
        if total_market_tam <= 0:
            raise ValueError("Total market TAM must be positive")
        return self.str_tam / total_market_tam