import numpy as np

# Define the list of cities
cities = ["AMS", "DUS", "BRU", "DEL", "AGR", "MUM", "KUL", "BKK", "SIN"]

# Define the cost matrix
cost = {
    ("AMS", "AMS"): 0, ("AMS", "DUS"): 10000, ("AMS", "BRU"): 10000, ("AMS", "DEL"): 360, ("AMS", "AGR"): 10000, ("AMS", "MUM"): 365, ("AMS", "KUL"): 410, ("AMS", "BKK"): 450, ("AMS", "SIN"): 400,
    ("DUS", "AMS"): 10000, ("DUS", "DUS"): 0, ("DUS", "BRU"): 10000, ("DUS", "DEL"): 360, ("DUS", "AGR"): 10000, ("DUS", "MUM"): 430, ("DUS", "KUL"): 370, ("DUS", "BKK"): 465, ("DUS", "SIN"): 380,
    ("BRU", "AMS"): 10000, ("BRU", "DUS"): 10000, ("BRU", "BRU"): 0, ("BRU", "DEL"): 430, ("BRU", "AGR"): 10000, ("BRU", "MUM"): 370, ("BRU", "KUL"): 415, ("BRU", "BKK"): 460, ("BRU", "SIN"): 440,
    ("DEL", "AMS"): 350, ("DEL", "DUS"): 364, ("DEL", "BRU"): 290, ("DEL", "DEL"): 0, ("DEL", "AGR"): 101, ("DEL", "MUM"): 10000, ("DEL", "KUL"): 150, ("DEL", "BKK"): 170, ("DEL", "SIN"): 160,
    ("AGR", "AMS"): 10000, ("AGR", "DUS"): 10000, ("AGR", "BRU"): 10000, ("AGR", "DEL"): 101, ("AGR", "AGR"): 0, ("AGR", "MUM"): 164, ("AGR", "KUL"): 10000, ("AGR", "BKK"): 10000, ("AGR", "SIN"): 10000,
    ("MUM", "AMS"): 400, ("MUM", "DUS"): 364, ("MUM", "BRU"): 280, ("MUM", "DEL"): 10000, ("MUM", "AGR"): 142, ("MUM", "MUM"): 0, ("MUM", "KUL"): 125, ("MUM", "BKK"): 170, ("MUM", "SIN"): 150,
    ("KUL", "AMS"): 370, ("KUL", "DUS"): 567, ("KUL", "BRU"): 423, ("KUL", "DEL"): 150, ("KUL", "AGR"): 10000, ("KUL", "MUM"): 170, ("KUL", "KUL"): 0, ("KUL", "BKK"): 92, ("KUL", "SIN"): 50,
    ("BKK", "AMS"): 390, ("BKK", "DUS"): 524, ("BKK", "BRU"): 363, ("BKK", "DEL"): 160, ("BKK", "AGR"): 10000, ("BKK", "MUM"): 150, ("BKK", "KUL"): 73, ("BKK", "BKK"): 0, ("BKK", "SIN"): 70,
    ("SIN", "AMS"): 375, ("SIN", "DUS"): 490, ("SIN", "BRU"): 500, ("SIN", "DEL"): 180, ("SIN", "AGR"): 10000, ("SIN", "MUM"): 190, ("SIN", "KUL"): 25, ("SIN", "BKK"): 60, ("SIN", "SIN"): 0
}

def random_schedule():
    # Initialize visited cities
    visited_cities = []

    # Pick start location
    start = np.random.choice(["AMS", "DUS", "BRU"])
    visited_cities.append(start)

    # Stopping conditions
    required_cities = ["AGR", "KUL", "BKK", "SIN"]

    while not all(city in visited_cities for city in required_cities):
        # Step 2
        step = np.random.choice(["DEL", "AGR", "MUM", "KUL", "BKK", "SIN"])
        visited_cities.append(step)

    # Pick end location
    end = np.random.choice(["AMS", "DUS", "BRU"])
    visited_cities.append(end)

    # Initialize cost
    total_cost = 0

    for i in range(len(visited_cities)-1):
        city = visited_cities[i]
        next_city = visited_cities[i+1]
        total_cost += cost[city, next_city]

    return visited_cities, total_cost

# Initialize simulation vars
best_total_cost = np.inf
best_schedule = None


for i in range(10000):
    visited_cities, total_cost = random_schedule()

    if total_cost < best_total_cost:
        best_total_cost = total_cost
        best_schedule = visited_cities
