from typing import Dict, List
import pandas as pd
from pathlib import Path
from .schemas import GeoMappingSchema, CleanerSchema

class DataLoader:
    """Handles loading and validation of simulation input data.
    
    This class is responsible for loading data from CSV files or test data
    and ensuring it conforms to the expected schemas before being used
    in the simulation.
    """
    
    def __init__(self, data_directory: str = None):
        """Initialize the DataLoader.
        
        Args:
            data_directory (str, optional): Path to directory containing input CSV files.
                If None, the loader will expect data to be provided directly.
        """
        self.data_directory = Path(data_directory) if data_directory else None
        
    def load_geo_mapping(self, data: pd.DataFrame = None) -> Dict[str, GeoMappingSchema]:
        """Load and validate geographic mapping data.
        
        Args:
            data (pd.DataFrame, optional): DataFrame containing geo mapping data.
                If None, will attempt to load from data_directory/geo_mapping.csv
                
        Returns:
            Dict[str, GeoMappingSchema]: Dictionary of validated geo mapping data,
                keyed by postal code
                
        Raises:
            FileNotFoundError: If no data provided and csv file not found
            ValidationError: If data doesn't match expected schema
        """
        if data is None:
            if self.data_directory is None:
                raise ValueError("Must provide either data or data_directory")
            data = pd.read_csv(self.data_directory / "geo_mapping.csv")
            
        validated_data = {}
        for _, row in data.iterrows():
            validated_data[row['postal_code']] = GeoMappingSchema(**row.to_dict())
            
        return validated_data
    
    def load_cleaners(self, data: pd.DataFrame = None) -> Dict[str, CleanerSchema]:
        """Load and validate cleaner data.
        
        Args:
            data (pd.DataFrame, optional): DataFrame containing cleaner data.
                If None, will attempt to load from data_directory/cleaners.csv
                
        Returns:
            Dict[str, CleanerSchema]: Dictionary of validated cleaner data,
                keyed by contractor_id
                
        Raises:
            FileNotFoundError: If no data provided and csv file not found
            ValidationError: If data doesn't match expected schema
        """
        if data is None:
            if self.data_directory is None:
                raise ValueError("Must provide either data or data_directory")
            data = pd.read_csv(self.data_directory / "cleaners.csv")
            
        validated_data = {}
        for _, row in data.iterrows():
            validated_data[row['contractor_id']] = CleanerSchema(**row.to_dict())
            
        return validated_data