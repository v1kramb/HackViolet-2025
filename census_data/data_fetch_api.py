"""
This file will fetch the following data from the Census API for every county in the US:
- Population Density
- Median Age
- Median Household Income
- Poverty Rate
- Unemployment Rate
- Education Level
- Average Age
- Minority Percentage
- Female Percentage
"""

import requests
import pandas as pd
import json

# Load API key from a separate file
with open("config.json") as f:
    config = json.load(f)
    API_KEY = config["CENSUS_API_KEY"]

# Define the Census API URL
BASE_URL = "https://api.census.gov/data/2021/acs/acs5/profile"
PARAMS = {
    "get": "DP05_0001E,DP05_0018E,DP03_0062E,DP03_0119PE,DP03_0009PE,DP02_0067PE,DP05_0019E,DP05_0077PE,DP05_0003PE",
    "for": "county:*",
    "in": "state:*",
    "key": API_KEY
}

# Column mapping for better readability
# Notes: DP05, DP03, DP02 are the table IDs for the Census data
COLUMN_MAPPING = {
    "DP05_0001E": "Population_Density",
    "DP05_0018E": "Median_Age",
    "DP03_0062E": "Median_Household_Income",
    "DP03_0119PE": "Poverty_Rate",
    "DP03_0009PE": "Unemployment_Rate",
    "DP02_0067PE": "Education_Level",
    "DP05_0019E": "Average_Age",
    "DP05_0077PE": "Minority_Percentage",
    "DP05_0003PE": "Female_Percentage",
    "state": "State_FIPS",
    "county": "County_FIPS"
}

# Fetch data from Census API
response = requests.get(BASE_URL, params=PARAMS)
if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data[1:], columns=data[0])
    df.rename(columns=COLUMN_MAPPING, inplace=True)
    print(df.head())
    # Save to CSV
    df.to_csv("census_county_data.csv", index=False)
else:
    print("Error fetching data:", response.status_code, response.text)