"""Tests for geographic models."""

import pytest
import numpy as np
from market_simulation.models.geo import GeoLocation, PostalCode
from market_simulation.data.schemas import GeoMappingSchema

@pytest.fixture
def geo_location():
    """Create a basic geographic location."""
    return GeoLocation(latitude=40.7505, longitude=-73.9965)

@pytest.fixture
def postal_code():
    """Create a single postal code."""
    return PostalCode(
        postal_code="10001",
        market="test_market",
        latitude=40.7505,
        longitude=-73.9965,
        str_tam=100
    )

@pytest.fixture
def sample_postal_codes():
    """Create a list of postal codes at known distances."""
    return [
        PostalCode(
            postal_code="10001",
            market="test_market",
            latitude=40.7505,
            longitude=-73.9965,
            str_tam=100
        ),
        PostalCode(  # ~4km away
            postal_code="10002",
            market="test_market",
            latitude=40.7168,
            longitude=-73.9861,
            str_tam=150
        ),
        PostalCode(  # ~2km away
            postal_code="10003",
            market="test_market",
            latitude=40.7317,
            longitude=-73.9885,
            str_tam=200
        ),
        PostalCode(  # ~1km away
            postal_code="10016",
            market="test_market",
            latitude=40.7459,
            longitude=-73.9777,
            str_tam=175
        ),
    ]

def test_geo_location_initialization():
    """Test basic geographic location initialization."""
    loc = GeoLocation(latitude=40.7505, longitude=-73.9965)
    assert loc.latitude == 40.7505
    assert loc.longitude == -73.9965

def test_geo_location_validation():
    """Test geographic location validation."""
    with pytest.raises(ValueError):
        GeoLocation(latitude=91, longitude=0)
    with pytest.raises(ValueError):
        GeoLocation(latitude=0, longitude=181)
    with pytest.raises(TypeError):
        GeoLocation(latitude="invalid", longitude=0)

def test_postal_code_initialization():
    """Test postal code initialization."""
    pc = PostalCode(
        postal_code="10001",
        market="test_market",
        latitude=40.7505,
        longitude=-73.9965,
        str_tam=100
    )
    assert pc.postal_code == "10001"
    assert pc.market == "test_market"
    assert pc.latitude == 40.7505
    assert pc.longitude == -73.9965
    assert pc.str_tam == 100

def test_postal_code_validation():
    """Test postal code validation."""
    # Test invalid coordinates
    with pytest.raises(ValueError):
        PostalCode(
            postal_code="10001",
            market="test",
            latitude=91,
            longitude=0,
            str_tam=100
        )
    
    # Test invalid str_tam
    with pytest.raises(ValueError):
        PostalCode(
            postal_code="10001",
            market="test",
            latitude=40.7505,
            longitude=-73.9965,
            str_tam=-1
        )

def test_calculate_distance(geo_location):
    """Test distance calculation."""
    # Test known distance
    distance = geo_location.calculate_distance(
        geo_location.latitude + 0.01,  # ~1.1km north
        geo_location.longitude
    )
    assert 1.0 <= float(distance) <= 1.2

    # Test zero distance
    distance = geo_location.calculate_distance(
        geo_location.latitude,
        geo_location.longitude
    )
    assert float(distance) == 0.0

def test_sample_point_in_radius(geo_location):
    """Test random point generation within radius."""
    np.random.seed(42)  # For reproducibility
    radius_km = 5.0
    
    # Test multiple points
    for _ in range(10):
        lat, lon = geo_location.sample_point_in_radius(radius_km)
        distance = geo_location.calculate_distance(lat, lon)
        assert float(distance) <= radius_km

    # Test invalid radius
    with pytest.raises(ValueError):
        geo_location.sample_point_in_radius(-1)

def test_postal_code_from_schema():
    """Test creation from schema."""
    schema = GeoMappingSchema(
        postal_code="10001",
        market="test_market",
        latitude=40.7505,
        longitude=-73.9965,
        str_tam=100
    )
    pc = PostalCode.from_schema(schema)
    assert pc.postal_code == schema.postal_code
    assert pc.market == schema.market
    assert pc.latitude == schema.latitude
    assert pc.longitude == schema.longitude
    assert pc.str_tam == schema.str_tam

def test_find_neighbors(postal_code, sample_postal_codes):
    """Test neighbor finding functionality."""
    # Test 2km radius
    neighbors = postal_code.find_neighbors(sample_postal_codes, 2.0)
    neighbor_ids = {pc.postal_code for pc in neighbors}
    assert len(neighbors) == 1  # Should find 10016
    assert "10016" in neighbor_ids

    # Test 5km radius
    neighbors = postal_code.find_neighbors(sample_postal_codes, 5.0)
    assert len(neighbors) == 3  # Should find all except self

    # Test invalid threshold
    with pytest.raises(ValueError):
        postal_code.find_neighbors(sample_postal_codes, -1)

def test_tam_weight(postal_code):
    """Test TAM weight calculation."""
    assert postal_code.get_tam_weight(1000) == 0.1
    
    with pytest.raises(ValueError):
        postal_code.get_tam_weight(0)
    
    with pytest.raises(ValueError):
        postal_code.get_tam_weight(-100)

def test_distance_calculations_consistency(sample_postal_codes):
    """Test that distance calculations are consistent."""
    pc1 = sample_postal_codes[0]
    pc2 = sample_postal_codes[1]
    
    # Distance should be the same regardless of direction
    dist1 = pc1.calculate_distance_to(pc2)
    dist2 = pc2.calculate_distance_to(pc1)
    assert float(dist1) == float(dist2)

def test_postal_code_with_area():
    """Test postal code creation with area."""
    pc = PostalCode(
        postal_code="10001",
        market="manhattan",
        latitude=40.7505,
        longitude=-73.9965,
        str_tam=100,
        area=2.5  # Area in square kilometers
    )
    assert pc.area == 2.5
    assert isinstance(pc.area, float)

def test_postal_code_without_area():
    """Test postal code creation without area."""
    pc = PostalCode(
        postal_code="10001",
        market="manhattan",
        latitude=40.7505,
        longitude=-73.9965,
        str_tam=100
    )
    assert pc.area is None

def test_postal_code_from_schema():
    """Test creating postal code from schema with area."""
    schema = GeoMappingSchema(
        postal_code="10001",
        market="manhattan",
        latitude=40.7505,
        longitude=-73.9965,
        str_tam=100,
        area=2.5
    )
    pc = PostalCode.from_schema(schema)
    assert pc.area == 2.5