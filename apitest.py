import requests
import json

# Define the GitHub API endpoint
url = "https://api.github.com"
# Send a GET request to the API
response = requests.get(url)

# Check if the request was successful (Status Code 200)
if response.status_code == 200:
    # Convert response to JSON and print it with indentation for readability
    data = response.json()
    first_five = dict(list(data.items())[:5])# The dict() function is used to create a new dictionary from the first five items of the original data dictionary. The list(data.items())[:5] expression retrieves the first five key-value pairs from the data dictionary as a list of tuples, and then dict() converts that list back into a dictionary format.
    print(json.dumps(first_five, indent=4))
    print(f"Successfully retrieved   data. Status code: {response.status_code}")
    #print(json.dumps(data, indent=4))# The json.dumps() function converts the Python dictionary (data) into a JSON-formatted string. The indent=4 argument makes the output more readable by adding indentation.
    #print(data.get("current_user_url"))#
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")