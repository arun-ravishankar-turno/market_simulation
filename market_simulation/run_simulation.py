import pandas as pd
from pathlib import Path
from typing import Dict, List
from market_simulation.models.market import Market
from market_simulation.models.cleaner import Cleaner
from market_simulation.models.geo import PostalCode
from market_simulation.simulation.config import SimulationConfig
from market_simulation.simulation.runner import SimulationRunner

def load_postal_codes(filepath: str) -> Dict[str, PostalCode]:
    """Load postal codes from CSV."""
    df = pd.read_csv(filepath)
    postal_codes = {}
    
    for _, row in df.iterrows():
        # Ensure postal code is string and padded with zeros if needed
        postal_code = str(row['postal_code']).zfill(5)
        postal_codes[postal_code] = PostalCode(
            postal_code=postal_code,
            market=row['market'],
            latitude=row['latitude'],
            longitude=row['longitude'],
            str_tam=int(row['str_tam'])  # Ensure TAM is integer
        )
    
    return postal_codes

def load_cleaners(filepath: str) -> List[Cleaner]:
    """Load cleaners from CSV."""
    df = pd.read_csv(filepath)
    cleaners = []
    
    for _, row in df.iterrows():
        # Ensure postal code is string and padded with zeros if needed
        postal_code = str(row['postal_code']).zfill(5)
        
        # Convert string boolean values if necessary
        bidding_active = row['bidding_active']
        if isinstance(bidding_active, str):
            bidding_active = bidding_active.lower() == 'true'
            
        assignment_active = row['assignment_active']
        if isinstance(assignment_active, str):
            assignment_active = assignment_active.lower() == 'true'
        
        cleaners.append(Cleaner(
            contractor_id=str(row['contractor_id']),
            latitude=float(row['latitude']),
            longitude=float(row['longitude']),
            postal_code=postal_code,
            bidding_active=bidding_active,
            assignment_active=assignment_active,
            cleaner_score=float(row['cleaner_score']),
            service_radius=float(row['service_radius']),
            team_size=int(row['team_size']),
            active_connections=int(row['active_connections'])
        ))
    
    return cleaners

def validate_data(postal_codes: Dict[str, PostalCode], cleaners: List[Cleaner]) -> None:
    """Validate that cleaner postal codes exist in postal_codes data."""
    postal_code_set = set(postal_codes.keys())
    for cleaner in cleaners:
        if cleaner.postal_code not in postal_code_set:
            raise ValueError(
                f"Cleaner {cleaner.contractor_id} has postal code {cleaner.postal_code} "
                f"which is not in the postal codes data. Available postal codes: "
                f"{sorted(postal_code_set)}"
            )

def main():
    # Create output directory
    output_dir = Path('simulation_results')
    output_dir.mkdir(exist_ok=True)
    
    print("Loading data...")
    
    # Load data
    postal_codes = load_postal_codes('data/sample_data/postal_codes.csv')
    print(f"Loaded {len(postal_codes)} postal codes")
    
    cleaners = load_cleaners('data/sample_data/cleaners.csv')
    print(f"Loaded {len(cleaners)} cleaners")
    
    # Validate data
    validate_data(postal_codes, cleaners)
    print("Data validation successful")
    
    # Configure simulation
    config = SimulationConfig(
        search_iterations=100,
        supply_configuration_iterations=1,
        random_seed=42,
        cleaner_base_bid_probability=0.14,
        connection_base_probability=0.4,
        distance_decay_factor=0.2,
        search_radius_km=10.0
    )
    
    # Initialize runner
    runner = SimulationRunner(
        config=config,
        output_dir=output_dir
    )
    
    print("\nSetting up market...")
    # Run postal code market simulation
    postal_market = runner.setup_postal_code_market(
        market_id="manhattan",
        postal_codes=postal_codes,
        cleaners=cleaners
    )
    
    print("\nRunning simulation...")
    metrics, stats, visualizations = runner.run_complete_simulation(
        postal_market,
        save_results=True
    )
    
    # Print summary statistics
    print("\nSummary Statistics:")
    print("-" * 50)
    for metric, value in stats.items():
        print(f"{metric}: {value:.3f}")
    
    print(f"\nResults saved to: {output_dir}")

if __name__ == "__main__":
    main()