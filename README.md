# Market Supply-Demand Simulation

A Python-based simulation system for analyzing market dynamics in two-sided marketplaces, with a focus on supply-demand balance and geographic distribution.

## Overview

This project provides tools to simulate and analyze marketplace behavior, particularly focusing on:
- Supply sufficiency analysis
- Geographic coverage patterns
- Cleaner-search matching dynamics
- Market health metrics

The system supports both postal code-based and location-based market definitions, allowing for flexible market analysis across different geographic structures.

## Installation

```bash
# Clone the repository
git clone [repository-url]
cd market_simulation

# Install dependencies
pip install -r requirements.txt
```

## Project Structure

```
market_simulation/
├── models/                 # Core domain models
│   ├── cleaner.py         # Cleaner representation
│   ├── geo.py            # Geographic models
│   └── market.py         # Market definition
├── simulation/            # Simulation components
│   ├── config.py         # Simulation configuration
│   ├── metrics.py        # Metrics calculation
│   ├── results.py        # Results data structures
│   ├── runner.py         # Simulation orchestration
│   └── simulator.py      # Core simulation engine
├── visualization/         # Visualization tools
│   └── visualizer.py     # Results visualization
└── tests/                # Test suite
```

## Usage

### Basic Simulation

1. Prepare your input data files:
   - `postal_codes.csv`: Market geography definition
   - `cleaners.csv`: Cleaner data

2. Run a simulation:

```python
from market_simulation.simulation.config import SimulationConfig
from market_simulation.simulation.runner import SimulationRunner

# Configure simulation
config = SimulationConfig(
    search_iterations=100,
    random_seed=42,
    search_radius_km=10.0
)

# Run simulation
runner = SimulationRunner(config=config)
results = runner.run_complete_simulation(market)
```

### Input Data Formats

#### postal_codes.csv
```csv
postal_code,market,latitude,longitude,str_tam
10001,manhattan,40.7505,-73.9965,250
10002,manhattan,40.7168,-73.9861,300
```

#### cleaners.csv
```csv
contractor_id,latitude,longitude,postal_code,bidding_active,assignment_active,cleaner_score,service_radius,team_size,active_connections
C001,40.7505,-73.9965,10001,true,true,0.92,5.0,3,8
C002,40.7168,-73.9861,10002,true,true,0.85,3.0,2,4
```

### Output Files

The simulation generates several output files in the specified output directory:
- `market_map.html`: Interactive map visualization
- `distance_distributions.png`: Distance analysis plots
- `score_distributions.png`: Score distribution plots
- `market_summary.png`: Key metrics summary
- `search_results.csv`: Detailed simulation results
- `summary_stats.json`: Aggregated statistics

## Market Types

The system supports two types of market definitions:

### Postal Code Based Markets
```python
market = runner.setup_postal_code_market(
    market_id="manhattan",
    postal_codes=postal_codes,
    cleaners=cleaners
)
```

### Location Based Markets
```python
market = runner.setup_location_market(
    market_id="manhattan",
    center_lat=40.7505,
    center_lon=-73.9965,
    radius_km=5.0,
    cleaners=cleaners
)
```

## Configuration Options

Key simulation parameters that can be configured:

```python
config = SimulationConfig(
    search_iterations=100,           # Number of searches to simulate
    supply_configuration_iterations=1,
    random_seed=42,                  # For reproducibility
    cleaner_base_bid_probability=0.14,
    connection_base_probability=0.4,
    distance_decay_factor=0.2,
    search_radius_km=10.0
)
```

## Key Metrics

The simulation tracks several key metrics:
- Connection Rate: Successful connections / total searches
- Coverage Ratio: Areas with cleaners / total areas
- Search Density: Searches per unit area
- Distance Distributions: Spatial patterns of connections
- Score Distributions: Quality metrics of matches

## Visualization

The system provides several visualization tools:
- Interactive maps showing cleaner locations and service areas
- Distance distribution plots
- Score distribution plots
- Market summary visualizations

## Testing

Run the test suite:
```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[Your License Here]

## Contact

[Your Contact Information]