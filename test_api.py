import requests
from dotenv import load_dotenv
import os

# Load the .env file so we can access CRICAPI_KEY safely
load_dotenv()
api_key = os.getenv("CRICAPI_KEY")

# Build the request
url = "https://api.cricapi.com/v1/currentMatches"
params = {
    "apikey": api_key,
    "offset": 0
}

# Make the request
response = requests.get(url, params=params)
data = response.json()

# Print basic info to confirm it worked
print("Status:", data.get("status"))
print("Number of matches returned:", len(data.get("data", [])))

# Print the first match's name as a sanity check
if data.get("data"):
    print("First match:", data["data"][0].get("name"))