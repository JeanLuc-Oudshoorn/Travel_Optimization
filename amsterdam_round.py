import random
import itertools

# Define the cities
cities = ['AMS', 'BLR', 'HKT', 'BKK', 'KL']

# Mandatory and optional cities
mandatory_cities = ['BLR', 'HKT']
optional_cities = ['BKK', 'KL']

# Flight costs for one-way flights (represented as a dictionary of dictionaries)
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

# High cost to represent unavailable round trips from other cities
round_trip_unavailable = 9999

# Number of iterations for the random search
iterations = 1000000

# Initialize the best cost and route
best_cost = float('inf')
best_route = None
best_flights = None  # To store the flight choices (one-way or round-trip)

def generate_random_route():
    """
    Generate a random route starting and ending at AMS,
    including mandatory cities and one optional city.
    """
    route = ['AMS']
    # Choose one optional city
    optional_city = random.choice(optional_cities)
    # Combine mandatory and optional cities
    middle_cities = mandatory_cities + [optional_city]
    # Randomize the order of middle cities
    random.shuffle(middle_cities)
    route.extend(middle_cities)
    route.append('AMS')  # End at AMS
    return route

def get_flight_cost(departure, arrival, flight_type):
    """
    Get the cost of a flight between two cities.
    flight_type can be 'one_way' or 'round_trip'.
    """
    if flight_type == 'one_way':
        return one_way_costs[departure][arrival]
    elif flight_type == 'round_trip':
        if departure == 'AMS':
            return round_trip_costs_AMS.get(arrival, round_trip_unavailable)
        elif departure == 'BLR':
            return round_trip_costs_BLR.get(arrival, round_trip_unavailable)
        else:
            return round_trip_unavailable
    else:
        return round_trip_unavailable

def is_round_trip_available(departure, arrival):
    """
    Check if a round-trip flight is available between two cities.
    """
    if departure == 'AMS' and arrival in round_trip_costs_AMS:
        return True
    if departure == 'BLR' and arrival in round_trip_costs_BLR:
        return True
    return False

for i in range(iterations):
    # Generate a random route
    route = generate_random_route()

    # Initialize total cost and flight choices
    total_cost = 0
    flights = []  # List to store flight details

    # Decide on flight types between each pair of cities
    j = 0
    while j < len(route) - 1:
        departure = route[j]
        arrival = route[j + 1]

        # Randomly decide to use one-way or round-trip flight
        if is_round_trip_available(departure, arrival) and random.choice([True, False]):
            # Use round-trip flight
            cost = get_flight_cost(departure, arrival, 'round_trip')
            if cost >= 9999:
                # If round-trip not available, use one-way
                cost = get_flight_cost(departure, arrival, 'one_way')
                flights.append((departure, arrival, 'one_way', cost))
                total_cost += cost
                j += 1
            else:
                # Need to adjust the route to include the return trip
                # Insert the departure city again after arrival
                route.insert(j + 2, departure)
                flights.append((departure, arrival, 'round_trip', cost))
                total_cost += cost
                j += 2  # Skip the next city since it's the return to departure
        else:
            # Use one-way flight
            cost = get_flight_cost(departure, arrival, 'one_way')
            flights.append((departure, arrival, 'one_way', cost))
            total_cost += cost
            j += 1

    # Update best route if total cost is lower
    if total_cost < best_cost:
        best_cost = total_cost
        best_route = route.copy()
        best_flights = flights.copy()

# Output the best route and cost
print("Optimal Route:", ' -> '.join(best_route))
print("Total Cost: €", best_cost)
print("Flight Details:")
for flight in best_flights:
    print(f"  {flight[0]} to {flight[1]} via {flight[2]} flight: €{flight[3]}")
