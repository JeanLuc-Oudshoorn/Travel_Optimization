import requests
import re
import random
import time
import os
import json
from typing import Dict, List

# List of cities
cities = ['AMS', 'IXA', 'SGN', 'HAN', 'SIN', 'TPE']

# Dates for the flights
start_date = '2025-01-20'
end_date = '2025-02-15'

# Initialize dictionaries to store costs and flight details
one_way_costs: Dict[str, Dict[str, int]] = {}
round_trip_costs: Dict[str, Dict[str, int]] = {}
one_way_flights: Dict[str, Dict[str, List[dict]]] = {}
round_trip_flights: Dict[str, Dict[str, List[dict]]] = {}

# Function to extract valid flights from the content
def extract_valid_flights(content: str) -> List[dict]:
    # Find all flight options in the content
    flight_infos = re.findall(r'aria-label="(.*?)"', content)
    valid_flights = []
    for flight_info in flight_infos:
        flight_data = {}
        # Check for multiple layovers ('2 stops' or '3 stops')
        layover_match = re.search(r'\b(\d+)\s?stop', flight_info, re.IGNORECASE)
        if layover_match:
            layovers = int(layover_match.group(1))
            if layovers >= 2:
                continue  # Skip flights with multiple layovers
        else:
            layovers = 0  # Non-stop flight
        flight_data['layovers'] = layovers

        # Check for total travel duration less than 20 hours
        duration_match = re.search(r'Total duration (\d+)\s*hr\s*(\d+)?\s*min', flight_info)
        if duration_match:
            hours = int(duration_match.group(1))
            minutes = int(duration_match.group(2) or 0)
            total_minutes = hours * 60 + minutes
            if total_minutes >= 20 * 60:
                continue  # Skip flights with duration 20 hours or more
        else:
            continue  # Can't find duration, skip
        flight_data['duration'] = f"{hours} hr {minutes} min"

        # Check departure time not between midnight and 7 AM
        departure_match = re.search(r'Leaves .* at (\d+):(\d+)\s*(AM|PM)', flight_info)
        if departure_match:
            dep_hour = int(departure_match.group(1))
            dep_min = int(departure_match.group(2))
            dep_period = departure_match.group(3)
            flight_data['departure_time'] = f"{dep_hour}:{dep_min:02d} {dep_period}"
            # Convert to 24-hour format
            if dep_period.upper() == 'PM' and dep_hour != 12:
                dep_hour += 12
            elif dep_period.upper() == 'AM' and dep_hour == 12:
                dep_hour = 0
            if 0 <= dep_hour < 7:
                continue  # Skip flights departing between midnight and 7 AM
        else:
            continue  # Can't find departure time, skip

        # Extract the price
        price_match = re.search(r'From\s*([0-9]+)\s*euros', flight_info)
        if price_match:
            price = float(price_match.group(1))
            if price < 25:
                price = 9999  # Consider it a mistake
        else:
            continue  # Can't find price, skip
        flight_data['price'] = price

        valid_flights.append(flight_data)
    return valid_flights

# One-way flights between all cities
for origin in cities:
    one_way_costs[origin] = {}
    one_way_flights[origin] = {}
    for destination in cities:
        if origin == destination:
            one_way_costs[origin][destination] = 9999
            one_way_flights[origin][destination] = []
            continue

        # Construct the URL for one-way flights
        url = f'https://www.google.com/travel/flights?hl=en&q=Flights%20to%20{destination}%20from%20{origin}%20on%20{start_date}%20oneway'

        try:
            response = requests.get(url)
            if response.status_code == 200:
                content = response.text
                valid_flights = extract_valid_flights(content)
                if valid_flights:
                    # Sort flights by price
                    valid_flights.sort(key=lambda x: x['price'])
                    min_price = valid_flights[0]['price']
                    one_way_costs[origin][destination] = int(min_price)
                    one_way_flights[origin][destination] = valid_flights
                    print(f"\nOne-way flights from {origin} to {destination}:")
                    for flight in valid_flights:
                        print(f"Departure: {flight['departure_time']}, Duration: {flight['duration']}, "
                              f"Layovers: {flight['layovers']}, Price: €{flight['price']}")
                else:
                    print(f"No valid flights found for one-way flight from {origin} to {destination}")
                    one_way_costs[origin][destination] = 9999
                    one_way_flights[origin][destination] = []
            else:
                print(f"Failed to retrieve content for one-way flight from {origin} to {destination}. Status code: {response.status_code}")
                one_way_costs[origin][destination] = 9999
                one_way_flights[origin][destination] = []
        except requests.exceptions.RequestException as e:
            print(f"An error occurred for one-way flight from {origin} to {destination}: {e}")
            one_way_costs[origin][destination] = 9999
            one_way_flights[origin][destination] = []

        # Sleep randomly between 3-5 seconds
        time.sleep(random.uniform(3, 5))

# Round-trip flights between all cities
for origin in cities:
    round_trip_costs[origin] = {}
    round_trip_flights[origin] = {}
    for destination in cities:
        if origin == destination:
            round_trip_costs[origin][destination] = 9999
            round_trip_flights[origin][destination] = []
            continue

        # Construct the URL for round-trip flights
        url_return = f'https://www.google.com/travel/flights?hl=en&q=Flights%20to%20{destination}%20from%20{origin}%20on%20{start_date}%20through%20{end_date}'

        try:
            response = requests.get(url_return)
            if response.status_code == 200:
                content = response.text
                valid_flights = extract_valid_flights(content)
                if valid_flights:
                    # Sort flights by price
                    valid_flights.sort(key=lambda x: x['price'])
                    min_price = valid_flights[0]['price']
                    round_trip_costs[origin][destination] = int(min_price)
                    round_trip_flights[origin][destination] = valid_flights
                    print(f"\nRound-trip flights from {origin} to {destination}:")
                    for flight in valid_flights:
                        print(f"Departure: {flight['departure_time']}, Duration: {flight['duration']}, "
                              f"Layovers: {flight['layovers']}, Price: €{flight['price']}")
                else:
                    print(f"No valid flights found for round-trip flight from {origin} to {destination}")
                    round_trip_costs[origin][destination] = 9999
                    round_trip_flights[origin][destination] = []
            else:
                print(f"Failed to retrieve content for round-trip flight from {origin} to {destination}. Status code: {response.status_code}")
                round_trip_costs[origin][destination] = 9999
                round_trip_flights[origin][destination] = []
        except requests.exceptions.RequestException as e:
            print(f"An error occurred for round-trip flight from {origin} to {destination}: {e}")
            round_trip_costs[origin][destination] = 9999
            round_trip_flights[origin][destination] = []

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
one_way_costs_file_path = os.path.join(data_folder, 'one_way_costs.json')
with open(one_way_costs_file_path, 'w') as f:
    json.dump(one_way_costs, f, indent=4)

# Save the round_trip_costs dictionary to a JSON file
round_trip_costs_file_path = os.path.join(data_folder, 'round_trip_costs.json')
with open(round_trip_costs_file_path, 'w') as f:
    json.dump(round_trip_costs, f, indent=4)

# Save the detailed flight information to JSON files
one_way_flights_file_path = os.path.join(data_folder, 'one_way_flights.json')
with open(one_way_flights_file_path, 'w') as f:
    json.dump(one_way_flights, f, indent=4)

round_trip_flights_file_path = os.path.join(data_folder, 'round_trip_flights.json')
with open(round_trip_flights_file_path, 'w') as f:
    json.dump(round_trip_flights, f, indent=4)

print("\nDictionaries have been saved to the 'data' folder.")
