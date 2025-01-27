import pytest
import numpy as np
from market_simulation.models.market import Market
from market_simulation.models.geo import PostalCode
from market_simulation.models.cleaner import Cleaner
from market_simulation.utils.geo_utils import calculate_haversine_distance

# --- Fixtures ---

@pytest.fixture
def postal_codes():
    """Create sample postal codes."""
    return {
        "10001": PostalCode(
            postal_code="10001",
            market="test_market",
            str_tam=100,
            latitude=40.7505,
            longitude=-73.9965
        ),
        "10002": PostalCode(  # ~4km away
            postal_code="10002",
            market="test_market",
            str_tam=150,
            latitude=40.7168,
            longitude=-73.9861
        ),
        "10003": PostalCode(  # ~2km away
            postal_code="10003",
            market="test_market",
            str_tam=200,
            latitude=40.7317,
            longitude=-73.9885
        ),
    }

@pytest.fixture
def sample_cleaner():
    """Create a sample cleaner."""
    return Cleaner(
        contractor_id="C1",
        latitude=40.7505,
        longitude=-73.9965,
        postal_code="10001",
        bidding_active=True,
        assignment_active=True,
        cleaner_score=0.8,
        service_radius=10.0,
        team_size=2,
        active_connections=5,
        active_connection_ratio=0.5
    )

@pytest.fixture
def postal_code_market(postal_codes):
    """Create a postal code-based market."""
    return Market(
        market_id="test_market",
        postal_codes=postal_codes
    )

@pytest.fixture
def location_based_market():
    """Create a location-based market."""
    return Market(
        market_id="test_market",
        center_lat=40.7505,
        center_lon=-73.9965,
        radius_km=5.0
    )

# --- Test Market Initialization ---

def test_postal_code_market_initialization(postal_codes):
    """Test postal code market initialization."""
    market = Market(
        market_id="test_market",
        postal_codes=postal_codes
    )
    assert market.market_id == "test_market"
    assert market.postal_codes == postal_codes
    assert market.cleaners == {}

def test_location_based_market_initialization():
    """Test location-based market initialization."""
    market = Market(
        market_id="test_market",
        center_lat=40.7505,
        center_lon=-73.9965,
        radius_km=5.0
    )
    assert market.market_id == "test_market"
    assert market.center_lat == 40.7505
    assert market.center_lon == -73.9965
    assert market.radius_km == 5.0
    assert market.cleaners == {}

def test_invalid_market_initialization():
    """Test invalid market configurations."""
    # Test missing both types
    with pytest.raises(ValueError):
        Market(market_id="test_market")
    
    # Test mixing types
    with pytest.raises(ValueError):
        Market(
            market_id="test_market",
            postal_codes={"10001": None},
            center_lat=40.7505
        )
    
    # Test invalid coordinates
    with pytest.raises(ValueError):
        Market(
            market_id="test_market",
            center_lat=91.0,
            center_lon=0.0,
            radius_km=5.0
        )
    
    # Test invalid radius
    with pytest.raises(ValueError):
        Market(
            market_id="test_market",
            center_lat=40.7505,
            center_lon=-73.9965,
            radius_km=-1.0
        )

# --- Test Cleaner Management ---

def test_add_cleaner_to_postal_code_market(postal_code_market, sample_cleaner):
    """Test adding cleaner to postal code market."""
    postal_code_market.add_cleaner(sample_cleaner)
    assert sample_cleaner.contractor_id in postal_code_market.cleaners
    
    # Test invalid postal code
    invalid_cleaner = Cleaner(
        contractor_id="C2",
        latitude=40.7505,
        longitude=-73.9965,
        postal_code="invalid",
        bidding_active=True,
        assignment_active=True,
        cleaner_score=0.8,
        service_radius=10.0,
        team_size=2,
        active_connections=5,
        active_connection_ratio=0.5
    )
    with pytest.raises(ValueError):
        postal_code_market.add_cleaner(invalid_cleaner)

def test_add_cleaner_to_location_based_market(location_based_market, sample_cleaner):
    """Test adding cleaner to location-based market."""
    # Test cleaner within radius
    location_based_market.add_cleaner(sample_cleaner)
    assert sample_cleaner.contractor_id in location_based_market.cleaners
    
    # Test cleaner outside radius
    far_cleaner = Cleaner(
        contractor_id="C2",
        latitude=41.0,  # Way outside radius
        longitude=-73.9965,
        postal_code=None,
        bidding_active=True,
        assignment_active=True,
        cleaner_score=0.8,
        service_radius=10.0,
        team_size=2,
        active_connections=5,
        active_connection_ratio=0.5
    )
    with pytest.raises(ValueError):
        location_based_market.add_cleaner(far_cleaner)

# --- Test Location Sampling ---

def test_postal_code_market_location_sampling(postal_code_market):
    """Test location sampling in postal code market."""
    np.random.seed(42)  # For reproducibility
    
    # Test multiple samples
    for _ in range(10):
        lat, lon, postal_code = postal_code_market.sample_location_by_tam()
        assert -90 <= lat <= 90
        assert -180 <= lon <= 180
        assert postal_code in postal_code_market.postal_codes
        
        # Check reasonable distance from postal code center
        pc = postal_code_market.postal_codes[postal_code]
        distance = calculate_haversine_distance(lat, lon, pc.latitude, pc.longitude)
        assert distance < 5  # Should be within 5km of center

def test_location_based_market_sampling(location_based_market):
    """Test location sampling in location-based market."""
    np.random.seed(42)
    
    # Test multiple samples
    for _ in range(10):
        lat, lon, postal_code = location_based_market.sample_location_by_tam()
        assert -90 <= lat <= 90
        assert -180 <= lon <= 180
        assert postal_code is None
        
        # Check within radius
        distance = calculate_haversine_distance(
            lat, lon,
            location_based_market.center_lat,
            location_based_market.center_lon
        )
        assert distance <= location_based_market.radius_km

# --- Test Cleaner Queries ---

def test_get_cleaners_in_range(postal_code_market, sample_cleaner):
    """Test finding cleaners within range."""
    postal_code_market.add_cleaner(sample_cleaner)
    
    # Test valid search
    cleaners = postal_code_market.get_cleaners_in_range(
        lat=sample_cleaner.latitude,
        lon=sample_cleaner.longitude,
        radius_km=1.0
    )
    assert len(cleaners) == 1
    assert cleaners[0] == sample_cleaner
    
    # Test no cleaners in range
    cleaners = postal_code_market.get_cleaners_in_range(
        lat=41.0,  # Far away
        lon=sample_cleaner.longitude,
        radius_km=1.0
    )
    assert len(cleaners) == 0
    
    # Test invalid radius
    with pytest.raises(ValueError):
        postal_code_market.get_cleaners_in_range(
            lat=sample_cleaner.latitude,
            lon=sample_cleaner.longitude,
            radius_km=-1.0
        )

# --- Test Market Properties ---

def test_total_str_tam(postal_code_market):
    """Test TAM calculation."""
    assert postal_code_market.total_str_tam == 450  # 100 + 150 + 200
    
    # Test location-based market
    location_market = Market(
        market_id="test_market",
        center_lat=40.7505,
        center_lon=-73.9965,
        radius_km=5.0
    )
    with pytest.raises(ValueError):
        _ = location_market.total_str_tam