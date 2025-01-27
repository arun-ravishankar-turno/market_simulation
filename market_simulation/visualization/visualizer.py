from typing import List, Dict, Optional, Tuple
import numpy as np
import folium
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass
from folium.vector_layers import Circle, CircleMarker

from market_simulation.models.market import Market
from market_simulation.simulation.metrics import SimulationMetrics

@dataclass
class MarketVisualizer:
    """Visualization tools for market simulation analysis."""
    metrics: SimulationMetrics
    
    def create_market_map(self, 
                        center_lat: Optional[float] = None,
                        center_lon: Optional[float] = None) -> folium.Map:
        """Create interactive map showing market activity."""
        # Determine map center
        if center_lat is None or center_lon is None:
            if self.metrics.market.postal_codes:
                postal_codes = list(self.metrics.market.postal_codes.values())
                center_lat = np.mean([pc.latitude for pc in postal_codes])
                center_lon = np.mean([pc.longitude for pc in postal_codes])
            else:
                center_lat = self.metrics.market.center_lat
                center_lon = self.metrics.market.center_lon
        
        # Create base map
        market_map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=12,
            tiles='cartodbpositron'
        )
        
        # Add market boundary for location-based markets first
        if not self.metrics.market.postal_codes and self.metrics.market.radius_km:
            boundary = folium.Circle(
                location=[self.metrics.market.center_lat,
                        self.metrics.market.center_lon],
                radius=self.metrics.market.radius_km * 1000,  # Convert km to m
                color='black',
                weight=2,
                fill=False,
                popup='Market Boundary'
            )
            boundary._name = 'market_boundary'
            boundary.add_to(market_map)
        
        # Add cleaners and their service areas
        for cleaner in self.metrics.market.cleaners.values():
            # Add service radius circle
            service_area = folium.Circle(
                location=[cleaner.latitude, cleaner.longitude],
                radius=cleaner.service_radius * 1000,  # Convert km to m
                color='blue' if cleaner.bidding_active else 'gray',
                fill=True,
                opacity=0.2,
                popup=f"Cleaner {cleaner.contractor_id}<br>"
                    f"Score: {cleaner.cleaner_score:.2f}<br>"
                    f"Team Size: {cleaner.team_size}<br>"
                    f"Active: {cleaner.bidding_active}"
            )
            service_area._name = f'service_area_{cleaner.contractor_id}'
            service_area.add_to(market_map)
            
            # Add cleaner marker
            marker = folium.CircleMarker(
                location=[cleaner.latitude, cleaner.longitude],
                radius=5,
                color='blue' if cleaner.bidding_active else 'gray',
                fill=True,
                popup=f"Cleaner {cleaner.contractor_id}"
            )
            marker._name = f'cleaner_{cleaner.contractor_id}'
            marker.add_to(market_map)
        
        # Get geospatial data
        geo_data = self.metrics.get_geospatial_data()
        
        # Add search points
        for i, (lat, lon) in enumerate(geo_data['searches']):
            search = folium.CircleMarker(
                location=[lat, lon],
                radius=3,
                color='red',
                fill=True,
                popup='Search'
            )
            search._name = f'search_{i}'
            search.add_to(market_map)
        
        # Add connection points
        for i, (lat, lon) in enumerate(geo_data['connections']):
            connection = folium.CircleMarker(
                location=[lat, lon],
                radius=3,
                color='green',
                fill=True,
                popup='Connection'
            )
            connection._name = f'connection_{i}'
            connection.add_to(market_map)
        
        return market_map
    
    def plot_distance_distributions(self) -> plt.Figure:
        """Plot distance distributions for offers, bids, and connections."""
        distances = self.metrics.get_distance_distributions()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        has_data = False
        # Plot kernel density estimates
        for key, data in distances.items():
            if data and len(data) > 1 and np.var(data) > 0:
                sns.kdeplot(data=data, label=key.replace('_', ' ').title())
                has_data = True
        
        if not has_data:
            ax.text(0.5, 0.5, 'No distribution data available',
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes)
        
        ax.set_xlabel('Distance (km)')
        ax.set_ylabel('Density')
        ax.set_title('Distance Distributions')
        if has_data:
            ax.legend()
        
        return fig
    
    def plot_score_distributions(self) -> plt.Figure:
        """Plot cleaner score distributions for offers, bids, and connections."""
        scores = self.metrics.get_score_distributions()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        has_data = False
        # Plot kernel density estimates
        for key, data in scores.items():
            if data and len(data) > 1 and np.var(data) > 0:
                sns.kdeplot(data=data, label=key.replace('_', ' ').title())
                has_data = True
        
        if not has_data:
            ax.text(0.5, 0.5, 'No distribution data available',
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes)
        
        ax.set_xlabel('Cleaner Score')
        ax.set_ylabel('Density')
        ax.set_title('Score Distributions')
        if has_data:
            ax.legend()
        
        return fig
    
    def plot_market_summary(self) -> plt.Figure:
        """Create summary visualization of key market metrics."""
        metrics = self.metrics.get_metrics()
        
        # Select key metrics to visualize
        key_metrics = {
            'Connection Rate': metrics.get('connection_rate', 0),
            'Coverage Ratio': metrics.get('coverage_ratio', 0),
            'Avg Bids/Search': metrics.get('avg_bids_per_search', 0),
            'Search Density': metrics.get('search_density', 0)
        }
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create bar plot
        bars = ax.bar(range(len(key_metrics)), list(key_metrics.values()))
        
        # Customize plot
        ax.set_xticks(range(len(key_metrics)))
        ax.set_xticklabels(key_metrics.keys(), rotation=45)
        ax.set_ylabel('Value')
        ax.set_title('Market Summary Metrics')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom')
        
        plt.tight_layout()
        return fig