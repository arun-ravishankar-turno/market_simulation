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