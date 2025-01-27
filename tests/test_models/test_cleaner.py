"""Tests for the Cleaner class."""

import pytest
import numpy as np
from market_simulation.models.cleaner import Cleaner
from market_simulation.data.schemas import CleanerSchema

# --- Fixtures ---

@pytest.fixture
def valid_cleaner_data():
    """Valid data for creating a cleaner."""
    return {
        'contractor_id': 'test_cleaner_1',
        'latitude': 40.7505,
        'longitude': -73.9965,
        'postal_code': '10001',
        'bidding_active': True,
        'assignment_active': True,
        'cleaner_score': 0.85,
        'service_radius': 10.0,
        'team_size': 3,
        'active_connections': 5,
        'active_connection_ratio': 0.5
    }

@pytest.fixture
def valid_cleaner(valid_cleaner_data):
    """Create a valid cleaner instance."""
    return Cleaner(**valid_cleaner_data)

@pytest.fixture
def valid_schema_data():
    """Valid data for creating a cleaner schema."""
    return {
        'contractor_id': 'test_cleaner_1',
        'latitude': 40.7505,
        'longitude': -73.9965,
        'postal_code': '10001',
        'bidding_active': True,
        'assignment_active': True,
        'cleaner_score': 0.85,
        'service_radius': 10.0,
        'team_size': 3,
        'active_connections': 5,
        'active_connection_ratio': 0.5
    }

# --- Test Initialization and Validation ---

def test_cleaner_initialization(valid_cleaner_data):
    """Test basic cleaner initialization with valid data."""
    cleaner = Cleaner(**valid_cleaner_data)
    for key, value in valid_cleaner_data.items():
        assert getattr(cleaner, key) == value

def test_cleaner_without_postal_code(valid_cleaner_data):
    """Test cleaner initialization without postal code."""
    data = valid_cleaner_data.copy()
    data.pop('postal_code')
    cleaner = Cleaner(**data)
    assert cleaner.postal_code is None

def test_invalid_latitude():
    """Test validation of invalid latitude."""
    with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
        Cleaner(
            contractor_id="test",
            latitude=91.0,
            longitude=0.0,
            cleaner_score=0.5
        )

def test_invalid_longitude():
    """Test validation of invalid longitude."""
    with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
        Cleaner(
            contractor_id="test",
            latitude=0.0,
            longitude=181.0,
            cleaner_score=0.5
        )

def test_invalid_cleaner_score():
    """Test validation of invalid cleaner score."""
    with pytest.raises(ValueError, match="Cleaner score must be between 0 and 1"):
        Cleaner(
            contractor_id="test",
            latitude=0.0,
            longitude=0.0,
            cleaner_score=1.5
        )

def test_invalid_service_radius():
    """Test validation of invalid service radius."""
    with pytest.raises(ValueError, match="Service radius must be positive"):
        Cleaner(
            contractor_id="test",
            latitude=0.0,
            longitude=0.0,
            service_radius=-1.0
        )

def test_invalid_team_size():
    """Test validation of invalid team size."""
    with pytest.raises(ValueError, match="Team size must be at least 1"):
        Cleaner(
            contractor_id="test",
            latitude=0.0,
            longitude=0.0,
            team_size=0
        )

def test_invalid_active_connections():
    """Test validation of invalid active connections."""
    with pytest.raises(ValueError, match="Active connections cannot be negative"):
        Cleaner(
            contractor_id="test",
            latitude=0.0,
            longitude=0.0,
            active_connections=-1
        )

def test_invalid_connection_ratio():
    """Test validation of invalid connection ratio."""
    with pytest.raises(ValueError, match="Active connection ratio must be between 0 and 1"):
        Cleaner(
            contractor_id="test",
            latitude=0.0,
            longitude=0.0,
            active_connection_ratio=1.5
        )

# --- Test Schema Conversion ---

def test_from_schema(valid_schema_data):
    """Test creating cleaner from schema."""
    schema = CleanerSchema(**valid_schema_data)
    cleaner = Cleaner.from_schema(schema)
    
    for key, value in valid_schema_data.items():
        assert getattr(cleaner, key) == value

def test_to_schema(valid_cleaner):
    """Test converting cleaner to schema."""
    schema = valid_cleaner.to_schema()
    assert isinstance(schema, CleanerSchema)
    
    for key in valid_cleaner.__dict__:
        assert getattr(schema, key) == getattr(valid_cleaner, key)

# --- Test Distance Calculations ---

def test_calculate_distance_to(valid_cleaner):
    """Test distance calculation."""
    # Test point ~1km north
    distance = valid_cleaner.calculate_distance_to(
        valid_cleaner.latitude + 0.01,
        valid_cleaner.longitude
    )
    assert 0.8 <= float(distance) <= 1.2  # Allow small margin due to approximation
    
    # Test same point
    distance = valid_cleaner.calculate_distance_to(
        valid_cleaner.latitude,
        valid_cleaner.longitude
    )
    assert distance == 0.0

def test_is_in_range(valid_cleaner):
    """Test range checking."""
    # Test point within range
    in_range = valid_cleaner.is_in_range(
        valid_cleaner.latitude + 0.01,  # ~1km
        valid_cleaner.longitude
    )
    assert bool(in_range) is True
    
    # Test point outside range
    in_range = valid_cleaner.is_in_range(
        valid_cleaner.latitude + 0.2,  # ~20km
        valid_cleaner.longitude
    )
    assert bool(in_range) is False

# --- Test Capacity and Probability Calculations ---

def test_max_connections(valid_cleaner):
    """Test maximum connections calculation."""
    assert valid_cleaner.max_connections == valid_cleaner.team_size * 10

def test_calculate_capacity_factor(valid_cleaner):
    """Test capacity factor calculation."""
    factor = valid_cleaner.calculate_capacity_factor()
    assert 0.1 <= factor <= 1.0
    
    # Test minimum factor
    max_connections = valid_cleaner.max_connections
    valid_cleaner.active_connections = max_connections
    assert valid_cleaner.calculate_capacity_factor() == 0.1

def test_bid_probability_components(valid_cleaner):
    """Test individual components of bid probability."""
    # Test inactive cleaner
    valid_cleaner.bidding_active = False
    assert valid_cleaner.calculate_bid_probability(distance=1.0) == 0.0
    
    # Test distance effect
    valid_cleaner.bidding_active = True
    prob_near = valid_cleaner.calculate_bid_probability(distance=1.0)
    prob_far = valid_cleaner.calculate_bid_probability(distance=10.0)
    assert prob_near > prob_far
    
    # Test cleaner score effect
    original_score = valid_cleaner.cleaner_score
    valid_cleaner.cleaner_score = 0.5
    prob_low_score = valid_cleaner.calculate_bid_probability(distance=1.0)
    valid_cleaner.cleaner_score = 1.0
    prob_high_score = valid_cleaner.calculate_bid_probability(distance=1.0)
    assert prob_high_score > prob_low_score
    valid_cleaner.cleaner_score = original_score

def test_bid_probability_bounds(valid_cleaner):
    """Test that bid probability stays within bounds."""
    # Test very short distance
    prob = valid_cleaner.calculate_bid_probability(
        distance=0.1,
        base_probability=1.0,
        distance_decay_factor=0.1
    )
    assert 0 <= prob <= 1
    
    # Test very long distance
    prob = valid_cleaner.calculate_bid_probability(
        distance=100.0,
        base_probability=1.0,
        distance_decay_factor=0.1
    )
    assert 0 <= prob <= 1

# --- Test State Changes ---

def test_activation_states(valid_cleaner):
    """Test changes in activation states."""
    # Test bidding state
    valid_cleaner.bidding_active = False
    assert valid_cleaner.calculate_bid_probability(distance=1.0) == 0.0
    
    valid_cleaner.bidding_active = True
    assert valid_cleaner.calculate_bid_probability(distance=1.0) > 0.0
    
    # Test assignment state changes
    valid_cleaner.assignment_active = False
    assert not valid_cleaner.assignment_active
    
    valid_cleaner.assignment_active = True
    assert valid_cleaner.assignment_active