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

  let countyTags: string[] = $state([]);
  let stateTags: string[] = $state([]);

  import { animate } from 'motion';
  import type { CensusData } from './api/census_data/+server.js';

  let infoDiv: HTMLDivElement;

  let censusData: CensusData | null = $state(null);

  let countyData: any | null = $state(null);

  // svelte-ignore state_referenced_locally
  let localSelectedCounty: typeof selectedCounty = $state($state.snapshot(selectedCounty));

  $effect(() => {
    localSelectedCounty = selectedCounty.county ? selectedCounty : localSelectedCounty;
  });

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
    console.log(countyTags);
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

  let countyTagsVisible = $state(false);
  let stateTagsVisible = $state(false);
</script>

<svelte:window onresize={calcInfoBoxSize} />

<div class="relative flex h-full w-full flex-col overflow-hidden transition-all lg:flex-row">
  <div class="relative h-full w-full">
    <div class="relative left-0 top-0 h-full w-full">
      {#if censusData}
        <CensusMap bind:selectedCounty {censusData} {countyTags} />
      {/if}
      <div class="absolute right-0 top-0 m-4 text-sm">
        <div class="flex flex-col items-end justify-end gap-2">
          <div
            class={`${countyTagsVisible ? 'w-58' : 'w-[42px]'} float-right rounded-3xl bg-white p-2 shadow-md outline-1 outline-slate-200 transition-all duration-300 ease-in-out`}
          >
            <div class="flex w-full items-end justify-end gap-1 text-stone-800">
              <div
                class={`${countyTagsVisible ? 'w-full opacity-100' : 'w-0 opacity-0'} overflow-x-clip text-nowrap pl-[0.05rem] transition-all duration-300 ease-in-out`}
              >
                <button
                  class="rounded-xl bg-white px-2 py-1 outline-1 outline-slate-200"
                  onclick={() => {
                    countyTags = Object.keys(labels);
                  }}>ALL</button
                >
                <button
                  class="rounded-xl bg-white px-2 py-1 outline-1 outline-slate-200"
                  onclick={() => {
                    countyTags = [];
                  }}>NONE</button
                >
              </div>
              <button
                class="cursor-pointer rounded-3xl bg-stone-100 px-2 py-1 outline-1 outline-slate-200 transition-colors hover:bg-red-300 hover:outline-red-400"
                onclick={() => {
                  countyTagsVisible = !countyTagsVisible;
                }}>C</button
              >
            </div>
            <div
              class={`${countyTagsVisible ? 'h-34 w-full opacity-100' : 'h-0 w-0 opacity-0'} justify-between gap-2 overflow-clip text-nowrap transition-all duration-300 ease-in-out`}
            >
              <div class="pt-2"></div>
              <div class="flex flex-wrap">
                {#each Object.entries(labels) as [key, value]}
                  <div class="mx-0.5 my-1">
                    <input
                      type="checkbox"
                      class="peer hidden"
                      id={key}
                      bind:group={countyTags}
                      value={key}
                    />
                    <label
                      for={key}
                      class="rounded-2xl px-1.5 py-0.5 outline-1 outline-gray-300 peer-checked:bg-red-200 peer-checked:outline-red-400"
                      >{value}</label
                    >
                  </div>
                {/each}
              </div>
            </div>
          </div>
          <div
            class={`${stateTagsVisible ? 'w-58' : 'w-[42px]'} float-right rounded-3xl bg-white p-2 shadow-md outline-1 outline-slate-200 transition-all duration-300 ease-in-out`}
          >
            <div class="flex w-full items-end justify-end gap-1 text-stone-800">
              <div
                class={`${stateTagsVisible ? 'w-full opacity-100' : 'w-0 opacity-0'} overflow-x-clip text-nowrap pl-[0.05rem] transition-all duration-300 ease-in-out`}
              >
                <button
                  class="rounded-xl bg-white px-2 py-1 outline-1 outline-slate-200"
                  onclick={() => {
                    
                  }}>QUERY</button
                >
                <button
                  class="rounded-xl bg-white px-2 py-1 outline-1 outline-slate-200"
                  onclick={() => {
                    stateTags = [];
                  }}>CLEAR</button
                >
              </div>
              <button
                class="cursor-pointer rounded-3xl bg-stone-100 px-2 py-1 outline-1 outline-slate-200 transition-colors hover:bg-red-300 hover:outline-red-400"
                onclick={() => {
                  stateTagsVisible = !stateTagsVisible;
                }}>S</button
              >
            </div>
            <div
              class={`${stateTagsVisible ? 'max-h-64 min-h-20 w-full opacity-100' : 'max-h-0 w-0 opacity-0'} flex flex-col gap-2 overflow-clip text-nowrap rounded-md transition-all duration-300 ease-in-out`}
            >
              <div class="relative mt-2 px-[0.055rem]">
                <input
                  type="search"
                  bind:value={search}
                  class="w-full rounded-2xl px-2 py-1 outline-1 outline-gray-300"
                  placeholder="Add a tag..."
                  onkeydown={(e) => {
                    if (e.key === 'Enter') {
                      if (search) stateTags = [...stateTags, search];
                      search = '';
                    }
                  }}
                />
                <button
                  class="absolute right-0 top-0 m-1 aspect-square h-[calc(100%-0.5rem)] rounded-2xl bg-stone-100 outline-1 outline-slate-200 transition-colors hover:bg-red-300 hover:outline-red-400"
                  onclick={() => {
                    if (search) stateTags = [...stateTags, search];
                    search = '';
                  }}>></button
                >
              </div>
              <div class="flex flex-wrap overflow-y-scroll">
                <div class="mt-2"></div>
                {#each stateTags as tag, i}
                  <div class="mx-0.5 my-1">
                    <button
                      class="rounded-2xl px-1.5 py-0.5 outline-1 outline-gray-300"
                      onclick={() => {
                        stateTags = stateTags.filter((_, j) => i !== j);
                      }}>{tag}</button
                    >
                  </div>
                {/each}
                {#if stateTags.length === 0}
                  <div class="mx-auto mt-2 text-gray-500">No tags</div>
                {/if}
              </div>
            </div>
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
    <div class="mt-3 h-[16rem] w-full space-y-4 p-4 lg:mt-[30vh] lg:h-full lg:w-[24rem] lg:p-6">
      <h1 class="w-full text-3xl font-bold text-gray-700">
        {localSelectedCounty.county}<span class="text-gray-500"
          >, {nameToAbbrev[localSelectedCounty.state]}</span
        >
      </h1>
      {#if countyData}
        <div class="flex flex-row flex-wrap gap-2">
          {#each Object.keys(countyData) as key}
            <div
              class={`grid grid-cols-[repeat(auto-fit,minmax(auto,1fr))] items-center gap-1 rounded-3xl px-2 py-1 outline-1 ${countyTags.includes(key) ? 'bg-red-100 text-black outline-red-500' : 'text-gray-500 outline-gray-500'}`}
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

<div class="pointer-events-none absolute left-0 top-0 m-1 text-xs opacity-30">Virgil</div>
