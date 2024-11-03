import requests
import re

url = 'https://www.expedia.com/Flights-Search?flight-type=on&mode=search&trip=roundtrip&leg1=from:Amsterdam,%20Netherlands%20(AMS-Schiphol),to:New%20York,%20NY,%20United%20States%20of%20America%20(JFK-John%20F.%20Kennedy%20Intl.),departure:11/17/2024TANYT,fromType:A,toType:A&leg2=from:New%20York,%20NY,%20United%20States%20of%20America%20(JFK-John%20F.%20Kennedy%20Intl.),to:Amsterdam,%20Netherlands%20(AMS-Schiphol),departure:11/24/2024TANYT,fromType:A,toType:A&options=cabinclass:economy&fromDate=11/17/2024&toDate=11/24/2024&d1=2024-11-17&d2=2024-11-24&passengers=adults:1,infantinlap:N'

try:
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Get the content of the page
        content = response.text

        # Regex pattern to capture sentences containing dollar or euro signs
        pattern = r'([A-Z][^.!?]*?[\$\€][^.!?]*?[.!?])'

        # Find all matches
        matches = re.findall(pattern, content)

        # Print the extracted sentences
        if matches:
            print("Sentences containing dollar or euro signs:")
            for match in matches:
                print(match.strip())
                print(match)
        else:
            print("No dollar or euro amounts found in the content.")

    else:
        print(f"Failed to retrieve content. Status code: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
