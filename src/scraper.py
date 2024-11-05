import requests
import re
import random
import time
import os
import json
from typing import Dict

# List of cities
cities = ['AMS', 'BLR', 'HKT', 'BKK', 'KUL']

# Dates for the flights
start_date = '2025-01-20'
end_date = '2025-02-14'

# Initialize dictionaries to store costs
one_way_costs: Dict[str, Dict[str, int]] = {}
round_trip_costs: Dict[str, Dict[str, int]] = {}

# Function to extract the first euro amount from the content
def extract_price(content: str) -> float:
    pattern = r'[\€]\s?([0-9]+(?:\.[0-9]{1,2})?)'
    matches = re.findall(pattern, content)
    if matches:
        return float(matches[0])
    else:
        return None

# One-way flights between all cities
for origin in cities:
    one_way_costs[origin] = {}
    for destination in cities:
        if origin == destination:
            one_way_costs[origin][destination] = 9999
            continue

        # Construct the URL for one-way flights
        url = f'https://www.google.com/travel/flights?hl=en&q=Flights%20to%20{destination}%20from%20{origin}%20on%20{start_date}%20oneway'

        try:
            response = requests.get(url)
            if response.status_code == 200:
                price = extract_price(response.text)
                if price is not None:
                    one_way_costs[origin][destination] = int(price)
                    print(f"One-way price from {origin} to {destination}: €{price}")
                else:
                    print(f"No price found for one-way flight from {origin} to {destination}")
                    one_way_costs[origin][destination] = 9999
            else:
                print(f"Failed to retrieve content for one-way flight from {origin} to {destination}. Status code: {response.status_code}")
                one_way_costs[origin][destination] = 9999
        except requests.exceptions.RequestException as e:
            print(f"An error occurred for one-way flight from {origin} to {destination}: {e}")
            one_way_costs[origin][destination] = 9999

        # Sleep randomly between 3-5 seconds
        time.sleep(random.uniform(3, 5))

# Round-trip flights between all cities
for origin in cities:
    round_trip_costs[origin] = {}
    for destination in cities:
        if origin == destination:
            round_trip_costs[origin][destination] = 9999
            continue

        # Construct the URL for round-trip flights
        url_return = f'https://www.google.com/travel/flights?hl=en&q=Flights%20to%20{destination}%20from%20{origin}%20on%20{start_date}%20through%20{end_date}'

        try:
            response = requests.get(url_return)
            if response.status_code == 200:
                price = extract_price(response.text)
                if price is not None:
                    round_trip_costs[origin][destination] = int(price)
                    print(f"Round-trip price from {origin} to {destination}: €{price}")
                else:
                    print(f"No price found for round-trip flight from {origin} to {destination}")
                    round_trip_costs[origin][destination] = 9999
            else:
                print(f"Failed to retrieve content for round-trip flight from {origin} to {destination}. Status code: {response.status_code}")
                round_trip_costs[origin][destination] = 9999
        except requests.exceptions.RequestException as e:
            print(f"An error occurred for round-trip flight from {origin} to {destination}: {e}")
            round_trip_costs[origin][destination] = 9999

        # Sleep randomly between 3-5 seconds
        time.sleep(random.uniform(3, 5))

# Output the results
print("\nOne-way flight costs:")
for origin, destinations in one_way_costs.items():
    print(f"{origin}: {destinations}")

print("\nRound-trip flight costs:")
for origin, destinations in round_trip_costs.items():
    print(f"{origin}: {destinations}")

# --------------------------------------------
# Saving the dictionaries to the 'data' folder
# --------------------------------------------

# Specify the path to your 'data' folder
data_folder = 'data'

# Create the 'data' folder if it doesn't exist
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# Save the one_way_costs dictionary to a JSON file
one_way_file_path = os.path.join(data_folder, 'one_way_costs.json')
with open(one_way_file_path, 'w') as f:
    json.dump(one_way_costs, f, indent=4)

# Save the round_trip_costs dictionary to a JSON file
round_trip_file_path = os.path.join(data_folder, 'round_trip_costs.json')
with open(round_trip_file_path, 'w') as f:
    json.dump(round_trip_costs, f, indent=4)

print("\nDictionaries have been saved to the 'data' folder.")
