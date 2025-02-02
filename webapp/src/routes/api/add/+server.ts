// This is the API to get the value of the counties

import { parse } from 'csv-parse';
import * as fs from 'fs';
import { dirname, resolve } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

type CountyData = {
  State: string;
  County: string;
  Median_Household_Income: number;
  Poverty_Rate: number;
  Unemployment_Rate: number;
  Population_Density: number;
  Median_Age: number;
  Average_Age: number;
  Minority_Percentage: number;
  Female_Percentage: number;
};

// Make a function that reads in the csv file and returns every county in that state with information
// about the county

// This function will take in a state and return all the counties in that state

export async function POST({ request }: { request: Request }) {
  try {
    // Parse JSON from request body
    const { state, county } = await request.json();

    if (!state) {
      return new Response('Invalid request: State is required', { status: 400 });
    }

    // Await the counties result
    const counties = await getCounties(state);

    if (county) {
      const countyData = counties.find((c) => c.County === county);
      if (!countyData) {
        return new Response('County not found', { status: 404 });
      }
      return new Response(JSON.stringify(countyData), {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
        },
      });
    }

    // Return the JSON response
    return new Response(JSON.stringify(counties), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } catch (error) {
    console.error('Error in POST handler:', error);
    return new Response('Error getting counties', { status: 500 });
  }
}

// con

const getCounties = async (state: string): Promise<CountyData[]> => {
  const csvFilePath = resolve(__dirname, 'census_county_data_scaled.csv');

  const headers = [
    'State',
    'County',
    'Median_Household_Income',
    'Poverty_Rate',
    'Unemployment_Rate',
    'Population_Density',
    'Median_Age',
    'Average_Age',
    'Minority_Percentage',
    'Female_Percentage',
  ];

  const fileContent = fs.readFileSync(csvFilePath, { encoding: 'utf-8' });

  return new Promise((resolve, reject) => {
    parse(
      fileContent,
      {
        delimiter: ',',
        columns: headers,
        trim: true,
      },
      (error, result: CountyData[]) => {
        if (error) {
          reject(error);
        } else {
          // Filter counties by state
          resolve(result.filter((county) => county.State === state));
        }
      },
    );
  });
};
