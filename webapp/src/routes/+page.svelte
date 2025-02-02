<script lang="ts">
  import Map from '$lib/Map.svelte';
  import { AbbrevToName } from '$lib/name_to_abbrev';

  let search = '';

  let countyData: {
    county: string;
    state: string;
  } = $state({
    county: '',
    state: '',
  });

  let tags: string[] = $state([]);

  import { animate } from 'motion';

  let infoDiv: HTMLDivElement;

  const calcInfoBoxSize = () => {
    if (window.innerWidth < 1024) {
      if (countyData.county) {
        animate(infoDiv, {
          height: '20rem',
          width: '100%',
        });
      } else {
        animate(infoDiv, {
          height: '0',
          width: '100%',
        });
      }
    } else {
      if (countyData.county) {
        animate(infoDiv, {
          width: '32rem',
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

  $effect(() => {
    calcInfoBoxSize();

    if (countyData.county) {
      (async () => {
        console.log({ state: AbbrevToName[countyData.state] });
        const response = await fetch('/api/add', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            state: AbbrevToName[countyData.state].toLowerCase(),
            county: countyData.county.toLowerCase(),
          }),
        });
        const data = await response.json();
        console.log(data);
      })();
    }
  });
</script>

<svelte:window onresize={calcInfoBoxSize} />

<div class="relative flex h-full w-full flex-col transition-all lg:flex-row">
  <div class="relative h-full w-full">
    <div class="relative left-0 top-0 h-full w-full">
      <Map bind:countyData />
      <div class="absolute right-0 top-0 m-4">
        <div class="w-60 space-y-2 rounded-3xl bg-white p-2 shadow-md outline-1 outline-gray-100">
          <div class="flex items-center gap-1">
            <input
              type="text"
              class="w-full rounded-2xl border border-gray-200 p-2"
              placeholder="Add a tag"
              bind:value={search}
              onkeydown={(e) => {
                if (e.key === 'Enter') {
                  tags = [...tags, search];
                  search = '';
                  if (e.target instanceof HTMLInputElement) e.target.value = '';
                }
              }}
            />
            <button class="rounded-2xl bg-blue-500 p-2 text-white">Add</button>
          </div>
          {#each tags as tag}
            <div
              class="mt-2 flex items-center justify-between gap-2 border-t-[1px] border-gray-300 px-2 pt-2"
            >
              <span>{tag}</span>
              <button class="rounded-lg bg-red-500 text-white">Remove</button>
            </div>
          {/each}
          {#if tags.length === 0}
            <div class="text-center text-gray-500">No tags added</div>
          {/if}
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
  <div bind:this={infoDiv} class="h-0 w-full grow-0 overflow-clip lg:h-full lg:w-0">
    <div class="h-[20rem] w-full p-2 lg:h-full lg:w-[32rem]">
      <h1 class="text-3xl font-bold text-gray-700">
        {countyData.county}<span class="text-gray-500">, {countyData.state}</span>
      </h1>
    </div>
  </div>
</div>

<div class="absolute left-0 top-0">
  <h1>{countyData.county}<span>{countyData.state}</span></h1>
</div>
