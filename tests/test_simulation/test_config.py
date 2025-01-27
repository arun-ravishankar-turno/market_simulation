import pytest
import numpy as np
from market_simulation.simulation.config import SimulationConfig

# --- Test Default Configuration ---

def test_default_config():
    """Test default configuration values."""
    config = SimulationConfig()
    
    # Test core parameters
    assert config.search_iterations == 10
    assert config.supply_configuration_iterations == 10
    assert config.random_seed is None
    assert config.search_radius_km == 10.0
    
    # Test probability parameters
    assert config.cleaner_base_bid_probability == 0.14
    assert config.connection_base_probability == 0.4
    assert config.distance_decay_factor == 0.2
    
    # Test capacity parameters
    assert config.max_connections_per_member == 10
    assert config.min_capacity_factor == 0.1
    
    # Test execution parameters
    assert config.parallel_execution is False
    assert config.max_workers == 4

# --- Test Parameter Validation ---

def test_iteration_validation():
    """Test validation of iteration parameters."""
    # Test invalid types
    with pytest.raises(TypeError):
        SimulationConfig(search_iterations=1.5)
    with pytest.raises(TypeError):
        SimulationConfig(supply_configuration_iterations="10")
    
    # Test invalid values
    with pytest.raises(ValueError):
        SimulationConfig(search_iterations=0)
    with pytest.raises(ValueError):
        SimulationConfig(supply_configuration_iterations=-1)

def test_probability_validation():
    """Test validation of probability parameters."""
    # Test invalid types
    with pytest.raises(TypeError):
        SimulationConfig(cleaner_base_bid_probability="0.5")
    with pytest.raises(TypeError):
        SimulationConfig(connection_base_probability="0.5")
    
    # Test invalid values
    with pytest.raises(ValueError):
        SimulationConfig(cleaner_base_bid_probability=-0.1)
    with pytest.raises(ValueError):
        SimulationConfig(cleaner_base_bid_probability=1.1)
    with pytest.raises(ValueError):
        SimulationConfig(connection_base_probability=-0.1)
    with pytest.raises(ValueError):
        SimulationConfig(connection_base_probability=1.1)

def test_factor_validation():
    """Test validation of factor parameters."""
    # Test invalid types
    with pytest.raises(TypeError):
        SimulationConfig(distance_decay_factor="0.2")
    with pytest.raises(TypeError):
        SimulationConfig(min_capacity_factor="0.1")
    with pytest.raises(TypeError):
        SimulationConfig(max_connections_per_member=10.5)
    
    # Test invalid values
    with pytest.raises(ValueError):
        SimulationConfig(distance_decay_factor=-0.1)
    with pytest.raises(ValueError):
        SimulationConfig(min_capacity_factor=0)
    with pytest.raises(ValueError):
        SimulationConfig(min_capacity_factor=1.1)
    with pytest.raises(ValueError):
        SimulationConfig(max_connections_per_member=0)

def test_execution_validation():
    """Test validation of execution parameters."""
    # Test invalid types
    with pytest.raises(TypeError):
        SimulationConfig(parallel_execution="true")
    with pytest.raises(TypeError):
        SimulationConfig(max_workers=4.5)
    
    # Test invalid values
    with pytest.raises(ValueError):
        SimulationConfig(max_workers=0)
    with pytest.raises(ValueError):
        SimulationConfig(max_workers=-1)

# --- Test Random Seed ---

def test_random_seed():
    """Test random seed functionality."""
    config1 = SimulationConfig(random_seed=42)
    val1 = np.random.rand()
    
    config2 = SimulationConfig(random_seed=42)
    val2 = np.random.rand()
    
    assert val1 == val2

# --- Test Properties ---

def test_total_iterations():
    """Test total iterations calculation."""
    config = SimulationConfig(
        search_iterations=5,
        supply_configuration_iterations=4
    )
    assert config.total_iterations == 20

# --- Test Serialization ---

def test_config_serialization():
    """Test configuration serialization."""
    original_config = SimulationConfig(
        search_iterations=5,
        supply_configuration_iterations=4,
        random_seed=42,
        cleaner_base_bid_probability=0.2,
        parallel_execution=True
    )
    
    # Convert to dict
    config_dict = original_config.asdict()
    
    # Create new config from dict
    new_config = SimulationConfig.from_dict(config_dict)
    
    # Compare all attributes
    assert new_config.search_iterations == original_config.search_iterations
    assert new_config.supply_configuration_iterations == original_config.supply_configuration_iterations
    assert new_config.random_seed == original_config.random_seed
    assert new_config.cleaner_base_bid_probability == original_config.cleaner_base_bid_probability
    assert new_config.parallel_execution == original_config.parallel_execution

# --- Test Immutability ---

def test_config_immutability():
    """Test that configuration is immutable."""
    config = SimulationConfig()
    
    with pytest.raises(Exception):  # dataclasses.FrozenInstanceError
        config.search_iterations = 20