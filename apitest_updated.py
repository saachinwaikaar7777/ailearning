import requests
import json

# Define the GitHub API endpoint (Try changing this to a broken URL to test it!)
url = "https://api.github.com"

try:
    # Send a GET request to the API
    response = requests.get(url)
    
    # This throws an exception if the server responded with an HTTP error (4xx or 5xx)
    response.raise_for_status()
    
    # If we get here, the request was successful (Status Code 200)
    data = response.json()
    first_five = dict(list(data.items())[:5])
    print("Success! First 5 items:")
    print(json.dumps(first_five, indent=4))

except requests.exceptions.MissingSchema:
    print("Error: Incomplete or invalid URL format (missing 'http://' or 'https://').")

except requests.exceptions.ConnectionError:
    print("Error: Could not connect to the server. Check your URL spelling or internet connection.")

except requests.exceptions.HTTPError as http_err:
    # Captures specific server errors like 404 Not Found or 500 Internal Server Error
    print(f"HTTP Error occurred: Status code {response.status_code}")

except Exception as err:
    # A catch-all for any other unexpected errors
    print(f"An unexpected error occurred: {err}")