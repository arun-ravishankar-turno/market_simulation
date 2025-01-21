from market_simulation.utils.geo_utils import calculate_haversine_distance

def test_calculate_haversine_distance():
    """Test distance calculation with known points."""
    # Manhattan to Brooklyn Bridge (approximately 2.5 km)
    distance = calculate_haversine_distance(
        lat1=40.7505,  # Manhattan
        lon1=-73.9965,
        lat2=40.7061,  # Brooklyn Bridge
        lon2=-73.9969
    )
    assert 2.4 < distance < 2.6
    
    # Test distance is symmetric
    distance_reverse = calculate_haversine_distance(
        lat1=40.7061,
        lon1=-73.9969,
        lat2=40.7505,
        lon2=-73.9965
    )
    assert abs(distance - distance_reverse) < 1e-10

    # Test zero distance for same point
    distance_same = calculate_haversine_distance(
        lat1=40.7505,
        lon1=-73.9965,
        lat2=40.7505,
        lon2=-73.9965
    )
    assert distance_same == 0.0