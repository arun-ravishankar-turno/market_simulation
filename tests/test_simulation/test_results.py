"""Tests for the simulation results classes."""

import pytest
import numpy as np
from market_simulation.simulation.results import (
    Offer, 
    Bid, 
    Connection,
    SearchResult
)

# --- Fixtures ---

@pytest.fixture
def valid_offer():
    """Create valid offer data."""
    return Offer(
        contractor_id="C1",
        distance=1.0,
        cleaner_score=0.8,
        active=True,
        team_size=2,
        active_connections=5
    )

@pytest.fixture
def valid_bid(valid_offer):
    """Create valid bid data."""
    return Bid(
        contractor_id=valid_offer.contractor_id,
        distance=valid_offer.distance,
        cleaner_score=valid_offer.cleaner_score,
        active=valid_offer.active,
        team_size=valid_offer.team_size,
        active_connections=valid_offer.active_connections,
        bid_amount=100.0,
        bid_time=1.5
    )

@pytest.fixture
def valid_connection(valid_bid):
    """Create valid connection data."""
    return Connection(
        contractor_id=valid_bid.contractor_id,
        distance=valid_bid.distance,
        cleaner_score=valid_bid.cleaner_score,
        active=valid_bid.active,
        team_size=valid_bid.team_size,
        active_connections=valid_bid.active_connections,
        bid_amount=valid_bid.bid_amount,
        bid_time=valid_bid.bid_time,
        connection_time=2.5
    )

@pytest.fixture
def sample_search_result(valid_offer, valid_bid, valid_connection):
    """Create sample search result with various outcomes."""
    return SearchResult(
        search_id="test_1",
        latitude=40.7505,
        longitude=-73.9965,
        postal_code="10001",
        offers=[
            valid_offer,
            Offer(  # Additional offer
                contractor_id="C2",
                distance=2.0,
                cleaner_score=0.9,
                active=True,
                team_size=3,
                active_connections=3
            )
        ],
        bids=[valid_bid],
        connections=[valid_connection]
    )

# --- Test Offer Class ---

def test_valid_offer(valid_offer):
    """Test valid offer initialization."""
    assert valid_offer.contractor_id == "C1"
    assert valid_offer.distance == 1.0
    assert valid_offer.cleaner_score == 0.8
    assert valid_offer.active is True
    assert valid_offer.team_size == 2
    assert valid_offer.active_connections == 5

def test_invalid_offer():
    """Test offer validation."""
    # Test invalid distance
    with pytest.raises(ValueError, match="Distance must be a non-negative number"):
        Offer(
            contractor_id="C1",
            distance=-1.0,
            cleaner_score=0.8,
            active=True,
            team_size=2,
            active_connections=5
        )
    
    # Test invalid cleaner score
    with pytest.raises(ValueError, match="Cleaner score must be between 0 and 1"):
        Offer(
            contractor_id="C1",
            distance=1.0,
            cleaner_score=1.5,
            active=True,
            team_size=2,
            active_connections=5
        )
    
    # Test invalid team size
    with pytest.raises(ValueError, match="Team size must be a positive integer"):
        Offer(
            contractor_id="C1",
            distance=1.0,
            cleaner_score=0.8,
            active=True,
            team_size=0,
            active_connections=5
        )
    
    # Test invalid active connections
    with pytest.raises(ValueError, match="Active connections must be a non-negative integer"):
        Offer(
            contractor_id="C1",
            distance=1.0,
            cleaner_score=0.8,
            active=True,
            team_size=2,
            active_connections=-1
        )

# --- Test Bid Class ---

def test_valid_bid(valid_bid):
    """Test valid bid initialization."""
    assert valid_bid.bid_amount == 100.0
    assert valid_bid.bid_time == 1.5
    # Test inheritance from Offer
    assert valid_bid.contractor_id == "C1"
    assert valid_bid.distance == 1.0

def test_optional_bid_fields():
    """Test bid initialization with optional fields."""
    bid = Bid(
        contractor_id="C1",
        distance=1.0,
        cleaner_score=0.8,
        active=True,
        team_size=2,
        active_connections=5
    )
    assert bid.bid_amount is None
    assert bid.bid_time is None

def test_invalid_bid():
    """Test bid validation."""
    # Test invalid bid amount
    with pytest.raises(ValueError, match="Bid amount must be positive"):
        Bid(
            contractor_id="C1",
            distance=1.0,
            cleaner_score=0.8,
            active=True,
            team_size=2,
            active_connections=5,
            bid_amount=-100.0
        )
    
    # Test invalid bid time
    with pytest.raises(ValueError, match="Bid time must be non-negative"):
        Bid(
            contractor_id="C1",
            distance=1.0,
            cleaner_score=0.8,
            active=True,
            team_size=2,
            active_connections=5,
            bid_time=-1.5
        )

# --- Test Connection Class ---

def test_valid_connection(valid_connection):
    """Test valid connection initialization."""
    assert valid_connection.connection_time == 2.5
    # Test inheritance from Bid
    assert valid_connection.bid_amount == 100.0
    assert valid_connection.bid_time == 1.5
    # Test inheritance from Offer
    assert valid_connection.contractor_id == "C1"
    assert valid_connection.distance == 1.0

def test_invalid_connection():
    """Test connection validation."""
    # Test connection time before bid time
    with pytest.raises(ValueError, match="Connection time cannot be before bid time"):
        Connection(
            contractor_id="C1",
            distance=1.0,
            cleaner_score=0.8,
            active=True,
            team_size=2,
            active_connections=5,
            bid_time=2.0,
            connection_time=1.0
        )
    
    # Test connection time without bid time
    with pytest.raises(ValueError, match="Connection must have bid time"):
        Connection(
            contractor_id="C1",
            distance=1.0,
            cleaner_score=0.8,
            active=True,
            team_size=2,
            active_connections=5,
            connection_time=1.0
        )

# --- Test SearchResult Class ---

def test_search_result_initialization(sample_search_result):
    """Test search result initialization."""
    assert sample_search_result.search_id == "test_1"
    assert sample_search_result.postal_code == "10001"
    assert len(sample_search_result.offers) == 2
    assert len(sample_search_result.bids) == 1
    assert len(sample_search_result.connections) == 1

def test_search_result_validation():
    """Test search result validation."""
    # Test invalid latitude
    with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
        SearchResult(
            search_id="test_1",
            latitude=91.0,
            longitude=0.0
        )
    
    # Test invalid longitude
    with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
        SearchResult(
            search_id="test_1",
            latitude=0.0,
            longitude=181.0
        )

def test_search_result_properties(sample_search_result):
    """Test search result property calculations."""
    assert sample_search_result.num_offers == 2
    assert sample_search_result.num_bids == 1
    assert sample_search_result.num_connections == 1

def test_unique_cleaners(sample_search_result):
    """Test unique cleaner calculations."""
    unique_cleaners = sample_search_result.get_unique_cleaners()
    assert len(unique_cleaners) == 2
    assert "C1" in unique_cleaners
    assert "C2" in unique_cleaners

    active_cleaners = sample_search_result.get_unique_active_cleaners()
    assert len(active_cleaners) == 2

def test_distance_metrics(sample_search_result):
    """Test distance metric calculations."""
    metrics = sample_search_result.calculate_distance_metrics()
    
    assert metrics["distance_min_offer"] == 1.0
    assert metrics["distance_max_offer"] == 2.0
    assert 1.0 <= metrics["distance_avg_offer"] <= 2.0
    assert "distance_avg_bid" in metrics
    assert "distance_avg_connection" in metrics

def test_score_metrics(sample_search_result):
    """Test cleaner score metric calculations."""
    metrics = sample_search_result.calculate_score_metrics()
    
    assert 0.8 <= metrics["score_avg_offer"] <= 0.9
    assert "score_avg_bid" in metrics
    assert metrics["score_avg_bid"] == 0.8
    assert "score_avg_connection" in metrics
    assert metrics["score_avg_connection"] == 0.8

def test_empty_search_result():
    """Test metrics with empty search result."""
    empty_result = SearchResult(
        search_id="empty",
        latitude=0.0,
        longitude=0.0
    )
    
    assert empty_result.num_offers == 0
    assert empty_result.num_bids == 0
    assert empty_result.num_connections == 0
    assert empty_result.calculate_distance_metrics() == {}
    assert empty_result.calculate_score_metrics() == {}

def test_all_metrics(sample_search_result):
    """Test comprehensive metrics calculation."""
    metrics = sample_search_result.get_all_metrics()
    
    # Test basic counts
    assert metrics["num_offers"] == 2
    assert metrics["num_bids"] == 1
    assert metrics["num_connections"] == 1
    
    # Test rates
    assert metrics["bid_rate"] == 0.5  # 1 bid / 2 offers
    assert metrics["offer_to_connection_rate"] == 0.5  # 1 connection / 2 offers
    assert metrics["acceptance_rate"] == 1.0  # 1 connection / 1 bid
    
    # Test existence of metric categories
    assert any(key.startswith("distance_") for key in metrics)
    assert any(key.startswith("score_") for key in metrics)