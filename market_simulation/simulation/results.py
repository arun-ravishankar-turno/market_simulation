from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
import numpy as np
from market_simulation.utils.geo_utils import calculate_haversine_distance

@dataclass
class Offer:
    """Represents an offer made to a cleaner."""
    contractor_id: str
    distance: float
    cleaner_score: float
    active: bool
    team_size: int
    active_connections: int
    
    def __post_init__(self):
        """Validate offer data."""
        if not isinstance(self.distance, (int, float)) or self.distance < 0:
            raise ValueError("Distance must be a non-negative number")
        if not 0 <= self.cleaner_score <= 1:
            raise ValueError("Cleaner score must be between 0 and 1")
        if not isinstance(self.team_size, int) or self.team_size <= 0:
            raise ValueError("Team size must be a positive integer")
        if not isinstance(self.active_connections, int) or self.active_connections < 0:
            raise ValueError("Active connections must be a non-negative integer")

@dataclass
class Bid(Offer):
    """Represents a bid made by a cleaner."""
    bid_amount: Optional[float] = None
    bid_time: Optional[float] = None
    
    def __post_init__(self):
        """Validate bid data."""
        super().__post_init__()
        if self.bid_amount is not None and self.bid_amount <= 0:
            raise ValueError("Bid amount must be positive")
        if self.bid_time is not None and self.bid_time < 0:
            raise ValueError("Bid time must be non-negative")

@dataclass
class Connection(Bid):
    """Represents a successful connection."""
    connection_time: Optional[float] = None
    
    def __post_init__(self):
        """Validate connection data."""
        super().__post_init__()
        if self.connection_time is not None:
            if self.bid_time is None:
                raise ValueError("Connection must have bid time")
            if self.connection_time < self.bid_time:
                raise ValueError("Connection time cannot be before bid time")

@dataclass
class SearchResult:
    """
    Results from a single search simulation.
    
    This class holds the outcomes of a simulated search including offers,
    bids, and connections. It provides methods to calculate various
    statistics and metrics about the search results.
    
    Attributes:
        search_id: Unique identifier for the search
        postal_code: Optional postal code where search originated
        latitude: Search location latitude
        longitude: Search location longitude
        offers: List of offers generated
        bids: List of bids received
        connections: List of successful connections
    """
    search_id: str
    latitude: float
    longitude: float
    postal_code: Optional[str] = None
    offers: List[Offer] = field(default_factory=list)
    bids: List[Bid] = field(default_factory=list)
    connections: List[Connection] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate search result data."""
        if not -90 <= self.latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        if not -180 <= self.longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180")
    
    @property
    def num_offers(self) -> int:
        """Number of offers generated."""
        return len(self.offers)
    
    @property
    def num_bids(self) -> int:
        """Number of bids received."""
        return len(self.bids)
    
    @property
    def num_connections(self) -> int:
        """Number of successful connections."""
        return len(self.connections)
    
    def get_unique_cleaners(self) -> Set[str]:
        """Get set of unique contractor IDs from offers."""
        return {o.contractor_id for o in self.offers}
    
    def get_unique_active_cleaners(self) -> Set[str]:
        """Get set of unique active contractor IDs from offers."""
        return {o.contractor_id for o in self.offers if o.active}
    
    def calculate_distance_metrics(self) -> Dict[str, float]:
        """Calculate distance-related metrics."""
        if not self.offers:
            return {}
            
        offer_distances = [o.distance for o in self.offers]
        bid_distances = [b.distance for b in self.bids]
        conn_distances = [c.distance for c in self.connections]
        
        metrics = {
            'distance_min_offer': min(offer_distances, default=0),
            'distance_max_offer': max(offer_distances, default=0),
            'distance_avg_offer': np.mean(offer_distances),
            'distance_med_offer': np.median(offer_distances)
        }
        
        if bid_distances:
            metrics.update({
                'distance_avg_bid': np.mean(bid_distances),
                'distance_med_bid': np.median(bid_distances)
            })
            
        if conn_distances:
            metrics.update({
                'distance_avg_connection': np.mean(conn_distances),
                'distance_med_connection': np.median(conn_distances)
            })
            
        return metrics
    
    def calculate_score_metrics(self) -> Dict[str, float]:
        """Calculate cleaner score metrics."""
        if not self.offers:
            return {}
            
        offer_scores = [o.cleaner_score for o in self.offers]
        bid_scores = [b.cleaner_score for b in self.bids]
        conn_scores = [c.cleaner_score for c in self.connections]
        
        metrics = {
            'score_avg_offer': np.mean(offer_scores),
            'score_med_offer': np.median(offer_scores)
        }
        
        if bid_scores:
            metrics.update({
                'score_avg_bid': np.mean(bid_scores),
                'score_med_bid': np.median(bid_scores)
            })
            
        if conn_scores:
            metrics.update({
                'score_avg_connection': np.mean(conn_scores),
                'score_med_connection': np.median(conn_scores)
            })
            
        return metrics
    
    def get_all_metrics(self) -> Dict[str, float]:
        """Get all available metrics."""
        metrics = {}
        
        # Basic counts
        metrics.update({
            'num_offers': self.num_offers,
            'num_bids': self.num_bids,
            'num_connections': self.num_connections,
            'num_unique_cleaners': len(self.get_unique_cleaners()),
            'num_unique_active_cleaners': len(self.get_unique_active_cleaners())
        })
        
        # Conversion rates
        if self.num_offers > 0:
            metrics['bid_rate'] = self.num_bids / self.num_offers
            metrics['offer_to_connection_rate'] = self.num_connections / self.num_offers
            
        if self.num_bids > 0:
            metrics['acceptance_rate'] = self.num_connections / self.num_bids
        
        # Other metrics
        metrics.update(self.calculate_distance_metrics())
        metrics.update(self.calculate_score_metrics())
        
        return metrics