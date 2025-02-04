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

## Quick Start

Run a simulation using sample data:

```bash
# For postal code based market
python run_simulation.py --type postal_code --market-id manhattan

# For location based market
python run_simulation.py --type location \
    --market-id manhattan \
    --center-lat 40.7505 \
    --center-lon -73.9965 \
    --market-radius 5.0
```

## Input Data Structure

The system expects input data in the following directory structure:
```
market_simulation/
├── data/
│   └── sample_data/
│       ├── cleaners.csv
│       └── postal_codes.csv
```

### Data Formats

#### postal_codes.csv
```csv
postal_code,market,latitude,longitude,str_tam,area
10001,manhattan,40.7505,-73.9965,250,2.1
10002,manhattan,40.7168,-73.9861,300,2.3
```

#### cleaners.csv
```csv
contractor_id,latitude,longitude,postal_code,bidding_active,assignment_active,cleaner_score,service_radius,team_size,active_connections
C001,40.7505,-73.9965,10001,true,true,0.92,5.0,3,8
C002,40.7168,-73.9861,10002,true,true,0.85,3.0,2,4
```

## Running Simulations

### Command Line Options

```bash
python run_simulation.py [options]

Required arguments:
  --type {postal_code,location}   Type of market simulation
  --market-id MARKET_ID          Identifier for the market

Optional arguments:
  --data-dir DATA_DIR           Custom data directory (defaults to sample_data)
  --search-iterations N         Number of search iterations (default: 100)
  --random-seed SEED           Random seed for reproducibility (default: 42)
  --search-radius RADIUS       Search radius in kilometers (default: 10.0)

Location-based required arguments:
  --center-lat LAT             Market center latitude
  --center-lon LON             Market center longitude
  --market-radius RADIUS       Market radius in kilometers
```

### Simulation Output

Each simulation creates a unique output directory with format:
```
simulation_results/
└── {type}_{simulation_id}_{timestamp}/
    ├── simulation_config.json    # Complete configuration
    ├── market_map.html          # Interactive visualization
    ├── distance_distributions.png
    ├── score_distributions.png
    ├── market_summary.png
    ├── search_results.csv       # Detailed results
    └── summary_stats.json       # Aggregated metrics
```

### Configuration File
Each simulation saves its configuration in `simulation_config.json`, containing:
- Simulation parameters
- Market configuration
- Random seeds
- Input data paths

This allows exact reproduction of simulations by loading the saved configuration.

## Key Metrics

The simulation tracks several key metrics:
- Connection Rate: Successful connections / total searches
- Coverage Ratio: Areas with cleaners / total market area
- Search Density: Searches per unit area
- Distance Distributions: Spatial patterns of connections
- Score Distributions: Quality metrics of matches

## Visualization

The system provides several visualization tools:
- Interactive maps showing:
  - Cleaner locations and service areas
  - Search points
  - Connection points
  - Market boundaries
- Distribution plots:
  - Distance distributions
  - Score distributions
  - Market summary metrics

## Development

### Project Structure
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
├── data/                 # Data handling
│   ├── data_loader.py    # Data loading and validation
│   ├── schemas.py        # Data schemas
│   └── sample_data/      # Sample input data
└── visualization/        # Visualization tools
    └── visualizer.py     # Results visualization
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_models/test_market.py

# Run with coverage
pytest --cov=market_simulation
```

## Improvements:
Here are some of the improvements that need to be made.

### Bugs
- get_cleaners_in_range currently obtains the number of cleaners in the range of a market - in reality, for a given point, we want to find the number of cleaners whose service radius allows them to be within the range of this point.

### Documentation
- Show sample outputs in the documentation.
- Once Offer to Bid and Bid to Connection models are ready, show adequate documentation for the same.

### Code Structure/Usability
- Dockerize everything for reproducibility.
- Currently input is for a simulation in a single market - need to incorporate multiple ways of running the simulation - single market (postal_code/location) with inputs of number of searches,  a list of markets, 

### Parallelization
- Allow for parallel markets to run

### Testing

### Simulation
- Add features to cleaners like days since last bid, days since last connection, days since last assignment, Offer to Bid rate for last 10 offers, days since last connection died, something indicating how competitive their local market is, their recent past bid to connection success rate, etc. that will feature in the offer to bid probability. 
- Implement Offer to Bid model.
- Appropriately use capacity and distance decay factors.

### Outputs/Metrics
- 

### Visualization
- Add details to each search point on each plot indicating their stats, ie. how many offer that search had, how many bids they received, number of connections, avg distance to offer/bid/connection, etc.
