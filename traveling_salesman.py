import pulp

# Define the list of cities
cities = ["A", "B", "C", "D"]

# Define the cost matrix (symmetric for TSP)
cost = {
    ("A", "B"): 10, ("A", "C"): 15, ("A", "D"): 20,
    ("B", "A"): 10, ("B", "C"): 35, ("B", "D"): 25,
    ("C", "A"): 15, ("C", "B"): 35, ("C", "D"): 30,
    ("D", "A"): 20, ("D", "B"): 25, ("D", "C"): 30
}

# Define the problem
prob = pulp.LpProblem("TSP", pulp.LpMinimize)

# Decision variables: x[i][j] is 1 if we travel from city i to city j, else 0
x = pulp.LpVariable.dicts("x", [(i, j) for i in cities for j in cities if i != j], cat="Binary")

# Auxiliary variables for subtour elimination
u = pulp.LpVariable.dicts("u", cities, lowBound=0, cat="Continuous")

# Objective function: minimize the total cost
prob += pulp.lpSum([cost[(i, j)] * x[(i, j)] for i in cities for j in cities if i != j])

# Constraints
# 1. Each city must have exactly one outgoing flight
for i in cities:
    prob += pulp.lpSum([x[(i, j)] for j in cities if i != j]) == 1, f"Out_{i}"

# 2. Each city must have exactly one incoming flight
for j in cities:
    prob += pulp.lpSum([x[(i, j)] for i in cities if i != j]) == 1, f"In_{j}"

# 3. Subtour elimination constraints
for i in cities:
    for j in cities:
        if i != j and (i != cities[0] and j != cities[0]):  # Ensure not applied to the start city
            prob += u[i] - u[j] + len(cities) * x[(i, j)] <= len(cities) - 1, f"Subtour_{i}_{j}"

# Solve the problem
prob.solve()

# Print the results
print(f"Status: {pulp.LpStatus[prob.status]}")
print("Optimal route with minimum cost:")
for i in cities:
    for j in cities:
        if i != j and pulp.value(x[(i, j)]) == 1:
            print(f"From {i} to {j} with cost {cost[(i, j)]}")

print(f"\nTotal cost: {pulp.value(prob.objective)}")
