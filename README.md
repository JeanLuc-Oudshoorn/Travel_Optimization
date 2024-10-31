# Travel Route Optimization Script

## Overview

This Python script implements an algorithm to find the most cost-effective travel route between several cities, given specific constraints and flight options. The goal is to minimize the total cost of a round-trip journey that:

- **Starts and ends in Amsterdam (AMS)**
- **Includes mandatory visits to Bangalore (BLR) and Phuket (HKT)**
- **Includes one optional city: either Bangkok (BKK) or Kuala Lumpur (KL)**

The script evaluates various combinations of one-way and round-trip flights, considering their costs and constraints, to determine the itinerary with the lowest total cost.

## Features

- **Flight Options**: Considers both one-way and round-trip flights between cities with different costs.
- **Mandatory and Optional Cities**: Ensures that the itinerary includes mandatory cities and one optional city as per the requirements.
- **Round-Trip Constraints**:
  - Each round-trip ticket can be purchased only once per route.
  - Both outbound and return legs of a round-trip ticket must be used exactly once.
- **Route Generation**: Generates random routes that start and end at AMS, allowing for multiple visits to the same city to accommodate round-trip tickets.
- **Cost Calculation**: Accurately calculates the total cost, accounting for the usage of round-trip tickets and one-way flights.
- **Optimization**: Runs multiple iterations to explore different route combinations, improving the chances of finding the optimal route.

## How It Works

1. **Data Setup**:
   - Defines cities and flight costs for one-way and round-trip flights.
   - Specifies mandatory and optional cities.

2. **Route Generation**:
   - Generates random routes starting from AMS and ending when AMS is selected again.
   - Allows cities to be visited multiple times to utilize round-trip tickets effectively.

3. **Route Validation**:
   - Ensures each route:
     - Starts and ends at AMS.
     - Includes visits to BLR and HKT.
     - Includes at least one of BKK or KL.

4. **Round-Trip Ticket Evaluation**:
   - Identifies possible round-trip tickets based on the cities visited in the route.
   - Considers all combinations of purchasing available round-trip tickets.
   - Ensures each round-trip ticket is purchased at most once.

5. **Cost Calculation**:
   - Tracks the usage of each leg of purchased round-trip tickets to prevent multiple uses.
   - Calculates the total cost of the route, adding costs of one-way flights and purchased round-trip tickets.
   - Ensures both legs of any purchased round-trip ticket are used exactly once.

6. **Optimization Loop**:
   - Repeats the above steps for a large number of iterations.
   - Keeps track of the route with the lowest total cost found.

## Requirements

- **Python 3.10**
- No external dependencies (uses only standard Python libraries)

## Usage

### Running the Script

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/JeanLuc-Oudshoorn/Travel_Optimization.git
   cd Travel_Optimization
   ``` 

2. **Run the script**:

   ```bash
   python amsterdam_round.py
   ```

### Example Output

   ```rust
   Optimal Route: AMS -> BLR -> HKT -> KL -> BLR -> AMS
   Total Cost: € 870
   Flight Details:
     AMS to BLR via Round-trip leg (no additional cost): €0
     BLR to HKT via One-way flight: €170
     HKT to KL via One-way flight: €40
     KL to BLR via One-way flight: €110
     BLR to AMS via Round-trip leg (no additional cost): €0
   ```

## Customization
**Adjust Iterations**: Modify the iterations variable in the script to increase or decrease the number of iterations for the random search.
**Flight Costs**: Update the flight costs in the script to reflect current prices or different scenarios.
**Cities and Constraints**: Add or remove cities and adjust mandatory or optional city requirements as needed.

## Limitations
**Random Search**: The algorithm uses random route generation, which may not guarantee finding the absolute optimal route every time.
**Performance**: Suitable for small datasets. For larger datasets, consider implementing more efficient algorithms or optimization techniques.
**Assumptions**:
Round-trip tickets are available only from AMS and BLR.
Each round-trip ticket can be purchased only once per journey.

## Contributing
Contributions are welcome! If you have suggestions for improvements or find any issues, please open an issue or submit a pull request.

## License
This project is licensed under the MIT License.


