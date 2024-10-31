import random
import itertools
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
population_size: int = 1000  # Increased population size
generations: int = 4  # Increased number of generations
mutation_rate: float = 0.4  # Increased mutation rate
tournament_size: int = 3  # Adjusted tournament size
elitism_count: int = 3  # Number of elites to preserve

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

        print(f"city: {city}, route: {route}")

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
            print()
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

def create_adjacency_matrix(parent1: List[str], parent2: List[str]) -> Dict[str, set]:
    """
    Create the adjacency matrix for ERO based on two parent routes.

    Args:
        parent1 (List[str]): The first parent route.
        parent2 (List[str]): The second parent route.

    Returns:
        Dict[str, set]: The adjacency matrix.
    """
    adjacency = {}
    parents = [parent1, parent2]
    for parent in parents:
        length = len(parent)
        for i, city in enumerate(parent):
            if city not in adjacency:
                adjacency[city] = set()
            prev_city = parent[i - 1] if i > 0 else parent[-1]
            next_city = parent[i + 1] if i < length - 1 else parent[0]
            adjacency[city].update([prev_city, next_city])
    return adjacency

def edge_recombination_crossover(parent1: List[str], parent2: List[str]) -> List[str]:
    """
    Perform Edge Recombination Operator (ERO) crossover on two parent routes.

    Args:
        parent1 (List[str]): The first parent route.
        parent2 (List[str]): The second parent route.

    Returns:
        List[str]: The child route.
    """
    adjacency = create_adjacency_matrix(parent1, parent2)
    cities_set = set(parent1 + parent2)
    current_city = random.choice([parent1[1], parent2[1]])  # Start from position 1 to skip 'AMS' at index 0
    child = [start_city]
    visited = set(start_city)

    while len(child) < len(parent1):
        child.append(current_city)
        visited.add(current_city)
        # Remove current city from adjacency lists
        for neighbors in adjacency.values():
            neighbors.discard(current_city)
        # Select next city
        if adjacency.get(current_city):
            # Choose neighbor with the fewest neighbors
            next_cities = list(adjacency[current_city])
            min_neighbors = min(len(adjacency.get(city, [])) for city in next_cities)
            candidates = [city for city in next_cities if len(adjacency.get(city, [])) == min_neighbors]
            next_city = random.choice(candidates)
        else:
            # Choose random unvisited city
            remaining_cities = cities_set - visited
            if remaining_cities:
                next_city = random.choice(list(remaining_cities))
            else:
                break  # No more cities to visit
        current_city = next_city

    # Ensure the route ends with the start city
    if child[-1] != start_city:
        child.append(start_city)

    return child

def mutate(route: List[str]) -> List[str]:
    """
    Mutate a route using inversion mutation.

    Args:
        route (List[str]): The route to mutate.

    Returns:
        List[str]: The mutated route.
    """
    route = route.copy()
    indices = [i for i in range(1, len(route) - 1)]  # Exclude start and end indices
    if len(indices) < 2:
        return route

    idx1, idx2 = sorted(random.sample(indices, 2))
    route[idx1:idx2] = reversed(route[idx1:idx2])
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

def run_genetic_algorithm():
    """
    Run the genetic algorithm with the specified parameters.
    """
    global best_cost, best_route, best_flights

    # Initialize population
    population: List[List[str]] = []
    for _ in range(population_size):
        while True:
            route = generate_random_route()
            population.append(route)
            break

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
            child = edge_recombination_crossover(parent1, parent2)
            # Mutation
            if random.random() < mutation_rate:
                child = mutate(child)

                # Local Search
                child = local_search(child)
                new_population.append(child)

        population = new_population

    # Output the best route and cost
    print("\nOptimal Route:", ' -> '.join(best_route))
    print(f"Total Cost: €{best_cost}")
    print("Flight Details:")
    for flight in best_flights:
        print(f"  {flight[0]} to {flight[1]} via {flight[2]}: €{flight[3]}")

def local_search(route: List[str]) -> List[str]:
    """
    Perform local search on the route to improve it.

    Args:
        route (List[str]): The route to improve.

    Returns:
        List[str]: The improved route.
    """
    best_route = route.copy()
    best_cost, _ = calculate_cost(best_route)

    # Try swapping every pair of cities (excluding start and end)
    indices = [i for i in range(1, len(route) - 1)]
    for i in indices:
        for j in indices:
            if i >= j:
                continue
            new_route = route.copy()
            new_route[i], new_route[j] = new_route[j], new_route[i]
            new_cost, _ = calculate_cost(new_route)
            if new_cost < best_cost:
                best_route = new_route
                best_cost = new_cost

    return best_route

if __name__ == "__main__":
    best_cost = float('inf')
    best_route = None
    best_flights = None
    run_genetic_algorithm()
