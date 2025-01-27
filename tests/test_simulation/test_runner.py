import pytest
import tempfile
from pathlib import Path
import numpy as np

from market_simulation.models.market import Market
from market_simulation.models.cleaner import Cleaner
from market_simulation.models.geo import PostalCode
from market_simulation.simulation.config import SimulationConfig
from market_simulation.simulation.runner import SimulationRunner

# --- Fixtures ---

@pytest.fixture
def base_config():
    """Create basic simulation configuration."""
    return SimulationConfig(
        search_iterations=5,
        supply_configuration_iterations=1,
        random_seed=42,
        cleaner_base_bid_probability=0.14,
        connection_base_probability=0.4,
        distance_decay_factor=0.2,
        search_radius_km=10.0
    )

@pytest.fixture
def sample_cleaners():
    """Create a list of test cleaners."""
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
def postal_code_market(sample_cleaners):
    """Create a postal code based market."""
    postal_codes = {
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
    
    market = Market(
        market_id="test_market",
        postal_codes=postal_codes
    )
    
    for cleaner in sample_cleaners:
        market.add_cleaner(cleaner)
    
    return market

@pytest.fixture
def location_market(sample_cleaners):
    """Create a location based market."""
    market = Market(
        market_id="test_market",
        center_lat=40.7505,
        center_lon=-73.9965,
        radius_km=5.0
    )
    
    for cleaner in sample_cleaners:
        market.add_cleaner(cleaner)
    
    return market

# --- Tests ---

def test_run_simulation_postal_code(base_config, postal_code_market):
    """Test running simulation on postal code market."""
    runner = SimulationRunner(config=base_config)
    metrics, stats = runner.run_simulation(postal_code_market)
    
    # Check basic outputs
    assert len(metrics.results) == base_config.search_iterations
    assert isinstance(stats, dict)
    
    # Check critical metrics existence
    assert 'connection_rate' in stats
    assert 'coverage_ratio' in stats
    assert 'search_density' in stats
    
    # Check metric values are reasonable
    assert 0 <= stats['connection_rate'] <= 1
    assert 0 <= stats['coverage_ratio'] <= 1

def test_run_simulation_location(base_config, location_market):
    """Test running simulation on location-based market."""
    runner = SimulationRunner(config=base_config)
    metrics, stats = runner.run_simulation(location_market)
    
    # Check basic outputs
    assert len(metrics.results) == base_config.search_iterations
    assert isinstance(stats, dict)
    
    # Check critical metrics existence
    assert 'connection_rate' in stats
    assert 'coverage_ratio' in stats
    assert 'search_density' in stats
    
    # Check metric values are reasonable
    assert 0 <= stats['connection_rate'] <= 1
    assert 0 <= stats['coverage_ratio'] <= 1

def test_simulation_reproducibility(base_config, postal_code_market):
    """Test that simulations are reproducible with same seed."""
    # Run two simulations with same seed
    runner1 = SimulationRunner(config=base_config)
    metrics1, stats1 = runner1.run_simulation(postal_code_market)
    
    runner2 = SimulationRunner(config=base_config)
    metrics2, stats2 = runner2.run_simulation(postal_code_market)
    
    # Check that results match
    assert len(metrics1.results) == len(metrics2.results)
    assert stats1 == stats2

def test_different_seeds_differ(postal_code_market):
    """Test that different seeds produce different results."""
    config1 = SimulationConfig(
        search_iterations=5,
        random_seed=42,
        search_radius_km=10.0
    )
    
    config2 = SimulationConfig(
        search_iterations=5,
        random_seed=43,
        search_radius_km=10.0
    )
    
    runner1 = SimulationRunner(config=config1)
    metrics1, stats1 = runner1.run_simulation(postal_code_market)
    
    runner2 = SimulationRunner(config=config2)
    metrics2, stats2 = runner2.run_simulation(postal_code_market)
    
    # Results should differ
    assert stats1 != stats2

def test_complete_simulation_outputs(base_config, postal_code_market):
    """Test outputs of complete simulation run."""
    with tempfile.TemporaryDirectory() as tmpdir:
        runner = SimulationRunner(
            config=base_config,
            output_dir=Path(tmpdir)
        )
        
        metrics, stats, viz = runner.run_complete_simulation(
            postal_code_market,
            save_results=True
        )
        
        # Check outputs
        assert len(metrics.results) > 0
        assert isinstance(stats, dict)
        assert isinstance(viz, dict)
        
        # Check visualizations
        assert 'market_map' in viz
        assert 'distance_distributions' in viz
        assert 'score_distributions' in viz
        assert 'market_summary' in viz
        
        # Check saved files
        output_dir = Path(tmpdir)
        assert (output_dir / 'search_results.csv').exists()
        assert (output_dir / 'summary_stats.json').exists()
        assert (output_dir / 'market_map.html').exists()