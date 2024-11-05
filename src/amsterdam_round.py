import random
import itertools

# Define the cities
cities = ['AMS', 'BLR', 'HKT', 'BKK', 'KL']

# Flight costs for one-way flights
one_way_costs = {
    'AMS': {'AMS': 9999, 'BLR': 405, 'HKT': 700, 'BKK': 530, 'KL': 425},
    'BLR': {'AMS': 325, 'BLR': 9999, 'HKT': 170, 'BKK': 160, 'KL': 150},
    'HKT': {'AMS': 750, 'BLR': 190, 'HKT': 9999, 'BKK': 50, 'KL': 40},
    'BKK': {'AMS': 555, 'BLR': 140, 'HKT': 35, 'BKK': 9999, 'KL': 90},
    'KL': {'AMS': 455, 'BLR': 110, 'HKT': 35, 'BKK': 100, 'KL': 9999},
}

# Flight costs for round-trip flights from AMS
round_trip_costs_AMS = {
    'BLR': 550,
    'HKT': 9999,
    'BKK': 630,
    'KL': 675,
}

# Flight costs for round-trip flights from BLR
round_trip_costs_BLR = {
    'HKT': 300,
    'BKK': 290,
    'KL': 250,
}

# Mandatory and optional cities
mandatory_cities = ['BLR', 'HKT']
optional_cities = ['BKK', 'KL']

# Number of iterations for the random search
iterations = 100000

# Initialize the best cost and route
best_cost = float('inf')
best_route = None
best_flights = None

def generate_random_route():
    """
    Generate a random route starting at AMS and ending when AMS is picked again.
    Cities can be visited multiple times.
    """
    route = ['AMS']

    while True:
        next_cities = ['AMS', 'BLR', 'HKT', 'BKK', 'KL']
        # Randomly pick the next city
        next_city = random.choice(next_cities)
        route.append(next_city)
        if next_city == 'AMS' and len(route) > 2:
            break  # End the route

        # To prevent infinite loops, limit the maximum route length
        if len(route) > 10:
            route.append('AMS')
            break
    return route

def is_valid_route(route):
    """
    Check if the route is valid:
    - Starts and ends at AMS
    - Visits BLR and HKT at least once
    - Visits at least one of BKK or KL
    """
    if route[0] != 'AMS' or route[-1] != 'AMS':
        return False
    route_set = set(route)
    if not all(city in route_set for city in mandatory_cities):
        return False
    if not any(city in route_set for city in optional_cities):
        return False
    return True

def find_round_trip_options(route):
    """
    Find possible round-trip tickets that can be purchased for the route.
    Each round-trip ticket can be purchased at most once.
    """
    options = []
    # Round-trip tickets from AMS
    if route.count('AMS') >= 2:
        for dest in round_trip_costs_AMS:
            if route.count(dest) >= 1:
                options.append(('AMS', dest))
    # Round-trip tickets from BLR
    if route.count('BLR') >= 2:
        for dest in round_trip_costs_BLR:
            if route.count(dest) >= 1 and dest != 'BLR':
                options.append(('BLR', dest))
    return options

def calculate_cost(route):
    """
    Calculate the total cost of the route, considering possible round-trip tickets.
    Each round-trip ticket and its legs can be used at most once.
    """
    min_total_cost = float('inf')
    best_flights = []
    # Find possible round-trip options
    round_trip_options = find_round_trip_options(route)
    # Generate all combinations of purchasing round-trip tickets
    for r in range(len(round_trip_options) + 1):
        for round_trips in itertools.combinations(round_trip_options, r):
            total_cost = 0
            flights = []
            used_round_trips = {}
            leg_usage = {}
            # Purchase the selected round-trip tickets
            valid_purchase = True
            for departure, arrival in round_trips:
                if departure == 'AMS':
                    cost = round_trip_costs_AMS[arrival]
                elif departure == 'BLR':
                    cost = round_trip_costs_BLR[arrival]
                else:
                    valid_purchase = False
                    break  # Invalid round-trip purchase
                total_cost += cost
                # Record that this round-trip ticket has been purchased
                used_round_trips[(departure, arrival)] = True
                # Initialize leg usage
                leg_usage[(departure, arrival)] = 0  # Outbound leg usage count
                leg_usage[(arrival, departure)] = 0  # Return leg usage count
            if not valid_purchase:
                continue
            # Now, go through the route and calculate the cost for each leg
            for i in range(len(route) - 1):
                departure = route[i]
                arrival = route[i + 1]
                flight_type = 'One-way flight'
                cost = one_way_costs[departure][arrival]
                # Check if this leg can be covered by a round-trip ticket
                if (departure, arrival) in leg_usage:
                    if leg_usage[(departure, arrival)] == 0:
                        # Use the leg from the round-trip ticket
                        cost = 0
                        flight_type = 'Round-trip leg (no additional cost)'
                        leg_usage[(departure, arrival)] += 1
                    else:
                        # Leg has already been used
                        pass  # Use one-way flight cost
                total_cost += cost
                flights.append((departure, arrival, flight_type, cost))
            # Check if any round-trip legs were unused (penalize or skip)
            all_legs_used = all(usage >= 1 for usage in leg_usage.values())
            if not all_legs_used:
                continue  # Skip this combination as not all legs of the purchased round-trip tickets were used
            # Update minimum total cost
            if total_cost < min_total_cost:
                min_total_cost = total_cost
                best_flights = flights.copy()
    return min_total_cost, best_flights

for _ in range(iterations):
    route = generate_random_route()
    if not is_valid_route(route):
        continue
    total_cost, flights = calculate_cost(route)
    if total_cost < best_cost:
        best_cost = total_cost
        best_route = route.copy()
        best_flights = flights.copy()

# Output the best route and cost
print("Optimal Route:", ' -> '.join(best_route))
print(f"Total Cost: € {best_cost}")
print("Flight Details:")
for flight in best_flights:
    print(f"  {flight[0]} to {flight[1]} via {flight[2]}: €{flight[3]}")
