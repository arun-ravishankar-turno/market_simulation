import pytest
import numpy as np
import folium
import matplotlib.pyplot as plt

from market_simulation.models.market import Market
from market_simulation.models.cleaner import Cleaner
from market_simulation.models.geo import PostalCode
from market_simulation.simulation.metrics import SimulationMetrics
from market_simulation.simulation.results import (
    SearchResult, Offer, Bid, Connection
)
from market_simulation.visualization.visualizer import MarketVisualizer

# --- Fixtures ---

@pytest.fixture
def postal_codes():
    """Create sample postal codes."""
    return {
        "10001": PostalCode(
            postal_code="10001",
            market="test_market",
            latitude=40.7505,
            longitude=-73.9965,
            str_tam=100
        ),
        "10002": PostalCode(
            postal_code="10002",
            market="test_market",
            latitude=40.7168,
            longitude=-73.9861,
            str_tam=150
        )
    }

@pytest.fixture
def sample_cleaners():
    """Create sample cleaners."""
    return [
        Cleaner(
            contractor_id="C1",
            latitude=40.7505,
            longitude=-73.9965,
            postal_code="10001",
            bidding_active=True,
            assignment_active=True,
            cleaner_score=0.8,
            service_radius=10.0,
            team_size=2,
            active_connections=5
        ),
        Cleaner(  # Inactive cleaner
            contractor_id="C2",
            latitude=40.7168,
            longitude=-73.9861,
            postal_code="10002",
            bidding_active=False,
            assignment_active=False,
            cleaner_score=0.9,
            service_radius=10.0,
            team_size=3,
            active_connections=3
        )
    ]

@pytest.fixture
def sample_search_results():
    """Create sample search results."""
    return [
        SearchResult(
            search_id="test_1",
            latitude=40.7505,
            longitude=-73.9965,
            postal_code="10001",
            offers=[
                Offer(
                    contractor_id="C1",
                    distance=1.0,
                    cleaner_score=0.8,
                    active=True,
                    team_size=2,
                    active_connections=5
                )
            ],
            bids=[
                Bid(
                    contractor_id="C1",
                    distance=1.0,
                    cleaner_score=0.8,
                    active=True,
                    team_size=2,
                    active_connections=5
                )
            ],
            connections=[
                Connection(
                    contractor_id="C1",
                    distance=1.0,
                    cleaner_score=0.8,
                    active=True,
                    team_size=2,
                    active_connections=5
                )
            ]
        ),
        SearchResult(  # Search without connection
            search_id="test_2",
            latitude=40.7168,
            longitude=-73.9861,
            postal_code="10002",
            offers=[
                Offer(
                    contractor_id="C2",
                    distance=2.0,
                    cleaner_score=0.9,
                    active=False,
                    team_size=3,
                    active_connections=3
                )
            ],
            bids=[],
            connections=[]
        )
    ]

@pytest.fixture
def postal_code_market(postal_codes, sample_cleaners):
    """Create a postal code-based market."""
    market = Market(
        market_id="test_market",
        postal_codes=postal_codes
    )
    for cleaner in sample_cleaners:
        market.add_cleaner(cleaner)
    return market

@pytest.fixture
def location_based_market(sample_cleaners):
    """Create a location-based market."""
    market = Market(
        market_id="test_market",
        center_lat=40.7505,
        center_lon=-73.9965,
        radius_km=5.0
    )
    for cleaner in sample_cleaners:
        market.add_cleaner(cleaner)
    return market

@pytest.fixture
def metrics_postal_code(postal_code_market, sample_search_results):
    """Create metrics for postal code market."""
    metrics = SimulationMetrics(market=postal_code_market)
    metrics.add_results(sample_search_results)
    return metrics

@pytest.fixture
def metrics_location(location_based_market, sample_search_results):
    """Create metrics for location-based market."""
    metrics = SimulationMetrics(market=location_based_market)
    metrics.add_results(sample_search_results)
    return metrics

# --- Test Map Creation ---

def test_create_market_map_postal_code(metrics_postal_code):
    """Test map creation for postal code market."""
    visualizer = MarketVisualizer(metrics=metrics_postal_code)
    market_map = visualizer.create_market_map()
    
    assert isinstance(market_map, folium.Map)
    
    # Count map elements by name
    service_areas = sum(1 for _, element in market_map._children.items()
                      if isinstance(element, folium.Circle) and
                      hasattr(element, '_name') and
                      'service_area' in element._name)
    
    cleaner_markers = sum(1 for _, element in market_map._children.items()
                        if isinstance(element, folium.CircleMarker) and
                        hasattr(element, '_name') and
                        'cleaner' in element._name)
    
    search_markers = sum(1 for _, element in market_map._children.items()
                       if isinstance(element, folium.CircleMarker) and
                       hasattr(element, '_name') and
                       'search' in element._name)
    
    # Verify counts
    assert service_areas == len(metrics_postal_code.market.cleaners)
    assert cleaner_markers == len(metrics_postal_code.market.cleaners)
    assert search_markers == len(metrics_postal_code.results)

def test_create_market_map_location(metrics_location):
    """Test map creation for location-based market."""
    visualizer = MarketVisualizer(metrics=metrics_location)
    market_map = visualizer.create_market_map()
    
    assert isinstance(market_map, folium.Map)
    
    # Check for market boundary
    boundary_circles = sum(1 for _, element in market_map._children.items()
                         if isinstance(element, folium.Circle) and
                         hasattr(element, '_name') and
                         element._name == 'market_boundary')
    assert boundary_circles == 1
    
    # Check for cleaner elements
    service_areas = sum(1 for _, element in market_map._children.items()
                      if isinstance(element, folium.Circle) and
                      hasattr(element, '_name') and
                      'service_area' in element._name)
    assert service_areas == len(metrics_location.market.cleaners)

# --- Test Distribution Plots ---

def test_plot_distance_distributions_empty():
    """Test distance distribution plotting with no data."""
    empty_market = Market(
        market_id="test",
        center_lat=0.0,
        center_lon=0.0,
        radius_km=1.0
    )
    empty_metrics = SimulationMetrics(market=empty_market)
    visualizer = MarketVisualizer(metrics=empty_metrics)
    
    fig = visualizer.plot_distance_distributions()
    assert isinstance(fig, plt.Figure)
    
    # Should show "No data" message
    text_elements = fig.axes[0].texts
    assert any('No distribution data available' in t.get_text() 
              for t in text_elements)

def test_plot_distance_distributions(metrics_postal_code):
    """Test distance distribution plotting."""
    visualizer = MarketVisualizer(metrics=metrics_postal_code)
    fig = visualizer.plot_distance_distributions()
    
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    
    # Check plot elements
    assert ax.get_xlabel().lower() == 'distance (km)'
    assert ax.get_ylabel().lower() == 'density'
    assert len(ax.get_lines()) > 0  # Should have at least one line
    assert ax.get_legend() is not None

def test_plot_score_distributions_empty():
    """Test score distribution plotting with no data."""
    empty_market = Market(
        market_id="test",
        center_lat=0.0,
        center_lon=0.0,
        radius_km=1.0
    )
    empty_metrics = SimulationMetrics(market=empty_market)
    visualizer = MarketVisualizer(metrics=empty_metrics)
    
    fig = visualizer.plot_score_distributions()
    assert isinstance(fig, plt.Figure)
    
    # Should show "No data" message
    text_elements = fig.axes[0].texts
    assert any('No distribution data available' in t.get_text() 
              for t in text_elements)

def test_plot_score_distributions(metrics_postal_code):
    """Test score distribution plotting."""
    visualizer = MarketVisualizer(metrics=metrics_postal_code)
    fig = visualizer.plot_score_distributions()
    
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    
    # Check plot elements
    assert ax.get_xlabel().lower() == 'cleaner score'
    assert ax.get_ylabel().lower() == 'density'
    assert len(ax.get_lines()) > 0
    assert ax.get_legend() is not None

def test_plot_market_summary(metrics_postal_code):
    """Test market summary plotting."""
    visualizer = MarketVisualizer(metrics=metrics_postal_code)
    fig = visualizer.plot_market_summary()
    
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    
    # Should have bars for key metrics
    assert len(ax.patches) >= 4  # At least 4 key metrics
    assert ax.get_ylabel().lower() == 'value'

# --- Test Edge Cases ---

def test_empty_market_visualization(postal_code_market):
    """Test visualization with no search results."""
    empty_metrics = SimulationMetrics(market=postal_code_market)
    visualizer = MarketVisualizer(metrics=empty_metrics)
    
    # Should still create map
    market_map = visualizer.create_market_map()
    assert isinstance(market_map, folium.Map)
    
    # Should create empty plots
    fig_dist = visualizer.plot_distance_distributions()
    assert isinstance(fig_dist, plt.Figure)
    
    fig_score = visualizer.plot_score_distributions()
    assert isinstance(fig_score, plt.Figure)
    
    fig_summary = visualizer.plot_market_summary()
    assert isinstance(fig_summary, plt.Figure)

def test_custom_map_center(metrics_postal_code):
    """Test map creation with custom center."""
    visualizer = MarketVisualizer(metrics=metrics_postal_code)
    custom_lat, custom_lon = 41.0, -74.0
    
    market_map = visualizer.create_market_map(
        center_lat=custom_lat,
        center_lon=custom_lon
    )
    
    assert isinstance(market_map, folium.Map)
    assert market_map.location == [custom_lat, custom_lon]