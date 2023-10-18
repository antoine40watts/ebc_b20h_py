<script>
  // import { store } from './stores.js';

  import IDBar from "./lib/IDBar.svelte";
  import BattState from "./lib/BattState.svelte";
  import BattChart from "./lib/BattChart.svelte";
  import BattCapacity from "./lib/BattCapacity.svelte";
  import BattControl from "./lib/BattControl.svelte";

  let cells_s = 1;
  let cells_p = 1;
  $: charge_v = Math.round(cells_s * 4.20 * 100) / 100;
  // $: charge_c = cells_p * 0.5;
  $: discharge_v = Math.round(cells_s * 2.70 * 100) / 100;
  // $: discharge_c = cells_p * 0.5;

</script>


<main>
  <IDBar />

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
        <!-- <BattControl {charge_v} {charge_c} {discharge_v} {discharge_c} /> -->
        <BattCapacity/>
      </div>
    </div>
  </div>

  <p class="version-label">v {import.meta.env.VITE_VERSION}</p>
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
</style>