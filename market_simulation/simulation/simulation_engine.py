from dataclasses import dataclass
from typing import List, Dict, Optional
import numpy as np
from market_simulation.models.market import Market
from market_simulation.data.schemas import (
    CleanerSchema, 
    SimulationResultsSchema,
    MarketSearchesSchema
)

@dataclass
class SimulationConfig:
    """Configuration parameters for market simulation.
    
    Attributes:
        supply_configuration_iterations: Number of iterations for each supply config
        search_iterations: Number of iterations for each search
        cleaner_base_bid_probability: Base probability of a cleaner bidding
        connection_base_probability: Base probability of a connection given a bid
        distance_decay_factor: Factor for how distance affects bid probability
    """
    supply_configuration_iterations: int = 10
    search_iterations: int = 10
    cleaner_base_bid_probability: float = 0.14  # From your data
    connection_base_probability: float = 0.4    # From your data
    distance_decay_factor: float = 0.2

@dataclass
class SearchResult:
    """Results from a single search simulation.
    
    Attributes:
        search_id: Unique identifier for the search
        postal_code: Postal code where search originated
        latitude: Search location latitude
        longitude: Search location longitude
        offers: List of offers generated
        bids: List of bids received
        connections: List of connections made
    """
    search_id: str
    postal_code: str
    latitude: float
    longitude: float
    offers: List[Dict] = None
    bids: List[Dict] = None
    connections: List[Dict] = None

class SimulationEngine:
    """Main engine for running market simulations."""
    
    def __init__(self, config: SimulationConfig):
        """Initialize simulation engine with configuration."""
        self.config = config
        
    def calculate_bid_probability(self, cleaner: CleanerSchema, 
                                distance: float) -> float:
        """Calculate probability of cleaner bidding based on properties and distance."""
        base_prob = self.config.cleaner_base_bid_probability
        
        # Adjust for cleaner properties
        quality_factor = cleaner.cleaner_score
        capacity_factor = 1 - (cleaner.active_connections / (cleaner.team_size * 10))
        capacity_factor = max(0.1, capacity_factor)  # Minimum 0.1
        
        # Distance decay
        distance_factor = np.exp(-self.config.distance_decay_factor * distance)
        
        return base_prob * quality_factor * capacity_factor * distance_factor
    
    def simulate_search(self, search_id: str, market: Market) -> SearchResult:
        """Simulate a single search in the market."""
        # Sample search location based on TAM distribution
        lat, lon, postal_code = market.sample_location_by_tam()
        
        result = SearchResult(
            search_id=search_id,
            postal_code=postal_code,
            latitude=lat,
            longitude=lon
        )
        
        # Generate offers for all cleaners in range
        cleaners = market.get_cleaners_in_range(lat, lon, radius_km=10.0)
        
        offers = []
        bids = []
        connections = []
        
        for cleaner in cleaners:
            # Calculate distance
            distance = market.calculate_distance(
                lat1=lat, lon1=lon,
                lat2=cleaner.latitude, lon2=cleaner.longitude
            )
            
            offer = {
                'cleaner_id': cleaner.contractor_id,
                'distance': distance,
                'cleaner_score': cleaner.cleaner_score
            }
            offers.append(offer)
            
            # Simulate bid
            bid_prob = self.calculate_bid_probability(cleaner, distance)
            if np.random.random() < bid_prob:
                bid = {**offer, 'bid': True}
                bids.append(bid)
                
                # Simulate connection
                connection_prob = self.config.connection_base_probability
                if np.random.random() < connection_prob:
                    connection = {**bid, 'connected': True}
                    connections.append(connection)
        
        result.offers = offers
        result.bids = bids
        result.connections = connections
        
        return result
    
    def run_market_simulation(self, 
                            market: Market,
                            market_searches: MarketSearchesSchema,
                            additional_cleaners: Optional[List[CleanerSchema]] = None
                            ) -> SimulationResultsSchema:
        """
        Run full market simulation with given parameters.
        
        Args:
            market: Market instance to simulate
            market_searches: Expected search volume data
            additional_cleaners: Optional list of additional cleaners to add
            
        Returns:
            Simulation results conforming to SimulationResultsSchema
        """
        # Add additional cleaners if provided
        if additional_cleaners:
            for cleaner in additional_cleaners:
                market.add_cleaner(cleaner)
        
        all_results = []
        
        # Run multiple iterations
        for _ in range(self.config.supply_configuration_iterations):
            search_results = []
            
            # Simulate searches
            for i in range(market_searches.projected_searches):
                search_id = f"search_{i}"
                for _ in range(self.config.search_iterations):
                    result = self.simulate_search(search_id, market)
                    search_results.append(result)
            
            all_results.extend(search_results)
        
        # Aggregate results and return metrics
        return self._calculate_metrics(market.market_id, all_results)
    
    def _calculate_metrics(self, market_id: str, results: List[SearchResult]) -> SimulationResultsSchema:
        """
        Calculate aggregate metrics from simulation results.
        
        Args:
            market_id: Identifier for the market
            results: List of search simulation results
            
        Returns:
            SimulationResultsSchema with computed metrics
        """
        if not results:
            raise ValueError("No simulation results to calculate metrics from")
        
        # Helper function for percentile calculation
        def calculate_percentiles(values: List[float]) -> tuple[float, float, float]:
            if not values:
                return 0.0, 0.0, 0.0
            return (
                np.percentile(values, 25),
                np.percentile(values, 50),
                np.percentile(values, 75)
            )
        
        # Initialize counters
        total_searches = len(results)
        total_offers = sum(len(r.offers) for r in results)
        total_bids = sum(len(r.bids) for r in results)
        total_connections = sum(len(r.connections) for r in results)
        
        # Per-search metrics
        offers_per_search = [len(r.offers) for r in results]
        bids_per_search = [len(r.bids) for r in results]
        connections_per_search = [len(r.connections) for r in results]
        
        # Distance metrics
        all_offer_distances = [
            offer['distance']
            for r in results
            for offer in r.offers
        ]
        
        bid_distances = [
            bid['distance']
            for r in results
            for bid in r.bids
        ]
        
        connection_distances = [
            conn['distance']
            for r in results
            for conn in r.connections
        ]
        
        # Cleaner score metrics
        offer_scores = [
            offer['cleaner_score']
            for r in results
            for offer in r.offers
        ]
        
        bid_scores = [
            bid['cleaner_score']
            for r in results
            for bid in r.bids
        ]
        
        connection_scores = [
            conn['cleaner_score']
            for r in results
            for conn in r.connections
        ]
        
        # Active cleaner metrics (assuming active status is in the offer data)
        active_offers_per_search = [
            len([o for o in r.offers if o.get('active', True)])
            for r in results
        ]
        
        active_bids_per_search = [
            len([b for b in r.bids if b.get('active', True)])
            for r in results
        ]
        
        # Calculate percentiles
        offers_p25, offers_p50, offers_p75 = calculate_percentiles(offers_per_search)
        dist_p25, dist_p50, dist_p75 = calculate_percentiles(all_offer_distances)
        score_p25, score_p50, score_p75 = calculate_percentiles(offer_scores)
        
        # Create SimulationResultsSchema
        return SimulationResultsSchema(
            market=market_id,
            searches=total_searches,
            number_of_cleaners=len(set(o['cleaner_id'] for r in results for o in r.offers)),
            number_of_active_cleaners=len(set(
                o['cleaner_id'] for r in results 
                for o in r.offers if o.get('active', True)
            )),
            total_str_tam=0,  # This should come from market data
            
            # Total counts
            total_bids=total_bids,
            total_connections=total_connections,
            
            # Average per-search metrics
            avg_offers_per_search=np.mean(offers_per_search),
            avg_bids_per_search=np.mean(bids_per_search),
            avg_connections_per_search=np.mean(connections_per_search),
            
            # Percentile metrics
            offers_per_search_p25=offers_p25,
            offers_per_search_p50=offers_p50,
            offers_per_search_p75=offers_p75,
            
            # Conversion metrics
            avg_bids_per_offer=total_bids / total_offers if total_offers > 0 else 0.0,
            avg_connections_per_offer=total_connections / total_offers if total_offers > 0 else 0.0,
            avg_connections_per_bid=total_connections / total_bids if total_bids > 0 else 0.0,
            
            # Active cleaner metrics
            avg_active_cleaner_offers_per_search=np.mean(active_offers_per_search),
            avg_active_cleaner_bids_per_search=np.mean(active_bids_per_search),
            
            # Distance metrics
            avg_distance_offers_per_search=np.mean(all_offer_distances),
            avg_distance_bids_per_search=np.mean(bid_distances),
            avg_distance_connections_per_search=np.mean(connection_distances),
            
            # Distance percentiles
            distance_offers_p25=dist_p25,
            distance_offers_p50=dist_p50,
            distance_offers_p75=dist_p75,
            
            # Cleaner score metrics
            avg_cleaner_score_per_search=np.mean(offer_scores),
            avg_cleaner_score_of_bidders_per_search=np.mean(bid_scores),
            avg_cleaner_score_of_connection_per_search=np.mean(connection_scores),
            
            # Cleaner score percentiles
            cleaner_score_p25=score_p25,
            cleaner_score_p50=score_p50,
            cleaner_score_p75=score_p75,
        )