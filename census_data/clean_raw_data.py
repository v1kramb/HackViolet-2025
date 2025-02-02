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

dp_03 = pd.read_csv("census_data/raw_data/dp_03/ACSDP5Y2023.DP03-Data.csv")
dp_05 = pd.read_csv("census_data/raw_data/dp_05/ACSDP5Y2023.DP05-Data.csv")

# Define the columns to extract
dp_03_columns = ["NAME", "DP03_0062E", "DP03_0119PE", "DP03_0009PE"]
dp_05_columns = ["NAME", "DP05_0001E", "DP05_0018E", "DP05_0019E", "DP05_0077PE", "DP05_0003PE"]

# Extract the desired columns
dp_03 = dp_03[dp_03_columns]
dp_05 = dp_05[dp_05_columns]

# Merge the dataframes
df = dp_03.merge(dp_05, on="NAME").drop(0, axis=0).replace('-', 0)
print(df.head())
print(df.columns)

# Column types
df = df.astype({
    "DP03_0062E": int,  # Median Household Income
    "DP03_0119PE": float,  # Poverty Rate
    "DP03_0009PE": float,  # Unemployment Rate
    "DP05_0001E": int,  # Population Density
    "DP05_0018E": float,  # Median Age
    "DP05_0019E": float,  # Average Age
    "DP05_0077PE": float,  # Minority Percentage
    "DP05_0003PE": float})

# Rename the columns for better readability
df.columns = ["Name", "Median_Household_Income", "Poverty_Rate", "Unemployment_Rate",
              "Population_Density", "Median_Age", "Average_Age", "Minority_Percentage", "Female_Percentage"]

# Save to CSV
df.to_csv("census_data/census_county_data.csv", index=False)

# Scale all the columns (except first one) to be between 0 and 1
df_scaled = df.copy()
for col in df_scaled.columns[1:]:
    df_scaled[col] = (df_scaled[col] - df_scaled[col].min()) / (df_scaled[col].max() - df_scaled[col].min())
    
# Split first column into county and state
df_scaled["County"] = df_scaled["Name"].apply(lambda x: x.split(",")[0])
df_scaled["State"] = df_scaled["Name"].apply(lambda x: x.split(",")[1])

# Remove the original Name column
df_scaled = df_scaled.drop("Name", axis=1)

# Make State the first column
df_scaled = df_scaled[["State", "County", "Median_Household_Income", "Poverty_Rate", "Unemployment_Rate",
                       "Population_Density", "Median_Age", "Average_Age", "Minority_Percentage", "Female_Percentage"]]

df_scaled.to_csv("census_data/census_county_data_scaled.csv", index=False)