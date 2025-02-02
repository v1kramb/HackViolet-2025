<script lang="ts">
  import { onMount } from "svelte";
  import "../app.css";

  let text = "";
  const targetText = "Virgil";
  let index = 0;
  let showPreloader = true;
  let showAuthors = false;
  let fadeOut = false;

  onMount(async () => {
    // Type out "Vigil" smoothly with a shorter delay
    for (index = 0; index < targetText.length; index++) {
      text += targetText[index];
      await new Promise((resolve) => setTimeout(resolve, 80)); // Shrink the delay to 80ms for faster typing
    }

    await new Promise((resolve) => setTimeout(resolve, 300)); // Hold "Vigil" for 2s
    showAuthors = true;

    await new Promise((resolve) => setTimeout(resolve, 1000)); // Show authors for 5s
    //fadeOut = true;

    await new Promise((resolve) => setTimeout(resolve, 1000)); // Smooth fade-out transition
    showPreloader = false;
  });
</script>

{#if showPreloader}
  <main class="preloader" class:fadeOut>
    <!-- Removed the torchbearer div for no torch animation -->
    <h1 class="typing">{text}</h1>
    {#if showAuthors}
      <div class="authors">
        <p>Authors:</p>
        <p>Soham Gandhi</p>
        <p>Alex Lin</p>
        <p>Vikram Bala</p>
      </div>
    {/if}
  </main>
{:else}
  <slot />
{/if}

<style>
  @import url('https://fonts.googleapis.com/css2?family=Raleway:wght@300;700&display=swap');

  .preloader {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background: white;
    color: black;
    font-size: 3rem;
    font-family: 'Raleway', sans-serif;
    text-align: center;
    position: relative;
    transition: opacity 1.8s ease-in-out, transform 1.5s ease-in-out;
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
    50% { border-color: transparent; }
  }

  /* Removed the .torchbearer class and moveAcross animation for the torch animation */

  .authors {
    font-size: 1.5rem;
    margin-top: 20px;
  }

  .fadeIn {
    opacity: 0;
    animation: fadeIn 2s ease-in-out forwards;
  }

  .delay-1 { animation-delay: 0.5s; }
  .delay-2 { animation-delay: 1s; }
  .delay-3 { animation-delay: 1.5s; }
  .delay-4 { animation-delay: 2s; }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .fadeOut {
    opacity: 0;
    transform: scale(1.1);
    visibility: hidden;
  }
</style>
