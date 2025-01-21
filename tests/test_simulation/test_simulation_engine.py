import pytest
import numpy as np
from market_simulation.simulation.simulation_engine import (
    SimulationConfig,
    SearchResult,
    SimulationEngine
)
from market_simulation.models.market import Market
from market_simulation.models.geo import PostalCode
from market_simulation.data.schemas import (
    CleanerSchema,
    MarketSearchesSchema,
    SimulationResultsSchema
)

@pytest.fixture
def simulation_config():
    """Basic simulation configuration."""
    return SimulationConfig(
        supply_configuration_iterations=2,
        search_iterations=2,
        cleaner_base_bid_probability=0.14,
        connection_base_probability=0.4,
        distance_decay_factor=0.2
    )

@pytest.fixture
def sample_market():
    """Create a small test market."""
    postal_codes = {
        "10001": PostalCode("10001", "test_market", 40.7505, -73.9965, 100),
        "10016": PostalCode("10016", "test_market", 40.7459, -73.9777, 150),
    }
    return Market("test_market", postal_codes)

@pytest.fixture
def sample_cleaners():
    """Create sample cleaners for testing."""
    return {
        "C1": CleanerSchema(
            contractor_id="C1",
            postal_code="10001",
            latitude=40.7505,
            longitude=-73.9965,
            active=True,
            cleaner_score=0.8,
            service_radius=10.0,
            active_connections=5,
            active_connection_ratio=0.5,
            team_size=2
        ),
        "C2": CleanerSchema(
            contractor_id="C2",
            postal_code="10016",
            latitude=40.7459,
            longitude=-73.9777,
            active=True,
            cleaner_score=0.9,
            service_radius=15.0,
            active_connections=3,
            active_connection_ratio=0.3,
            team_size=3
        )
    }

@pytest.fixture
def sample_market_searches():
    """Create sample market searches data."""
    return MarketSearchesSchema(
        market="test_market",
        projected_searches=5,
        past_period_searches=4
    )

@pytest.fixture
def sample_search_result():
    """Create a sample search result."""
    return SearchResult(
        search_id="test_search_1",
        postal_code="10001",
        latitude=40.7505,
        longitude=-73.9965,
        offers=[
            {
                'cleaner_id': 'C1',
                'distance': 1.0,
                'cleaner_score': 0.8,
                'active': True
            },
            {
                'cleaner_id': 'C2',
                'distance': 2.0,
                'cleaner_score': 0.9,
                'active': True
            }
        ],
        bids=[
            {
                'cleaner_id': 'C1',
                'distance': 1.0,
                'cleaner_score': 0.8,
                'active': True,
                'bid': True
            }
        ],
        connections=[
            {
                'cleaner_id': 'C1',
                'distance': 1.0,
                'cleaner_score': 0.8,
                'active': True,
                'bid': True,
                'connected': True
            }
        ]
    )

def test_simulation_config():
    """Test SimulationConfig initialization and defaults."""
    config = SimulationConfig()
    assert config.supply_configuration_iterations == 10
    assert config.search_iterations == 10
    assert 0 < config.cleaner_base_bid_probability < 1
    assert 0 < config.connection_base_probability < 1
    assert config.distance_decay_factor > 0

def test_search_result_initialization():
    """Test SearchResult initialization."""
    result = SearchResult(
        search_id="test_1",
        postal_code="10001",
        latitude=40.7505,
        longitude=-73.9965
    )
    assert result.search_id == "test_1"
    assert result.postal_code == "10001"
    assert result.offers is None
    assert result.bids is None
    assert result.connections is None

def test_calculate_bid_probability(simulation_config, sample_cleaners):
    """Test bid probability calculation."""
    engine = SimulationEngine(simulation_config)
    cleaner = sample_cleaners["C1"]
    
    # Test probability decreases with distance
    prob_near = engine.calculate_bid_probability(cleaner, distance=1.0)
    prob_far = engine.calculate_bid_probability(cleaner, distance=10.0)
    assert prob_near > prob_far
    
    # Test probability is affected by cleaner score
    high_score_cleaner = sample_cleaners["C2"]
    prob_high = engine.calculate_bid_probability(high_score_cleaner, distance=1.0)
    assert prob_high > prob_near

def test_simulate_search(simulation_config, sample_market, sample_cleaners):
    """Test single search simulation."""
    engine = SimulationEngine(simulation_config)
    sample_market.initialize_cleaners(sample_cleaners)
    
    np.random.seed(42)  # For reproducibility
    result = engine.simulate_search("test_1", sample_market)
    
    assert result.search_id == "test_1"
    assert result.postal_code in ["10001", "10016"]
    assert len(result.offers) > 0
    assert all(isinstance(o["distance"], float) for o in result.offers)
    assert all(isinstance(o["cleaner_score"], float) for o in result.offers)

def test_calculate_metrics(simulation_config, sample_search_result):
    """Test metrics calculation from search results."""
    engine = SimulationEngine(simulation_config)
    metrics = engine._calculate_metrics(
        "test_market", 
        [sample_search_result] * 3  # Use multiple copies for testing
    )
    
    assert isinstance(metrics, SimulationResultsSchema)
    assert metrics.market == "test_market"
    assert metrics.searches == 3
    assert metrics.total_bids == 3  # One bid per search result
    assert metrics.total_connections == 3  # One connection per search result
    assert metrics.avg_offers_per_search == 2.0
    assert metrics.avg_bids_per_search == 1.0
    assert metrics.avg_connections_per_search == 1.0
    assert 0 < metrics.avg_cleaner_score_per_search <= 1

def test_calculate_metrics_empty_results(simulation_config):
    """Test metrics calculation with empty results."""
    engine = SimulationEngine(simulation_config)
    with pytest.raises(ValueError):
        engine._calculate_metrics("test_market", [])

def test_full_market_simulation(
    simulation_config,
    sample_market,
    sample_cleaners,
    sample_market_searches
):
    """Test full market simulation flow."""
    engine = SimulationEngine(simulation_config)
    sample_market.initialize_cleaners(sample_cleaners)
    
    np.random.seed(42)  # For reproducibility
    results = engine.run_market_simulation(
        market=sample_market,
        market_searches=sample_market_searches
    )
    
    assert isinstance(results, SimulationResultsSchema)
    assert results.market == "test_market"
    assert results.searches > 0
    assert results.total_bids >= 0
    assert results.avg_offers_per_search > 0
    assert 0 <= results.avg_bids_per_offer <= 1
    assert 0 <= results.avg_cleaner_score_per_search <= 1

def test_simulation_with_additional_cleaners(
    simulation_config,
    sample_market,
    sample_cleaners,
    sample_market_searches
):
    """Test simulation with additional cleaners."""
    engine = SimulationEngine(simulation_config)
    sample_market.initialize_cleaners(sample_cleaners)
    
    additional_cleaner = CleanerSchema(
        contractor_id="C3",
        postal_code="10001",
        latitude=40.7505,
        longitude=-73.9965,
        active=True,
        cleaner_score=0.95,
        service_radius=12.0,
        active_connections=1,
        active_connection_ratio=0.1,
        team_size=4
    )
    
    np.random.seed(42)  # For reproducibility
    results = engine.run_market_simulation(
        market=sample_market,
        market_searches=sample_market_searches,
        additional_cleaners=[additional_cleaner]
    )
    
    assert isinstance(results, SimulationResultsSchema)
    assert results.number_of_cleaners > len(sample_cleaners)