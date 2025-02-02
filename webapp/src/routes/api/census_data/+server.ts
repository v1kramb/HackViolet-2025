// API to get county data
import { parse } from 'csv-parse';
import * as fs from 'fs';
import { dirname, resolve } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Define the CountyData type
interface CountyData {
  State: string;
  County: string;
  data: Record<string, number>;
  percentage: Record<string, number>;
}

// Handles the POST request
export async function POST({ request }: { request: Request }) {
  try {
    const { state, county } = await request.json();
    if (!state) {
      return new Response('Invalid request: State is required', { status: 400 });
    }

    const counties = await getCounties(state);
    if (county) {
      const countyData = counties.find((c) => c.County === county);
      if (!countyData) {
        return new Response('County not found', { status: 404 });
      }
      return jsonResponse(countyData);
    }

    return jsonResponse(counties);
  } catch (error) {
    console.error('Error in POST handler:', error);
    return new Response('Error getting counties', { status: 500 });
  }
}

// Reads the CSV file and returns county data for a given state
const getCounties = async (state: string): Promise<CountyData[]> => {
  const csvFilePath = resolve(__dirname, 'census_county_data_scaled.csv');
  const headers = [
    'State', 'County',
    'Median_Household_Income_x', 'Poverty_Rate_x', 'Unemployment_Rate_x', 'Population_Density_x',
    'Median_Age_x', 'Average_Age_x', 'Minority_Percentage_x', 'Female_Percentage_x',
    'Median_Household_Income_y', 'Poverty_Rate_y', 'Unemployment_Rate_y', 'Population_Density_y',
    'Median_Age_y', 'Average_Age_y', 'Minority_Percentage_y', 'Female_Percentage_y'
  ];

  const fileContent = fs.readFileSync(csvFilePath, { encoding: 'utf-8' });

  return new Promise((resolve, reject) => {
    parse(
      fileContent,
      { delimiter: ',', columns: headers, trim: true },
      (error, result) => {
        if (error) return reject(error);
        
        const filteredCounties = result.filter((county) => county.State === state).map((county) => ({
          State: county.State,
          County: county.County,
          data: extractCountyData(county, '_x'),
          percentage: extractCountyData(county, '_y'),
        }));

        resolve(filteredCounties);
      }
    );
  });
};

// Extracts numerical data from county records
const extractCountyData = (county: any, suffix: string) => ({
  Median_Household_Income: county[`Median_Household_Income${suffix}`],
  Poverty_Rate: county[`Poverty_Rate${suffix}`],
  Unemployment_Rate: county[`Unemployment_Rate${suffix}`],
  Population_Density: county[`Population_Density${suffix}`],
  Median_Age: county[`Median_Age${suffix}`],
  Average_Age: county[`Average_Age${suffix}`],
  Minority_Percentage: county[`Minority_Percentage${suffix}`],
  Female_Percentage: county[`Female_Percentage${suffix}`],
});

// Returns a JSON response
const jsonResponse = (data: any) => new Response(JSON.stringify(data), {
  status: 200,
  headers: { 'Content-Type': 'application/json' },
});
