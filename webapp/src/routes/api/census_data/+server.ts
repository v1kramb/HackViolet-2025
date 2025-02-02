// API to get county data
import { parse } from 'csv-parse/sync';

import censusDataCsv from './census_county_data_scaled.csv?raw';
import { nameToAbbrev } from '$lib/name_to_abbrev';

// Define the CountyData type
export interface CountyData {
  State: string;
  County: string;
  data: {
    Median_Household_Income: number;
    Poverty_Rate: number;
    Unemployment_Rate: number;
    Population_Density: number;
    Median_Age: number;
    Average_Age: number;
    Minority_Percentage: number;
    Female_Percentage: number;
  };
  percentage: {
    Median_Household_Income: number;
    Poverty_Rate: number;
    Unemployment_Rate: number;
    Population_Density: number;
    Median_Age: number;
    Average_Age: number;
    Minority_Percentage: number;
    Female_Percentage: number;
  };
}

export type CensusData = {
  [key in keyof typeof nameToAbbrev]: {
    [key: string]: CountyData;
  };
};

// Handles the POST request
export async function GET() {

  const counties = getData();

  return jsonResponse(counties);
}

// Reads the CSV file and returns county data for a given state
const getData = (): CensusData => {
  const headers = [
    'State',
    'County',
    'Median_Household_Income_x',
    'Poverty_Rate_x',
    'Unemployment_Rate_x',
    'Population_Density_x',
    'Median_Age_x',
    'Average_Age_x',
    'Minority_Percentage_x',
    'Female_Percentage_x',
    'Median_Household_Income_y',
    'Poverty_Rate_y',
    'Unemployment_Rate_y',
    'Population_Density_y',
    'Median_Age_y',
    'Average_Age_y',
    'Minority_Percentage_y',
    'Female_Percentage_y',
  ];
  const data = parse(censusDataCsv, {
    delimiter: ',',
    columns: headers,
    trim: true,
  });
  const stateData: CensusData = Object.keys(nameToAbbrev).reduce((acc: any, key: string) => {
    acc[key.toLowerCase()] = data
      .filter((county: any) => county.State === key.toLowerCase())
      .reduce((a: any, county: any) => {
        a[county.County] = {
          State: county.State,
          County: county.County,
          data: {
            Median_Household_Income: county.Median_Household_Income_x,
            Poverty_Rate: county.Poverty_Rate_x,
            Unemployment_Rate: county.Unemployment_Rate_x,
            Population_Density: county.Population_Density_x,
            Median_Age: county.Median_Age_x,
            Average_Age: county.Average_Age_x,
            Minority_Percentage: county.Minority_Percentage_x,
            Female_Percentage: county.Female_Percentage_x,
          },
          percentage: {
            Median_Household_Income: county.Median_Household_Income_y,
            Poverty_Rate: county.Poverty_Rate_y,
            Unemployment_Rate: county.Unemployment_Rate_y,
            Population_Density: county.Population_Density_y,
            Median_Age: county.Median_Age_y,
            Average_Age: county.Average_Age_y,
            Minority_Percentage: county.Minority_Percentage_y,
            Female_Percentage: county.Female_Percentage_y,
          },
        };
        return a;
      }, {});
    return acc;
  }, {});
  return stateData;
};

// Returns a JSON response
const jsonResponse = (data: any) =>
  new Response(JSON.stringify(data), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
