"""
Extract data from the raw CSV files, extract the desired columns, and clean the data.

This file will fetch the following data from the Census API for every county in the US:
Wanted Data:
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

import pandas as pd

# Load the raw data
dp_02 = pd.read_csv("census_data/raw_data\DP02/ACSDP1Y2023.DP02-Data.csv")
dp_03 = pd.read_csv("census_data/raw_data/DP03/ACSDP1Y2023.DP03-Data.csv")
dp_05 = pd.read_csv("census_data/raw_data/DP05/ACSDP1Y2023.DP05-Data.csv")

# Define the columns to extract
dp_02_columns = ["GEO_ID", "DP02_0067PE"]
dp_03_columns = ["GEO_ID", "DP03_0062E", "DP03_0119PE", "DP03_0009PE"]
dp_05_columns = ["GEO_ID", "DP05_0001E", "DP05_0018E", "DP05_0019E", "DP05_0077PE", "DP05_0003PE"]

# Extract the desired columns
dp_02 = dp_02[dp_02_columns]
dp_03 = dp_03[dp_03_columns]
dp_05 = dp_05[dp_05_columns]

# Merge the dataframes
df = dp_02.merge(dp_03, on="GEO_ID").merge(dp_05, on="GEO_ID")

# Rename the columns for better readability
df.columns = ["GEO_ID", "Education_Level", "Median_Household_Income", "Poverty_Rate", "Unemployment_Rate",
              "Population_Density", "Median_Age", "Average_Age", "Minority_Percentage", "Female_Percentage"]

# Save to CSV
df.to_csv("census_data/census_county_data.csv", index=False)