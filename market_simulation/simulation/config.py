from dataclasses import dataclass
from typing import Optional
import numpy as np

@dataclass(frozen=True)
class SimulationConfig:
    """
    Configuration parameters for market simulation.
    
    This class defines and validates all parameters needed to run a market simulation.
    It's immutable (frozen) to prevent accidental modification during simulation.
    
    Core Parameters:
        search_iterations: Number of iterations per search
        supply_configuration_iterations: Number of supply config iterations
        random_seed: Optional seed for reproducibility
        search_radius_km: Radius for search location sampling
    
    Probability Parameters:
        cleaner_base_bid_probability: Base probability of cleaner bidding
        connection_base_probability: Base probability of connection given a bid
        distance_decay_factor: How distance affects bid probability
    
    Capacity Parameters:
        max_connections_per_member: Maximum connections per team member
        min_capacity_factor: Minimum capacity ratio allowed
    
    Execution Parameters:
        parallel_execution: Whether to use parallel processing
        max_workers: Maximum number of parallel workers
    """
    # Core parameters
    search_iterations: int = 10
    supply_configuration_iterations: int = 10
    random_seed: Optional[int] = None
    search_radius_km: float = 10.0
    
    # Probability parameters
    cleaner_base_bid_probability: float = 0.14
    connection_base_probability: float = 0.4
    distance_decay_factor: float = 0.2
    
    # Capacity parameters
    max_connections_per_member: int = 10
    min_capacity_factor: float = 0.1
    
    # Execution parameters
    parallel_execution: bool = False
    max_workers: int = 4
    
    def __post_init__(self):
        """Validate all configuration parameters."""
        self._validate_iterations()
        self._validate_probabilities()
        self._validate_factors()
        self._validate_execution()
        
        # Set random seed if provided
        if self.random_seed is not None:
            np.random.seed(self.random_seed)
    
    def _validate_iterations(self):
        """Validate iteration counts."""
        if not isinstance(self.search_iterations, int):
            raise TypeError("search_iterations must be an integer")
        if not isinstance(self.supply_configuration_iterations, int):
            raise TypeError("supply_configuration_iterations must be an integer")
        
        if self.search_iterations <= 0:
            raise ValueError("search_iterations must be positive")
        if self.supply_configuration_iterations <= 0:
            raise ValueError("supply_configuration_iterations must be positive")
    
    def _validate_probabilities(self):
        """Validate probability parameters."""
        if not isinstance(self.cleaner_base_bid_probability, (int, float)):
            raise TypeError("cleaner_base_bid_probability must be numeric")
        if not isinstance(self.connection_base_probability, (int, float)):
            raise TypeError("connection_base_probability must be numeric")
            
        if not 0 <= self.cleaner_base_bid_probability <= 1:
            raise ValueError("cleaner_base_bid_probability must be between 0 and 1")
        if not 0 <= self.connection_base_probability <= 1:
            raise ValueError("connection_base_probability must be between 0 and 1")
    
    def _validate_factors(self):
        """Validate factor parameters."""
        if not isinstance(self.distance_decay_factor, (int, float)):
            raise TypeError("distance_decay_factor must be numeric")
        if not isinstance(self.min_capacity_factor, (int, float)):
            raise TypeError("min_capacity_factor must be numeric")
            
        if self.distance_decay_factor < 0:
            raise ValueError("distance_decay_factor must be non-negative")
        if not 0 < self.min_capacity_factor <= 1:
            raise ValueError("min_capacity_factor must be between 0 and 1")
            
        if not isinstance(self.max_connections_per_member, int):
            raise TypeError("max_connections_per_member must be an integer")
        if self.max_connections_per_member <= 0:
            raise ValueError("max_connections_per_member must be positive")
    
    def _validate_execution(self):
        """Validate execution parameters."""
        if not isinstance(self.parallel_execution, bool):
            raise TypeError("parallel_execution must be a boolean")
        if not isinstance(self.max_workers, int):
            raise TypeError("max_workers must be an integer")
            
        if self.max_workers <= 0:
            raise ValueError("max_workers must be positive")
    
    @property
    def total_iterations(self) -> int:
        """Calculate total number of simulation iterations."""
        return self.search_iterations * self.supply_configuration_iterations
    
    def asdict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            'search_iterations': self.search_iterations,
            'supply_configuration_iterations': self.supply_configuration_iterations,
            'random_seed': self.random_seed,
            'cleaner_base_bid_probability': self.cleaner_base_bid_probability,
            'connection_base_probability': self.connection_base_probability,
            'distance_decay_factor': self.distance_decay_factor,
            'max_connections_per_member': self.max_connections_per_member,
            'min_capacity_factor': self.min_capacity_factor,
            'parallel_execution': self.parallel_execution,
            'max_workers': self.max_workers
        }
        
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'SimulationConfig':
        """Create configuration from dictionary."""
        return cls(**config_dict)