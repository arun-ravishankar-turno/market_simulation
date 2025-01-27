from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
import numpy as np
from collections import defaultdict

from market_simulation.models.market import Market
from market_simulation.models.cleaner import Cleaner
from market_simulation.simulation.results import SearchResult

@dataclass
class GeographicMetrics:
    """
    Geographic distribution metrics for market analysis.
    
    Tracks spatial distribution of:
    - Search locations
    - Cleaner locations
    - Service coverage
    - Connection patterns
    """
    search_points: List[Tuple[float, float]] = field(default_factory=list)
    connection_points: List[Tuple[float, float]] = field(default_factory=list)
    
    def add_search(self, result: SearchResult) -> None:
        """Add search result to geographic metrics."""
        self.search_points.append((result.latitude, result.longitude))
        
        if result.connections:
            self.connection_points.append((result.latitude, result.longitude))
    
    def calculate_coverage_metrics(self, market: Market) -> Dict[str, float]:
        """
        Calculate geographic coverage metrics.
        
        For postal code markets:
        - Density is calculated per total market area
        - Coverage is based on cleaner service areas, considering overlaps
        - Active coverage considers only active cleaners
        
        For location-based markets:
        - Density is calculated per unit area
        - Coverage is based on cleaner service areas
        """
        metrics = {}
        
        if not self.search_points:
            return metrics
            
        total_area = market.total_area
        if total_area  <= 0:
            return {
                'search_density': 0.0,
                'connection_density': 0.0,
                'coverage_ratio': 0.0,
                'active_coverage_ratio': 0.0
            }
            
        metrics['search_density'] = len(self.search_points) / total_area
        metrics['connection_density'] = len(self.connection_points) / total_area
        
        # For postal code markets
        if market.postal_codes:
            # Create a mapping of postal codes to their cleaners
            pc_cleaners = defaultdict(list)
            for cleaner in market.cleaners.values():
                if cleaner.postal_code:
                    pc_cleaners[cleaner.postal_code].append(cleaner)
            
            # Calculate covered area
            covered_area = 0.0
            active_covered_area = 0.0
            
            for postal_code, pc_data in market.postal_codes.items():
                if postal_code in pc_cleaners:
                    # Get cleaners in this postal code
                    cleaners = pc_cleaners[postal_code]
                    if cleaners:
                        # Calculate maximum service coverage in this postal code
                        pc_area = pc_data.area if pc_data.area is not None else 0
                        
                        # Consider service radius overlap
                        max_radius = max(c.service_radius for c in cleaners)
                        pc_covered_area = min(
                            np.pi * (max_radius ** 2),  # Maximum possible coverage
                            pc_area  # Limited by postal code area
                        )
                        covered_area += pc_covered_area
                        
                        # Calculate active coverage
                        active_cleaners = [c for c in cleaners if c.bidding_active]
                        if active_cleaners:
                            max_active_radius = max(c.service_radius for c in active_cleaners)
                            pc_active_covered = min(
                                np.pi * (max_active_radius ** 2),
                                pc_area
                            )
                            active_covered_area += pc_active_covered
        
        # For location-based markets
        else:
            total_area = np.pi * (market.radius_km ** 2)
            
            # Calculate total coverage considering overlaps
            # Note: This is a simplification; actual overlap calculation would be more complex
            max_radius = max((c.service_radius for c in market.cleaners.values()), default=0)
            covered_area = min(
                np.pi * (max_radius ** 2) * len(market.cleaners),
                total_area
            )
            
            # Calculate active coverage
            active_cleaners = [c for c in market.cleaners.values() if c.bidding_active]
            if active_cleaners:
                max_active_radius = max(c.service_radius for c in active_cleaners)
                active_covered_area = min(
                    np.pi * (max_active_radius ** 2) * len(active_cleaners),
                    total_area
                )
            else:
                active_covered_area = 0.0
        
        # Calculate final ratios
        metrics['coverage_ratio'] = covered_area / total_area
        metrics['active_coverage_ratio'] = active_covered_area / total_area
        
        # Add average service radius for active cleaners
        active_cleaners = [c for c in market.cleaners.values() if c.bidding_active]
        if active_cleaners:
            metrics['avg_service_radius'] = np.mean([c.service_radius for c in active_cleaners])
        
        return metrics

@dataclass
class MarketMetrics:
    """
    Market-level metrics for simulation analysis.
    
    Tracks:
    - Search success rates
    - Cleaner utilization
    - Market coverage
    - Supply-demand balance
    
    Attributes:
        geographic: Geographic distribution metrics
        search_count: Total number of searches
        connection_count: Total successful connections
        bid_counts: Number of bids per search
        distances: Distance metrics
        cleaner_scores: Cleaner quality metrics
    """
    geographic: GeographicMetrics = field(default_factory=GeographicMetrics)
    search_count: int = 0
    connection_count: int = 0
    bid_counts: List[int] = field(default_factory=list)
    distances: Dict[str, List[float]] = field(default_factory=lambda: defaultdict(list))
    cleaner_scores: Dict[str, List[float]] = field(default_factory=lambda: defaultdict(list))
    
    def add_result(self, result: SearchResult) -> None:
        """Process a search result and update metrics."""
        self.search_count += 1
        self.bid_counts.append(len(result.bids))
        self.connection_count += len(result.connections)
        
        # Update geographic metrics
        self.geographic.add_search(result)
        
        # Track distances
        for offer in result.offers:
            self.distances['offer'].append(offer.distance)
        for bid in result.bids:
            self.distances['bid'].append(bid.distance)
        for conn in result.connections:
            self.distances['connection'].append(conn.distance)
            
        # Track cleaner scores
        for offer in result.offers:
            self.cleaner_scores['offer'].append(offer.cleaner_score)
        for bid in result.bids:
            self.cleaner_scores['bid'].append(bid.cleaner_score)
        for conn in result.connections:
            self.cleaner_scores['connection'].append(conn.cleaner_score)
    
    def calculate_metrics(self, market: Market) -> Dict[str, float]:
        """Calculate comprehensive market metrics."""
        metrics = {}
        
        # Basic rates
        metrics['connection_rate'] = (
            self.connection_count / self.search_count if self.search_count > 0 else 0
        )
        
        # Bid metrics
        if self.bid_counts:
            metrics.update({
                'avg_bids_per_search': np.mean(self.bid_counts),
                'med_bids_per_search': np.median(self.bid_counts),
                'pct_searches_with_bids': np.mean([n > 0 for n in self.bid_counts])
            })
        
        # Distance metrics
        for key in ['offer', 'bid', 'connection']:
            if self.distances[key]:
                metrics.update({
                    f'avg_{key}_distance': np.mean(self.distances[key]),
                    f'med_{key}_distance': np.median(self.distances[key])
                })
        
        # Score metrics
        for key in ['offer', 'bid', 'connection']:
            if self.cleaner_scores[key]:
                metrics.update({
                    f'avg_{key}_score': np.mean(self.cleaner_scores[key]),
                    f'med_{key}_score': np.median(self.cleaner_scores[key])
                })
        
        # Geographic metrics
        metrics.update(self.geographic.calculate_coverage_metrics(market))
        
        return metrics

@dataclass
class SimulationMetrics:
    """
    Container for all simulation metrics and analysis functions.
    
    Handles:
    - Result collection
    - Metric calculation
    - Geographic analysis
    - Time series analysis
    """
    market: Market
    results: List[SearchResult] = field(default_factory=list)
    market_metrics: MarketMetrics = field(default_factory=MarketMetrics)
    
    def add_results(self, results: List[SearchResult]) -> None:
        """Add simulation results for analysis."""
        self.results.extend(results)
        for result in results:
            self.market_metrics.add_result(result)
    
    def get_metrics(self) -> Dict[str, float]:
        """Get comprehensive metrics dictionary."""
        return self.market_metrics.calculate_metrics(self.market)
    
    def get_geospatial_data(self) -> Dict[str, List[Tuple[float, float]]]:
        """Get data for geographic visualization."""
        return {
            'searches': self.market_metrics.geographic.search_points,
            'connections': self.market_metrics.geographic.connection_points,
            'cleaners': [(c.latitude, c.longitude) for c in self.market.cleaners.values()],
            'service_areas': [
                (c.latitude, c.longitude, c.service_radius)
                for c in self.market.cleaners.values()
            ]
        }
    
    def get_score_distributions(self) -> Dict[str, List[float]]:
        """Get cleaner score distributions for visualization."""
        return {
            'offer_scores': self.market_metrics.cleaner_scores['offer'],
            'bid_scores': self.market_metrics.cleaner_scores['bid'],
            'connection_scores': self.market_metrics.cleaner_scores['connection']
        }
    
    def get_distance_distributions(self) -> Dict[str, List[float]]:
        """Get distance distributions for visualization."""
        return {
            'offer_distances': self.market_metrics.distances['offer'],
            'bid_distances': self.market_metrics.distances['bid'],
            'connection_distances': self.market_metrics.distances['connection']
        }