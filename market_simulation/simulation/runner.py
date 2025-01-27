from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Union
import numpy as np
import pandas as pd
from pathlib import Path
import json

from market_simulation.models.market import Market
from market_simulation.models.cleaner import Cleaner
from market_simulation.models.geo import PostalCode
from market_simulation.simulation.config import SimulationConfig
from market_simulation.simulation.simulator import Simulator
from market_simulation.simulation.metrics import SimulationMetrics
from market_simulation.visualization.visualizer import MarketVisualizer

@dataclass
class SimulationRunner:
    """
    Orchestrates complete market simulations.
    
    This class brings together all components:
    - Market setup
    - Simulation execution
    - Metrics collection
    - Visualization generation
    
    It supports both postal code and location-based markets.
    
    Attributes:
        config: Simulation configuration
        output_dir: Directory for saving results
    """
    config: SimulationConfig
    output_dir: Optional[Path] = None
    
    def setup_postal_code_market(
        self,
        market_id: str,
        postal_codes: Dict[str, PostalCode],
        cleaners: List[Cleaner]
    ) -> Market:
        """Set up a postal code-based market."""
        market = Market(
            market_id=market_id,
            postal_codes=postal_codes
        )
        for cleaner in cleaners:
            market.add_cleaner(cleaner)
        return market
    
    def setup_location_market(
        self,
        market_id: str,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        cleaners: List[Cleaner]
    ) -> Market:
        """Set up a location-based market."""
        market = Market(
            market_id=market_id,
            center_lat=center_lat,
            center_lon=center_lon,
            radius_km=radius_km
        )
        for cleaner in cleaners:
            market.add_cleaner(cleaner)
        return market
    
    def run_simulation(self, market: Market) -> Tuple[SimulationMetrics, Dict[str, float]]:
        """
        Run complete simulation for a market.
        
        Args:
            market: Market to simulate
            
        Returns:
            Tuple of (metrics, summary_stats)
        """
        # Initialize components
        simulator = Simulator(market=market, config=self.config)
        metrics = SimulationMetrics(market=market)
        
        # Run simulation
        results = simulator.run_simulation()
        metrics.add_results(results)
        
        # Calculate summary statistics
        summary_stats = metrics.get_metrics()
        
        return metrics, summary_stats
    
    def generate_visualizations(
        self,
        metrics: SimulationMetrics,
        save: bool = False
    ) -> Dict[str, Union[str, bytes]]:
        """
        Generate all visualizations for simulation results.
        
        Args:
            metrics: Simulation metrics
            save: Whether to save visualizations to disk
            
        Returns:
            Dictionary of visualization names and their data/paths
        """
        visualizer = MarketVisualizer(metrics=metrics)
        visualizations = {}
        
        # Generate map
        market_map = visualizer.create_market_map()
        if save and self.output_dir:
            map_path = self.output_dir / 'market_map.html'
            market_map.save(str(map_path))
            visualizations['market_map'] = str(map_path)
        else:
            visualizations['market_map'] = market_map._repr_html_()
        
        # Generate distribution plots
        dist_fig = visualizer.plot_distance_distributions()
        if save and self.output_dir:
            dist_path = self.output_dir / 'distance_distributions.png'
            dist_fig.savefig(dist_path)
            visualizations['distance_distributions'] = str(dist_path)
        else:
            visualizations['distance_distributions'] = dist_fig
        
        score_fig = visualizer.plot_score_distributions()
        if save and self.output_dir:
            score_path = self.output_dir / 'score_distributions.png'
            score_fig.savefig(score_path)
            visualizations['score_distributions'] = str(score_path)
        else:
            visualizations['score_distributions'] = score_fig
        
        summary_fig = visualizer.plot_market_summary()
        if save and self.output_dir:
            summary_path = self.output_dir / 'market_summary.png'
            summary_fig.savefig(summary_path)
            visualizations['market_summary'] = str(summary_path)
        else:
            visualizations['market_summary'] = summary_fig
        
        return visualizations
    
    def save_results(
        self,
        metrics: SimulationMetrics,
        summary_stats: Dict[str, float],
        visualizations: Dict[str, Union[str, bytes]]
    ) -> None:
        """Save all simulation results to disk."""
        if not self.output_dir:
            raise ValueError("Output directory not set")
            
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save configuration
        config_path = self.output_dir / 'config.json'
        with open(config_path, 'w') as f:
            json.dump(self.config.asdict(), f, indent=2)
        
        # Save summary statistics
        stats_path = self.output_dir / 'summary_stats.json'
        with open(stats_path, 'w') as f:
            json.dump(summary_stats, f, indent=2)
            
        # Save search results as CSV
        results_df = pd.DataFrame([
            {
                'search_id': r.search_id,
                'latitude': r.latitude,
                'longitude': r.longitude,
                'postal_code': r.postal_code,
                'num_offers': len(r.offers),
                'num_bids': len(r.bids),
                'num_connections': len(r.connections)
            }
            for r in metrics.results
        ])
        results_df.to_csv(self.output_dir / 'search_results.csv', index=False)
        
        # Save visualizations (if not already saved)
        if not isinstance(visualizations['market_map'], str):
            map_path = self.output_dir / 'market_map.html'
            with open(map_path, 'w') as f:
                f.write(visualizations['market_map'])
            
        for name, fig in visualizations.items():
            if name != 'market_map' and not isinstance(fig, str):
                fig.savefig(self.output_dir / f'{name}.png')
    
    def run_complete_simulation(
        self,
        market: Market,
        save_results: bool = False
    ) -> Tuple[SimulationMetrics, Dict[str, float], Dict[str, Union[str, bytes]]]:
        """
        Run complete simulation with all components.
        
        Args:
            market: Market to simulate
            save_results: Whether to save results to disk
            
        Returns:
            Tuple of (metrics, summary_stats, visualizations)
        """
        # Run simulation
        metrics, summary_stats = self.run_simulation(market)
        
        # Generate visualizations
        visualizations = self.generate_visualizations(
            metrics,
            save=save_results
        )
        
        # Save results if requested
        if save_results:
            self.save_results(metrics, summary_stats, visualizations)
        
        return metrics, summary_stats, visualizations