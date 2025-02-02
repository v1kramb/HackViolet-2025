import { csv } from 'd3-fetch';

// Create a method that returns all of the counties for a specific state.
// This method will be used in the webapp/src/components/Map.tsx file to filter the data based on the selected state.
// Read in the csv file directly and filter the data based on the state.
export const loadStateData = async (state: string) => {
  const data = await csv('/data/census_county_data_scaled.csv');
  return data.filter((d) => d.State === state);
};