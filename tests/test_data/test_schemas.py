import pytest
from pydantic import ValidationError
from market_simulation.data.schemas import GeoMappingSchema, CleanerSchema, MarketSearchesSchema, SimulationResultsSchema

def test_valid_geo_mapping():
    """Test that valid geo mapping data is accepted."""
    geo = GeoMappingSchema(
        postal_code="12345",
        market="test_market",
        latitude=40.7128,
        longitude=-74.0060,
        str_tam=100
    )
    assert geo.postal_code == "12345"
    assert geo.latitude == 40.7128
    assert geo.str_tam == 100

def test_invalid_geo_mapping_latitude():
    """Test that invalid latitude is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        GeoMappingSchema(
            postal_code="12345",
            market="test_market",
            latitude=100,  # Invalid: > 90
            longitude=-74.0060,
            str_tam=100
        )
    assert "latitude" in str(exc_info.value)

def test_invalid_geo_mapping_negative_str_tam():
    """Test that negative STR TAM is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        GeoMappingSchema(
            postal_code="12345",
            market="test_market",
            latitude=40.7128,
            longitude=-74.0060,
            str_tam=-1  # Invalid: negative
        )
    assert "str_tam" in str(exc_info.value)

def test_valid_cleaner():
    """Test that valid cleaner data is accepted."""
    cleaner = CleanerSchema(
        contractor_id="C1",
        postal_code="12345",
        latitude=40.7128,
        longitude=-74.0060,
        bidding_active=True,
        assignment_active=True,
        cleaner_score=0.8,
        service_radius=10.0,
        active_connections=5,
        active_connection_ratio=0.5,
        team_size=2
    )
    assert cleaner.contractor_id == "C1"
    assert cleaner.cleaner_score == 0.8
    assert cleaner.team_size == 2

def test_invalid_cleaner_score():
    """Test that invalid cleaner score is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        CleanerSchema(
            contractor_id="C1",
            postal_code="12345",
            latitude=40.7128,
            longitude=-74.0060,
            active=True,
            cleaner_score=1.5,  # Invalid: > 1
            service_radius=10.0,
            active_connections=5,
            active_connection_ratio=0.5,
            team_size=2
        )
    assert "cleaner_score" in str(exc_info.value)

def test_invalid_service_radius():
    """Test that invalid service radius is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        CleanerSchema(
            contractor_id="C1",
            postal_code="12345",
            latitude=40.7128,
            longitude=-74.0060,
            active=True,
            cleaner_score=0.8,
            service_radius=-1.0,  # Invalid: negative
            active_connections=5,
            active_connection_ratio=0.5,
            team_size=2
        )
    assert "service_radius" in str(exc_info.value)

def test_valid_market_searches():
    """Test that valid market searches data is accepted."""
    market_searches = MarketSearchesSchema(
        market="test_market",
        projected_searches=100,
        past_period_searches=90
    )
    assert market_searches.market == "test_market"
    assert market_searches.projected_searches == 100
    assert market_searches.past_period_searches == 90

def test_invalid_market_searches_negative_values():
    """Test that negative values are rejected in market searches."""
    with pytest.raises(ValidationError) as exc_info:
        MarketSearchesSchema(
            market="test_market",
            projected_searches=-1,  # Invalid: negative
            past_period_searches=90
        )
    assert "projected_searches" in str(exc_info.value)

def test_valid_simulation_results():
    """Test that valid simulation results data is accepted."""
    results = SimulationResultsSchema(
        market="test_market",
        searches=100,
        number_of_cleaners=50,
        number_of_active_cleaners=40,
        total_str_tam=1000,
        total_bids=200,
        total_connections=80,
        avg_offers_per_search=5.0,
        avg_bids_per_search=2.0,
        avg_connections_per_search=0.8,
        offers_per_search_p25=3.0,
        offers_per_search_p50=5.0,
        offers_per_search_p75=7.0,
        avg_bids_per_offer=0.4,
        avg_connections_per_offer=0.16,
        avg_connections_per_bid=0.4,
        avg_active_cleaner_offers_per_search=4.0,
        avg_active_cleaner_bids_per_search=1.6,
        avg_distance_offers_per_search=5.0,
        avg_distance_bids_per_search=4.5,
        avg_distance_connections_per_search=4.0,
        distance_offers_p25=3.0,
        distance_offers_p50=5.0,
        distance_offers_p75=7.0,
        avg_cleaner_score_per_search=0.8,
        avg_cleaner_score_of_bidders_per_search=0.85,
        avg_cleaner_score_of_connection_per_search=0.9,
        cleaner_score_p25=0.7,
        cleaner_score_p50=0.8,
        cleaner_score_p75=0.9
    )
    assert results.market == "test_market"
    assert results.avg_cleaner_score_per_search == 0.8
    assert results.offers_per_search_p50 == 5.0

def test_invalid_simulation_results_score_range():
    """Test that cleaner scores outside [0,1] are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        SimulationResultsSchema(
            market="test_market",
            searches=100,
            number_of_cleaners=50,
            number_of_active_cleaners=40,
            total_str_tam=1000,
            total_bids=200,
            total_connections=80,
            avg_offers_per_search=5.0,
            avg_bids_per_search=2.0,
            avg_connections_per_search=0.8,
            offers_per_search_p25=3.0,
            offers_per_search_p50=5.0,
            offers_per_search_p75=7.0,
            avg_bids_per_offer=0.4,
            avg_connections_per_offer=0.16,
            avg_connections_per_bid=0.4,
            avg_active_cleaner_offers_per_search=4.0,
            avg_active_cleaner_bids_per_search=1.6,
            avg_distance_offers_per_search=5.0,
            avg_distance_bids_per_search=4.5,
            avg_distance_connections_per_search=4.0,
            distance_offers_p25=3.0,
            distance_offers_p50=5.0,
            distance_offers_p75=7.0,
            avg_cleaner_score_per_search=1.5,  # Invalid: > 1
            avg_cleaner_score_of_bidders_per_search=0.85,
            avg_cleaner_score_of_connection_per_search=0.9,
            cleaner_score_p25=0.7,
            cleaner_score_p50=0.8,
            cleaner_score_p75=0.9
        )
    assert "avg_cleaner_score_per_search" in str(exc_info.value)