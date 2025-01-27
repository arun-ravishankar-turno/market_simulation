import pytest
import numpy as np
from market_simulation.models.market import Market
from market_simulation.models.cleaner import Cleaner
from market_simulation.models.geo import PostalCode
from market_simulation.simulation.results import (
    Offer, Bid, Connection, SearchResult
)
from market_simulation.simulation.metrics import (
    GeographicMetrics,
    MarketMetrics,
    SimulationMetrics
)

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
        "10002": PostalCode(  # ~4km away
            postal_code="10002",
            market="test_market",
            latitude=40.7168,
            longitude=-73.9861,
            str_tam=150
        ),
        "10003": PostalCode(  # ~2km away
            postal_code="10003",
            market="test_market",
            latitude=40.7317,
            longitude=-73.9885,
            str_tam=200
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
        Cleaner(
            contractor_id="C2",
            latitude=40.7168,
            longitude=-73.9861,
            postal_code="10002",
            bidding_active=True,
            assignment_active=True,
            cleaner_score=0.9,
            service_radius=10.0,
            team_size=3,
            active_connections=3
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
def sample_search_result(sample_cleaners):
    """Create a sample search result."""
    offers = [
        Offer(
            contractor_id=c.contractor_id,
            distance=1.0,
            cleaner_score=c.cleaner_score,
            active=c.bidding_active,
            team_size=c.team_size,
            active_connections=c.active_connections
        )
        for c in sample_cleaners
    ]
    
    bids = [
        Bid(
            contractor_id=c.contractor_id,
            distance=1.0,
            cleaner_score=c.cleaner_score,
            active=c.bidding_active,
            team_size=c.team_size,
            active_connections=c.active_connections
        )
        for c in sample_cleaners if c.contractor_id == "C1"
    ]
    
    connections = [
        Connection(
            contractor_id="C1",
            distance=1.0,
            cleaner_score=0.8,
            active=True,
            team_size=2,
            active_connections=5
        )
    ]
    
    return SearchResult(
        search_id="test_1",
        latitude=40.7505,
        longitude=-73.9965,
        postal_code="10001",
        offers=offers,
        bids=bids,
        connections=connections
    )

# --- Test Geographic Metrics ---

def test_geographic_metrics_initialization():
    """Test geographic metrics initialization."""
    metrics = GeographicMetrics()
    assert len(metrics.search_points) == 0
    assert len(metrics.connection_points) == 0
    
    # Test initial metrics calculation returns empty dict
    empty_market = Market(
        market_id="test",
        center_lat=0.0,
        center_lon=0.0,
        radius_km=1.0
    )
    assert metrics.calculate_coverage_metrics(empty_market) == {}

def test_geographic_metrics_add_search(sample_search_result):
    """Test adding search results to geographic metrics."""
    metrics = GeographicMetrics()
    metrics.add_search(sample_search_result)
    
    assert len(metrics.search_points) == 1
    assert metrics.search_points[0] == (40.7505, -73.9965)
    
    assert len(metrics.connection_points) == 1
    assert metrics.connection_points[0] == (40.7505, -73.9965)

def test_geographic_coverage_metrics_postal_code(postal_code_market):
    """Test coverage metrics for postal code market."""
    metrics = GeographicMetrics()
    
    # Add a search result
    search_result = SearchResult(
        search_id="test_1",
        latitude=40.7505,
        longitude=-73.9965,
        postal_code="10001",
        offers=[],
        bids=[],
        connections=[]
    )
    metrics.add_search(search_result)
    
    coverage = metrics.calculate_coverage_metrics(postal_code_market)
    
    # Check metric presence
    assert 'search_density' in coverage
    assert 'coverage_ratio' in coverage
    
    # Check metric values
    assert coverage['search_density'] == 1 / len(postal_code_market.postal_codes)
    assert 0 <= coverage['coverage_ratio'] <= 1
    assert 0 <= coverage.get('active_coverage_ratio', 1) <= 1

def test_geographic_coverage_metrics_location(location_based_market):
    """Test coverage metrics for location-based market."""
    metrics = GeographicMetrics()
    
    # Add a search result
    search_result = SearchResult(
        search_id="test_1",
        latitude=40.7505,
        longitude=-73.9965,
        postal_code=None,
        offers=[],
        bids=[],
        connections=[]
    )
    metrics.add_search(search_result)
    
    coverage = metrics.calculate_coverage_metrics(location_based_market)
    
    # Check metric presence
    assert 'search_density' in coverage
    assert 'coverage_ratio' in coverage
    assert 'avg_service_radius' in coverage
    
    # Check metric values
    area = np.pi * (location_based_market.radius_km ** 2)
    assert coverage['search_density'] == 1 / area
    assert 0 <= coverage['coverage_ratio'] <= 1
    assert coverage['avg_service_radius'] > 0

def test_empty_geographic_metrics(postal_code_market):
    """Test geographic metrics with no data."""
    metrics = GeographicMetrics()
    coverage = metrics.calculate_coverage_metrics(postal_code_market)
    assert coverage == {}

def test_geographic_metrics_with_connections(postal_code_market):
    """Test geographic metrics with connections."""
    metrics = GeographicMetrics()
    
    # Add a search result with connection
    search_result = SearchResult(
        search_id="test_1",
        latitude=40.7505,
        longitude=-73.9965,
        postal_code="10001",
        offers=[],
        bids=[],
        connections=[Connection(
            contractor_id="C1",
            distance=1.0,
            cleaner_score=0.8,
            active=True,
            team_size=2,
            active_connections=5
        )]
    )
    metrics.add_search(search_result)
    
    coverage = metrics.calculate_coverage_metrics(postal_code_market)
    assert 'connection_density' in coverage
    assert 'connection_ratio' in coverage
    assert coverage['connection_ratio'] == 1.0

# --- Test Market Metrics ---

def test_market_metrics_initialization():
    """Test market metrics initialization."""
    metrics = MarketMetrics()
    assert metrics.search_count == 0
    assert metrics.connection_count == 0
    assert len(metrics.bid_counts) == 0

def test_market_metrics_add_result(sample_search_result):
    """Test adding search results to market metrics."""
    metrics = MarketMetrics()
    metrics.add_result(sample_search_result)
    
    assert metrics.search_count == 1
    assert metrics.connection_count == 1
    assert len(metrics.bid_counts) == 1
    assert metrics.bid_counts[0] == 1
    
    # Check distance tracking
    assert len(metrics.distances['offer']) == 2  # Two offers
    assert len(metrics.distances['bid']) == 1    # One bid
    assert len(metrics.distances['connection']) == 1  # One connection
    
    # Check score tracking
    assert len(metrics.cleaner_scores['offer']) == 2
    assert len(metrics.cleaner_scores['bid']) == 1
    assert len(metrics.cleaner_scores['connection']) == 1

def test_market_metrics_calculation(postal_code_market, sample_search_result):
    """Test market metrics calculation."""
    metrics = MarketMetrics()
    metrics.add_result(sample_search_result)
    
    results = metrics.calculate_metrics(postal_code_market)
    assert isinstance(results, dict)
    
    # Check required metrics
    assert 'connection_rate' in results
    assert 'avg_bids_per_search' in results
    assert 'avg_offer_distance' in results
    assert 'avg_offer_score' in results
    assert 'search_density' in results
    assert 'coverage_ratio' in results
    
    # Verify values
    assert 0 <= results['connection_rate'] <= 1
    assert results['avg_bids_per_search'] > 0
    assert results['coverage_ratio'] > 0

# --- Test Simulation Metrics ---

def test_simulation_metrics_initialization(postal_code_market):
    """Test simulation metrics initialization."""
    metrics = SimulationMetrics(market=postal_code_market)
    assert len(metrics.results) == 0
    assert isinstance(metrics.market_metrics, MarketMetrics)

def test_simulation_metrics_add_results(postal_code_market, sample_search_result):
    """Test adding results to simulation metrics."""
    metrics = SimulationMetrics(market=postal_code_market)
    metrics.add_results([sample_search_result])
    
    assert len(metrics.results) == 1
    assert metrics.market_metrics.search_count == 1

def test_simulation_metrics_get_metrics(postal_code_market, sample_search_result):
    """Test getting comprehensive metrics."""
    metrics = SimulationMetrics(market=postal_code_market)
    metrics.add_results([sample_search_result])
    
    results = metrics.get_metrics()
    assert isinstance(results, dict)
    assert 'connection_rate' in results

def test_simulation_metrics_geospatial_data(postal_code_market, sample_search_result):
    """Test getting geospatial data for visualization."""
    metrics = SimulationMetrics(market=postal_code_market)
    metrics.add_results([sample_search_result])
    
    data = metrics.get_geospatial_data()
    assert 'searches' in data
    assert 'connections' in data
    assert 'cleaners' in data
    assert 'service_areas' in data
    
    assert len(data['searches']) == 1
    assert len(data['connections']) == 1
    assert len(data['cleaners']) == 2
    assert len(data['service_areas']) == 2

def test_simulation_metrics_distributions(postal_code_market, sample_search_result):
    """Test getting distribution data for visualization."""
    metrics = SimulationMetrics(market=postal_code_market)
    metrics.add_results([sample_search_result])
    
    scores = metrics.get_score_distributions()
    assert 'offer_scores' in scores
    assert 'bid_scores' in scores
    assert 'connection_scores' in scores
    
    distances = metrics.get_distance_distributions()
    assert 'offer_distances' in distances
    assert 'bid_distances' in distances
    assert 'connection_distances' in distances