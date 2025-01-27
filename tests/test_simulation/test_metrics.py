import pytest
import numpy as np
from market_simulation.simulation.metrics import GeographicMetrics
from market_simulation.models.market import Market
from market_simulation.models.cleaner import Cleaner
from market_simulation.models.geo import PostalCode
from market_simulation.simulation.results import SearchResult, Offer, Bid, Connection

# --- Fixtures ---

@pytest.fixture
def sample_postal_codes():
    """Create sample postal codes with known areas."""
    return {
        "10001": PostalCode(
            postal_code="10001",
            market="test_market",
            latitude=40.7505,
            longitude=-73.9965,
            str_tam=100,
            area=2.0  # 2 sq km
        ),
        "10002": PostalCode(
            postal_code="10002",
            market="test_market",
            latitude=40.7168,
            longitude=-73.9861,
            str_tam=150,
            area=3.0  # 3 sq km
        ),
        "10003": PostalCode(
            postal_code="10003",
            market="test_market",
            latitude=40.7317,
            longitude=-73.9885,
            str_tam=200,
            area=2.5  # 2.5 sq km
        )
    }

@pytest.fixture
def sample_cleaners():
    """Create sample cleaners with known service radii."""
    return [
        Cleaner(
            contractor_id="C1",
            latitude=40.7505,
            longitude=-73.9965,
            postal_code="10001",
            bidding_active=True,
            assignment_active=True,
            cleaner_score=0.8,
            service_radius=1.0,  # 1 km radius
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
            service_radius=1.5,  # 1.5 km radius
            team_size=3,
            active_connections=3
        ),
        Cleaner(  # Inactive cleaner
            contractor_id="C3",
            latitude=40.7317,
            longitude=-73.9885,
            postal_code="10003",
            bidding_active=False,
            assignment_active=False,
            cleaner_score=0.7,
            service_radius=1.2,  # 1.2 km radius
            team_size=1,
            active_connections=0
        )
    ]

@pytest.fixture
def postal_code_market(sample_postal_codes, sample_cleaners):
    """Create a postal code market with known areas."""
    market = Market(
        market_id="test_market",
        postal_codes=sample_postal_codes
    )
    for cleaner in sample_cleaners:
        market.add_cleaner(cleaner)
    return market

@pytest.fixture
def location_market(sample_cleaners):
    """Create a location-based market with known radius."""
    market = Market(
        market_id="test_market",
        center_lat=40.7505,
        center_lon=-73.9965,
        radius_km=5.0  # 5 km radius (area ≈ 78.54 sq km)
    )
    for cleaner in sample_cleaners:
        market.add_cleaner(cleaner)
    return market

@pytest.fixture
def sample_search_result():
    """Create a sample search result."""
    return SearchResult(
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
    )

# --- Tests ---

def test_postal_code_market_total_area(postal_code_market):
    """Test total area calculation for postal code market."""
    expected_area = sum(pc.area for pc in postal_code_market.postal_codes.values())
    assert postal_code_market.total_area == expected_area
    assert expected_area == 7.5  # 2.0 + 3.0 + 2.5

def test_location_market_total_area(location_market):
    """Test total area calculation for location-based market."""
    expected_area = np.pi * (location_market.radius_km ** 2)
    assert abs(location_market.total_area - expected_area) < 0.01

def test_coverage_metrics_postal_code(postal_code_market, sample_search_result):
    """Test coverage metrics for postal code market."""
    metrics = GeographicMetrics()
    metrics.add_search(sample_search_result)
    
    coverage_metrics = metrics.calculate_coverage_metrics(postal_code_market)
    
    # Check presence of metrics
    assert 'coverage_ratio' in coverage_metrics
    assert 'active_coverage_ratio' in coverage_metrics
    assert 'search_density' in coverage_metrics
    
    # Verify search density
    assert coverage_metrics['search_density'] == 1 / postal_code_market.total_area
    
    # Verify coverage ratios
    assert 0 < coverage_metrics['coverage_ratio'] <= 1.0
    assert 0 < coverage_metrics['active_coverage_ratio'] <= 1.0
    assert coverage_metrics['active_coverage_ratio'] <= coverage_metrics['coverage_ratio']

def test_coverage_metrics_location(location_market, sample_search_result):
    """Test coverage metrics for location-based market."""
    metrics = GeographicMetrics()
    metrics.add_search(sample_search_result)
    
    coverage_metrics = metrics.calculate_coverage_metrics(location_market)
    
    # Check metric presence
    assert 'coverage_ratio' in coverage_metrics
    assert 'active_coverage_ratio' in coverage_metrics
    assert 'avg_service_radius' in coverage_metrics
    
    # Verify coverage ratios
    total_area = np.pi * (location_market.radius_km ** 2)
    assert coverage_metrics['coverage_ratio'] <= 1.0
    assert coverage_metrics['active_coverage_ratio'] <= coverage_metrics['coverage_ratio']

def test_no_active_cleaners_coverage(postal_code_market, sample_search_result):
    """Test coverage metrics when no cleaners are active."""
    # Make all cleaners inactive
    for cleaner in postal_code_market.cleaners.values():
        cleaner.bidding_active = False
    
    metrics = GeographicMetrics()
    metrics.add_search(sample_search_result)
    
    coverage_metrics = metrics.calculate_coverage_metrics(postal_code_market)
    assert coverage_metrics['active_coverage_ratio'] == 0.0
    assert coverage_metrics['coverage_ratio'] > 0.0

def test_service_radius_overlap(postal_code_market, sample_search_result):
    """Test that overlapping service areas are handled correctly."""
    # Add overlapping cleaner
    overlapping_cleaner = Cleaner(
        contractor_id="C4",
        latitude=40.7505,  # Same location as C1
        longitude=-73.9965,
        postal_code="10001",
        bidding_active=True,
        assignment_active=True,
        cleaner_score=0.8,
        service_radius=1.0,
        team_size=2,
        active_connections=5
    )
    postal_code_market.add_cleaner(overlapping_cleaner)
    
    metrics = GeographicMetrics()
    metrics.add_search(sample_search_result)
    
    coverage_metrics = metrics.calculate_coverage_metrics(postal_code_market)
    
    # Coverage shouldn't exceed postal code area even with overlap
    pc_area = postal_code_market.postal_codes["10001"].area
    assert coverage_metrics['coverage_ratio'] <= 1.0
    
def test_empty_market_coverage(postal_code_market, sample_search_result):
    """Test coverage metrics for market with no cleaners."""
    postal_code_market.cleaners.clear()
    
    metrics = GeographicMetrics()
    metrics.add_search(sample_search_result)
    
    coverage_metrics = metrics.calculate_coverage_metrics(postal_code_market)
    assert coverage_metrics['coverage_ratio'] == 0.0
    assert coverage_metrics['active_coverage_ratio'] == 0.0