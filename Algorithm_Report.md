# Space Station Cargo Management System: Algorithm Report

This report provides an explanation of the key algorithms implemented in the Space Station Cargo Management System, a comprehensive solution for managing cargo inside a space station environment like the International Space Station (ISS).

## System Architecture

The system is built using a modern tech stack:
- **Backend**: Python with FastAPI
- **Frontend**: React with TypeScript and Material-UI
- **Database**: SQLite
- **Containerization**: Docker

## Key Algorithms

### 1. Placement Algorithm

The placement algorithm is implemented in `AdvancedPlacementService` and is responsible for determining the optimal location for new items entering the space station.

#### Multi-criteria Sorting

Items are sorted based on multiple criteria before placement:
```python
items_data.sort(key=lambda x: (
    -x["priority"],                           # Highest priority first
    -(x["width"] * x["depth"] * x["height"]), # Largest volume first
    x.get("expiryDate", "9999-12-31")        # Soonest expiry first
))
```

#### Two-Pass Placement Strategy

The algorithm uses a two-pass strategy:
1. **First Pass**: Attempts to place items in their preferred zones
2. **Second Pass**: Places remaining items in any available container

#### Container Efficiency Calculation

Containers are sorted by efficiency for each item using a scoring function that considers:
- Available space
- Fit quality (minimizing wasted space)
- Center of mass balance
- Zone preference

#### 3D Space Optimization

The algorithm uses a 3D grid representation of containers and implements bin packing techniques to maximize space utilization while maintaining stability:

- Items are placed to minimize wasted space
- The algorithm considers the center of mass to maintain stability
- Multiple orientations are evaluated to find the optimal fit

#### Rearrangement Logic

When direct placement fails, the system attempts to rearrange existing items:
1. Identifies candidate items for rearrangement
2. Simulates rearrangements to find a valid solution
3. Generates step-by-step instructions for astronauts

### 2. Retrieval Algorithm

The retrieval algorithm in `AdvancedRetrievalService` optimizes the process of finding and accessing items.

#### Multi-factor Retrieval Score

When multiple matching items exist, the algorithm selects the optimal one based on a weighted score:
```python
return 0.5 * steps_score + 0.3 * expiry_score + 0.2 * priority_score
```

This considers:
- Ease of retrieval (fewer steps is better)
- Proximity to expiry (closer to expiry is better)
- Priority (higher priority is better)

#### Physical Constraint Modeling

The algorithm models physical constraints including:
1. **Gravity** - items cannot float
2. **Support** - items must have adequate support
3. **Accessibility** - physical path for removal
4. **Stability** - arrangement must remain stable during retrieval

#### Path Finding

The system uses a modified breadth-first search algorithm to determine the optimal sequence of item movements required to access a target item:

1. Builds a 3D grid representation of the container
2. Identifies items blocking direct access
3. Determines which items can be safely moved
4. Generates a sequence of steps that maintains stability

### 3. Waste Management Algorithm

The `WasteService` implements algorithms for identifying, managing, and returning waste items.

#### Waste Identification

The system automatically identifies waste items based on two criteria:
1. **Expired items**: Items past their expiration date
2. **Depleted items**: Items with zero remaining uses

#### Return Plan Optimization

The return plan algorithm optimizes the loading of waste items into undocking containers:

1. **Weight-based sorting**: Prioritizes heavier items first
2. **Volume and weight constraints**: Ensures container capacity and weight limits are not exceeded
3. **Retrieval path planning**: Generates optimal steps to retrieve waste items

#### Knapsack Problem Approach

The algorithm uses a greedy approach to solve a variant of the knapsack problem, maximizing the total waste volume returned while respecting weight constraints.

### 4. Time Simulation Algorithm

The `SimulationService` implements algorithms for simulating the passage of time in the space station.

#### Time-based State Changes

The simulation algorithm:
1. Advances the system date by the specified number of days
2. Processes daily item usage based on specified patterns
3. Automatically identifies newly expired items
4. Updates item states (marking depleted or expired items as waste)

#### Usage Simulation

The algorithm simulates item usage patterns:
```python
# Decrement remaining uses
if item.remaining_uses > 0:
    item.remaining_uses -= 1
    
    # Check if item is now depleted
    if item.remaining_uses == 0:
        item.is_waste = True
```

## Performance Considerations

The algorithms are designed with space station constraints in mind:

1. **Computational Efficiency**: Algorithms use heuristics and optimizations to minimize computational requirements
2. **Memory Usage**: Data structures are optimized for minimal memory footprint
3. **Real-time Response**: Critical operations like search and retrieval are optimized for quick response

## Conclusion

The Space Station Cargo Management System implements sophisticated algorithms that address the unique challenges of cargo management in a space environment. The system balances multiple competing factors including space utilization, item priority, accessibility, stability, and waste management to provide an efficient and reliable solution for astronauts.