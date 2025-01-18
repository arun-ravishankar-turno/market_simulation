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
        'active': [True, False],
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
    assert validated_data['C1'].active == True
    assert validated_data['C2'].team_size == 3

def test_cleaners_validation_failure():
    invalid_data = pd.DataFrame({
        'contractor_id': ['C1'],
        'postal_code': ['12345'],
        'latitude': [40.7128],
        'longitude': [-74.0060],
        'active': [True],
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