from typing import Dict, List
import pandas as pd
from pathlib import Path
from .schemas import GeoMappingSchema, CleanerSchema, MarketSearchesSchema, SimulationResultsSchema

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
            data = pd.read_csv(self.data_directory / "postal_codes.csv")
        
        validated_data = {}
        for _, row in data.iterrows():
            # Ensure postal_code is string
            row_dict = row.to_dict()
            row_dict['postal_code'] = str(row_dict['postal_code'])
            
            validated_data[row_dict['postal_code']] = GeoMappingSchema(**row_dict)
        
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
            # Convert row to dictionary and handle type conversions
            row_dict = row.to_dict()
            
            # Ensure postal_code is string
            row_dict['postal_code'] = str(row_dict['postal_code'])
            
            # Convert string boolean values if necessary
            for bool_field in ['bidding_active', 'assignment_active']:
                if isinstance(row_dict.get(bool_field), str):
                    row_dict[bool_field] = row_dict[bool_field].lower() == 'true'
            
            # Calculate active_connection_ratio if not provided
            if 'active_connection_ratio' not in row_dict and 'team_size' in row_dict:
                max_connections = row_dict['team_size'] * 10  # Assuming 10 connections per team member
                row_dict['active_connection_ratio'] = row_dict.get('active_connections', 0) / max_connections
            
            # Create validated cleaner
            validated_data[row_dict['contractor_id']] = CleanerSchema(**row_dict)
        
        return validated_data

    def load_market_searches(self, data: pd.DataFrame = None) -> Dict[str, MarketSearchesSchema]:
        """Load and validate market search data.
        
        Args:
            data (pd.DataFrame, optional): DataFrame containing market search data.
                If None, will attempt to load from data_directory/market_searches.csv
                
        Returns:
            Dict[str, MarketSearchesSchema]: Dictionary of validated market search data,
                keyed by market
                
        Raises:
            FileNotFoundError: If no data provided and csv file not found
            ValidationError: If data doesn't match expected schema
        """
        if data is None:
            if self.data_directory is None:
                raise ValueError("Must provide either data or data_directory")
            data = pd.read_csv(self.data_directory / "market_searches.csv")
            
        validated_data = {}
        for _, row in data.iterrows():
            validated_data[row['market']] = MarketSearchesSchema(**row.to_dict())
            
        return validated_data

    def load_simulation_results(self, data: pd.DataFrame = None) -> Dict[str, SimulationResultsSchema]:
        """Load and validate simulation results data.
        
        Args:
            data (pd.DataFrame, optional): DataFrame containing simulation results.
                If None, will attempt to load from data_directory/simulation_results.csv
                
        Returns:
            Dict[str, SimulationResultsSchema]: Dictionary of validated simulation results,
                keyed by market
                
        Raises:
            FileNotFoundError: If no data provided and csv file not found
            ValidationError: If data doesn't match expected schema
        """
        if data is None:
            if self.data_directory is None:
                raise ValueError("Must provide either data or data_directory")
            data = pd.read_csv(self.data_directory / "simulation_results.csv")
            
        validated_data = {}
        for _, row in data.iterrows():
            validated_data[row['market']] = SimulationResultsSchema(**row.to_dict())
            
        return validated_data