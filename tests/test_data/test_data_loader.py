import pytest
import pandas as pd
from pathlib import Path
from market_simulation.data.data_loader import DataLoader
from pydantic import ValidationError

@pytest.fixture
def valid_geo_mapping_data():
    return pd.DataFrame({
        'postal_code': ['12345', '67890'],
        'market': ['market1', 'market2'],
        'latitude': [40.7128, 34.0522],
        'longitude': [-74.0060, -118.2437],
        'str_tam': [100, 200]
    })

@pytest.fixture
def valid_cleaner_data():
    return pd.DataFrame({
        'contractor_id': ['C1', 'C2'],
        'postal_code': ['12345', '67890'],
        'latitude': [40.7128, 34.0522],
        'longitude': [-74.0060, -118.2437],
        'bidding_active': [True, False],
        'assignment_active': [True, False],
        'cleaner_score': [0.8, 0.9],
        'service_radius': [10.0, 15.0],
        'active_connections': [5, 3],
        'active_connection_ratio': [0.5, 0.3],
        'team_size': [2, 3]
    })

def test_data_loader_initialization():
    loader = DataLoader("dummy/path")
    assert loader.data_directory == Path("dummy/path")

def test_geo_mapping_validation_success(valid_geo_mapping_data):
    loader = DataLoader()
    validated_data = loader.load_geo_mapping(valid_geo_mapping_data)
    assert len(validated_data) == 2
    assert validated_data['12345'].str_tam == 100
    assert validated_data['67890'].market == 'market2'

def test_geo_mapping_validation_failure():
    invalid_data = pd.DataFrame({
        'postal_code': ['12345'],
        'market': ['market1'],
        'latitude': [91],  # Invalid latitude
        'longitude': [-74.0060],
        'str_tam': [100]
    })
    loader = DataLoader()
    with pytest.raises(ValidationError):
        loader.load_geo_mapping(invalid_data)

def test_cleaners_validation_success(valid_cleaner_data):
    loader = DataLoader()
    validated_data = loader.load_cleaners(valid_cleaner_data)
    assert len(validated_data) == 2
    assert validated_data['C1'].bidding_active == True
    assert validated_data['C2'].team_size == 3

def test_cleaners_validation_failure():
    invalid_data = pd.DataFrame({
        'contractor_id': ['C1'],
        'postal_code': ['12345'],
        'latitude': [40.7128],
        'longitude': [-74.0060],
        'bidding_active': [True],
        'assignment_active': [True],
        'cleaner_score': [1.5],  # Invalid score > 1
        'service_radius': [10.0],
        'active_connections': [5],
        'active_connection_ratio': [0.5],
        'team_size': [2]
    })
    loader = DataLoader()
    with pytest.raises(ValidationError):
        loader.load_cleaners(invalid_data)

def test_no_data_provided():
    loader = DataLoader()
    with pytest.raises(ValueError):
        loader.load_geo_mapping()
    with pytest.raises(ValueError):
        loader.load_cleaners()

@pytest.fixture
def valid_market_searches_data():
    return pd.DataFrame({
        'market': ['market1', 'market2'],
        'projected_searches': [100, 150],
        'past_period_searches': [90, 140]
    })

@pytest.fixture
def valid_simulation_results_data():
    return pd.DataFrame({
        'market': ['market1'],
        'searches': [100],
        'number_of_cleaners': [50],
        'number_of_active_cleaners': [40],
        'total_str_tam': [1000],
        'total_bids': [200],
        'total_connections': [80],
        'avg_offers_per_search': [5.0],
        'avg_bids_per_search': [2.0],
        'avg_connections_per_search': [0.8],
        'offers_per_search_p25': [3.0],
        'offers_per_search_p50': [5.0],
        'offers_per_search_p75': [7.0],
        'avg_bids_per_offer': [0.4],
        'avg_connections_per_offer': [0.16],
        'avg_connections_per_bid': [0.4],
        'avg_active_cleaner_offers_per_search': [4.0],
        'avg_active_cleaner_bids_per_search': [1.6],
        'avg_distance_offers_per_search': [5.0],
        'avg_distance_bids_per_search': [4.5],
        'avg_distance_connections_per_search': [4.0],
        'distance_offers_p25': [3.0],
        'distance_offers_p50': [5.0],
        'distance_offers_p75': [7.0],
        'avg_cleaner_score_per_search': [0.8],
        'avg_cleaner_score_of_bidders_per_search': [0.85],
        'avg_cleaner_score_of_connection_per_search': [0.9],
        'cleaner_score_p25': [0.7],
        'cleaner_score_p50': [0.8],
        'cleaner_score_p75': [0.9]
    })

def test_market_searches_validation_success(valid_market_searches_data):
    loader = DataLoader()
    validated_data = loader.load_market_searches(valid_market_searches_data)
    assert len(validated_data) == 2
    assert validated_data['market1'].projected_searches == 100
    assert validated_data['market2'].past_period_searches == 140

def test_simulation_results_validation_success(valid_simulation_results_data):
    loader = DataLoader()
    validated_data = loader.load_simulation_results(valid_simulation_results_data)
    assert len(validated_data) == 1
    assert validated_data['market1'].total_bids == 200
    assert validated_data['market1'].avg_cleaner_score_per_search == 0.8