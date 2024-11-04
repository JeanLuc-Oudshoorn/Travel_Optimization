import random
from collections import Counter
from typing import List, Tuple
import os
import json

# Specify the path to your 'data' folder
data_folder = 'data'

# Load the one_way_costs dictionary from the JSON file
one_way_file_path = os.path.join(data_folder, 'one_way_costs.json')
with open(one_way_file_path, 'r') as f:
    one_way_costs = json.load(f)

# Load the round_trip_costs_AMS dictionary from the JSON file
round_trip_file_path = os.path.join(data_folder, 'round_trip_costs.json')
with open(round_trip_file_path, 'r') as f:
    round_trip_costs = json.load(f)

# Small correction
round_trip_costs['HKT']['AMS'] = 9999

# Now you can use the dictionaries in your script
print("Loaded one_way_costs:")
print(one_way_costs)

print("\nLoaded round_trip_costs:")
print(round_trip_costs)


# Define the cities
cities = ['AMS', 'BLR', 'HKT', 'BKK', 'KUL']

# Mandatory and optional cities
mandatory_cities: List[str] = ['BLR', 'HKT']
optional_cities: List[str] = ['BKK', 'KUL']
start_city: str = 'AMS'

# Memetic Algorithm Parameters
population_size: int = 1000 # Increased population size
generations: int = 50  # Increased number of generations
mutation_rate: float = 0.4  # Increased mutation rate
tournament_size: int = 3  # Adjusted tournament size
elitism_count: int = 0  # Number of elites to preserve

def generate_random_route() -> List[str]:
    """
    Generate a random valid route starting and ending at the start city.
    Each mandatory and optional city appears twice in the pool.
    Once all mandatory cities are picked at least once, and at least one optional city is picked,
    the start city is added to the pool. When the start city is picked, the route ends.

    Returns:
        List[str]: A valid route.
    """
    route: List[str] = [start_city]
    city_pool: List[str] = mandatory_cities * 2 + optional_cities * 2
    random.shuffle(city_pool)
    mandatory_remaining: List[str] = mandatory_cities.copy()
    optional_picked: int = 0

    while True:
        # Pick random starting
        city = city_pool.pop()
        route.append(city)

        # Remove the city from mandatory cities
        if city in mandatory_remaining:
            mandatory_remaining.remove(city)

        # If the city is in optiona cities
        if city in optional_cities:
            optional_picked += 1

        if not mandatory_remaining and optional_picked >= 1:
            city_pool.append(start_city)
            random.shuffle(city_pool)

        if city is start_city:
            return route


def find_round_trip_options(route: List[str]) -> List[Tuple[str, str]]:
    """
    Find possible round-trip tickets in the route.
    A round-trip is identified when a departure city appears twice in the route,
    and the cities immediately after the first occurrence and immediately before
    the second occurrence are the same arrival city.

    Args:
        route (List[str]): The route to analyze.

    Returns:
        List[Tuple[str, str]]: A list of possible round-trip tickets as (departure, arrival).
    """
    options: List[Tuple[str, str]] = []
    route_length = len(route)
    for i, departure_city in enumerate(route):
        # Only consider valid departure cities for round-trip tickets
        if departure_city not in round_trip_costs:
            continue
        # Find the next occurrence of the departure city
        try:
            next_index = route.index(departure_city, i + 1)
        except ValueError:
            continue  # No second occurrence found
        # Ensure indices are within bounds
        if i + 1 >= route_length or next_index - 1 < 0:
            continue
        arrival_city_first = route[i + 1]
        arrival_city_second = route[next_index - 1]
        # Check if the arrival cities are the same and valid
        if arrival_city_first == arrival_city_second and arrival_city_first in round_trip_costs[departure_city]:
            options.append((departure_city, arrival_city_first))
    # Remove duplicates
    options = list(set(options))
    return options


def calculate_cost(route: List[str]) -> Tuple[int, List[Tuple[str, str, str, int]]]:
    """
    Calculate the total cost of the route, considering possible round-trip tickets.

    Args:
        route (List[str]): The route to calculate the cost for.

    Returns:
        Tuple[int, List[Tuple[str, str, str, int]]]: The total cost and flight details.
    """
    total_cost = 0
    flights = []

    # Create list of legs in the route
    legs = [(route[i], route[i + 1]) for i in range(len(route) - 1)]

    # Initialize leg coverage
    leg_covered = set()

    # Find round-trip options using the updated method
    round_trip_options = find_round_trip_options(route)

    # For each identified round-trip option, cover the corresponding legs
    for departure, arrival in round_trip_options:
        leg1 = (departure, arrival)
        leg2 = (arrival, departure)
        # Purchase the round-trip ticket
        total_cost += round_trip_costs[departure][arrival]
        # Mark legs as covered
        leg_covered.update([leg1, leg2])
        # Add flights with zero cost for legs covered by round-trip ticket
        flights.append((leg1[0], leg1[1], 'Round-trip leg (no additional cost)', 0))
        flights.append((leg2[0], leg2[1], 'Round-trip leg (no additional cost)', 0))

    # Cover remaining legs with one-way tickets
    for leg in legs:
        if leg not in leg_covered:
            departure, arrival = leg
            cost = one_way_costs[departure][arrival]
            total_cost += cost
            flights.append((departure, arrival, 'One-way flight', cost))

    return total_cost, flights



def crossover(parent1: List[str], parent2: List[str]) -> Tuple[List[str], List[str]]:
    """
    Perform crossover between two parents to produce two offspring.
    The offspring are repaired to ensure they are valid.

    Args:
        parent1 (List[str]): The first parent route.
        parent2 (List[str]): The second parent route.

    Returns:
        Tuple[List[str], List[str]]: The two offspring routes.
    """
    # Exclude start and end city for splitting
    min_length = min(len(parent1), len(parent2)) - 2  # Exclude start and end city
    if min_length < 1:
        return parent1, parent2  # Can't perform crossover

    # Choose a random split index
    split_index = random.randint(1, min_length)  # Index between 1 and min_length

    # Create offspring
    offspring1 = parent1[:split_index] + parent2[split_index:]
    offspring2 = parent2[:split_index] + parent1[split_index:]

    # Repair offspring
    offspring1 = repair_offspring(offspring1)
    offspring2 = repair_offspring(offspring2)

    return offspring1, offspring2

def repair_offspring(offspring: List[str]) -> List[str]:
    """
    Repair an offspring to ensure it meets the constraints:
    - Starts and ends with the starting city
    - Each city (except the starting city) appears at most twice
    - All mandatory cities are included at least once
    - At least one optional city is included

    Args:
        offspring (List[str]): The offspring route to repair.

    Returns:
        List[str]: The repaired offspring route.
    """
    # Ensure start and end city
    if offspring[0] != start_city:
        offspring.insert(0, start_city)
    if offspring[-1] != start_city:
        offspring.append(start_city)

    # Count city occurrences
    city_counts = Counter(city for city in offspring if city != start_city)

    # Add missing mandatory cities
    for city in mandatory_cities:
        if city_counts.get(city, 0) == 0:
            # Insert at a random position (excluding start and end)
            idx_to_insert = random.randint(1, len(offspring) - 1)
            offspring.insert(idx_to_insert, city)

    # Ensure at least one optional city is included
    if not any(city in optional_cities for city in offspring):
        # Insert a random optional city at a random position
        optional_city = random.choice(optional_cities)
        idx_to_insert = random.randint(1, len(offspring) - 1)
        offspring.insert(idx_to_insert, optional_city)

    # Ensure that each city appears at most twice
    for city, count in city_counts.items():
        while count > 2:
            # Find indices of the city (excluding start and end)
            indices = [i for i, c in enumerate(offspring[1:-1], 1) if c == city]
            if indices:
                idx_to_remove = random.choice(indices)
                del offspring[idx_to_remove]
                count -= 1
            else:
                break

    return offspring

def mutate(route: List[str], min_optional_cities: int = 1) -> List[str]:
    """
    Mutate a route by performing inversion mutation and adjusting optional cities.

    - If the number of optional cities is greater than the minimum required, randomly delete an optional city.
    - If any optional city occurs less than twice in the route, randomly add it to the route.

    Args:
        route (List[str]): The route to mutate.
        min_optional_cities (int): The minimum number of optional cities that have to be visited in the solution.

    Returns:
        List[str]: The mutated route.
    """
    route = route.copy()

    # Perform inversion mutation
    indices = [i for i in range(1, len(route) - 1)]  # Exclude start and end indices
    if len(indices) >= 2:
        idx1, idx2 = sorted(random.sample(indices, 2))
        route[idx1:idx2] = reversed(route[idx1:idx2])

    # Count occurrences of each city
    city_counts = Counter(city for city in route if city != start_city)

    # List of optional cities currently in the route
    optional_cities_in_route = [city for city in route if city in optional_cities]
    num_optional_cities = len(optional_cities_in_route)

    random_roll = random.random()

    if random_roll < 0.75:
        # If more optional cities than required, randomly delete an optional city
        if num_optional_cities > min_optional_cities:
            # Choose a random optional city to remove
            city_to_remove = random.choice(optional_cities_in_route)
            # Remove one occurrence of the city (excluding start and end positions)
            indices_to_remove = [i for i, city in enumerate(route) if city == city_to_remove and i != 0 and i != len(route) - 1]
            if indices_to_remove:
                idx_to_remove = random.choice(indices_to_remove)
                del route[idx_to_remove]

    else:
        # For optional cities that occur less than twice, randomly add one
        for city in optional_cities:
            if city_counts.get(city, 0) < 2:
                # Insert at a random position (excluding start and end)
                idx_to_insert = random.randint(1, len(route) - 1)
                route.insert(idx_to_insert, city)
                city_counts[city] += 1
                continue

    return route


def tournament_selection(population: List[List[str]], fitnesses: List[int], k: int) -> List[str]:
    """
    Select an individual from the population using tournament selection.

    Args:
        population (List[List[str]]): The current population.
        fitnesses (List[int]): The fitness scores of the population.
        k (int): The tournament size.

    Returns:
        List[str]: The selected individual.
    """
    selected_indices = random.sample(range(len(population)), k)
    best_idx = min(selected_indices, key=lambda idx: fitnesses[idx])
    return population[best_idx]

def local_search(route: List[str]) -> List[str]:
    """
    Perform local search on the route by swapping adjacent cities (excluding start and end).

    Args:
        route (List[str]): The route to improve.

    Returns:
        List[str]: The improved route.
    """
    best_route = route.copy()
    best_cost, _ = calculate_cost(best_route)

    # Swap adjacent cities (excluding start and end)
    for i in range(1, len(route) - 2):  # Exclude last index to avoid swapping end city
        new_route = route.copy()
        # Swap cities at positions i and i+1
        new_route[i], new_route[i + 1] = new_route[i + 1], new_route[i]
        new_cost, _ = calculate_cost(new_route)
        if new_cost < best_cost:
            best_route = new_route
            best_cost = new_cost

    return best_route


def run_genetic_algorithm():
    """
    Run the genetic algorithm with the specified parameters.
    """
    global best_cost, best_route, best_flights

    # Initialize population
    population: List[List[str]] = []
    for _ in range(population_size):
        route = generate_random_route()
        population.append(route)

    # Evolutionary loop
    for generation in range(generations):
        fitnesses: List[int] = []
        for route in population:
            cost, _ = calculate_cost(route)
            fitnesses.append(cost)
            if cost < best_cost:
                best_cost = cost
                best_route = route.copy()
                _, best_flights = calculate_cost(best_route)

        # Print best cost and route of the current generation
        print(f"Generation {generation+1}: Best Cost = €{best_cost}, Route = {' -> '.join(best_route)}")

        new_population: List[List[str]] = []
        # Elitism: Preserve the best individuals
        elites = [population[idx] for idx in sorted(range(len(fitnesses)), key=lambda i: fitnesses[i])[:elitism_count]]
        new_population.extend(elites)

        while len(new_population) < population_size:
            # Selection
            parent1 = tournament_selection(population, fitnesses, tournament_size)
            parent2 = tournament_selection(population, fitnesses, tournament_size)

            # Crossover
            offspring1, offspring2 = crossover(parent1, parent2)

            # Mutation
            if random.random() < mutation_rate:
                offspring1 = mutate(offspring1)
            if random.random() < mutation_rate:
                offspring2 = mutate(offspring2)

            # Local search
            offspring1 = local_search(offspring1)
            new_population.append(offspring1)

            if len(new_population) < population_size:
                offspring2 = local_search(offspring2)
                new_population.append(offspring2)

        population = new_population

    # Output the best route and cost
    print("\nOptimal Route:", ' -> '.join(best_route))
    print(f"Total Cost: €{best_cost}")
    print("Flight Details:")
    for flight in best_flights:
        print(f"  {flight[0]} to {flight[1]} via {flight[2]}: €{flight[3]}")


if __name__ == "__main__":
    best_cost = float('inf')
    best_route = None
    best_flights = None
    run_genetic_algorithm()