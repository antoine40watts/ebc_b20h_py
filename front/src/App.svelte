<script>
  // import { deviceData } from './stores.js';

  import IDBar from "./lib/IDBar.svelte";
  import BattState from "./lib/BattState.svelte";
  import BattChart from "./lib/BattChart.svelte";
  import BattCapacity from "./lib/BattCapacity.svelte";
  import BattControl from "./lib/BattControl.svelte";
  import ErrorModal from './lib/ErrorModal.svelte';

</script>


<main>
  <IDBar />

  <h2>Courbe de décharge</h2>
  <div class="chart-container">
    <BattChart />
  </div>

  <div>
    <div class="control-container">
      <div>
        <BattState />
      </div>
      <div class="border-left">
        <BattControl />
      </div>
      <div class="border-left">
        <BattCapacity/>
      </div>
    </div>
  </div>

  <p class="version-label">v {import.meta.env.VITE_VERSION}</p>
  <ErrorModal />
</main>



<style>
  .chart-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    height: 380px;
    margin: 25px 16px 32px 16px;
  }

  .control-container {
    display: flex;
    align-items: center;
    max-width: fit-content;
    /* justify-content: space-around; */
    margin: auto;
  }
  .control-container div {
    padding: 0px 50px 0px 50px;
  }

  .border-left {
    border-left: 1px solid rgba(10, 59, 23, 0.4);
  }

  .version-label {
    position: fixed;
    bottom: -8px;
    right: 10px;
    font-weight: bold;
  }

  h2 {
    display: none;
  }

  @media print {
    h2 {
      display: block;
      text-align: left;
    }
  }
</style>