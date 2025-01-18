import pytest
import numpy as np
from market_simulation.models.geo import PostalCode
from market_simulation.data.schemas import GeoMappingSchema

@pytest.fixture
def sample_postal_code():
    return PostalCode(
        postal_code="12345",
        market="test_market",
        latitude=40.7128,
        longitude=-74.0060,
        str_tam=100
    )

@pytest.fixture
def sample_postal_codes():
    # Create a list of postal codes around New York City
    return [
        PostalCode("10001", "NYC", 40.7505, -73.9965, 150),  # Manhattan
        PostalCode("11201", "NYC", 40.7052, -73.9931, 120),  # Brooklyn
        PostalCode("10451", "NYC", 40.8195, -73.9269, 80),   # Bronx
        PostalCode("11101", "NYC", 40.7505, -73.9237, 90),   # Queens
        PostalCode("07302", "NYC", 40.7178, -74.0431, 60),   # Jersey City
    ]

def test_create_from_schema():
    """Test creation of PostalCode from GeoMappingSchema."""
    schema = GeoMappingSchema(
        postal_code="12345",
        market="test_market",
        latitude=40.7128,
        longitude=-74.0060,
        str_tam=100
    )
    pc = PostalCode.from_schema(schema)
    assert pc.postal_code == "12345"
    assert pc.market == "test_market"
    assert pc.str_tam == 100

def test_calculate_distance(sample_postal_codes):
    """Test distance calculation between postal codes."""
    manhattan = sample_postal_codes[0]  # 10001
    brooklyn = sample_postal_codes[1]   # 11201
    
    distance = manhattan.calculate_distance(brooklyn)
    
    # Distance between these points should be approximately 5.3 km
    assert 5.0 < distance < 5.5

def test_find_neighbors(sample_postal_codes):
    """Test finding neighboring postal codes within threshold."""
    manhattan = sample_postal_codes[0]
    neighbors = manhattan.find_neighbors(sample_postal_codes, threshold_km=6.0)
    
    # Should include Brooklyn but not Bronx
    neighbor_codes = [pc.postal_code for pc in neighbors]
    assert "11201" in neighbor_codes  # Brooklyn
    assert "10451" not in neighbor_codes  # Bronx

def test_tam_weight(sample_postal_code):
    """Test TAM weight calculation."""
    weight = sample_postal_code.get_tam_weight(total_market_tam=1000)
    assert weight == 0.1  # 100/1000
    
    with pytest.raises(ValueError):
        sample_postal_code.get_tam_weight(0)