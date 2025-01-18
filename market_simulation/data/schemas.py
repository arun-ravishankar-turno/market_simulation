from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import pandas as pd

class GeoMappingSchema(BaseModel):
    """Schema for validating postal code geographic data.
    
    Attributes:
        postal_code (str): Unique identifier for the postal code area
        market (str): Market identifier that contains this postal code
        latitude (float): Latitude of postal code centroid
        longitude (float): Longitude of postal code centroid
        str_tam (int): Short term rental total addressable market count
    """
    postal_code: str = Field(..., description="Unique postal code identifier")
    market: str = Field(..., description="Market identifier")
    latitude: float = Field(..., ge=-90, le=90, description="Postal code centroid latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Postal code centroid longitude")
    str_tam: int = Field(..., ge=0, description="Short term rental total addressable market")

    class Config:
        frozen = True

class CleanerSchema(BaseModel):
    """Schema for validating cleaner data.
    
    Attributes:
        contractor_id (str): Unique identifier for the cleaner
        postal_code (str): Postal code where cleaner is based
        latitude (float): Latitude of cleaner location
        longitude (float): Longitude of cleaner location
        active (bool): Whether the cleaner is currently active
        cleaner_score (float): Score between 0 and 1 indicating cleaner quality
        service_radius (float): Maximum service radius in kilometers
        active_connections (int): Number of current active connections
        active_connection_ratio (float): Ratio of active to total possible connections
        team_size (int): Number of team members
    """
    contractor_id: str = Field(..., description="Unique cleaner identifier")
    postal_code: str = Field(..., description="Postal code location")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    active: bool = Field(..., description="Active status")
    cleaner_score: float = Field(..., ge=0, le=1)
    service_radius: float = Field(..., gt=0)
    active_connections: int = Field(..., ge=0)
    active_connection_ratio: float = Field(..., ge=0, le=1)
    team_size: int = Field(..., gt=0)

    class Config:
        frozen = True

class MarketSearchesSchema(BaseModel):
    """Schema for market search volume data.
    
    Attributes:
        market (str): Market identifier
        projected_searches (int): Expected number of searches for next period
        past_period_searches (int): Actual number of searches from last period
    """
    market: str = Field(..., description="Market identifier")
    projected_searches: int = Field(..., ge=0, description="Projected number of searches")
    past_period_searches: int = Field(..., ge=0, description="Past period actual searches")

    class Config:
        frozen = True

class SimulationResultsSchema(BaseModel):
    """Schema for simulation results and metrics.
    
    Contains both aggregate metrics and their distributions for comparing
    simulation outputs with historical data.
    """
    # Market identifiers
    market: str = Field(..., description="Market identifier")
    searches: int = Field(..., ge=0)
    number_of_cleaners: int = Field(..., ge=0)
    number_of_active_cleaners: int = Field(..., ge=0)
    total_str_tam: int = Field(..., ge=0)
    
    # Aggregate metrics
    total_bids: int = Field(..., ge=0)
    total_connections: int = Field(..., ge=0)
    
    # Average per-search metrics
    avg_offers_per_search: float = Field(..., ge=0.0)
    avg_bids_per_search: float = Field(..., ge=0.0)
    avg_connections_per_search: float = Field(..., ge=0.0)
    
    # Percentiles for offers per search
    offers_per_search_p25: float = Field(..., ge=0.0)
    offers_per_search_p50: float = Field(..., ge=0.0)
    offers_per_search_p75: float = Field(..., ge=0.0)
    
    # Conversion metrics
    avg_bids_per_offer: float = Field(..., ge=0.0)
    avg_connections_per_offer: float = Field(..., ge=0.0)
    avg_connections_per_bid: float = Field(..., ge=0.0)
    
    # Active cleaner metrics
    avg_active_cleaner_offers_per_search: float = Field(..., ge=0.0)
    avg_active_cleaner_bids_per_search: float = Field(..., ge=0.0)
    
    # Distance metrics (in km)
    avg_distance_offers_per_search: float = Field(..., ge=0.0)
    avg_distance_bids_per_search: float = Field(..., ge=0.0)
    avg_distance_connections_per_search: float = Field(..., ge=0.0)
    
    # Distance percentiles
    distance_offers_p25: float = Field(..., ge=0.0)
    distance_offers_p50: float = Field(..., ge=0.0)
    distance_offers_p75: float = Field(..., ge=0.0)
    
    # Cleaner score metrics (0 to 1)
    avg_cleaner_score_per_search: float = Field(..., ge=0.0, le=1.0)
    avg_cleaner_score_of_bidders_per_search: float = Field(..., ge=0.0, le=1.0)
    avg_cleaner_score_of_connection_per_search: float = Field(..., ge=0.0, le=1.0)
    
    # Cleaner score percentiles
    cleaner_score_p25: float = Field(..., ge=0.0, le=1.0)
    cleaner_score_p50: float = Field(..., ge=0.0, le=1.0)
    cleaner_score_p75: float = Field(..., ge=0.0, le=1.0)

    class Config:
        frozen = True