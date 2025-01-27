from dataclasses import dataclass
from typing import Optional
import numpy as np
from market_simulation.data.schemas import CleanerSchema
from market_simulation.utils.geo_utils import calculate_haversine_distance

@dataclass
class Cleaner:
    """
    Represents a cleaner with their properties and business logic.
    
    A cleaner can be associated with a postal code (market-based) or just have 
    a lat-lon location (location-based). The cleaner's ability to receive and 
    accept work is controlled by bidding_active and assignment_active flags.
    
    Attributes:
        contractor_id: Unique identifier for the cleaner
        latitude: Latitude of cleaner's location
        longitude: Longitude of cleaner's location
        postal_code: Optional postal code where cleaner is based
        bidding_active: Whether cleaner can receive and bid on new work
        assignment_active: Whether cleaner can be assigned to existing work
        cleaner_score: Quality score between 0 and 1
        service_radius: Maximum service radius in kilometers
        team_size: Number of team members
        active_connections: Number of current active connections
        active_connection_ratio: Ratio of active to total possible connections
    """
    contractor_id: str
    latitude: float
    longitude: float
    postal_code: Optional[str] = None
    bidding_active: bool = True
    assignment_active: bool = True
    cleaner_score: float = 0.5
    service_radius: float = 10.0
    team_size: int = 1
    active_connections: int = 0
    active_connection_ratio: float = 0.0
    
    def __post_init__(self):
        """Validate cleaner attributes."""
        if not -90 <= self.latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        if not -180 <= self.longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180")
        if not 0 <= self.cleaner_score <= 1:
            raise ValueError("Cleaner score must be between 0 and 1")
        if self.service_radius <= 0:
            raise ValueError("Service radius must be positive")
        if self.team_size < 1:
            raise ValueError("Team size must be at least 1")
        if self.active_connections < 0:
            raise ValueError("Active connections cannot be negative")
        if not 0 <= self.active_connection_ratio <= 1:
            raise ValueError("Active connection ratio must be between 0 and 1")
    
    @classmethod
    def from_schema(cls, schema: CleanerSchema) -> 'Cleaner':
        """Create a Cleaner instance from a validated schema."""
        return cls(
            contractor_id=schema.contractor_id,
            latitude=schema.latitude,
            longitude=schema.longitude,
            postal_code=schema.postal_code,
            bidding_active=schema.bidding_active,
            assignment_active=schema.assignment_active,
            cleaner_score=schema.cleaner_score,
            service_radius=schema.service_radius,
            team_size=schema.team_size,
            active_connections=schema.active_connections,
            active_connection_ratio=schema.active_connection_ratio
        )
    
    def to_schema(self) -> CleanerSchema:
        """Convert to schema for validation/serialization."""
        return CleanerSchema(
            contractor_id=self.contractor_id,
            latitude=self.latitude,
            longitude=self.longitude,
            postal_code=self.postal_code,
            bidding_active=self.bidding_active,
            assignment_active=self.assignment_active,
            cleaner_score=self.cleaner_score,
            service_radius=self.service_radius,
            team_size=self.team_size,
            active_connections=self.active_connections,
            active_connection_ratio=self.active_connection_ratio
        )
    
    def calculate_distance_to(self, lat: float, lon: float) -> float:
        """Calculate distance to a point in kilometers."""
        return calculate_haversine_distance(
            self.latitude, self.longitude,
            lat, lon
        )
    
    def is_in_range(self, lat: float, lon: float) -> bool:
        """Check if a location is within service radius."""
        return self.calculate_distance_to(lat, lon) <= self.service_radius
    
    @property
    def max_connections(self) -> int:
        """Calculate maximum number of possible connections based on team size."""
        MAX_CONNECTIONS_PER_MEMBER = 10  # This could be made configurable
        return self.team_size * MAX_CONNECTIONS_PER_MEMBER
    
    def calculate_capacity_factor(self) -> float:
        """
        Calculate current capacity factor based on team size and connections.
        
        Returns a value between 0.1 and 1.0 indicating available capacity.
        A value of 1.0 means fully available, while 0.1 means nearly at capacity.
        """
        capacity_factor = 1 - (self.active_connections / self.max_connections)
        return max(0.1, capacity_factor)
    
    def calculate_bid_probability(
        self,
        distance: float,
        distance_decay_factor: float = 0.2,
        base_probability: float = 0.14
    ) -> float:
        """
        Calculate probability of bidding on an offer.
        
        The probability is affected by:
        - Bidding status (must be active to bid)
        - Cleaner quality (higher score = higher probability)
        - Available capacity (more capacity = higher probability)
        - Distance (further = lower probability)
        
        Args:
            distance: Distance to property in kilometers
            distance_decay_factor: Factor controlling distance decay (higher = steeper decay)
            base_probability: Base probability of bidding before adjustments
            
        Returns:
            float: Probability between 0 and 1
        """
        if not self.bidding_active:
            return 0.0
        
        # Calculate component factors
        quality_factor = self.cleaner_score
        capacity_factor = self.calculate_capacity_factor()
        distance_factor = np.exp(-distance_decay_factor * distance)
        
        # Combine factors
        probability = base_probability * quality_factor * capacity_factor * distance_factor
        
        # Ensure result is between 0 and 1
        return max(0.0, min(1.0, probability))