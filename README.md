# Travel Route Optimization Script

## Overview

The Python script implements a memetic algorithm to find the most cost-effective travel route between several cities, given specific constraints and flight options. 
The cities for which the best route is found can be adapted. In the current implementation the goal is to minimize the total cost of a round-trip journey that:

- **Starts and ends in Amsterdam (AMS)**
- **Includes mandatory visits to Bangalore (BLR) and Phuket (HKT)**
- **Includes one optional city: either Bangkok (BKK) or Kuala Lumpur (KUL)**

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

3. **Round-Trip Ticket Evaluation**:
   - Identifies possible round-trip tickets based on the cities visited in the route.
   - Considers all combinations of purchasing available round-trip tickets.
   - Ensures each round-trip ticket is purchased at most once.

4. **Cost Calculation**:
   - Tracks the usage of each leg of purchased round-trip tickets to prevent multiple uses.
   - Calculates the total cost of the route, adding costs of one-way flights and purchased round-trip tickets.
   - Ensures both legs of any purchased round-trip ticket are used exactly once.

5. **Optimization Loop**:
   - Uses crossover, mutations and local search heuristics to create better routes.
   - Keeps track of the route with the lowest total cost found.

## Requirements

- **Python 3.10**
- No external dependencies (uses only standard Python libraries)

## Usage

### Running the Script

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/JeanLuc-Oudshoorn/Travel_Optimization.git
   cd Travel_Optimization/src
   ``` 

2. **Run the script**:

   ```bash
   python memetic_algorithm.py
   ```

### Example Output

   ```rust
   Optimal Route: AMS -> BLR -> HKT -> KL -> BLR -> AMS
   Total Cost: € 870
   Flight Details:
     AMS to BLR via Round-trip leg (no additional cost): €0
     BLR to HKT via One-way flight: €170
     HKT to KUL via One-way flight: €40
     KUL to BLR via One-way flight: €110
     BLR to AMS via Round-trip leg (no additional cost): €0
   ```

## Customization
- **Adjust Iterations**: Modify the iterations variable in the script to increase or decrease the number of iterations for the random search.
- **Flight Costs**: Enter your own flight costs or use the scraper in `src/scraper.py` to fetch them from Google Flights.
- **Cities and Constraints**: Add or remove cities and adjust mandatory or optional city requirements as needed.

## Flight Options
The selected flights by the scraper are filtered for the following criteria.
- **No Nightly Departures**: Only flights departing before midnight or after 07:00 AM (local time) are considered valid.
- **Max 1. Stop**: Only flights with maximum one layover are considered valid.
- **Less than 20 hr. Flight Duration**: Only flights with a total duration of less than 20 hours are considered valid.

## Limitations
- **Scraping Flight Prices**: Currently the scraper simply picks the cheapest suggested flight from Google Flights for a route on a specific date. You can enter your own prices, but this may be labour intensive if you want to consider more than a handful of cities. 
- **Price Data is Indicative**: Prices found by the scraper (or displayed on comparison websites) may not give you all the information. You may have to pay extra for selecting a seat or booking luggage.
- **Time Duration**: If 10+ cities need to be considered it may take the algorithm a significant amount of time to find a good solution.
- **Fixed Start and End**: The trip must start and end in the same city.
- **Global Optimum**: While for smaller problems it has been validated that the global optimum is found relatively quick, it cannot be guaranteed that a global optimum is found for larger problems.

## Contributing
Contributions are welcome! If you have suggestions for improvements or find any issues, please open an issue or submit a pull request.

## License
This project is licensed under the MIT License.


