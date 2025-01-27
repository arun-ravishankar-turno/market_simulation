import argparse
from pathlib import Path
import json
from datetime import datetime
import hashlib

from market_simulation.data.data_loader import DataLoader
from market_simulation.models.market import Market
from market_simulation.simulation.config import SimulationConfig
from market_simulation.simulation.runner import SimulationRunner

def generate_simulation_id(config_dict: dict) -> str:
    """Generate unique simulation ID based on configuration."""
    # Create a string of key parameters
    config_str = json.dumps(config_dict, sort_keys=True)
    # Generate hash
    hash_obj = hashlib.md5(config_str.encode())
    # Use first 8 characters of hash
    return hash_obj.hexdigest()[:8]

def create_output_directory(base_dir: Path, simulation_type: str, simulation_id: str) -> Path:
    """Create and return output directory for simulation results."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = base_dir / f"{simulation_type}_{simulation_id}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def save_configuration(output_dir: Path, config_dict: dict) -> None:
    """Save simulation configuration to file."""
    config_path = output_dir / "simulation_config.json"
    with open(config_path, 'w') as f:
        json.dump(config_dict, f, indent=2)

def load_saved_configuration(config_path: Path) -> dict:
    """Load configuration from saved file."""
    with open(config_path) as f:
        return json.load(f)

def run_simulation(simulation_type: str,
                  data_dir: str,
                  **kwargs) -> None:
    """
    Run market simulation with specified configuration.
    
    Args:
        simulation_type: Type of simulation ('postal_code' or 'location')
        data_dir: Directory containing input data
        **kwargs: Additional configuration parameters
    """
    # Set up data directory
    if data_dir is None:
        base_dir = Path(__file__).parent.parent  # Get project root
        data_dir = base_dir / "data" / "sample_data"
    else:
        data_dir = Path(data_dir)
    
    # Load data
    loader = DataLoader(data_dir)
    
    # Create simulation configuration
    sim_config = {
        'type': simulation_type,
        'search_iterations': kwargs.get('search_iterations', 100),
        'supply_configuration_iterations': kwargs.get('supply_iterations', 1),
        'random_seed': kwargs.get('random_seed', 42),
        'cleaner_base_bid_probability': kwargs.get('bid_probability', 0.14),
        'connection_base_probability': kwargs.get('connection_probability', 0.4),
        'distance_decay_factor': kwargs.get('distance_decay', 0.2),
        'search_radius_km': kwargs.get('search_radius', 10.0)
    }
    
    # Add market-specific configuration
    if simulation_type == 'postal_code':
        sim_config.update({
            'market_id': kwargs['market_id'],
            'postal_codes_file': kwargs.get('postal_codes_file', 'postal_codes.csv')
        })
    else:  # location-based
        sim_config.update({
            'market_id': kwargs['market_id'],
            'center_lat': kwargs['center_lat'],
            'center_lon': kwargs['center_lon'],
            'market_radius_km': kwargs['market_radius']
        })
    
    # Generate simulation ID and create output directory
    sim_id = generate_simulation_id(sim_config)
    output_dir = create_output_directory(
        Path(kwargs.get('output_base', 'simulation_results')),
        simulation_type,
        sim_id
    )
    
    # Save configuration
    save_configuration(output_dir, sim_config)
    
    # Set up simulation
    config = SimulationConfig(
        search_iterations=sim_config['search_iterations'],
        supply_configuration_iterations=sim_config['supply_configuration_iterations'],
        random_seed=sim_config['random_seed'],
        cleaner_base_bid_probability=sim_config['cleaner_base_bid_probability'],
        connection_base_probability=sim_config['connection_base_probability'],
        distance_decay_factor=sim_config['distance_decay_factor'],
        search_radius_km=sim_config['search_radius_km']
    )
    
    runner = SimulationRunner(
        config=config,
        output_dir=output_dir
    )
    
    # Load cleaners data
    cleaners_data = loader.load_cleaners()
    
    # Set up market based on type
    if simulation_type == 'postal_code':
        postal_codes_data = loader.load_geo_mapping()
        market = runner.setup_postal_code_market(
            market_id=sim_config['market_id'],
            postal_codes=postal_codes_data,
            cleaners=list(cleaners_data.values())
        )
    else:
        market = runner.setup_location_market(
            market_id=sim_config['market_id'],
            center_lat=sim_config['center_lat'],
            center_lon=sim_config['center_lon'],
            radius_km=sim_config['market_radius_km'],
            cleaners=list(cleaners_data.values())
        )
    
    # Run simulation
    print(f"\nRunning simulation {sim_id} in {output_dir}")
    metrics, stats, visualizations = runner.run_complete_simulation(
        market,
        save_results=True
    )
    
    print("\nSimulation complete. Summary statistics:")
    print("-" * 50)
    for metric, value in stats.items():
        print(f"{metric}: {value:.3f}")
    
    print(f"\nResults saved to: {output_dir}")

def main():
    parser = argparse.ArgumentParser(description='Run market simulation')
    parser.add_argument('--type', choices=['postal_code', 'location'], required=True,
                       help='Type of market simulation')
    parser.add_argument('--data-dir', required=True,
                       help='Directory containing input data files')
    parser.add_argument('--market-id', required=True,
                       help='Identifier for the market')
    
    # Optional parameters
    parser.add_argument('--search-iterations', type=int, default=100,
                       help='Number of search iterations')
    parser.add_argument('--random-seed', type=int, default=42,
                       help='Random seed for reproducibility')
    parser.add_argument('--search-radius', type=float, default=10.0,
                       help='Search radius in kilometers')
    
    # Location-based parameters
    parser.add_argument('--center-lat', type=float,
                       help='Market center latitude (for location-based)')
    parser.add_argument('--center-lon', type=float,
                       help='Market center longitude (for location-based)')
    parser.add_argument('--market-radius', type=float,
                       help='Market radius in kilometers (for location-based)')
    
    args = parser.parse_args()
    
    # Validate arguments based on simulation type
    if args.type == 'location':
        if None in (args.center_lat, args.center_lon, args.market_radius):
            parser.error("Location-based simulation requires --center-lat, "
                       "--center-lon, and --market-radius")
    
    # Run simulation with provided arguments
    run_simulation(
        simulation_type=args.type,
        data_dir=args.data_dir,
        market_id=args.market_id,
        search_iterations=args.search_iterations,
        random_seed=args.random_seed,
        search_radius=args.search_radius,
        center_lat=args.center_lat,
        center_lon=args.center_lon,
        market_radius=args.market_radius
    )

if __name__ == "__main__":
    main()