<script lang="ts">
  import CensusMap from '$lib/CensusMap.svelte';
  import { nameToAbbrev } from '$lib/name_to_abbrev';

  let search = $state('');

  let selectedCounty: {
    county: string;
    state: string;
  } = $state({
    county: '',
    state: '',
  });

  let tags: string[] = $state([]);

  import { animate, keyframes } from 'motion';
  import type { CensusData, CountyData } from './api/census_data/+server.js';
  import countyCensusCsv from './api/census_data/census_county_data_scaled.csv?raw';

  let infoDiv: HTMLDivElement;

  let censusData: CensusData | null = $state(null);

  let countyData: any | null = $state(null);

  $effect(() => {
    (async () => {
      // console.log('fetching census data');
      censusData = await (await fetch('/api/census_data', { method: 'GET' })).json();
      // console.log(censusData);
    })();
  });

  const calcInfoBoxSize = () => {
    if (window.innerWidth < 1024) {
      if (selectedCounty.county) {
        animate(infoDiv, {
          height: '16rem',
          width: '100%',
        });
      } else {
        animate(infoDiv, {
          height: '0',
          width: '100%',
        });
      }
    } else {
      if (selectedCounty.county) {
        animate(infoDiv, {
          width: '24rem',
          height: '100%',
        });
      } else {
        animate(infoDiv, {
          width: '0',
          height: '100%',
        });
      }
    }
  };

  const curr_format = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    trailingZeroDisplay: 'stripIfInteger',
  });
  const num_format = new Intl.NumberFormat('en-US', {
    style: 'decimal',
    maximumFractionDigits: 2,
  });

  $effect(() => {
    calcInfoBoxSize();
    if (selectedCounty.county) {
      const county =
        censusData[selectedCounty.state.toLowerCase()][selectedCounty.county.toLowerCase()].data;
      countyData = {
        Median_Household_Income: curr_format.format(county.Median_Household_Income),
        Poverty_Rate: `${num_format.format(county.Poverty_Rate)}%`,
        Unemployment_Rate: `${num_format.format(county.Unemployment_Rate)}%`,
        Population_Density: num_format.format(county.Population_Density),
        Median_Age: num_format.format(county.Median_Age),
        Minority_Percentage: `${num_format.format(county.Minority_Percentage)}%`,
        Female_Percentage: `${num_format.format(county.Female_Percentage)}%`,
      };
    }
  });

  $effect(() => {
    console.log(tags);
  });

  const labels = {
    Median_Household_Income: 'Median Income',
    Poverty_Rate: 'Poverty Rate',
    Unemployment_Rate: 'Unemployment',
    Population_Density: 'Population',
    Median_Age: 'Median Age',
    Minority_Percentage: 'Minority %',
    Female_Percentage: 'Female %',
  };

  let tagsVisible = $state(true);
</script>

<svelte:window onresize={calcInfoBoxSize} />

<div class="relative flex h-full w-full flex-col overflow-hidden transition-all lg:flex-row">
  <div class="relative h-full w-full">
    <div class="relative left-0 top-0 h-full w-full">
      {#if censusData}
        <CensusMap bind:selectedCounty {censusData} bind:tags />
      {/if}
      <div class="absolute right-0 top-0 m-4 text-xs">
        <div
          class={`${tagsVisible ? 'w-full' : 'w-10'} float-right rounded-3xl bg-white p-2 shadow-md outline-1 outline-slate-200 transition-all duration-300 ease-in-out`}
        >
          <div class="flex w-full items-end justify-end gap-1 text-stone-800">
            <div
              class={`${tagsVisible ? 'w-full opacity-100' : 'w-0 opacity-0'} overflow-x-clip text-nowrap transition-all duration-300 ease-in-out`}
            >
              <button
                class="rounded-xl bg-white px-2 py-1 outline-1 outline-slate-200"
                onclick={() => {
                  tags = Object.keys(labels);
                }}>ALL</button
              >
              <button
                class="rounded-xl bg-white px-2 py-1 outline-1 outline-slate-200"
                onclick={() => {
                  tags = [];
                }}>NONE</button
              >
            </div>
            <button
              class="rounded-xl bg-stone-100 px-2 py-1 outline-1 outline-slate-200 hover:bg-red-300 hover:outline-red-400 transition-colors cursor-pointer"
              onclick={() => {
                tagsVisible = !tagsVisible;
              }}>T</button
            >
          </div>
          <div
            class={`${tagsVisible ? 'h-50 w-full opacity-100' : 'h-0 w-0 opacity-0'} flex flex-col justify-between gap-2 overflow-clip text-nowrap transition-all duration-300 ease-in-out`}
          >
            <div class="pt-1"></div>
            {#each Object.entries(labels) as [key, value]}
              <div class="flex items-center justify-between gap-2">
                <label class="relative flex cursor-pointer items-center">
                  <input
                    type="checkbox"
                    class="peer h-5 w-5 cursor-pointer appearance-none rounded-lg border border-slate-300 bg-slate-100 checked:border-red-400 checked:bg-red-400"
                    id={key}
                    bind:group={tags}
                    value={key}
                  />
                  <span
                    class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 transform text-white opacity-0 peer-checked:opacity-100"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      class="h-3.5 w-3.5"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                      stroke="currentColor"
                      stroke-width="1"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clip-rule="evenodd"
                      ></path>
                    </svg>
                  </span>
                </label>
                <label for={key}>{value}</label>
              </div>
            {/each}
          </div>
        </div>
      </div>
    </div>

    <div
      class="transform-[translateY(-50%)] pointer-events-none absolute left-0 top-[50%] m-4 flex h-[min(80%,40rem)] flex-col items-center rounded-2xl bg-white px-0.5 py-1 text-xs font-semibold text-gray-600 outline-1 outline-gray-300"
    >
      <p>100</p>
      <div
        class="bg-linear-to-t/oklab from-low to-high h-full w-8 rounded-lg p-2 shadow-md outline-1 outline-gray-100"
      ></div>
      <p>0</p>
    </div>
  </div>
  <div bind:this={infoDiv} class="h-0 w-full grow-0 lg:h-full lg:w-0">
    <div class="mt-3 h-[16rem] w-full space-y-4 p-4 lg:mt-[30vh] lg:h-full lg:w-[24rem] lg:p-2">
      <h1 class="w-full text-3xl font-bold text-gray-700">
        {selectedCounty.county}<span class="text-gray-500"
          >, {nameToAbbrev[selectedCounty.state]}</span
        >
      </h1>
      {#if countyData}
        <div class="flex flex-row flex-wrap gap-2">
          {#each Object.keys(countyData) as key}
            <div
              class={`grid grid-cols-[repeat(auto-fit,minmax(auto,1fr))] items-center gap-1 rounded-3xl px-2 py-1 outline-1 ${tags.includes(key) ? 'bg-red-100 text-black outline-red-500' : 'text-gray-500 outline-gray-500'}`}
            >
              <div>
                <span class=""
                  >{key
                    .replace('_Density', '')
                    .replaceAll('_', ' ')
                    .replaceAll('Percentage', '')}</span
                >:
                <span class="text-gray-700">{countyData[key]}</span>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>
</div>

<div class="absolute left-0 top-0">
  <h1>{selectedCounty.county}<span>{selectedCounty.state}</span></h1>
</div>
