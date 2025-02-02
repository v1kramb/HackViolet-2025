<script lang="ts">
  import Map from '$lib/Map.svelte';

  let search = '';

  let tags: string[] = $state([]);
</script>

<Map />

<div class="absolutee left-0 top-0">
  <h1>Hello</h1>
</div>

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

<div
  class="transform-[translateY(-50%)] pointer-events-none absolute left-0 top-[50%] m-4 h-[min(80%,40rem)]"
>
  <div
    class="h-full w-8 rounded-lg bg-gradient-to-t from-[rgb(255,0,0)] to-[rgb(0,255,0)] p-2 shadow-md outline-1 outline-gray-100"
  ></div>
</div>
