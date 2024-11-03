import random
import itertools
from collections import Counter
from typing import List, Tuple, Dict

# Define the cities
cities = ['AMS', 'BLR', 'HKT', 'BKK', 'KL']

# Flight costs for one-way flights
one_way_costs: Dict[str, Dict[str, int]] = {
    'AMS': {'AMS': 9999, 'BLR': 405, 'HKT': 700, 'BKK': 530, 'KL': 425},
    'BLR': {'AMS': 325, 'BLR': 9999, 'HKT': 170, 'BKK': 160, 'KL': 150},
    'HKT': {'AMS': 750, 'BLR': 190, 'HKT': 9999, 'BKK': 50, 'KL': 40},
    'BKK': {'AMS': 555, 'BLR': 140, 'HKT': 35, 'BKK': 9999, 'KL': 90},
    'KL': {'AMS': 455, 'BLR': 110, 'HKT': 35, 'BKK': 100, 'KL': 9999},
}

# Flight costs for round-trip flights from AMS
round_trip_costs_AMS: Dict[str, int] = {
    'BLR': 550,
    'HKT': 9999,
    'BKK': 630,
    'KL': 675,
}

# Flight costs for round-trip flights from BLR
round_trip_costs_BLR: Dict[str, int] = {
    'HKT': 300,
    'BKK': 290,
    'KL': 250,
}

# Mandatory and optional cities
mandatory_cities: List[str] = ['BLR', 'HKT']
optional_cities: List[str] = ['BKK', 'KL']
start_city: str = 'AMS'

# Memetic Algorithm Parameters
population_size: int = 10 # Increased population size
generations: int = 100  # Increased number of generations
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
    Find possible round-trip tickets that can be purchased for the route.
    Each round-trip ticket can be purchased at most once.

    Args:
        route (List[str]): The route to analyze.

    Returns:
        List[Tuple[str, str]]: A list of possible round-trip tickets.
    """
    options: List[Tuple[str, str]] = []
    # Round-trip tickets from AMS
    if route.count('AMS') >= 2:
        for dest in round_trip_costs_AMS:
            if dest in route:
                options.append(('AMS', dest))
    # Round-trip tickets from BLR
    if route.count('BLR') >= 1:
        for dest in round_trip_costs_BLR:
            if dest in route and dest != 'BLR':
                options.append(('BLR', dest))
    return options

def calculate_cost(route: List[str]) -> Tuple[int, List[Tuple[str, str, str, int]]]:
    """
    Calculate the total cost of the route, considering possible round-trip tickets.
    Each round-trip ticket and its legs can be used at most once.

    Args:
        route (List[str]): The route to calculate the cost for.

    Returns:
        Tuple[int, List[Tuple[str, str, str, int]]]: The total cost and flight details.
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
            # Check if all purchased round-trip legs were used exactly once
            all_legs_used = all(usage >= 1 for usage in leg_usage.values())
            if not all_legs_used:
                continue  # Skip this combination as not all legs of the purchased round-trip tickets were used
            # Update minimum total cost
            if total_cost < min_total_cost:
                min_total_cost = total_cost
                best_flights = flights.copy()
    return min_total_cost, best_flights

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