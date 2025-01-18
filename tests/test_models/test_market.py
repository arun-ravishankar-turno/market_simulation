import pytest
import numpy as np
from market_simulation.models.market import Market
from market_simulation.models.geo import PostalCode
from market_simulation.data.schemas import CleanerSchema

@pytest.fixture
def sample_market():
    # Using closer coordinates in Manhattan
    postal_codes = {
        "10001": PostalCode("10001", "test_market", 40.7505, -73.9965, 100),  # Manhattan
        "10016": PostalCode("10016", "test_market", 40.7459, -73.9777, 150),  # 2km away
    }
    return Market("test_market", postal_codes)

@pytest.fixture
def sample_cleaners():
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

def test_market_initialization(sample_market):
    assert sample_market.market_id == "test_market"
    assert len(sample_market.postal_codes) == 2
    assert sample_market.total_str_tam == 250

def test_initialize_cleaners(sample_market, sample_cleaners):
    sample_market.initialize_cleaners(sample_cleaners)
    assert len(sample_market.cleaners) == 2
    assert "C1" in sample_market.cleaners

def test_get_postal_code_neighbors(sample_market):
    # The postal codes are about 2km apart, so using 3km threshold
    neighbors = sample_market.get_postal_code_neighbors("10001", 3.0)
    assert len(neighbors) == 1
    assert neighbors[0].postal_code == "10016"

def test_get_cleaners_in_range(sample_market, sample_cleaners):
    sample_market.initialize_cleaners(sample_cleaners)
    # Using coordinates from first postal code and 3km range
    cleaners = sample_market.get_cleaners_in_range(40.7505, -73.9965, 3.0)
    assert len(cleaners) == 2

def test_sample_location_by_tam(sample_market):
    np.random.seed(42)  # For reproducibility
    lat, lon, pc = sample_market.sample_location_by_tam()
    
    # Check if sampled location is reasonably close to one of the postal codes
    assert 40.7 < lat < 40.8
    assert -74.0 < lon < -73.9
    assert pc in ["10001", "10016"]

def test_get_cleaners_without_initialization(sample_market):
    with pytest.raises(ValueError):
        sample_market.get_cleaners_in_range(40.7505, -73.9965, 3.0)

def test_invalid_postal_code_neighbors(sample_market):
    with pytest.raises(ValueError):
        sample_market.get_postal_code_neighbors("99999", 3.0)