<script lang="ts">
  import { onMount } from 'svelte';
  import '../app.css';
  import { pre } from 'motion/react-client';

  let text = '';
  const targetText = 'Virgil🔦';
  let index = 0;
  let showPreloader = true;
  let showAuthors = false;
  let fadeOut = false;

  let preloader: HTMLDivElement;

  onMount(async () => {
    // Type out "Virgil" smoothly with a shorter delay
    (async () => {for (index = 0; index < targetText.length; index++) {
      text += targetText[index];
      await new Promise((resolve) => setTimeout(resolve, 270 - (index**2 * 10))); // Shrink the delay to 80ms for faster typing
    }})();

    await new Promise((resolve) => setTimeout(resolve, 250)); // Hold "Vigil" for 2s
    showAuthors = true;

    await new Promise((resolve) => setTimeout(resolve, 1500)); // Show authors for 5s
    showPreloader = false;

    await new Promise((resolve) => setTimeout(resolve, 2400)); // Smooth fade-out transition

    preloader.remove();
  });
</script>

<slot />

<div
  bind:this={preloader}
  class={`absolute left-0 top-0 h-full w-full ${showPreloader ? 'opacity-100' : 'translate-y-10 opacity-0'} preloader transition-all  duration-1000 ease-in-out`}
>
  <!-- Removed the torchbearer div for no torch animation -->
  <h1 class="typing starting:opacity-0 opacity-100 transition-all duration-700 ease-out starting:w-0 w-fit">
    {#each text as letter}
      <span class="starting:opacity-0 opacity-100 transition-opacity duration-500 ease-out">{letter}</span>
    {/each}
  </h1>
  <div class={`${showAuthors ? 'opacity-100' : 'opacity-0'} authors transition-opacity duration-700 ease-in-out`}>
    <p class={`${showAuthors ? 'opacity-100' : 'opacity-0'} duration-700 ease-in transition-opacity text-lg font-light`}>Authors:</p>
    <p class={`${showAuthors ? 'opacity-100' : 'opacity-0'} duration-700 ease-in delay-200 transition-opacity`}>Soham Gandhi</p>
    <p class={`${showAuthors ? 'opacity-100' : 'opacity-0'} duration-700 ease-in delay-400 transition-opacity`}>Alex Lin</p>
    <p class={`${showAuthors ? 'opacity-100' : 'opacity-0'} duration-700 ease-in delay-600 transition-opacity`}>Vikram Bala</p>
  </div>
</div>

<style>
  @import url('https://fonts.googleapis.com/css2?family=Raleway:wght@300;700&display=swap');

  .preloader {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: white;
    color: black;
    font-size: 3rem;
    font-family: 'Raleway', sans-serif;
    text-align: center;
  }

  .typing {
    font-size: 4rem;
    font-weight: 700;
    text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
    border-right: 3px solid black;
    padding-right: 5px;
    animation: blinkCursor 0.8s infinite;
  }

  @keyframes blinkCursor {
    50% {
      border-color: transparent;
    }
  }

  /* Removed the .torchbearer class and moveAcross animation for the torch animation */

  .authors {
    font-size: 1.5rem;
    margin-top: 20px;
  }
</style>
