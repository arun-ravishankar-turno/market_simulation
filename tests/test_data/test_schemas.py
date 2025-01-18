import pytest
from pydantic import ValidationError
from market_simulation.data.schemas import GeoMappingSchema, CleanerSchema

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
        active=True,
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