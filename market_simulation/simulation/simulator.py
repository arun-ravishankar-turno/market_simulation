from dataclasses import dataclass
from typing import List, Dict, Optional, Set, Tuple
import uuid
import numpy as np

from market_simulation.models.market import Market
from market_simulation.models.cleaner import Cleaner
from market_simulation.models.geo import GeoLocation, PostalCode
from market_simulation.simulation.config import SimulationConfig
from market_simulation.simulation.results import (
    Offer,
    Bid,
    Connection,
    SearchResult
)

@dataclass
class Simulator:
    """
    Core simulation engine for market supply-demand analysis.
    
    This class orchestrates the simulation of market interactions between
    cleaners and search requests. It supports both postal code-based and
    location-based markets.
    
    For postal code-based markets:
    - Location sampling is weighted by TAM
    - Search locations are centered around postal codes
    
    For location-based markets:
    - Location sampling is uniform within radius
    - Search locations can be anywhere within market radius
    
    Attributes:
        market: Market instance containing cleaners and geography
        config: Configuration parameters for simulation
    """
    market: Market
    config: SimulationConfig
    
    def __post_init__(self):
        """Validate simulator configuration."""
        if self.market.postal_codes is None and (
            self.market.center_lat is None or
            self.market.center_lon is None or
            self.market.radius_km is None
        ):
            raise ValueError(
                "Market must have either postal_codes or (center_lat, center_lon, radius_km)"
            )
    
    def simulate_search(self) -> SearchResult:
        """
        Simulate a single search interaction in the market.
        
        Works with both postal code-based and location-based markets:
        - For postal code markets: Samples location weighted by TAM
        - For location markets: Samples uniform location within radius
        
        Steps:
        1. Sample search location based on market type
        2. Find cleaners in range
        3. Generate offers
        4. Simulate bid decisions
        5. Simulate connection decisions
        
        Returns:
            SearchResult containing all interactions
        """
        # Sample location based on market type
        lat, lon, postal_code = self.market.sample_location_by_tam()
        search_id = str(uuid.uuid4())
        
        # Initialize result container
        result = SearchResult(
            search_id=search_id,
            latitude=lat,
            longitude=lon,
            postal_code=postal_code
        )
        
        # Find cleaners and generate offers
        search_radius = self.config.search_radius_km
        cleaners = self.market.get_cleaners_in_range(lat, lon, search_radius)
        result.offers = self._generate_offers(cleaners, lat, lon)
        
        # Simulate bid decisions
        result.bids = self._simulate_bids(result.offers)
        
        # Simulate connection decisions if there are bids
        if result.bids:
            result.connections = self._simulate_connections(result.bids)
            
        return result
    
    def _generate_offers(
        self, 
        cleaners: List[Cleaner], 
        lat: float, 
        lon: float
    ) -> List[Offer]:
        """Generate offers for cleaners in range."""
        return [
            Offer(
                contractor_id=cleaner.contractor_id,
                distance=cleaner.calculate_distance_to(lat, lon),
                cleaner_score=cleaner.cleaner_score,
                active=cleaner.bidding_active,
                team_size=cleaner.team_size,
                active_connections=cleaner.active_connections
            )
            for cleaner in cleaners
        ]
    
    def _simulate_bids(self, offers: List[Offer]) -> List[Bid]:
        """
        Simulate bid decisions from cleaners.
        
        Uses cleaner properties and distance to determine bid probability.
        """
        bids = []
        for offer in offers:
            # Skip inactive cleaners
            if not offer.active:
                continue
                
            # Calculate bid probability
            base_prob = self.config.cleaner_base_bid_probability
            distance_factor = np.exp(-self.config.distance_decay_factor * offer.distance)
            quality_factor = offer.cleaner_score
            capacity_factor = 1 - (offer.active_connections / (offer.team_size * 10))
            capacity_factor = max(self.config.min_capacity_factor, capacity_factor)
            
            probability = base_prob * distance_factor * quality_factor * capacity_factor
            
            # Make bid decision
            if np.random.random() < probability:
                bid = Bid(
                    contractor_id=offer.contractor_id,
                    distance=offer.distance,
                    cleaner_score=offer.cleaner_score,
                    active=offer.active,
                    team_size=offer.team_size,
                    active_connections=offer.active_connections
                )
                bids.append(bid)
        
        return bids
    
    def _simulate_connections(self, bids: List[Bid]) -> List[Connection]:
        """
        Simulate connection decisions for received bids.
        
        Uses bid properties and cleaner scores to determine connection probability.
        Only one connection can be made per search.
        """
        if not bids:
            return []
            
        # Sort bids by score for preference
        sorted_bids = sorted(bids, key=lambda x: x.cleaner_score, reverse=True)
        
        for bid in sorted_bids:
            # Calculate connection probability
            base_prob = self.config.connection_base_probability
            score_factor = bid.cleaner_score
            distance_factor = np.exp(-self.config.distance_decay_factor * bid.distance)
            
            probability = base_prob * score_factor * distance_factor
            
            # Make connection decision
            if np.random.random() < probability:
                connection = Connection(
                    contractor_id=bid.contractor_id,
                    distance=bid.distance,
                    cleaner_score=bid.cleaner_score,
                    active=bid.active,
                    team_size=bid.team_size,
                    active_connections=bid.active_connections
                )
                return [connection]  # Only one connection per search
        
        return []  # No connection made
    
    def run_simulation(self, iterations: Optional[int] = None) -> List[SearchResult]:
        """
        Run multiple search simulations.
        
        Args:
            iterations: Number of iterations (defaults to config value)
            
        Returns:
            List of SearchResult objects
        """
        n_iter = iterations or self.config.search_iterations
        
        # Reset random seed if configured
        if self.config.random_seed is not None:
            np.random.seed(self.config.random_seed)
        
        results = []
        for _ in range(n_iter):
            result = self.simulate_search()
            results.append(result)
            
        return results