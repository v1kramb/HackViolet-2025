"""
Fetch all legislation passed in every state for the last year 
"""

import requests
import json
from datetime import datetime, timedelta

# LegiScan API Key (Replace with your actual API key)
API_KEY = "b35e159d59fb4138f400194dc24fcce9"

# Base URL for the LegiScan API
BASE_URL = "https://api.legiscan.com/?key=" + API_KEY

# Date range for last year
one_year_ago = datetime.strptime((datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"), "%Y-%m-%d")

# List of U.S. states (LegiScan uses abbreviations)
STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]

def get_state_id(state_name):
    """Fetches the state ID from LegiScan based on state name."""
    url = f"{BASE_URL}&op=getMasterList&state={state_name.lower()}"
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "masterlist" in data:
            return data["masterlist"]
    print(f"Error fetching state ID for {state_name}: {response.status_code}")
    return None

def fetch_legislation(state_name):
    """Fetches all passed legislation for a given state."""
    state_data = get_state_id(state_name)
    if not state_data:
        return []

    passed_bills = []
    for bill_id, bill_info in state_data.items():
        if isinstance(bill_info, dict) and "status_date" in bill_info:
            if not bill_info["status_date"]:
                continue
            bill_date = datetime.strptime(bill_info["status_date"], "%Y-%m-%d")
            if bill_date >= one_year_ago and bill_info["status"] == 4: 
                passed_bills.append(bill_info)

    return passed_bills

def main():
    all_legislation = {}

    for state in STATES:
        print(f"Fetching legislation for {state}...")
        bills = fetch_legislation(state)
        all_legislation[state] = bills

    # Save to JSON file
    with open("legislation_last_year.json", "w") as f:
        json.dump(all_legislation, f, indent=4)

    print("Legislation data saved to legislation_last_year.json")

if __name__ == "__main__":
    main()
