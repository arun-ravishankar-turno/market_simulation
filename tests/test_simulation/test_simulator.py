import pytest
import numpy as np
from market_simulation.models.market import Market
from market_simulation.models.cleaner import Cleaner
from market_simulation.models.geo import PostalCode
from market_simulation.simulation.config import SimulationConfig
from market_simulation.simulation.simulator import Simulator

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
        ),
        Cleaner(  # Inactive cleaner
            contractor_id="C3",
            latitude=40.7317,
            longitude=-73.9885,
            postal_code="10003",
            bidding_active=False,
            assignment_active=False,
            cleaner_score=0.7,
            service_radius=10.0,
            team_size=1,
            active_connections=0
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
def config():
    """Create simulation configuration."""
    return SimulationConfig(
        search_iterations=10,
        supply_configuration_iterations=1,
        random_seed=42,
        cleaner_base_bid_probability=0.14,
        connection_base_probability=0.4,
        distance_decay_factor=0.2,
        search_radius_km=10.0
    )

# --- Test Simulator Initialization ---

def test_simulator_initialization_postal_code(postal_code_market, config):
    """Test simulator initialization with postal code market."""
    simulator = Simulator(market=postal_code_market, config=config)
    assert simulator.market == postal_code_market
    assert simulator.config == config

def test_simulator_initialization_location_based(location_based_market, config):
    """Test simulator initialization with location-based market."""
    simulator = Simulator(market=location_based_market, config=config)
    assert simulator.market == location_based_market
    assert simulator.config == config

def test_invalid_market_initialization(config):
    """Test simulator initialization with invalid market."""
    # Create a market with invalid configuration
    with pytest.raises(ValueError, match="Must provide either postal_codes or"):
        Market(
            market_id="invalid",
            postal_codes=None,
            center_lat=None,
            center_lon=None,
            radius_km=None
        )

# --- Test Offer Generation ---

def test_offer_generation(postal_code_market, config):
    """Test offer generation for cleaners."""
    simulator = Simulator(market=postal_code_market, config=config)
    cleaners = postal_code_market.cleaners.values()
    
    lat, lon = 40.7505, -73.9965  # Test location
    offers = simulator._generate_offers(list(cleaners), lat, lon)
    
    assert len(offers) == len(cleaners)
    for offer in offers:
        assert offer.contractor_id in postal_code_market.cleaners
        assert 0 <= offer.distance <= 10.0  # Within service radius
        assert 0 <= offer.cleaner_score <= 1.0

# --- Test Bid Simulation ---

def test_bid_simulation(postal_code_market, config):
    """Test bid simulation from offers."""
    simulator = Simulator(market=postal_code_market, config=config)
    
    # Generate some test offers
    cleaners = postal_code_market.cleaners.values()
    lat, lon = 40.7505, -73.9965
    offers = simulator._generate_offers(list(cleaners), lat, lon)
    
    # Simulate bids
    bids = simulator._simulate_bids(offers)
    
    # Active cleaners should have a chance to bid
    active_cleaners = sum(1 for c in cleaners if c.bidding_active)
    assert len(bids) <= active_cleaners
    
    # Check bid properties
    for bid in bids:
        cleaner = postal_code_market.cleaners[bid.contractor_id]
        assert cleaner.bidding_active  # Only active cleaners should bid
        assert 0 <= bid.cleaner_score <= 1.0

# --- Test Connection Simulation ---

def test_connection_simulation(postal_code_market, config):
    """Test connection simulation from bids."""
    simulator = Simulator(market=postal_code_market, config=config)
    
    # Generate test bids
    cleaners = postal_code_market.cleaners.values()
    lat, lon = 40.7505, -73.9965
    offers = simulator._generate_offers(list(cleaners), lat, lon)
    bids = simulator._simulate_bids(offers)
    
    # Simulate connections
    connections = simulator._simulate_connections(bids)
    
    # Should have at most one connection
    assert len(connections) <= 1
    
    # Check connection properties if one was made
    if connections:
        connection = connections[0]
        assert connection.contractor_id in postal_code_market.cleaners
        cleaner = postal_code_market.cleaners[connection.contractor_id]
        assert cleaner.bidding_active

# --- Test Full Search Simulation ---

def test_single_search_postal_code(postal_code_market, config):
    """Test complete search simulation in postal code market."""
    simulator = Simulator(market=postal_code_market, config=config)
    result = simulator.simulate_search()
    
    assert result.search_id is not None
    assert -90 <= result.latitude <= 90
    assert -180 <= result.longitude <= 180
    assert result.postal_code in postal_code_market.postal_codes
    
    # Should have generated offers
    assert len(result.offers) > 0
    
    # Might have bids and connections
    assert len(result.bids) <= len(result.offers)
    assert len(result.connections) <= 1

def test_single_search_location_based(location_based_market, config):
    """Test complete search simulation in location-based market."""
    simulator = Simulator(market=location_based_market, config=config)
    result = simulator.simulate_search()
    
    assert result.search_id is not None
    assert -90 <= result.latitude <= 90
    assert -180 <= result.longitude <= 180
    assert result.postal_code is None  # Location-based markets don't use postal codes
    
    # Calculate distance from market center
    distance = location_based_market.cleaners["C1"].calculate_distance_to(
        result.latitude,
        result.longitude
    )
    assert distance <= location_based_market.radius_km

# --- Test Multiple Simulations ---

def test_run_simulation(postal_code_market, config):
    """Test running multiple search simulations."""
    simulator = Simulator(market=postal_code_market, config=config)
    results = simulator.run_simulation(iterations=5)
    
    assert len(results) == 5
    for result in results:
        assert result.search_id is not None
        assert len(result.offers) > 0

def test_simulation_reproducibility(postal_code_market, config):
    """Test that simulations are reproducible with same seed."""
    # First simulation
    np.random.seed(42)  # Explicitly set seed
    simulator1 = Simulator(market=postal_code_market, config=config)
    results1 = simulator1.run_simulation(iterations=5)
    
    # Second simulation
    np.random.seed(42)  # Reset seed to same value
    simulator2 = Simulator(market=postal_code_market, config=config)
    results2 = simulator2.run_simulation(iterations=5)
    
    # Compare results (focusing on simulation outcomes)
    for r1, r2 in zip(results1, results2):
        # Search locations should be identical
        assert r1.latitude == r2.latitude
        assert r1.longitude == r2.longitude
        assert r1.postal_code == r2.postal_code
        
        # Offers should match
        assert len(r1.offers) == len(r2.offers)
        for o1, o2 in zip(sorted(r1.offers, key=lambda x: x.contractor_id), 
                         sorted(r2.offers, key=lambda x: x.contractor_id)):
            assert o1.contractor_id == o2.contractor_id
            assert o1.distance == o2.distance
            assert o1.cleaner_score == o2.cleaner_score
            assert o1.active == o2.active
            assert o1.team_size == o2.team_size
            assert o1.active_connections == o2.active_connections
        
        # Bids should match
        assert len(r1.bids) == len(r2.bids)
        for b1, b2 in zip(sorted(r1.bids, key=lambda x: x.contractor_id),
                         sorted(r2.bids, key=lambda x: x.contractor_id)):
            assert b1.contractor_id == b2.contractor_id
            assert b1.distance == b2.distance
            assert b1.cleaner_score == b2.cleaner_score
        
        # Connections should match
        assert len(r1.connections) == len(r2.connections)
        if r1.connections:
            c1 = r1.connections[0]
            c2 = r2.connections[0]
            assert c1.contractor_id == c2.contractor_id
            assert c1.distance == c2.distance
            assert c1.cleaner_score == c2.cleaner_score