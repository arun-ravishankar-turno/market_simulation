from market_simulation.utils.geo_utils import calculate_haversine_distance

def test_calculate_haversine_distance():
    """Test distance calculation with known points."""
    # Manhattan to Brooklyn Bridge
    distance = calculate_haversine_distance(
        lat1=40.7505,  # Manhattan
        lon1=-73.9965,
        lat2=40.7061,  # Brooklyn Bridge
        lon2=-73.9969
    )
    
    # Distance should be ~4.9 km
    assert 4.8 < distance < 5.0  # Updated expected range based on actual distance
    
    # Test zero distance
    distance_zero = calculate_haversine_distance(
        lat1=40.7505,
        lon1=-73.9965,
        lat2=40.7505,
        lon2=-73.9965
    )
    assert distance_zero == 0.0